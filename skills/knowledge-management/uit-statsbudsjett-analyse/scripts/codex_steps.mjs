import { execFile } from 'node:child_process'
import { createHash } from 'node:crypto'
import { promises as fs } from 'node:fs'
import path from 'node:path'
import { promisify } from 'node:util'

const execFileAsync = promisify(execFile)
const OUTPUT_LIMIT = 32 * 1024
const SUBPROCESS_LIMIT = 8 * 1024 * 1024

export const SCRIPT_NAMES = Object.freeze({
  fetch: 'fetch_sources.py',
  extract: 'extract_documents.py',
  parse: 'parse_blaatt_hefte_table.py',
  manage: 'manage_workflow.py',
  hits: 'extract_hits.py',
  reconcile: 'reconcile_budget.py',
  frame: 'build_frame_workbook.py',
})

export class ScriptError extends Error {
  constructor(message, details = {}) {
    super(message)
    this.name = 'ScriptError'
    this.code = details.code || 'SCRIPT_FAILED'
    this.exitCode = details.exitCode ?? null
    this.signal = details.signal ?? null
    this.command = details.command || []
    this.stdout = details.stdout || ''
    this.stderr = details.stderr || ''
  }
}

function asPath(value, fallback) {
  return path.resolve(String(value || fallback))
}

export function pathsFor(a = {}) {
  const project = asPath(a.project, '/home/sihal7953/repos/uit-statsbudsjett')
  const skill = asPath(a.skill, '/home/sihal7953/repos/skills/skills/knowledge-management/uit-statsbudsjett-analyse')
  const year = Number(a.budget_year || 2025)
  const previousYear = year - 1
  const runId = String(a.run_id || `${year}-codex-v1`)
  const run = path.join(project, 'leveranser', runId)
  const sourcesDir = path.join(project, 'analyse', 'kilder', String(year))
  const basisDir = path.join(project, 'analyse', 'kilder', `saldert-${previousYear}`)
  const quickDir = path.join(run, 'hurtigsvar')
  const runtime = path.join(run, 'runtime')
  return {
    project, skill, year, previousYear, runId, run, runtime,
    runtimeScripts: path.join(runtime, 'scripts'),
    sourcesDir, basisDir,
    basisInput: path.join(basisDir, 'kilder-input.json'),
    basisJson: path.join(project, 'analyse', `saldert-${previousYear}.json`),
    uitSourcesDir: path.join(project, 'analyse', 'kilder', `uit-forutsetninger-${year}`),
    assumptionsFile: path.join(project, 'analyse', `uit-forutsetninger-${year}.md`),
    sourcesInput: path.resolve(project, String(a.sources_input || `analyse/kilder/${year}/kilder-input.json`)),
    config: path.resolve(project, String(a.config || `arbeidsflyt/arbeidsdeling-${year}.json`)),
    quickDir,
    quickInput: path.join(quickDir, 'kilder-hurtig.json'),
    tableJson: path.join(quickDir, 'blaatt-hefte-tabell.json'),
    quickWorkbook: path.join(run, `uit-ramme-${year}.xlsx`),
    quickMarkdown: path.join(run, 'hurtigsvar.md'),
    hitsDir: path.join(run, 'treff'),
    bridgeInput: path.join(project, 'analyse', `${year}-rammebro-input.json`),
    exposureLog: path.join(run, 'eksponeringslogg.md'),
    manifest: path.join(run, 'manifest.json'),
    summary: path.join(run, 'summary.json'),
    status: path.join(run, 'status.json'),
    verification: path.join(run, 'verifikasjon.md'),
  }
}

async function ensureDir(directory) {
  await fs.mkdir(directory, { recursive: true })
}

async function exists(file) {
  try {
    await fs.access(file)
    return true
  } catch {
    return false
  }
}

async function readJson(file, fallback = null) {
  try {
    return JSON.parse(await fs.readFile(file, 'utf8'))
  } catch (error) {
    if (fallback !== null && (error.code === 'ENOENT' || error instanceof SyntaxError)) return fallback
    throw error
  }
}

