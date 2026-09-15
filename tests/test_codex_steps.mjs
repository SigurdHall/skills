import assert from 'node:assert/strict'
import { chmod, mkdir, mkdtemp, readFile, writeFile } from 'node:fs/promises'
import { createHash } from 'node:crypto'
import { tmpdir } from 'node:os'
import path from 'node:path'
import test from 'node:test'

import { fetchSources, finalize, prepareQuick } from '../skills/knowledge-management/uit-statsbudsjett-analyse/scripts/codex_steps.mjs'

const skill = path.resolve('skills/knowledge-management/uit-statsbudsjett-analyse')

async function fakePython(directory, exitCode = 0) {
  const file = path.join(directory, 'fake-python')
  await writeFile(file, `#!/bin/sh
name=$(basename "$1")
if [ "$name" = "fetch_sources.py" ]; then exit ${exitCode}; fi
if [ "$name" = "extract_documents.py" ]; then printf '# Kilde: fake\\n' > "$4"; exit 0; fi
if [ "$name" = "parse_blaatt_hefte_table.py" ]; then printf '{"pdf_page": 3, "column_count": 6, "uit": {"institution": "UiT", "values": [1, 2, 3, 4, 5, 15]}}\\n' > "$4"; exit 0; fi
if [ "$name" = "manage_workflow.py" ]; then exit 2; fi
exit 0
`)
  await chmod(file, 0o755)
  return file
}

function source(id, year, url = `https://example.test/${id}.pdf`) {
  return { id, url, budget_year: year, stage: 'forslag', title: id }
}

async function archiveSource(directory, item, content = '%PDF-1.7\nfake\n') {
  const pdf = path.join(directory, `${item.id}.pdf`)
  await writeFile(pdf, content)
  const digest = createHash('sha256').update(content).digest('hex')
  const record = { ...item, file: `${item.id}.pdf`, effective_url: item.url, retrieved_at_utc: '2026-09-15T00:00:00+00:00', sha256: digest, bytes: Buffer.byteLength(content), classification_verified: false }
  return record
}

test('reuses a source only when metadata and PDF hash match', async () => {
  const root = await mkdtemp(path.join(tmpdir(), 'codex-steps-'))
  const directory = path.join(root, 'sources')
  const runtime = path.join(root, 'runtime')
  await mkdir(directory)
  await mkdir(runtime, { recursive: true })
  const item = source('blaatt-hefte-forslag-2025', 2025)
  const record = await archiveSource(directory, item)
  await writeFile(path.join(directory, 'sources.json'), `${JSON.stringify([record])}\n`)
  const p = { ...{
    runtimeScripts: runtime, skill, python: await fakePython(root, 19), run: root,
  } }
  const reused = await fetchSources({}, p, [item], directory, 'reuse')
  assert.deepEqual(reused.reused, [item.id])
  const changed = { ...item, title: 'changed' }
  await assert.rejects(() => fetchSources({}, p, [changed], directory, 'mismatch'), error => error.exitCode === 19)
})

test('quick preparation writes only the two required source ids and fails when one is absent', async () => {
  const root = await mkdtemp(path.join(tmpdir(), 'codex-steps-'))
  const project = path.join(root, 'project')
  const sourcesDir = path.join(project, 'analyse', 'kilder', '2025')
  await mkdir(sourcesDir, { recursive: true })
  const selected = [source('blaatt-hefte-forslag-2025', 2025), source('kd-prop-2025', 2025)]
  const records = []
  for (const item of selected) records.push(await archiveSource(sourcesDir, item))
  await writeFile(path.join(sourcesDir, 'sources.json'), `${JSON.stringify(records)}\n`)
  const input = path.join(project, 'analyse', 'kilder-input.json')
  await writeFile(input, JSON.stringify([...selected, source('fin-skatt-prop-2025', 2025)]))
  const fake = await fakePython(root)
  const result = await prepareQuick({ project, skill, python: fake, budget_year: 2025, run_id: 'run-1', sources_input: 'analyse/kilder-input.json' })
  assert.equal(result.uit_row_found, true)
  assert.deepEqual(JSON.parse(await readFile(path.join(project, 'leveranser/run-1/hurtigsvar/kilder-hurtig.json'))).map(item => item.id), selected.map(item => item.id))
  await writeFile(input, JSON.stringify([selected[0]]))
  await assert.rejects(() => prepareQuick({ project, skill, python: fake, budget_year: 2025, run_id: 'run-2', sources_input: 'analyse/kilder-input.json' }), error => error.code === 'MISSING_QUICK_SOURCE')
})

