import test from 'node:test'
import assert from 'node:assert/strict'
import { chmod, mkdtemp, mkdir, readFile, writeFile } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { join, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

const runtimePath = resolve(fileURLToPath(new URL('../skills/knowledge-management/uit-statsbudsjett-analyse/scripts/codex_runtime.mjs', import.meta.url)))

async function fakeCodex(root, body) {
  const file = join(root, 'fake codex.mjs')
  const fixture = body.replaceAll('console.log(JSON.stringify(', 'emit(JSON.stringify(')
  await writeFile(file, `#!/usr/bin/env node\nimport { spawnSync } from 'node:child_process'\nconst emit = (value) => spawnSync('/bin/echo', [value], { stdio: ['ignore', 1, 2] })\n${fixture}\n`, 'utf8')
  await chmod(file, 0o755)
  return file
}

async function makeRoot(t) {
  const root = await mkdtemp(join(tmpdir(), 'codex-runtime-'))
  t.after(async () => {})
  return root
}

test('agent invokes codex with argv, writes isolated files, exposure instruction and metadata', async (t) => {
  const root = await makeRoot(t)
  const project = join(root, 'project with spaces')
  const runDir = join(root, 'run with spaces')
  await mkdir(project, { recursive: true })
  const capture = join(root, 'argv.json')
  const codex = await fakeCodex(root, `
import { appendFileSync, writeFileSync } from 'node:fs'
const args = process.argv.slice(2)
writeFileSync(process.env.CAPTURE, JSON.stringify(args))
const result = args[args.indexOf('--output-last-message') + 1]
writeFileSync(result, JSON.stringify({ ok: true, value: 4 }))
console.log(JSON.stringify({ type: 'thread.started', model: 'reported-model' }))
console.log(JSON.stringify({ type: 'turn.completed', usage: { input_tokens: 8, output_tokens: 5 }, model: 'reported-model' }))
`)
  const { createRuntime } = await import(runtimePath)
  const runtime = createRuntime({ project, run_dir: runDir, workflow: 'test', codex, timeout_ms: 5000 })
  const oldCapture = process.env.CAPTURE
  process.env.CAPTURE = capture
  t.after(() => { if (oldCapture === undefined) delete process.env.CAPTURE; else process.env.CAPTURE = oldCapture })
  const answer = await runtime.agent('Read UiT source. EXPOSURE_LOG', {
    model: 'gpt-test', effort: 'low', label: 'rolle: kd / test', phase: 'Fagroller',
    schema: { type: 'object', properties: { ok: { type: 'boolean' }, value: { type: 'integer' } } },
  })
  const metadata = await runtime.finish()
  assert.deepEqual(answer, { ok: true, value: 4 })
  const args = JSON.parse(await readFile(capture, 'utf8'))
  assert.deepEqual(args.slice(0, 9), [
    'exec', '-C', project, '--skip-git-repo-check', '--sandbox', 'workspace-write', '--json',
    '--output-schema', args[args.indexOf('--output-schema') + 1],
  ])
  assert.equal(args[args.indexOf('-m') + 1], 'gpt-test')
  assert.equal(args[args.indexOf('-c') + 1], 'model_reasoning_effort="low"')
  assert.equal(args.at(-1), '-')
  const workflowDir = join(runDir, 'runtime', 'test')
  const [label] = ['rolle_kd_test']
  const callDir = join(workflowDir, label)
  assert.equal(await readFile(join(callDir, 'prompt.md'), 'utf8').then((s) => s.includes(join(callDir, 'exposure.md'))), true)
  assert.equal(JSON.parse(await readFile(join(callDir, 'schema.json'), 'utf8')).required.sort().join(','), 'ok,value')
  assert.deepEqual(JSON.parse(await readFile(join(callDir, 'result.json'), 'utf8')), answer)
  assert.equal(JSON.parse(await readFile(join(callDir, 'metadata.json'), 'utf8')).requested.effort, 'low')
  assert.equal(metadata.calls.length, 1)
  assert.equal(metadata.calls[0].usage.input_tokens, 8)
  assert.equal(metadata.calls[0].model, 'reported-model')
})

test('open map schemas omit strict output-schema but still validate locally', async (t) => {
  const root = await makeRoot(t)
  const codex = await fakeCodex(root, `
import { writeFileSync } from 'node:fs'
const args = process.argv.slice(2)
writeFileSync(process.env.CAPTURE, JSON.stringify(args))
writeFileSync(args[args.indexOf('--output-last-message') + 1], JSON.stringify({ hits_per_part: { hod: 2, kd: 3 } }))
console.log(JSON.stringify({ type: 'turn.completed' }))
`)
  const capture = join(root, 'argv.json')
  const { createRuntime } = await import(runtimePath)
  const runtime = createRuntime({ project: root, run_dir: join(root, 'run'), workflow: 'maps', codex })
  const oldCapture = process.env.CAPTURE
  process.env.CAPTURE = capture
  t.after(() => { if (oldCapture === undefined) delete process.env.CAPTURE; else process.env.CAPTURE = oldCapture })
  const answer = await runtime.agent('map', {
    label: 'prep', schema: { type: 'object', properties: { hits_per_part: { type: 'object', additionalProperties: { type: 'integer' } } }, required: ['hits_per_part'] },
  })
  assert.deepEqual(answer.hits_per_part, { hod: 2, kd: 3 })
  const args = JSON.parse(await readFile(capture, 'utf8'))
  assert.equal(args.includes('--output-schema'), false)
})

test('parallel limits active processes and preserves result order', async (t) => {
  const root = await makeRoot(t)
  const timeline = join(root, 'timeline.jsonl')
  const codex = await fakeCodex(root, `
import { appendFileSync, writeFileSync } from 'node:fs'
const args = process.argv.slice(2)
const result = args[args.indexOf('--output-last-message') + 1]
const id = result.split('/').at(-2)
appendFileSync(process.env.TIMELINE, JSON.stringify({ event: 'start', id, at: Date.now() }) + '\\n')
await new Promise((resolve) => setTimeout(resolve, 80))
appendFileSync(process.env.TIMELINE, JSON.stringify({ event: 'end', id, at: Date.now() }) + '\\n')
writeFileSync(result, JSON.stringify({ id }))
console.log(JSON.stringify({ type: 'turn.completed' }))
`)
  const { createRuntime } = await import(runtimePath)
  const runtime = createRuntime({ project: root, run_dir: join(root, 'run'), workflow: 'parallel', codex, concurrency: 2 })
  const old = process.env.TIMELINE
  process.env.TIMELINE = timeline
  t.after(() => { if (old === undefined) delete process.env.TIMELINE; else process.env.TIMELINE = old })
  const result = await runtime.parallel(['a', 'b', 'c', 'd'].map((id) => () => runtime.agent(`ID=${id}`, { label: id, schema: { type: 'object', properties: { id: { type: 'string' } } } })))
  assert.deepEqual(result.map((x) => x.id), ['a', 'b', 'c', 'd'])
  const events = (await readFile(timeline, 'utf8')).trim().split('\n').map(JSON.parse)
  const starts = events.filter((x) => x.event === 'start')
  const ends = events.filter((x) => x.event === 'end')
  assert.equal(starts.length, 4)
  assert.ok(starts[2].at >= ends[0].at || starts[2].at >= ends[1].at)
})

test('finish waits for active calls and cancels queued calls', async (t) => {
  const root = await makeRoot(t)
  const timeline = join(root, 'timeline.jsonl')
  const codex = await fakeCodex(root, `
import { appendFileSync, writeFileSync } from 'node:fs'
const args = process.argv.slice(2)
const result = args[args.indexOf('--output-last-message') + 1]
const id = result.split('/').at(-2)
appendFileSync(process.env.TIMELINE, JSON.stringify({ event: 'start', id }) + '\\n')
await new Promise((resolve) => setTimeout(resolve, 50))
writeFileSync(result, JSON.stringify({ id }))
console.log(JSON.stringify({ type: 'turn.completed' }))
`)
  const old = process.env.TIMELINE
  process.env.TIMELINE = timeline
  t.after(() => { if (old === undefined) delete process.env.TIMELINE; else process.env.TIMELINE = old })
  const { createRuntime } = await import(runtimePath)
  const runtime = createRuntime({ project: root, run_dir: join(root, 'run'), workflow: 'finish', codex, concurrency: 1 })
  const schema = { type: 'object', properties: { id: { type: 'string' } } }
  const first = runtime.agent('first', { label: 'first', schema })
  for (let attempt = 0; attempt < 40; attempt += 1) {
    if ((await readFile(timeline, 'utf8').catch(() => '')).includes('first')) break
    await new Promise((resolve) => setTimeout(resolve, 5))
  }
  const second = runtime.agent('second', { label: 'second', schema })
  const summaryPromise = runtime.finish()
  await first
  await assert.rejects(second, /avbrutt|avsluttes/i)
  const summary = await summaryPromise
  assert.deepEqual(summary.calls.map((call) => call.status), ['succeeded', 'cancelled'])
  assert.deepEqual((await readFile(timeline, 'utf8')).trim().split('\\n').map(JSON.parse).map((event) => event.id), ['first'])
})

test('failures, malformed results, schema mismatches and timeout retain diagnostics', async (t) => {
const root = await makeRoot(t)
  const codex = await fakeCodex(root, `
import { writeFileSync } from 'node:fs'
const args = process.argv.slice(2)
const result = args[args.indexOf('--output-last-message') + 1]
const mode = result.split('/').at(-2)
if (mode === 'NONZERO') { console.error('diagnostic stderr'); console.log(JSON.stringify({ type: 'turn.failed', error: { message: 'failed turn' } })); process.exit(7) }
if (mode === 'BADJSON') { writeFileSync(result, '{bad'); console.log(JSON.stringify({ type: 'turn.completed' })); process.exit(0) }
if (mode === 'MISMATCH') { writeFileSync(result, JSON.stringify({ value: 'wrong' })); console.log(JSON.stringify({ type: 'turn.completed' })); process.exit(0) }
if (mode === 'HANG') { setInterval(() => {}, 1000) }
writeFileSync(result, JSON.stringify({ value: 3 })); console.log(JSON.stringify({ type: 'turn.completed' }))
`)
  const { createRuntime } = await import(runtimePath)
  const runtime = createRuntime({ project: root, run_dir: join(root, 'run'), workflow: 'failures', codex, timeout_ms: 60 })
  const schema = { type: 'object', properties: { value: { type: 'integer' } } }
  for (const [prompt, message] of [['NONZERO', 'retur|exit'], ['BADJSON', 'JSON'], ['MISMATCH', 'type|schema'], ['HANG', 'tidsgrense|timeout']]) {
    await assert.rejects(runtime.agent(prompt, { label: prompt, schema }), new RegExp(message, 'i'))
    const dir = join(root, 'run', 'runtime', 'failures', prompt)
    assert.ok((await readFile(join(dir, 'stderr.log'), 'utf8').catch(() => '')).length >= 0)
    assert.ok((await readFile(join(dir, 'events.jsonl'), 'utf8').catch(() => '')).length >= 0)
  }
})