function truncate(value) {
  const text = String(value || '')
  return text.length <= OUTPUT_LIMIT ? text : `${text.slice(0, OUTPUT_LIMIT)}\n[… output avkortet …]`
}

function relativeToRun(file, p) {
  return path.relative(p.run, file).split(path.sep).join('/') || path.basename(file)
}

async function runScript(p, label, scriptName, scriptArgs, allowedExitCodes = [0]) {
  await ensureDir(p.runtimeScripts)
  const python = String(p.python || 'python3')
  const command = [scriptName, ...scriptArgs.map(String)]
  let result
  try {
    result = await execFileAsync(python, command, {
      shell: false,
      encoding: 'utf8',
      maxBuffer: SUBPROCESS_LIMIT,
      windowsHide: true,
    })
    result = { stdout: truncate(result.stdout), stderr: truncate(result.stderr), exitCode: 0, signal: null }
  } catch (error) {
    result = {
      stdout: truncate(error.stdout),
      stderr: truncate(error.stderr || error.message),
      exitCode: typeof error.code === 'number' ? error.code : null,
      signal: error.signal || null,
      spawnError: typeof error.code !== 'number' && !error.signal,
    }
  }
  const log = [
    `command: ${python} ${command.join(' ')}`,
    `exit_code: ${result.exitCode ?? 'null'}`,
    `signal: ${result.signal || ''}`,
    '',
    'stdout:', result.stdout || '', '',
    'stderr:', result.stderr || '', '',
  ].join('\n')
  await fs.writeFile(path.join(p.runtimeScripts, `${label}.log`), `${log}\n`, 'utf8')
  if (result.spawnError) {
    throw new ScriptError(`Kunne ikke starte ${scriptName}`, { code: 'SCRIPT_SPAWN_FAILED', ...result, command })
  }
  if (!allowedExitCodes.includes(result.exitCode)) {
    throw new ScriptError(`${scriptName} feilet med returkode ${result.exitCode}`, { ...result, command })
  }
  return result
}

function projectConfig(a, p) {
  return { ...p, python: String(a.python || 'python3') }
}

async function readSources(input) {
  const data = await readJson(input)
  if (!Array.isArray(data)) throw new Error(`Kildelisten er ikke en JSON-liste: ${input}`)
  return data
}

async function manifestRecords(directory) {
  const file = path.join(directory, 'sources.json')
  const data = await readJson(file, [])
  if (!Array.isArray(data)) throw new Error(`sources.json er ikke en liste: ${file}`)
  return data
}

async function sha256(file) {
  return createHash('sha256').update(await fs.readFile(file)).digest('hex')
}

function exactSourceMetadata(source, record) {
  return record && ['id', 'url', 'budget_year', 'stage', 'title'].every(key => source[key] === record[key])
}

/** Fetch only sources absent from an exact metadata+content match. */
export async function fetchSources(a, p, sources, outputDir, label) {
  const records = await manifestRecords(outputDir)
  const pending = []
  const reused = []
  for (const source of sources) {
    const record = records.find(item => item.id === source.id)
    const target = record?.file ? path.join(outputDir, record.file) : null
    const hashMatches = Boolean(target && await exists(target) && record.sha256 === await sha256(target))
    if (exactSourceMetadata(source, record) && hashMatches) reused.push(source.id)
    else pending.push(source)
  }
  if (pending.length) {
    const pendingFile = path.join(p.runtimeScripts, `${label}-pending.json`)
    await ensureDir(p.runtimeScripts)
    await fs.writeFile(pendingFile, `${JSON.stringify(pending, null, 2)}\n`, 'utf8')
    await runScript(p, `${label}-fetch`, path.join(p.skill, 'scripts', SCRIPT_NAMES.fetch), [pendingFile, outputDir])
  }
  const after = await manifestRecords(outputDir)
  return { records: after, fetched: pending.length, reused, pending: pending.map(source => source.id) }
}

