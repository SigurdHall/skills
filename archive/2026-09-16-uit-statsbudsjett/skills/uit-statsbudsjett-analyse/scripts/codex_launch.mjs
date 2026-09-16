import { readFile, writeFile, mkdir, readdir, stat, open, rm } from 'node:fs/promises';
import { spawn } from 'node:child_process';
import { fileURLToPath, pathToFileURL } from 'node:url';
import path from 'node:path';

const skill = fileURLToPath(new URL('..', import.meta.url));
const repo = path.resolve(skill, '../../..');
const efforts = ['low', 'medium', 'high', 'xhigh'];
const plans = {
  ramme: {
    assumptions: { model: 'gpt-6-astra', effort: 'high' },
    quick: { model: 'gpt-6-astra', effort: 'high' },
    deviation: { model: 'gpt-6-astra', effort: 'high' },
  },
  departementer: {
    role_critical: { model: 'gpt-5.6-luna', effort: 'high' },
    role_other: { model: 'gpt-5.6-luna', effort: 'medium' },
    duplicate: { model: 'gpt-6-astra', effort: 'high' },
    review: { model: 'gpt-6-astra', effort: 'high' },
    editor: { model: 'gpt-6-astra', effort: 'high' },
  },
};

export function modelPlan(kind, overrides = {}) {
  const all = { ...plans.ramme, ...plans.departementer };
  for (const [key, value] of Object.entries(overrides)) {
    if (!(key in all)) throw new Error('Ukjent modellfase: ' + key);
    if (!value || Object.keys(value).some(k => !['model', 'effort'].includes(k))) throw new Error('Ugyldig modellvalg: ' + key);
    if (value.effort && !efforts.includes(value.effort)) throw new Error('Ugyldig effort: ' + value.effort);
    if (value.model !== undefined && (typeof value.model !== 'string' || !value.model.trim())) throw new Error('Tom modell: ' + key);
  }
  return Object.fromEntries(Object.entries(plans[kind]).map(([k, v]) => [k, { ...v, ...overrides[k] }]));
}

function relativeFile(value, key) {
  if (typeof value !== 'string' || path.isAbsolute(value) || value.split(/[\\/]/).includes('..')) throw new Error(key + ' må være en relativ prosjektsti uten ..');
  return value;
}

export function normalizeArgs(input, kind) {
  if (!Number.isInteger(input.budget_year) || input.budget_year < 2000 || input.budget_year > 2100) throw new Error('budget_year må være et heltall mellom 2000 og 2100');
  const year = input.budget_year;
  const a = {
    project: path.resolve(repo, '../uit-statsbudsjett'), skill, python: 'python3',
    run_id: `codex-${year}-v1`, config: `arbeidsflyt/arbeidsdeling-${year}.json`,
    sources_input: `analyse/kilder/${year}/kilder-input.json`,
    phase_set: 'alt', stage: 'forslag', mode: 'prøve', concurrency: 3,
    archive: false, keep_prepared: false, continue_missing: true,
    ...input,
  };
  if (!/^[a-zA-Z0-9][a-zA-Z0-9_-]{0,79}$/.test(a.run_id)) throw new Error('Ugyldig run_id');
  if (!['grunnlag', 'budsjettdag', 'alt'].includes(a.phase_set)) throw new Error('Ugyldig phase_set');
  if (a.stage !== 'forslag') throw new Error('stage: Bare forslag støttes automatisk; andre stadier krever egen kildeavklaring');
  if (!['prøve', 'skarp'].includes(a.mode)) throw new Error('Ugyldig mode');
  if (!Number.isInteger(a.concurrency) || a.concurrency < 1 || a.concurrency > 8) throw new Error('concurrency må være 1–8');
  if (a.timeout_ms !== undefined && (!Number.isInteger(a.timeout_ms) || a.timeout_ms < 1000)) throw new Error('timeout_ms må være minst 1000');
  if (typeof a.python !== 'string' || !a.python.trim()) throw new Error('python må være én kjørbar fil, uten kommandoprefiks');
  for (const field of ['archive', 'keep_prepared', 'continue_missing', 'check_only']) if (a[field] !== undefined && typeof a[field] !== 'boolean') throw new Error(field + ' må være boolean');
  a.project = path.resolve(a.project);
  a.skill = path.resolve(a.skill);
  relativeFile(a.config, 'config'); relativeFile(a.sources_input, 'sources_input');
  if (a.forbidden_dirs !== undefined && !Array.isArray(a.forbidden_dirs)) throw new Error('forbidden_dirs må være en liste');
  a.forbidden_dirs = [...new Set([...(a.forbidden_dirs || []), ...(a.mode === 'prøve' ? [`${year}/`] : [])])];
  a.forbidden_dirs.forEach(d => relativeFile(d, 'forbidden_dirs'));
  a.run_dir = path.join(a.project, 'leveranser', a.run_id);
  modelPlan(kind, a.models);
  return a;
}

