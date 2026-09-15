import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdtemp, readFile, writeFile, readdir } from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import { normalizeArgs, modelPlan, runConfig, writeRunConfig, parseCli, requireFrame } from '../skills/knowledge-management/uit-statsbudsjett-analyse/scripts/codex_launch.mjs';

test('budsjettår og faser valideres før noen skriveoperasjon', () => {
  assert.throws(() => normalizeArgs({ budget_year: '2025' }, 'ramme'), /budget_year/);
  assert.throws(() => normalizeArgs({ budget_year: 2025, phase_set: 'feil' }, 'ramme'), /phase_set/);
  assert.throws(() => normalizeArgs({ budget_year: 2025, run_id: '../feil' }, 'ramme'), /run_id/);
  assert.throws(() => normalizeArgs({ budget_year: 2025, config: '../feil.json' }, 'ramme'), /config/);
  assert.throws(() => normalizeArgs({ budget_year: 2025, stage: 'rnb' }, 'ramme'), /stage/);
});

test('prøveåret er alltid forbudt, uten å miste andre grenser', () => {
  const a = normalizeArgs({ budget_year: 2025, forbidden_dirs: ['2024/'] }, 'ramme');
  assert.equal(a.run_id, 'codex-2025-v1');
  assert.deepEqual(a.forbidden_dirs, ['2024/', '2025/']);
});

test('Luna er arbeidshest og effort kan overstyres eksplisitt', () => {
  assert.equal(modelPlan('departementer').role_other.model, 'gpt-5.6-luna');
  assert.equal(modelPlan('departementer', { role_other: { effort: 'high' } }).role_other.model, 'gpt-5.6-luna');
  assert.equal(modelPlan('departementer', { role_other: { effort: 'high' } }).role_other.effort, 'high');
  assert.throws(() => modelPlan('departementer', { typo: {} }), /fase/);
  assert.throws(() => modelPlan('ramme', { quick: { effort: 'minimal' } }), /effort/);
});

test('run-konfigurasjonen retter identitet og år uten å mutere årsfilen', async () => {
  const dir = await mkdtemp(path.join(os.tmpdir(), 'codex-launch-'));
  const original = { budget_year: 2024, run_id: 'claude', history_years: [2023, 2025], roles: [{ id: 'kd_ramme', parts: ['ramme'], keywords: ['UiT'], history: 'arbeidsminne/kd_ramme/historikk.md' }], editor: { id: 'redaktor', history: 'arbeidsminne/redaktor/historikk.md', deliverables: [] } };
  const src = path.join(dir, 'original.json');
  await writeFile(src, JSON.stringify(original));
  const a = normalizeArgs({ budget_year: 2025, project: dir }, 'ramme');
  const config = runConfig(original, a);
  assert.equal(config.run_id, 'codex-2025-v1');
  assert.deepEqual(config.history_years, [2023]);
  assert.equal(original.run_id, 'claude');
  await writeRunConfig(src, path.join(dir, 'run.json'), a);
  assert.deepEqual(JSON.parse(await readFile(src, 'utf8')), original);
  assert.equal(JSON.parse(await readFile(path.join(dir, 'run.json'), 'utf8')).budget_year, 2025);
});

test('departementene krever fullført og kontrollert rammekjøring', () => {
  assert.throws(() => requireFrame({ completed: ['ramme-grunnlag'] }, {}), /ramme/);
  assert.throws(() => requireFrame({ completed: ['ramme-alt'] }, { quick_answer: { visually_verified: false } }), /kontroll/);
  assert.doesNotThrow(() => requireFrame({ completed: ['ramme-alt'] }, { quick_answer: { visually_verified: true, bridge_residual_nok_thousand: 0 } }));
});

test('ufullstendig arbeidsdeling avvises før oppstart', () => {
  const a = normalizeArgs({ budget_year: 2025 }, 'ramme');
  assert.throws(() => runConfig({ roles: [], editor: {} }, a), /roller/);
  assert.throws(() => runConfig({ roles: [{ id: 'kd', parts: null, history: 'h.md' }], editor: {} }, a), /parts/);
  assert.throws(() => normalizeArgs({ budget_year: 2025, timeout_ms: -1 }, 'ramme'), /timeout_ms/);
});

test('CLI krever eksplisitt argumentfil; dry-run utløser ingen kjøring', async () => {
  const dir = await mkdtemp(path.join(os.tmpdir(), 'codex-dry-'));
  const file = path.join(dir, 'args.json');
  await writeFile(file, '{"budget_year":2025}');
  assert.deepEqual(await parseCli(['--args', file, '--dry-run']), { input: { budget_year: 2025 }, dryRun: true });
  assert.deepEqual(await readdir(dir), ['args.json']);
  await assert.rejects(parseCli(['--execute']), /Ukjent/);
});
