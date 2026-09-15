import { spawn } from 'node:child_process'
import { mkdir, readFile, writeFile } from 'node:fs/promises'
import { existsSync } from 'node:fs'
import { dirname, join, resolve } from 'node:path'
import process from 'node:process'

const own = (object, key) => Object.prototype.hasOwnProperty.call(object, key)

function json(value) {
  return JSON.stringify(value, null, 2) + '\n'
}

function safeLabel(value) {
  const label = String(value ?? 'agent')
    .normalize('NFKC')
    .replace(/[^a-zA-Z0-9._-]+/g, '_')
    .replace(/^\.+|\.+$/g, '')
  return label || 'agent'
}

function containsOpenMap(schema) {
  if (!schema || typeof schema !== 'object') return false
  if (Array.isArray(schema)) return schema.some(containsOpenMap)
  if (own(schema, 'additionalProperties') && schema.additionalProperties !== false) return true
  return Object.values(schema).some(containsOpenMap)
}

// Codex structured output requires strict objects. Open maps are left open and
// cause the caller to omit --output-schema; they are checked after the call.
function normalizeSchema(schema) {
  if (!schema || typeof schema !== 'object') return schema
  if (Array.isArray(schema)) return schema.map(normalizeSchema)
  const result = {}
  for (const [key, value] of Object.entries(schema)) result[key] = normalizeSchema(value)
  const objectType = result.type === 'object' || (Array.isArray(result.type) && result.type.includes('object'))
  if (objectType || own(result, 'properties') || own(result, 'additionalProperties')) {
    const properties = result.properties && typeof result.properties === 'object' && !Array.isArray(result.properties)
      ? result.properties
      : {}
    result.properties = properties
    if (!own(result, 'additionalProperties')) result.additionalProperties = false
    if (result.additionalProperties === false) result.required = Object.keys(properties)
    else if (!own(result, 'required')) result.required = []
  }
  return result
}

function typeMatches(value, type) {
  if (type === 'null') return value === null
  if (type === 'object') return value !== null && typeof value === 'object' && !Array.isArray(value)
  if (type === 'array') return Array.isArray(value)
  if (type === 'integer') return Number.isInteger(value)
  if (type === 'number') return typeof value === 'number' && Number.isFinite(value)
  if (type === 'boolean') return typeof value === 'boolean'
  if (type === 'string') return typeof value === 'string'
  return true
}

function validate(value, schema, path = '$') {
  if (!schema || typeof schema !== 'object') return null
  if (own(schema, 'enum') && !schema.enum.some((candidate) => Object.is(candidate, value))) {
    return `${path} må være en av enum-verdiene`
  }
  if (own(schema, 'type')) {
    const types = Array.isArray(schema.type) ? schema.type : [schema.type]
    if (!types.some((type) => typeMatches(value, type))) return `${path} har feil type (forventet ${types.join(' eller ')})`
  }
  if (value === null || value === undefined) return null
  if (typeMatches(value, 'object') && (schema.type === 'object' || own(schema, 'properties') || own(schema, 'additionalProperties'))) {
    const properties = schema.properties && typeof schema.properties === 'object' ? schema.properties : {}
    for (const required of schema.required || []) {
      if (!own(value, required)) return `${path}.${required} mangler`
    }
    for (const [key, child] of Object.entries(value)) {
      if (own(properties, key)) {
        const error = validate(child, properties[key], `${path}.${key}`)
        if (error) return error
      } else if (schema.additionalProperties === false) {
        return `${path}.${key} er ikke tillatt`
      } else if (schema.additionalProperties && typeof schema.additionalProperties === 'object') {
        const error = validate(child, schema.additionalProperties, `${path}.${key}`)
        if (error) return error
      }
    }
  }
  if (Array.isArray(value) && schema.items) {
    for (let index = 0; index < value.length; index += 1) {
      const error = validate(value[index], schema.items, `${path}[${index}]`)
      if (error) return error
    }
  }
  return null
}