export function runConfig(original, a) {
  const c = structuredClone(original);
  if (!Array.isArray(c.roles) || !c.roles.length || !c.editor) throw new Error('Arbeidsdelingen mangler roller eller redaktør');
  const parts = new Set(); const roles = new Set();
  for (const role of c.roles) {
    if (!/^[a-z0-9_]+$/.test(role.id) || roles.has(role.id)) throw new Error('Ugyldig eller duplisert rolle');
    roles.add(role.id); relativeFile(role.history, 'history');
    if (!Array.isArray(role.parts) || !role.parts.length) throw new Error('parts mangler for ' + role.id);
    if (!Array.isArray(role.keywords) || role.keywords.some(k => typeof k !== 'string')) throw new Error('keywords må være tekstliste for ' + role.id);
    for (const p of role.parts) {
      if (!/^[a-z0-9_]+$/.test(p) || parts.has(p)) throw new Error('Ugyldig eller duplisert del');
      parts.add(p);
    }
  }
  if (!/^[a-z0-9_]+$/.test(c.editor.id)) throw new Error('Ugyldig editor.id');
  relativeFile(c.editor.history, 'editor.history');
  if (!Array.isArray(c.editor.deliverables)) throw new Error('editor.deliverables må være en liste');
  c.editor.deliverables.forEach(d => relativeFile(d, 'editor.deliverables'));
  if (!Array.isArray(c.history_years) || c.history_years.some(y => !Number.isInteger(y))) throw new Error('history_years må være liste med årstall');
  c.budget_year = a.budget_year; c.run_id = a.run_id;
  c.stage = 'regjeringens opprinnelige forslag';
  c.history_years = (c.history_years || []).filter(y => y < a.budget_year);
  return c;
}

export function requireFrame(state, result) {
  if (!state.completed.some(k => ['ramme-alt', 'ramme-budsjettdag'].includes(k))) throw new Error('Fullfør ramme-workflowen før departementene');
  if (!result?.quick_answer?.visually_verified || result.quick_answer.bridge_residual_nok_thousand !== 0) throw new Error('Rammekjøringen mangler godkjent kontroll');
}

export async function writeRunConfig(source, destination, a) {
  const config = runConfig(JSON.parse(await readFile(source, 'utf8')), a);
  await writeFile(destination, JSON.stringify(config, null, 2) + '\n');
  return config;
}

export async function parseCli(argv) {
  let file; let dryRun = false;
  for (let i = 0; i < argv.length; i++) {
    if (argv[i] === '--args' && argv[i + 1]) file = argv[++i];
    else if (argv[i] === '--dry-run') dryRun = true;
    else throw new Error('Ukjent argument: ' + argv[i]);
  }
  if (!file) throw new Error('Bruk --args <JSON-fil> [--dry-run]');
  return { input: JSON.parse(await readFile(file, 'utf8')), dryRun };
}

export const isMain = url => process.argv[1] && url === pathToFileURL(path.resolve(process.argv[1])).href;
async function exists(file) { try { await stat(file); return true; } catch (e) { if (e.code === 'ENOENT') return false; throw e; } }

async function script(a, name, args, accepted = [0]) {
  const command = [path.join(a.skill, 'scripts', name), ...args];
  console.log('[skript] ' + name);
  const code = await new Promise((resolve, reject) => {
    const child = spawn(a.python, command, { cwd: a.project, shell: false, stdio: 'inherit' });
    child.on('error', reject); child.on('close', (code, signal) => signal ? reject(new Error(name + ': ' + signal)) : resolve(code));
  });
  if (!accepted.includes(code)) throw new Error(`${name} avsluttet med kode ${code}`);
  return code;
}