function sourceRecordFiles(records, sources, directory) {
  const allowed = new Set(sources.map(source => source.id))
  return records
    .filter(record => allowed.has(record.id) && typeof record.file === 'string' && record.file.toLowerCase().endsWith('.pdf'))
    .map(record => {
      const pdf = path.resolve(directory, record.file)
      const root = path.resolve(directory) + path.sep
      if (!pdf.startsWith(root)) throw new Error(`Ugyldig kildefil i sources.json: ${record.file}`)
      return { record, pdf, text: pdf.replace(/\.pdf$/i, '.txt') }
    })
}

async function extractMissing(a, p, sources, directory, label) {
  const records = await manifestRecords(directory)
  const files = sourceRecordFiles(records, sources, directory)
  let written = 0
  for (const [index, item] of files.entries()) {
    if (!await exists(item.pdf)) continue
    let needsExtract = !await exists(item.text)
    if (!needsExtract) {
      const old = await fs.readFile(item.text, 'utf8')
      needsExtract = !old.includes(`SHA-256: ${item.record.sha256}`)
    }
    if (needsExtract) {
      await runScript(p, `${label}-extract-${index + 1}`, path.join(p.skill, 'scripts', SCRIPT_NAMES.extract), [item.pdf, '--output', item.text])
      written += 1
    }
  }
  return { files, written }
}

function appendExposure(p, phase, lines) {
  return (async () => {
    await ensureDir(p.run)
    const header = `# Eksponeringslogg\n\n- Kjøring: ${p.runId}\n- Budsjettår: ${p.year}\n- Startet: ${p.started}\n- Forbudte mapper: ${p.forbidden.join(', ') || 'ingen oppgitt'}\n\n`
    let current = await exists(p.exposureLog) ? await fs.readFile(p.exposureLog, 'utf8') : header
    if (!current.includes(`## ${phase}`)) current += `\n## ${phase}\n\n`
    const body = lines.filter(Boolean).map(line => `- ${line}`).join('\n')
    if (body && !current.includes(body)) current += `${body}\n`
    await fs.writeFile(p.exposureLog, current.endsWith('\n') ? current : `${current}\n`, 'utf8')
  })()
}

function runtimePaths(a) {
  const base = pathsFor(a)
  return {
    ...base,
    python: String(a.python || 'python3'),
    started: String(a.run_started_utc || 'unknown'),
    forbidden: Array.isArray(a.forbidden_dirs) ? a.forbidden_dirs : [`${base.year}/`],
  }
}

export async function prepareBasis(a = {}) {
  const p = runtimePaths(a)
  await ensureDir(p.run)
  const problems = []
  let basisPdf = null
  let table = null
  let uitCount = 0
  if (await exists(p.basisInput)) {
    const sources = await readSources(p.basisInput)
    const fetched = await fetchSources(a, p, sources, p.basisDir, 'basis')
    const extracted = await extractMissing(a, p, sources, p.basisDir, 'basis')
    const records = fetched.records
    const pdfs = sourceRecordFiles(records, sources, p.basisDir)
    basisPdf = pdfs[0]?.pdf || null
    if (pdfs[0]?.text) {
      const result = await runScript(p, 'basis-parse', path.join(p.skill, 'scripts', SCRIPT_NAMES.parse), [pdfs[0].text, '--output', p.basisJson], [0, 2])
      if (result.exitCode === 2) problems.push('Hovedtabellen eller UiT-raden for basisåret ble ikke funnet.')
      table = await readJson(p.basisJson, null)
    }
    uitCount = sources.length
    await appendExposure(p, 'Grunnlag', [`Hentet basis-kilder: ${sources.map(source => source.id).join(', ') || 'ingen'} (ikke lest av denne helperen).`, `Uttrekk skrevet: ${extracted.written}.`])
  } else {
    problems.push(`Grunnlaget for ${p.previousYear} er ikke tilgjengelig: ${relativeToRun(p.basisInput, p)}.`)
  }
  if (await exists(p.uitSourcesDir) && !await exists(p.assumptionsFile)) {
    const input = path.join(p.uitSourcesDir, 'kilder-input.json')
    if (await exists(input)) {
      const sources = await readSources(input)
      const fetched = await fetchSources(a, p, sources, p.uitSourcesDir, 'uit')
      const extracted = await extractMissing(a, p, sources, p.uitSourcesDir, 'uit')
      uitCount = sources.length
      await appendExposure(p, 'UiT-forutsetninger', [`Hentet UiT-kilder: ${sources.map(source => source.id).join(', ') || 'ingen'} (ikke lest av denne helperen).`, `Uttrekk skrevet: ${extracted.written}.`])
    }
  }
  const uit = table?.uit
  return {
    vedtatt_pdf: basisPdf,
    vedtatt_total_nok_thousand: Array.isArray(uit?.values) ? (uit.values.at(-1) ?? null) : null,
    table_pdf_page: table?.pdf_page ?? null,
    column_count: table?.column_count ?? null,
    basis_json: await exists(p.basisJson) ? p.basisJson : null,
    uit_documents_fetched: uitCount,
    problems,
  }
}