function parseEvents(stdout) {
  const events = []
  for (const line of stdout.split(/\r?\n/)) {
    if (!line.trim()) continue
    try {
      events.push(JSON.parse(line))
    } catch {
      events.push({ parse_error: 'Ugyldig JSON-linje fra Codex', raw_line: line })
    }
  }
  return events
}

function eventFailure(events) {
  for (const event of events) {
    const type = typeof event?.type === 'string' ? event.type.toLowerCase() : ''
    if (type === 'turn.failed' || type === 'turn.error' || type === 'error' || type.endsWith('.failed') || type.endsWith('.error')) {
      return event.error?.message || event.message || `Codex rapporterte ${event.type}`
    }
  }
  return null
}

function eventUsage(events) {
  for (const event of events) {
    if (event?.type === 'turn.completed' && event.usage && typeof event.usage === 'object') return event.usage
  }
  for (const event of events) {
    if (event?.usage && typeof event.usage === 'object') return event.usage
    if (event?.response?.usage && typeof event.response.usage === 'object') return event.response.usage
  }
  return null
}

function eventModel(events) {
  for (const event of events) {
    if (typeof event?.model === 'string') return event.model
    if (typeof event?.response?.model === 'string') return event.response.model
  }
  return null
}

function eventServiceTier(events) {
  for (const event of events) {
    if (typeof event?.service_tier === 'string') return event.service_tier
    if (typeof event?.response?.service_tier === 'string') return event.response.service_tier
  }
  return null
}

function errorWithDiagnostics(message, callDir, metadata) {
  const error = new Error(`${message} (${callDir})`)
  error.call_dir = callDir
  error.metadata = metadata
  return error
}

async function writeFileSafe(path, contents) {
  await mkdir(dirname(path), { recursive: true })
  await writeFile(path, contents, 'utf8')
}