async function discover(a, kind) {
  const basis = kind === 'ramme' && ['grunnlag', 'alt'].includes(a.phase_set);
  const day = kind === 'departementer' || ['budsjettdag', 'alt'].includes(a.phase_set);
  let wroteUit = false;
  for (const [needed, year, stage, target, suffix] of [
    [basis, a.budget_year - 1, 'saldert', `saldert-${a.budget_year - 1}`, '-grunnlag'],
    [day, a.budget_year, 'forslag', String(a.budget_year), ''],
  ]) {
    if (!needed) continue;
    const report = path.join(a.run_dir, `kildesjekk${suffix}.json`);
    const code = await script(a, 'discover_sources.py', ['check', '--year', String(year), '--stage', stage, '--output', report], [0, 2, 3]);
    if (a.check_only) continue;
    if (code === 2 || (code === 3 && !a.continue_missing)) throw new Error('Kildegrunnlaget er ikke publisert eller mangler nødvendige dokumenter: ' + report);
    const output = suffix ? path.join(a.project, 'analyse/kilder', target, 'kilder-input.json') : path.join(a.project, a.sources_input);
    const args = ['write', '--from', report, '--output', output];
    if (!wroteUit && !a.keep_prepared) {
      args.push('--uit-output', path.join(a.project, `analyse/kilder/uit-forutsetninger-${a.budget_year}/kilder-input.json`));
      wroteUit = true;
    }
    await script(a, 'discover_sources.py', args);
  }
  await writeFile(path.join(a.run_dir, 'oppstart-eksponering.md'), '# Oppstart\nPubliseringssjekken søkte dokumenttitler og URL-er. Den gir ingen garanti om senere agenters lesinger.\nForbudte mapper: ' + a.forbidden_dirs.join(', ') + '\n');
}

async function memoryList(a, config) {
  const allowed = [];
  for (const role of [...config.roles, config.editor]) {
    const folder = path.join(a.project, 'arbeidsminne', role.id);
    if (!await exists(folder)) continue;
    for (const file of await readdir(folder)) {
      const match = /^erfaringer-(\d{4})-proeve\.md$/.exec(file);
      if (match && Number(match[1]) < a.budget_year) allowed.push(path.relative(a.project, path.join(folder, file)));
    }
  }
  await writeFile(path.join(a.run_dir, 'minnegrunnlag.json'), JSON.stringify({ budget_year: a.budget_year, allowed_previous_trials: allowed, excluded: 'Årets og senere prøveminner samt review-minner uten kjent budsjettår' }, null, 2) + '\n');
}