export async function prepareQuick(a = {}) {
  const p = runtimePaths(a)
  await ensureDir(p.quickDir)
  const sources = await readSources(p.sourcesInput)
  const wantedIds = [`blaatt-hefte-forslag-${p.year}`, `kd-prop-${p.year}`]
  const selected = wantedIds.map(id => sources.find(source => source.id === id)).filter(Boolean)
  const missing = wantedIds.filter(id => !selected.some(source => source.id === id))
  if (missing.length) {
    const error = new Error(`Manglende hurtigkilde: ${missing.join(', ')}`)
    error.code = 'MISSING_QUICK_SOURCE'
    error.missing = missing
    throw error
  }
  await fs.writeFile(p.quickInput, `${JSON.stringify(selected, null, 2)}\n`, 'utf8')
  const fetched = await fetchSources(a, p, selected, p.sourcesDir, 'quick')
  const extracted = await extractMissing(a, p, selected, p.sourcesDir, 'quick')
  const blue = fetched.records.find(record => record.id === wantedIds[0])
  const blueText = path.join(p.sourcesDir, blue.file.replace(/\.pdf$/i, '.txt'))
  const parseResult = await runScript(p, 'quick-parse', path.join(p.skill, 'scripts', SCRIPT_NAMES.parse), [blueText, '--output', p.tableJson], [0, 2])
  const table = await readJson(p.tableJson, {})
  const problems = []
  if (parseResult.exitCode === 2 || !table.uit) problems.push('UiT-raden ble ikke funnet i hovedtabellen.')
  const result = {
    blaatt_hefte_pdf: path.join(p.sourcesDir, blue.file),
    blaatt_hefte_sha256: blue.sha256,
    table_json: p.tableJson,
    table_pdf_page: table.pdf_page ?? null,
    uit_row_found: Boolean(table.uit),
    column_count: table.column_count ?? null,
    basis_available: await exists(p.basisJson),
    assumptions_available: await exists(p.assumptionsFile),
    problems,
  }
  await appendExposure(p, 'Hurtigsvar', [`Hentet hurtigkilder: ${selected.map(source => source.id).join(', ')} (ikke lest av denne helperen).`, `Uttrekk skrevet: ${extracted.written}.`])
  return result
}