export function createRuntime({
  project,
  run_dir,
  workflow,
  concurrency = 3,
  codex = 'codex',
  timeout_ms = 900000,
} = {}) {
  if (!project || !run_dir || !workflow) throw new TypeError('project, run_dir og workflow er påkrevd')
  if (!Number.isInteger(concurrency) || concurrency < 1) throw new TypeError('concurrency må være et positivt heltall')
  if (!Number.isFinite(timeout_ms) || timeout_ms <= 0) throw new TypeError('timeout_ms må være positiv')

  const projectPath = resolve(project)
  const runPath = resolve(run_dir)
  const workflowPath = join(runPath, 'runtime', safeLabel(workflow))
  const calls = []
  const pending = new Set()
  const usedLabels = new Set()
  const queue = []
  const children = new Set()
  let active = 0
  let callSequence = 0
  let finished = false
  let finishing = false

  function drain() {
    while (!finishing && active < concurrency && queue.length) {
      active += 1
      queue.shift().resolve()
    }
  }

  function slot() {
    if (finishing) return Promise.reject(new Error('Runtime avsluttes; kølagte Codex-kall ble avbrutt'))
    return new Promise((resolveSlot, rejectSlot) => {
      queue.push({ resolve: resolveSlot, reject: rejectSlot })
      drain()
    })
  }

  function cancelQueued(reason) {
    while (queue.length) queue.shift().reject(reason)
  }

  function callDirectory(label) {
    const base = safeLabel(label)
    let candidate = base
    let number = 2
    while (usedLabels.has(candidate) || existsSync(join(workflowPath, candidate))) candidate = `${base}-${number++}`
    usedLabels.add(candidate)
    return join(workflowPath, candidate)
  }

  async function killChild(child) {
    if (!child || child.exitCode !== null || child.signalCode !== null) return
    if (process.platform === 'win32') {
      try { child.kill() } catch { /* prosessen kan ha avsluttet i mellomtiden */ }
      return
    }
    try { process.kill(-child.pid, 'SIGTERM') } catch { try { child.kill('SIGTERM') } catch { /* avsluttet */ } }
    await new Promise((resolveKill) => setTimeout(resolveKill, 75))
    if (child.exitCode === null && child.signalCode === null) {
      try { process.kill(-child.pid, 'SIGKILL') } catch { try { child.kill('SIGKILL') } catch { /* avsluttet */ } }
    }
  }

  const signalHandlers = {}
  for (const signal of ['SIGINT', 'SIGTERM', 'SIGHUP']) {
    signalHandlers[signal] = () => {
      Promise.all([...children].map(killChild)).finally(() => {
        try { process.kill(process.pid, signal) } catch { /* prosessen avsluttes */ }
      })
    }
    process.once(signal, signalHandlers[signal])
  }

  async function execute(prompt, options = {}) {
    if (finished) throw new Error('Runtime er allerede avsluttet')
    const {
      model = null,
      effort = null,
      label = 'agent',
      phase = null,
      schema = null,
    } = options
    const callIndex = callSequence++
    const callDir = callDirectory(label)
    await mkdir(callDir, { recursive: true })
    const exposurePath = join(callDir, 'exposure.md')
    const finalPrompt = `${String(prompt).replaceAll('EXPOSURE_LOG', exposurePath)}\n\nRuntime-instruks: Når du logger kildeeksponering, bruk bare denne loggfilen: ${exposurePath}. Øvrige leveranser skrives som oppdraget angir. Har du ikke åpnet UiT-materiale, skriv det eksplisitt i loggen.`
    const normalized = schema ? normalizeSchema(schema) : null
    await writeFileSafe(join(callDir, 'prompt.md'), finalPrompt)
    await writeFileSafe(join(callDir, 'schema.json'), json(normalized ?? {}))
    await writeFileSafe(exposurePath, '')

    const outputPath = join(callDir, 'result.json')
    const eventsPath = join(callDir, 'events.jsonl')
    const stderrPath = join(callDir, 'stderr.log')
    await writeFileSafe(outputPath, '')
    await writeFileSafe(eventsPath, '')
    await writeFileSafe(stderrPath, '')
    const args = ['exec', '-C', projectPath, '--skip-git-repo-check', '--sandbox', 'workspace-write', '--json']
    if (normalized && !containsOpenMap(normalized)) args.push('--output-schema', join(callDir, 'schema.json'))
    args.push('--output-last-message', outputPath)
    if (model) args.push('-m', String(model))
    if (effort) args.push('-c', `model_reasoning_effort="${String(effort)}"`)
    args.push('-')

    const requested = { model, effort }
    const started = Date.now()
    let stdout = ''
    let stderr = ''
    let timedOut = false
    let exitCode = null
    let signal = null
    let spawnError = null
    let child
    try {
      await slot()
    } catch (error) {
      const metadata = {
        workflow: String(workflow),
        call_index: callIndex,
        label: String(label),
        phase,
        call_dir: callDir,
        command: [codex, ...args],
        requested: { model, effort },
        model: null,
        actual_model: null,
        service_tier: null,
        actual_service_tier: null,
        usage: null,
        elapsed_ms: Date.now() - started,
        exit_code: null,
        signal: null,
        timed_out: false,
        turn_failed: false,
        event_parse_errors: 0,
        status: 'cancelled',
        error: error.message,
      }
      calls.push(metadata)
      await writeFileSafe(join(callDir, 'metadata.json'), json(metadata))
      await writeFileSafe(join(callDir, 'error.json'), json({ error: error.message, metadata }))
      throw errorWithDiagnostics(error.message, callDir, metadata)
    }
    try {
      const result = await new Promise((resolveProcess) => {
        let timeoutKill = null
        child = spawn(codex, args, {
          cwd: projectPath,
          env: process.env,
          shell: false,
          detached: process.platform !== 'win32',
          stdio: ['pipe', 'pipe', 'pipe'],
        })
        children.add(child)
        child.stdout.on('data', (chunk) => { stdout += chunk.toString() })
        child.stderr.on('data', (chunk) => { stderr += chunk.toString() })
        child.once('error', (error) => { spawnError = error })
        child.once('close', (code, childSignal) => {
          exitCode = code
          signal = childSignal
          children.delete(child)
          Promise.resolve(timeoutKill).then(resolveProcess)
        })
        child.stdin.on('error', () => {})
        child.stdin.end(finalPrompt)
        const timer = setTimeout(async () => {
          timedOut = true
          timeoutKill = killChild(child)
        }, timeout_ms)
        child.once('close', () => clearTimeout(timer))
      })
      void result
    } finally {
      active -= 1
      drain()
    }

    const elapsed = Date.now() - started
    const events = parseEvents(stdout)
    await writeFileSafe(eventsPath, stdout)
    await writeFileSafe(stderrPath, stderr)
    let resultValue = null
    let resultText = null
    let resultError = null
    try {
      resultText = await readFile(outputPath, 'utf8')
      resultValue = JSON.parse(resultText)
    } catch (error) {
      resultError = error
    }

    const metadata = {
      workflow: String(workflow),
      call_index: callIndex,
      label: String(label),
      phase,
      call_dir: callDir,
      command: [codex, ...args],
      requested,
      model: eventModel(events),
      actual_model: eventModel(events),
      service_tier: eventServiceTier(events),
      actual_service_tier: eventServiceTier(events),
      usage: eventUsage(events),
      elapsed_ms: elapsed,
      exit_code: exitCode,
      signal,
      timed_out: timedOut,
      turn_failed: Boolean(eventFailure(events)),
      event_parse_errors: events.filter((event) => event.parse_error).length,
      status: 'succeeded',
    }
    let failure = null
    if (timedOut) failure = `Codex-kall overskred tidsgrensen på ${timeout_ms} ms`
    else if (spawnError) failure = `Kunne ikke starte Codex: ${spawnError.message}`
    else if (exitCode !== 0) failure = `Codex avsluttet med returkode ${exitCode}`
    else if (eventFailure(events)) failure = eventFailure(events)
    else if (resultError) failure = `Resultatfilen mangler eller er ugyldig JSON: ${resultError.message}`
    else if (normalized) failure = validate(resultValue, schema)
    if (failure) {
      metadata.status = 'failed'
      metadata.error = failure
      calls.push(metadata)
      await writeFileSafe(join(callDir, 'metadata.json'), json(metadata))
      await writeFileSafe(join(callDir, 'error.json'), json({ error: failure, metadata }))
      throw errorWithDiagnostics(failure, callDir, metadata)
    }
    await writeFileSafe(join(callDir, 'metadata.json'), json(metadata))
    calls.push(metadata)
    return resultValue
  }

  function agent(prompt, options) {
    const operation = execute(prompt, options)
    pending.add(operation)
    operation.then(() => pending.delete(operation), () => pending.delete(operation))
    return operation
  }

  async function parallel(thunks) {
    if (!Array.isArray(thunks)) throw new TypeError('parallel forventer en array av thunks')
    return Promise.all(thunks.map((thunk) => {
      if (typeof thunk !== 'function') throw new TypeError('parallel forventer funksjoner')
      return thunk()
    }))
  }

  function log(message) {
    console.log(`[${workflow}] ${message}`)
  }

  function phase(name) {
    console.log(`[${workflow}] fase: ${name}`)
  }

  async function finish() {
    if (finished) return {
      workflow: String(workflow),
      project: projectPath,
      run_dir: runPath,
      concurrency,
      calls: [...calls].sort((left, right) => left.call_index - right.call_index),
    }
    finishing = true
    finished = true
    cancelQueued(new Error('Runtime avsluttes; kølagte Codex-kall ble avbrutt'))
    await Promise.allSettled([...pending])
    for (const [signal, handler] of Object.entries(signalHandlers)) process.removeListener(signal, handler)
    const summary = {
      workflow: String(workflow),
      project: projectPath,
      run_dir: runPath,
      concurrency,
      calls: [...calls].sort((left, right) => left.call_index - right.call_index),
      finished_at_utc: new Date().toISOString(),
    }
    await writeFileSafe(join(workflowPath, 'timing.json'), json(summary))
    return summary
  }

  return { agent, parallel, log, phase, finish }
}

export const _testing = { normalizeSchema, containsOpenMap, validate, safeLabel }