export async function launch(run, argv, kind) {
  let lock; let lockPath; let runtime; let state; let a; let executionStarted = false;
  try {
    const parsed = await parseCli(argv);
    a = normalizeArgs(parsed.input, kind);
    if (parsed.dryRun) {
      console.log(JSON.stringify({ ...a, model_plan: modelPlan(kind, a.models), dry_run: true }, null, 2));
      return;
    }
    lockPath = path.join(a.project, '.codex-statsbudsjett.lock');
    lock = await open(lockPath, 'wx');
    await lock.writeFile(JSON.stringify({ pid: process.pid, run_id: a.run_id, started: new Date().toISOString() }));
    const statePath = path.join(a.run_dir, 'codex-state.json');
    const existing = await exists(statePath);
    if (!existing) {
      let config;
      if (!a.check_only) {
        let source = path.join(a.project, a.config);
        if (!await exists(source)) {
          const candidates = (await readdir(path.join(a.project, 'arbeidsflyt'))).filter(f => /^arbeidsdeling-\d{4}\.json$/.test(f) && Number(f.slice(13, 17)) < a.budget_year).sort();
          if (!candidates.length) throw new Error('Ingen arbeidsdeling finnes for dette eller tidligere år');
          source = path.join(a.project, 'arbeidsflyt', candidates.at(-1));
        }
        config = runConfig(JSON.parse(await readFile(source, 'utf8')), a);
      }
      if (!a.check_only) {
        const clean = ['--project', a.project, '--year', String(a.budget_year), '--run-id', a.run_id];
        if (a.keep_prepared) clean.push('--keep-prepared');
        if (a.archive) clean.push('--archive');
        await script(a, 'check_clean_state.py', clean);
      } else if (await exists(a.run_dir)) throw new Error('Velg ubrukt run_id for check_only');
      await mkdir(a.run_dir, { recursive: true });
      executionStarted = true;
      state = { budget_year: a.budget_year, run_id: a.run_id, completed: [], started: new Date().toISOString() };
      a.run_started_utc = state.started;
      if (!a.check_only) {
        await writeFile(path.join(a.run_dir, 'arbeidsdeling.json'), JSON.stringify(config, null, 2) + '\n');
        await memoryList(a, config);
      }
      await discover(a, kind);
      if (a.check_only) { console.log('Kildesjekk ferdig; ingen agenter startet.'); return; }
    } else {
      state = JSON.parse(await readFile(statePath, 'utf8'));
      if (state.run_id !== a.run_id || state.budget_year !== a.budget_year) throw new Error('Kjøringsidentitet avviker');
      if (await exists(path.join(a.run_dir, 'manifest.json'))) throw new Error('Kjøringen er fryst. Bruk nytt run_id');
      a.run_started_utc = state.started;
    }
    a.config = path.relative(a.project, path.join(a.run_dir, 'arbeidsdeling.json'));
    const config = JSON.parse(await readFile(path.join(a.project, a.config), 'utf8'));
    a.roles = config.roles;
    a.editor = config.editor;
    const duplicateParts = a.duplicate_parts || ['ramme'];
    if (!Array.isArray(duplicateParts) || duplicateParts.some(p => p !== 'ingen' && !config.roles.some(r => r.parts.includes(p)))) throw new Error('Ukjent duplicate_parts');
    const key = kind === 'ramme' ? `ramme-${a.phase_set}` : kind;
    if (state.completed.includes(key) || state.failed) throw new Error('Fasen er allerede kjørt eller avbrutt. Bruk nytt run_id');
    if (kind === 'ramme' && ((a.phase_set === 'alt' && state.completed.length) || (a.phase_set !== 'alt' && state.completed.includes('ramme-alt')))) throw new Error('Fasene overlapper en fullført rammekjøring');
    if (kind === 'ramme' && a.phase_set === 'budsjettdag' && !await exists(path.join(a.project, a.sources_input))) await discover(a, kind);
    if (kind === 'departementer') {
      const frameKey = state.completed.find(k => ['ramme-alt', 'ramme-budsjettdag'].includes(k));
      const result = frameKey ? JSON.parse(await readFile(path.join(a.run_dir, `${frameKey}-resultat.json`), 'utf8')) : null;
      requireFrame(state, result);
      if (!await exists(path.join(a.run_dir, 'hurtigsvar.md')) || !await exists(path.join(a.run_dir, `uit-ramme-${a.budget_year}.xlsx`))) throw new Error('Rammeleveransen mangler filer');
    }
    await writeFile(statePath, JSON.stringify(state, null, 2) + '\n');
    executionStarted = true;
    const { createRuntime } = await import('./codex_runtime.mjs');
    runtime = createRuntime({ project: a.project, run_dir: a.run_dir, workflow: key, concurrency: a.concurrency, codex: a.codex || 'codex', timeout_ms: a.timeout_ms || 900000 });
    const summary = await run(a, runtime);
    await runtime.finish(); runtime = null;
    state.completed.push(key);
    await writeFile(statePath, JSON.stringify(state, null, 2) + '\n');
    await writeFile(path.join(a.run_dir, `${key}-resultat.json`), JSON.stringify(summary, null, 2) + '\n');
    if (kind === 'departementer') {
      const { finalize } = await import('./codex_steps.mjs');
      const result = await finalize(a, summary);
      console.log(JSON.stringify(result, null, 2));
      if (!result.ready) process.exitCode = 2;
    }
  } catch (error) {
    if (runtime) { try { await runtime.finish(); } catch {} }
    if (state && a && executionStarted) {
      state.failed = String(error.message);
      await writeFile(path.join(a.run_dir, 'codex-state.json'), JSON.stringify(state, null, 2) + '\n');
    }
    console.error('STOPP: ' + error.message); process.exitCode = 1;
  } finally {
    if (lock) { await lock.close(); await rm(lockPath); }
  }
}