export async function prepareDepartments(a = {}) {
  const p = runtimePaths(a)
  await ensureDir(p.run)
  const allSources = await readSources(p.sourcesInput)
  const quickIds = new Set([`blaatt-hefte-forslag-${p.year}`, `kd-prop-${p.year}`])
  const remaining = allSources.filter(source => !quickIds.has(source.id))
  let fetched = { records: await manifestRecords(p.sourcesDir), fetched: 0 }
  let extracted = { written: 0 }
  if (remaining.length) {
    fetched = await fetchSources(a, p, remaining, p.sourcesDir, 'departments')
    extracted = await extractMissing(a, p, remaining, p.sourcesDir, 'departments')
  }
  const missing = []
  const quickAnswerPresent = await exists(p.quickMarkdown) && await exists(p.quickWorkbook)
  if (!quickAnswerPresent) missing.push(`Mangler hurtigsvar: ${relativeToRun(p.quickMarkdown, p)} eller arbeidsbok.`)
  const configPresent = await exists(p.config)
  if (!configPresent) missing.push(`Mangler arbeidsdeling: ${p.config}`)
  let workOrdersWritten = 0
  let hitsPerPart = {}
  if (configPresent) {
    await runScript(p, 'departments-prepare', path.join(p.skill, 'scripts', SCRIPT_NAMES.manage), ['prepare', p.config, '--project', p.project])
    const hitResult = await runScript(p, 'departments-hits', path.join(p.skill, 'scripts', SCRIPT_NAMES.hits), [p.config, '--sources-dir', p.sourcesDir, '--output', p.hitsDir, '--year', String(p.year)], [0, 3])
    if (hitResult.exitCode === 3) missing.push('Ett eller flere forventede kildeuttrekk mangler.')
    const config = await readJson(p.config)
    workOrdersWritten = Array.isArray(config.roles) ? config.roles.length : 0
    for (const role of config.roles || []) {
      for (const part of role.parts || []) {
        const file = path.join(p.hitsDir, `${part}-treff.json`)
        const data = await readJson(file, null)
        hitsPerPart[part] = data ? Object.values(data.files || {}).reduce((sum, hits) => sum + hits.length, 0) : 0
      }
    }
  }
  await appendExposure(p, 'Departementer', [`Hentet resterende kilder: ${remaining.map(source => source.id).join(', ') || 'ingen'}.`, `Uttrekk skrevet: ${extracted.written}.`])
  return {
    quick_answer_present: quickAnswerPresent,
    sources_fetched: fetched.fetched,
    sources_failed: [],
    extracts_written: extracted.written,
    work_orders_written: workOrdersWritten,
    hits_per_part: hitsPerPart,
    exposure_log: p.exposureLog,
    missing,
  }
}

async function walkFiles(directory) {
  const result = []
  if (!await exists(directory)) return result
  for (const entry of await fs.readdir(directory, { withFileTypes: true })) {
    const file = path.join(directory, entry.name)
    if (entry.isDirectory()) result.push(...await walkFiles(file))
    else result.push(file)
  }
  return result
}

async function externalEntries(p) {
  const candidates = [p.sourcesInput, p.config, p.assumptionsFile, p.bridgeInput]
  for (const directory of [p.sourcesDir, p.basisDir, p.uitSourcesDir]) {
    const manifest = path.join(directory, 'sources.json')
    candidates.push(manifest)
    const records = await readJson(manifest, [])
    for (const record of records) if (record.file) candidates.push(path.join(directory, record.file))
  }
  const unique = [...new Set(candidates.map(file => path.resolve(file)))]
  const entries = []
  for (const file of unique.sort()) {
    if (!await exists(file)) continue
    entries.push({ path: file, sha256: await sha256(file), bytes: (await fs.stat(file)).size })
  }
  return entries
}

async function bridgeComparison(p) {
  const quickFile = path.join(p.quickDir, 'rammebro-kontroll.json')
  const roleFile = path.join(p.run, 'deler', 'kd_ramme', 'ramme', 'rammebro-kontroll.json')
  const result = { quick: quickFile, role: roleFile, comparable: false, equal: false, issues: [] }
  const quick = await exists(quickFile) ? await readJson(quickFile, null) : null
  const role = await exists(roleFile) ? await readJson(roleFile, null) : null
  if (!quick || !role) {
    if (await exists(quickFile) || await exists(roleFile)) result.issues.push('Mangler en av hurtigsvar- og rollebrokontrollene.')
    return result
  }
  result.comparable = true
  const keys = ['opening', 'expected_total', 'proposed_total', 'expected_residual', 'proposed_residual', 'difference_residual']
  const valid = value => (typeof value === 'number' || typeof value === 'string') && String(value).trim() !== '' && Number.isFinite(Number(value))
  result.comparable = keys.every(key => valid(quick[key]) && valid(role[key]))
  result.equal = result.comparable && keys.every(key => Number(quick[key]) === Number(role[key]))
  if (quick.status !== 'avstemt' || role.status !== 'avstemt' || keys.slice(3).some(key => Number(quick[key]) !== 0 || Number(role[key]) !== 0)) result.issues.push('En rammebro er ufullstendig eller har rest.')
  if (!result.equal) result.issues.push('Hurtigsvarbroen og kd_ramme-broen har ulike kontrollverdier.')
  result.quick_values = Object.fromEntries(keys.map(key => [key, quick[key] ?? null]))
  result.role_values = Object.fromEntries(keys.map(key => [key, role[key] ?? null]))
  return result
}