test('finalize records incomplete manage check and produces a stable manifest', async () => {
  const root = await mkdtemp(path.join(tmpdir(), 'codex-steps-'))
  const project = path.join(root, 'project')
  await mkdir(path.join(project, 'arbeidsflyt'), { recursive: true })
  await writeFile(path.join(project, 'arbeidsflyt', 'arbeidsdeling-2025.json'), '{}')
  const fake = await fakePython(root)
  const args = { project, skill, python: fake, budget_year: 2025, run_id: 'run-1', run_started_utc: '2026-09-15T00:00:00Z', config: 'arbeidsflyt/arbeidsdeling-2025.json' }
  const first = await finalize(args, { runtime_failure: false })
  const manifest1 = await readFile(first.manifest, 'utf8')
  const second = await finalize(args, { runtime_failure: false })
  assert.equal(second.ready, false)
  assert.match(await readFile(path.join(project, 'leveranser/run-1/status.json'), 'utf8'), /incomplete_check/)
  assert.equal(await readFile(second.manifest, 'utf8'), manifest1)
})

test('complete fixture passes only with matching bridges, role log and explicit visual review', async () => {
  const root = await mkdtemp(path.join(tmpdir(), 'codex-final-'))
  const run = path.join(root, 'leveranser/codex-test')
  const quick = path.join(run, 'hurtigsvar')
  const role = path.join(run, 'deler/kd_ramme/ramme')
  const call = path.join(run, 'runtime/departementer/rolle_kd_ramme')
  for (const folder of [quick, role, call, path.join(root, 'analyse')]) await mkdir(folder, { recursive: true })
  const bridge = { opening: 100, expected_total: 110, proposed_total: 115, expected_residual: '0', proposed_residual: '0', difference_residual: '0', status: 'avstemt' }
  const python = path.join(root, 'fake-python')
  await writeFile(python, `#!/bin/sh
case "$1" in
  *manage_workflow.py) printf '%s' '{"ready":true,"issues":[]}' > "$7" ;;
  *reconcile_budget.py) printf '%s' '${JSON.stringify(bridge)}' > "$4" ;;
  *build_frame_workbook.py) printf 'synthetic workbook' > "$4" ;;
esac
`)
  await chmod(python, 0o755)
  const files = {
    'arbeidsdeling.json': '{}',
    'hurtigsvar/rammeark-input.json': '{}',
    'deler/kd_ramme/ramme/rammebro-kontroll.json': JSON.stringify(bridge),
    'runtime/departementer/rolle_kd_ramme/metadata.json': '{"label":"rolle:kd_ramme","status":"succeeded"}',
    'runtime/departementer/rolle_kd_ramme/exposure.md': 'Ingen UiT-dokumenter: syntetisk test.',
    'oppstart-eksponering.md': 'Publiseringssjekk: syntetisk.',
    'statsbudsjettet-2025.pptx': 'synthetic pptx placeholder',
    'lysark-01.png': 'synthetic png placeholder',
    'visuell-kontroll.json': JSON.stringify({ pptx: 'statsbudsjettet-2025.pptx', approved: true, inspected_slide_images: ['lysark-01.png'] }),
  }
  for (const [file, content] of Object.entries(files)) await writeFile(path.join(run, file), content)
  await writeFile(path.join(root, 'analyse/2025-rammebro-input.json'), '{}')
  const a = { project: root, skill, python, budget_year: 2025, run_id: 'codex-test', config: 'leveranser/codex-test/arbeidsdeling.json', roles: [{ id: 'kd_ramme' }] }
  const result = await finalize(a, {})
  assert.deepEqual(result.issues, [])
  assert.equal(result.ready, true)
  const manifest = JSON.parse(await readFile(result.manifest, 'utf8'))
  for (const record of manifest.files) assert.equal(createHash('sha256').update(await readFile(path.join(run, record.path))).digest('hex'), record.sha256)
  await writeFile(path.join(role, 'rammebro-kontroll.json'), JSON.stringify({ ...bridge, proposed_total: 116 }))
  await writeFile(path.join(run, 'visuell-kontroll.json'), '{"approved":true,"inspected_slide_images":7}')
  const invalid = await finalize(a, {})
  assert.equal(invalid.ready, false)
  assert.ok(invalid.issues.some(s => s.includes('ulike kontrollverdier')))
  assert.ok(invalid.issues.some(s => s.includes('lysbilder')))
})
