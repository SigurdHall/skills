import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdtemp, mkdir, writeFile } from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import { run as frame } from '../.claude/workflows/codex-uit-ramme.js';
import { run as departments } from '../.claude/workflows/codex-uit-departementer.js';
import { normalizeArgs } from '../skills/knowledge-management/uit-statsbudsjett-analyse/scripts/codex_launch.mjs';

test('hurtigsvaret vises før avviksagenten starter', async () => {
  const project = await mkdtemp(path.join(os.tmpdir(), 'codex-frame-'));
  const a = normalizeArgs({ project, budget_year: 2025, phase_set: 'budsjettdag' }, 'ramme');
  await mkdir(a.run_dir, { recursive: true });
  await writeFile(path.join(a.run_dir, 'hurtigsvar.md'), 'TESTSVAR');
  const events = [];
  const runtime = { phase() {}, log: s => events.push(s), agent: async (prompt, options) => {
    events.push(options.label);
    assert.ok(!prompt.includes('2024-v2'));
    if (options.label === 'hurtigsvar') return { visually_verified: true, bridge_residual_nok_thousand: 0, workbook: 'test.xlsx' };
    return {};
  } };
  await frame(a, runtime, { prepareQuick: async () => ({ assumptions_available: true }) });
  assert.ok(events.indexOf('TESTSVAR') < events.indexOf('avvik'));
});

test('manglende visuell kontroll stopper før avvik', async () => {
  const a = normalizeArgs({ budget_year: 2025, phase_set: 'budsjettdag' }, 'ramme');
  const labels = [];
  await assert.rejects(frame(a, { phase() {}, log() {}, agent: async (_, o) => { labels.push(o.label); return { visually_verified: false }; } }, { prepareQuick: async () => ({}) }), /visuell/);
  assert.deepEqual(labels, ['hurtigsvar']);
});

test('Luna-roller, uavhengig utkast og review følger faktiske avhengigheter', async () => {
  const a = normalizeArgs({ budget_year: 2025 }, 'departementer');
  a.roles = [{ id: 'kd_ramme', parts: ['ramme'], history: 'arbeidsminne/kd_ramme/historikk.md' }, { id: 'nordomraader_energi', parts: ['ud'], history: 'arbeidsminne/nordomraader_energi/historikk.md' }];
  const completed = [];
  const runtime = {
    phase() {}, log() {}, parallel: thunks => Promise.all(thunks.map(f => f())),
    agent: async (prompt, o) => {
      if (o.label.startsWith('rolle:')) assert.equal(o.model, 'gpt-5.6-luna');
      if (o.label === 'kontroll:ramme') {
        assert.ok(completed.includes('rolle:kd_ramme'));
        assert.ok(completed.includes('andreutkast:kd_ramme'));
        completed.push(o.label); return { conditions_lost: [] };
      }
      if (o.label === 'redaktor') assert.ok(completed.includes('kontroll:ramme'));
      if (o.label.startsWith('andreutkast:')) {
        assert.ok(prompt.includes('Ikke les årets prøveminner'));
        assert.ok(prompt.includes('uavhengig andreutkast'));
      }
      assert.ok(!prompt.includes('leveranser/2024-v2'));
      completed.push(o.label);
      return { parts: [], role: o.label.split(':')[1] };
    },
  };
  const result = await departments(a, runtime, { prepareDepartments: async () => ({ sources_failed: [], missing: [], hits_per_part: {} }) });
  assert.deepEqual(result.not_delivered, []);
  assert.equal(completed.filter(s => s.startsWith('rolle:')).length, 2);
});