async function visualCheck(p) {
  const file = path.join(p.run, 'visuell-kontroll.json')
  if (!await exists(file)) return { present: false, approved: false, issues: ['Mangler visuell-kontroll.json.'] }
  let data
  try { data = await readJson(file) } catch { return { present: true, approved: false, issues: ['visuell-kontroll.json er ugyldig JSON.'] } }
  const issues = []
  if (data?.approved !== true) issues.push('Visuell kontroll er ikke godkjent.')
  if (!Array.isArray(data?.inspected_slide_images) || !data.inspected_slide_images.length) issues.push('Visuell kontroll mangler inspiserte lysbilder.')
  if (typeof data?.pptx !== 'string' || path.isAbsolute(data.pptx) || data.pptx.split(/[\\/]/).includes('..')) issues.push('Visuell kontroll har ikke en relativ PPTX-sti.')
  let pptx = null
  if (typeof data?.pptx === 'string' && !path.isAbsolute(data.pptx) && !data.pptx.split(/[\\/]/).includes('..')) {
    pptx = path.resolve(p.run, data.pptx)
    if (pptx !== path.resolve(p.run, `statsbudsjettet-${p.year}.pptx`)) issues.push('Visuell kontroll peker på feil PPTX.')
    else if (!await exists(pptx)) issues.push('PPTX fra visuell kontroll finnes ikke.')
  }
  for (const image of Array.isArray(data?.inspected_slide_images) ? data.inspected_slide_images : []) {
    if (typeof image !== 'string' || path.isAbsolute(image) || image.split(/[\\/]/).includes('..') || !image.toLowerCase().endsWith('.png')) {
      issues.push(`Ugyldig lysbildebilde i visuell kontroll: ${image}`)
      continue
    }
    if (!await exists(path.resolve(p.run, image))) issues.push(`Mangler lysbildebilde: ${image}`)
  }
  return { present: true, approved: issues.length === 0, pptx, issues }
}

async function mergeExposureFragments(p) {
  const candidates = (await walkFiles(p.runtime)).filter(file => path.basename(file).toLowerCase() === 'exposure.md').sort()
  const files = []
  for (const file of candidates) if ((await fs.readFile(file, 'utf8')).trim()) files.push(file)
  const metadataFiles = (await walkFiles(p.runtime)).filter(file => path.basename(file) === 'metadata.json').sort()
  const missingMetadataExposure = []
  for (const metadata of metadataFiles) {
    const exposure = path.join(path.dirname(metadata), 'exposure.md')
    if (!await exists(exposure) || !(await fs.readFile(exposure, 'utf8')).trim()) missingMetadataExposure.push(relativeToRun(exposure, p))
  }
  let base = await exists(p.exposureLog) ? await fs.readFile(p.exposureLog, 'utf8') : `# Eksponeringslogg\n\n- Kjøring: ${p.runId}\n- Budsjettår: ${p.year}\n- Startet: ${p.started}\n\n`
  const startup = path.join(p.run, 'oppstart-eksponering.md')
  if (await exists(startup)) {
    const startupText = await fs.readFile(startup, 'utf8')
    const startupSection = `## Oppstart\n\n${startupText.trim()}\n`
    if (!base.includes(startupSection)) base += `\n${startupSection}`
  }
  const marker = '\n## Fagrolleksponering\n'
  const index = base.indexOf(marker)
  if (index >= 0) base = base.slice(0, index).replace(/\s*$/, '\n')
  const sections = (await Promise.all(files.map(async file => `### ${path.relative(p.runtime, file).split(path.sep).join('/')}\n\n${(await fs.readFile(file, 'utf8')).trim()}\n`))).join('\n')
  if (sections) base += `${marker}\n${sections}`
  if (!base.includes('Loggen er fryst før fasit.')) base += '\nLoggen er fryst før fasit.\n'
  await fs.writeFile(p.exposureLog, base.endsWith('\n') ? base : `${base}\n`, 'utf8')
  return { files, count: files.length, metadataFiles, missingMetadataExposure }
}

function hasRuntimeFailure(summary, checks) {
  if (summary?.runtime_failure || summary?.runtime_failed) return true
  if (Array.isArray(summary?.failures) && summary.failures.length) return true
  if (Array.isArray(summary?.runtime_failures) && summary.runtime_failures.length) return true
  if (Array.isArray(summary?.not_delivered) && summary.not_delivered.length) return true
  return checks.some(check => check.exitCode !== 0 && check.exitCode !== 2)
}

function stable(value) {
  if (Array.isArray(value)) return value.map(stable)
  if (value && typeof value === 'object') return Object.fromEntries(Object.keys(value).sort().map(key => [key, stable(value[key])]))
  return value
}

export async function finalize(a = {}, summary = {}) {
  const p = runtimePaths(a)
  await ensureDir(p.run)
  const scriptChecks = []
  const checkIssues = []
  let incompleteCheck = false
  if (await exists(p.config)) {
    try {
      const result = await runScript(p, 'final-manage-check', path.join(p.skill, 'scripts', SCRIPT_NAMES.manage), ['check', p.config, '--project', p.project, '--output', path.join(p.run, 'kontroll.json')], [0, 2])
      scriptChecks.push({ name: 'manage_workflow check', exitCode: result.exitCode })
      incompleteCheck = result.exitCode === 2
      const check = await readJson(path.join(p.run, 'kontroll.json'), {})
      if (typeof check.ready !== 'boolean') checkIssues.push('Leveransekontrollen mangler gyldig resultatfil.')
      else if (!check.ready) incompleteCheck = true
      if (Array.isArray(check.issues)) checkIssues.push(...check.issues)
    } catch (error) {
      scriptChecks.push({ name: 'manage_workflow check', exitCode: error.exitCode ?? null, error: error.message })
      checkIssues.push(error.message)
    }
  } else {
    checkIssues.push(`Mangler arbeidsdeling: ${p.config}`)
  }
  const frameInput = path.join(p.quickDir, 'rammeark-input.json')
  if (await exists(frameInput)) {
    try {
      const result = await runScript(p, 'final-frame', path.join(p.skill, 'scripts', SCRIPT_NAMES.frame), [frameInput, '--output', path.join(p.quickDir, 'kontroll-uit-ramme.xlsx')], [0])
      scriptChecks.push({ name: 'build_frame_workbook', exitCode: result.exitCode })
    } catch (error) {
      scriptChecks.push({ name: 'build_frame_workbook', exitCode: error.exitCode ?? null, error: error.message })
      checkIssues.push(error.message)
    }
  } else checkIssues.push(`Mangler rammeinput: ${frameInput}`)
  if (await exists(p.bridgeInput)) {
    try {
      const result = await runScript(p, 'final-reconcile', path.join(p.skill, 'scripts', SCRIPT_NAMES.reconcile), [p.bridgeInput, '--output', path.join(p.quickDir, 'rammebro-kontroll.json')], [0, 2])
      scriptChecks.push({ name: 'reconcile_budget', exitCode: result.exitCode })
      if (result.exitCode !== 0) checkIssues.push(`Rammebro-kontrollen returnerte ${result.exitCode}.`)
    } catch (error) {
      scriptChecks.push({ name: 'reconcile_budget', exitCode: error.exitCode ?? null, error: error.message })
      checkIssues.push(error.message)
    }
  } else checkIssues.push(`Mangler rammebro-input: ${p.bridgeInput}`)
  const exposure = await mergeExposureFragments(p)
  const expectedPptx = path.join(p.run, `statsbudsjettet-${p.year}.pptx`)
  const pptxPresent = await exists(expectedPptx) || Boolean(summary?.editor?.pptx && await exists(summary.editor.pptx))
  const visual = await visualCheck(p)
  const visualQa = visual.approved
  const bridge = await bridgeComparison(p)
  const issues = [...checkIssues]
  if (summary?.preparation?.missing?.length) issues.push(...summary.preparation.missing)
  if (summary?.roles?.some(role => role.parts?.some(part => part.source_missing))) issues.push('En fagrolle mangler primærkilde.')
  if (!pptxPresent) issues.push('Mangler PowerPoint-fil.')
  if (!visualQa) issues.push(...visual.issues)
  if (!bridge.comparable) issues.push('Mangler sammenlignbare rammebrokontroller.')
  issues.push(...bridge.issues)
  const roleIds = Array.isArray(a.roles) ? a.roles.map(role => String(role.id)) : []
  const workflowDirs = [...new Set(exposure.metadataFiles.map(file => path.dirname(path.dirname(file))))]
  const expectedRoleLogs = roleIds.map(roleId => {
    const found = exposure.files.find(file => path.basename(path.dirname(file)) === `rolle_${roleId}`)
    return found || path.join(workflowDirs[0] || p.runtime, `rolle_${roleId}`, 'exposure.md')
  })
  const missingRoleLogs = []
  for (const file of expectedRoleLogs) {
    if (!await exists(file) || !(await fs.readFile(file, 'utf8')).trim()) missingRoleLogs.push(relativeToRun(file, p))
  }
  if (!exposure.count || missingRoleLogs.length) {
    issues.push(`Mangler eksponeringslogger fra fagroller${missingRoleLogs.length ? `: ${missingRoleLogs.join(', ')}` : '.'}`)
  }
  if (exposure.missingMetadataExposure.length) issues.push(`Runtime-kall mangler eksponeringslogg: ${exposure.missingMetadataExposure.join(', ')}`)
  if (hasRuntimeFailure(summary, scriptChecks)) issues.push('En runtime- eller skriptfase feilet.')
  const ready = issues.length === 0 && !incompleteCheck
  const status = stable({
    workflow: 'uit-statsbudsjett', run_id: p.runId, ready, incomplete_check: incompleteCheck,
    issues, exposure_role_logs: exposure.count, visual_qa: visualQa,
    pptx_present: pptxPresent, bridge_comparison: bridge, script_checks: scriptChecks,
  })
  await fs.writeFile(p.summary, `${JSON.stringify(stable({ ...summary, finalize: status }), null, 2)}\n`, 'utf8')
  await fs.writeFile(p.status, `${JSON.stringify(status, null, 2)}\n`, 'utf8')
  await fs.writeFile(p.verification, [
    `# Verifikasjon`, '', `Kjøring: ${p.runId}`, `Budsjettår: ${p.year}`, '',
    `Status: ${ready ? 'klar' : 'ufullstendig'}.`,
    `manage_workflow check: ${incompleteCheck ? 'ufullstendig (returkode 2)' : 'kontrollert'}.`,
    `Eksponeringslogger fra fagroller: ${exposure.count}.`,
    `PowerPoint til stede: ${pptxPresent}. Visuell QA-kvittering: ${visualQa}.`, '',
    'Skriptkontroller:', ...scriptChecks.map(check => `- ${check.name}: returkode ${check.exitCode ?? 'ukjent'}.`), '',
    'Denne kontrollen beviser ikke faglig riktighet eller visuell kvalitet.', '',
  ].join('\n'), 'utf8')
  const files = (await walkFiles(p.run)).filter(file => path.resolve(file) !== path.resolve(p.manifest)).sort()
  const external = await externalEntries(p)
  const skillEntry = { path: path.join(p.skill, 'SKILL.md'), sha256: await sha256(path.join(p.skill, 'SKILL.md')) }
  const manifest = {
    run_id: p.runId,
    created_at_utc: p.started,
    files: await Promise.all(files.map(async file => ({ path: relativeToRun(file, p), sha256: await sha256(file), bytes: (await fs.stat(file)).size }))),
    skill: skillEntry,
    external_files: [skillEntry, ...external],
  }
  await fs.writeFile(p.manifest, `${JSON.stringify(manifest, null, 2)}\n`, 'utf8')
  return { ...status, summary: p.summary, verification: p.verification, manifest: p.manifest }
}
