import { readFile } from 'node:fs/promises'
import { isMain, launch, modelPlan } from '../../skills/knowledge-management/uit-statsbudsjett-analyse/scripts/codex_launch.mjs'
import { prepareBasis, prepareQuick } from '../../skills/knowledge-management/uit-statsbudsjett-analyse/scripts/codex_steps.mjs'

// Codex-variant av uit-ramme.js ved 0fbd0f6. Kjøres med Node, uten Claude Workflow-verktøyet.
export const meta = {
  name: 'codex-uit-ramme',
  description: 'Workflow 1: UiT\'s frame in blått hefte as an Excel workbook (previous year adopted budget, price adjustment, bridge table), then the deviation against UiT\'s preliminary allocation',
  whenToUse: 'Started by $codex-uit-statsbudsjett-proeve. phase_set grunnlag in September (previous year adopted budget and UiT assumptions), budsjettdag when the proposal is published',
  phases: [
    { title: 'Grunnlag', detail: 'fetch blått hefte for the previous year after vedtak, parse the UiT row; fetch UiT board case documents', model: null },
    { title: 'Forutsetninger', detail: 'document UiT preliminary allocation for the year (or reuse the prepared note)', model: 'gpt-6-astra' },
    { title: 'Hurtigsvar', detail: 'fetch blått hefte and KD, parse the table, check against the previous year, build the Excel workbook and hurtigsvar.md', model: 'gpt-6-astra' },
    { title: 'Avvik', detail: 'bridge proposal against the preliminary allocation; extend workbook and hurtigsvar', model: 'gpt-6-astra' },
  ],
}

// ---------------------------------------------------------------------------
// Kjør fra WSL/Linux med --args <JSON-fil>. --dry-run viser valgene uten å starte.
// phase_set: 'grunnlag' (September), 'budsjettdag' (the day the proposal is
// published; reuses the prepared basis), 'alt' (everything, for tests).
// ---------------------------------------------------------------------------
export async function run(a, runtime, steps = { prepareBasis, prepareQuick }) {
const { agent, log, phase } = runtime
const PROJECT = a.project
const SKILL = a.skill
const PY = "'" + a.python.replaceAll("'", "'\\''") + "'"
const CONFIG = a.config
const YEAR = a.budget_year
const PREV = YEAR - 1
const RUN_ID = a.run_id
const STAGE = a.stage || 'regjeringens opprinnelige forslag'
const SOURCES_INPUT = a.sources_input || `analyse/kilder/${YEAR}/kilder-input.json`
const STARTED = a.run_started_utc
const PHASE_SET = a.phase_set || 'alt'
const RUN_BASIS = ['grunnlag', 'alt'].includes(PHASE_SET)
const RUN_DAY = ['budsjettdag', 'alt'].includes(PHASE_SET)
const FORBIDDEN = Array.isArray(a.forbidden_dirs) ? a.forbidden_dirs : [`${YEAR}/`]

const PROFILE = 'codex-rask'
const PLAN = modelPlan('ramme', a.models)
function opts(stage, extra) { return Object.assign({}, PLAN[stage], extra) }
function describe(stage) { const p = PLAN[stage] || {}; return `${p.model || 'sesjonens modell'}, effort ${p.effort || 'sesjonens'}` }

const RUN = `${PROJECT}/leveranser/${RUN_ID}`
const SCRIPTS = `${SKILL}/scripts`
const SOURCES_DIR = `${PROJECT}/analyse/kilder/${YEAR}`
const BASIS_DIR = `${PROJECT}/analyse/kilder/saldert-${PREV}`
const BASIS_JSON = `${PROJECT}/analyse/saldert-${PREV}.json`
const UIT_SOURCES_DIR = `${PROJECT}/analyse/kilder/uit-forutsetninger-${YEAR}`
const ASSUMPTIONS_FILE = `${PROJECT}/analyse/uit-forutsetninger-${YEAR}.md`
const BRIDGE_INPUT = `${PROJECT}/analyse/${YEAR}-rammebro-input.json`
const QUICK_DIR = `${RUN}/hurtigsvar`
const WORKBOOK = `${RUN}/uit-ramme-${YEAR}.xlsx`
const QUICK_MD = `${RUN}/hurtigsvar.md`

const ENV = `Miljø: kjør skript med ${PY} <skript> <argumenter>. Les og skriv filer direkte på POSIX-stiene. Siter alle stier som separate shell-argumenter.`

const COMMON = `
Prosjekt: ${PROJECT}. Skill: ${SKILL}. Kjøring: ${RUN_ID}, budsjettår ${YEAR}, stadium: ${STAGE}. Startet ${STARTED} UTC.
${ENV}
Les først ${SKILL}/SKILL.md og ${SKILL}/references/hurtigsvar-format.md.
Forbudt å åpne eller liste: ${FORBIDDEN.map(d => `${PROJECT}/${d}`).join(', ')} og alle UiT-dokumenter om ${YEAR} datert etter framleggelsen. Alle lesinger av UiT-materiale skal noteres i EXPOSURE_LOG.
Prioritet 1 er korrekt informasjon: eksakte beløp i 1 000 kroner, riktig år og stadium, riktig PDF-side, tall kontrollert visuelt mot siden. Prioritet 2 er fart: skriv kort og bruk skriptene til alt som kan regnes eller kontrolleres maskinelt. Ukjent beløp er JSON null eller «ukjent» i tekst, aldri tallet 0. Skriv norsk.
Returner bare det strukturerte resultatet; ikke skriv en melding til et menneske.`

log(`codex-uit-ramme, fasesett ${PHASE_SET}. Modellplan (${PROFILE}): henting med skript; forutsetninger ${describe('assumptions')}; hurtigsvar ${describe('quick')}; avvik ${describe('deviation')}`)

let basis = null
let assumptions = null
let quickPrep = null
let quick = null
let deviation = null

// ---------------------------------------------------------------------------
if (RUN_BASIS) {
  phase('Grunnlag')
  basis = await steps.prepareBasis(a)
  if (basis) log(`Grunnlag: vedtatt ${PREV} for UiT = ${basis.vedtatt_total_nok_thousand ?? 'ukjent'} tusen kr (PDF-side ${basis.table_pdf_page ?? '?'}); UiT-dokumenter hentet: ${basis.uit_documents_fetched}`)

  phase('Forutsetninger')
  const ASSUMPTIONS_SCHEMA = {
    type: 'object',
    properties: {
      found: { type: 'boolean' },
      reused_existing_note: { type: 'boolean' },
      file: { type: 'string' },
      board_case: { type: 'string' },
      decision_date: { type: 'string' },
      kd_frame_nok_thousand: { type: ['integer', 'null'] },
      sources: { type: 'array', items: { type: 'string' } },
      gaps: { type: 'array', items: { type: 'string' } },
    },
    required: ['found', 'reused_existing_note', 'file', 'sources', 'gaps'],
  }
  assumptions = await agent(`${COMMON}
Du kjører som ${describe('assumptions')}.
Oppgave: dokumenter UiTs forhåndsforutsetninger for budsjettåret ${YEAR}. Det avgjørende er den eksakte KD-rammen i 1 000 kroner og hver linje i broen fra saldert ${PREV}; kontroller tabellen visuelt mot PDF-siden (render siden til PNG med ${PY} og pymupdf) før du skriver tallene. Lagre kontrollen med kildeside i samme fasekatalog. Vedtatt ${PREV} fra blått hefte etter vedtak står i ${BASIS_JSON} (UiT-radens siste tall); UiTs bro skal starte på samme tall, ellers forklar avviket.
Hvis ${ASSUMPTIONS_FILE} allerede finnes og har KD-ramme med kilde: les den, kontroller at kildene og ${BRIDGE_INPUT} finnes, sett reused_existing_note true og returner uten å skrive om.
Ellers: bruk ${RUN}/kildesjekk-grunnlag.json og ${SKILL}/references/kildekart.md. Dokumentene og .txt-uttrekkene ligger i ${UIT_SOURCES_DIR}/. Skriv ${ASSUMPTIONS_FILE} med KD-ramme, bro, kildesider og dokumenterte mangler, og ${BRIDGE_INPUT} i formatet fra ${SKILL}/references/scripts.md med UiT-siden fylt ut (opening, expected per rad, expected_total) og forslagssiden null.
Ikke åpne UiTs analyse av statsbudsjettet ${YEAR}, endelig fordeling ${YEAR} eller tildelingsbrev. Noter alle åpnede UiT-dokumenter i EXPOSURE_LOG.`,
    opts('assumptions', { label: 'uit-forutsetninger', phase: 'Forutsetninger', schema: ASSUMPTIONS_SCHEMA }))
  if (assumptions && assumptions.found) log(`UiTs forutsetninger: ${assumptions.board_case || 'sak ukjent'} ${assumptions.decision_date || ''}, KD-ramme ${assumptions.kd_frame_nok_thousand ?? 'ukjent'} tusen kr${assumptions.reused_existing_note ? ' (forberedt notat gjenbrukt)' : ''}`)
  else log('UiTs forhåndsforutsetninger ble ikke funnet')
}

// ---------------------------------------------------------------------------
if (RUN_DAY) {
  phase('Hurtigsvar')
  quickPrep = await steps.prepareQuick(a)
  if (!quickPrep) throw new Error('Hentingen av blått hefte feilet; ingen agentresultat')
  log(`Blått hefte hentet; UiT-rad ${quickPrep.uit_row_found ? 'funnet' : 'IKKE funnet'} på PDF-side ${quickPrep.table_pdf_page ?? 'ukjent'}, ${quickPrep.column_count ?? '?'} kolonner; grunnlag ${PREV}: ${quickPrep.basis_available ? 'ja' : 'nei'}; forutsetninger: ${quickPrep.assumptions_available ? 'ja' : 'nei'}`)

  const QUICK_SCHEMA = {
    type: 'object',
    properties: {
      workbook: { type: 'string' },
      hurtigsvar: { type: 'string' },
      input_json: { type: 'string' },
      saldert_nok_thousand: { type: ['integer', 'null'] },
      vedtatt_prev_nok_thousand: { type: ['integer', 'null'] },
      previous_year_residual: { type: ['integer', 'null'] },
      proposed_nok_thousand: { type: ['integer', 'null'] },
      change_pct: { type: ['number', 'null'] },
      sector_change_pct: { type: ['number', 'null'] },
      price_rate_pct: { type: ['number', 'null'] },
      price_amount_nok_thousand: { type: ['integer', 'null'] },
      bridge_residual_nok_thousand: { type: ['integer', 'null'] },
      columns: { type: 'array', items: { type: 'string' } },
      follow_up: { type: 'array', items: { type: 'string' } },
      source_pages: { type: 'array', items: { type: 'string' } },
      visually_verified: { type: 'boolean' },
    },
    required: ['workbook', 'hurtigsvar', 'input_json', 'saldert_nok_thousand', 'vedtatt_prev_nok_thousand', 'previous_year_residual', 'proposed_nok_thousand', 'change_pct', 'sector_change_pct', 'price_rate_pct', 'price_amount_nok_thousand', 'bridge_residual_nok_thousand', 'columns', 'follow_up', 'source_pages', 'visually_verified'],
  }
  quick = await agent(`${COMMON}
Du kjører som ${describe('quick')}. Dette er dagens første svar: hvor mye penger UiT har fått i budsjettforslaget, forklart i et Excel-ark slik UiTs arbeidsbøker fra 2018 og 2019 gjorde det: vedtatt budsjett ${PREV}, prisjustering, hver justering, forslag ${YEAR}. Ferdig på minutter, riktig på tallene.
Grunnlag: ${QUICK_DIR}/blaatt-hefte-tabell.json (alle institusjonsrader fra hovedtabellen, tall i 1 000 kroner, header_lines er teksten over tabellen), ${SOURCES_DIR}/blaatt-hefte-forslag-${YEAR}.txt og PDF, ${SOURCES_DIR}/sources.json (SHA-256, URL, hentetid), ${BASIS_JSON} (vedtatt ${PREV} fra blått hefte etter vedtak, når den finnes).
1. Tolk kolonnene: render tabellsiden (PDF-side ${quickPrep.table_pdf_page ?? 'fra tabell-json'}) til PNG med ${PY} og pymupdf, les kolonneoverskriftene visuelt og gi hver kolonne en presis etikett i rekkefølge; første kolonne er normalt saldert ${PREV}, siste er forslaget ${YEAR}. Kontroller at UiT-radens tall i JSON stemmer med bildet, siffer for siffer. Ikke fortsett med tall du ikke har sett i bildet.
2. Finn prissatsen i blått heftes tekst (setningen om satsen for prisjustering for ${YEAR}, normalt i kapittelet om budsjettendringar) med PDF-side, og hva prisjusteringskolonnen inneholder (for eksempel videreført kompensasjon).
3. Skriv ${QUICK_DIR}/rammeark-input.json i formatet fra ${PY} ${SCRIPTS}/build_frame_workbook.py --example: year, stage, source, columns (key, label, header_text; prisjusteringskolonnen får key "pris"), institutions (alle rader uten sum-rader), uit_name som i tabellen, previous_year (vedtatt_total fra ${BASIS_JSON} med kilde, eller null hvis grunnlaget mangler), price (column_key "pris", rate_pct, note, source_page), preliminary null, checks. Kjør ${PY} ${SCRIPTS}/build_frame_workbook.py ${QUICK_DIR}/rammeark-input.json --output ${WORKBOOK}. Returkode 2 betyr at UiT-broen ikke summerer til tabellens forslag; finn feilen i kolonnetolkningen før du går videre. Er previous_year_residual ulik 0, er saldert ${PREV} i tabellen ikke lik vedtatt ${PREV}; skriv det tydelig, ikke juster tallene.
4. Skriv ${QUICK_MD} i det faste formatet med det som finnes nå. Avvik mot UiTs foreløpige fordeling kommer i neste fase. Skriv at ${WORKBOOK} er leveransen.
Noter i EXPOSURE_LOG hvilke dokumenter du leste. Ikke åpne fagproposisjonene.`,
    opts('quick', { label: 'hurtigsvar', phase: 'Hurtigsvar', schema: QUICK_SCHEMA }))
  if (quick) {
    log(`HURTIGSVAR ${YEAR}: UiT forslag ${quick.proposed_nok_thousand ?? 'ukjent'} tusen kr, saldert ${PREV} ${quick.saldert_nok_thousand ?? 'ukjent'} (vedtatt ${PREV} ${quick.vedtatt_prev_nok_thousand ?? 'ukjent'}, rest ${quick.previous_year_residual ?? '?'}), endring ${quick.change_pct ?? '?'} % (sektor ${quick.sector_change_pct ?? '?'} %), prissats ${quick.price_rate_pct ?? '?'} %; bro-rest ${quick.bridge_residual_nok_thousand ?? '?'}; visuelt kontrollert: ${quick.visually_verified}. Excel: ${quick.workbook}`)
  } else {
    log('Hurtigsvaret feilet; ingen agentresultat')
  }

  if (!quick?.visually_verified) throw new Error('Hurtigsvaret mangler visuell kontroll')
  if (quick.bridge_residual_nok_thousand !== 0) throw new Error('UiT-broen har rest eller mangler kontroll')
  log(await readFile(QUICK_MD, 'utf8'))
  log('Excel: ' + WORKBOOK)

  const assumptionsAvailable = (assumptions && assumptions.found) || quickPrep.assumptions_available
  if (quick && assumptionsAvailable) {
    phase('Avvik')
    const DEVIATION_SCHEMA = {
      type: 'object',
      properties: {
        workbook: { type: 'string' },
        hurtigsvar: { type: 'string' },
        expected_nok_thousand: { type: ['integer', 'null'] },
        proposed_nok_thousand: { type: ['integer', 'null'] },
        difference_nok_thousand: { type: ['integer', 'null'] },
        bridge_status: { type: 'string' },
        components: { type: 'integer' },
        open_causes: { type: 'array', items: { type: 'string' } },
      },
      required: ['workbook', 'hurtigsvar', 'expected_nok_thousand', 'proposed_nok_thousand', 'difference_nok_thousand', 'bridge_status', 'components', 'open_causes'],
    }
    deviation = await agent(`${COMMON}
Du kjører som ${describe('deviation')}. Oppgave: avviket mellom regjeringens forslag og UiTs foreløpige fordeling for ${YEAR}, lagt inn i Excel-arket og hurtigsvaret.
Grunnlag: ${QUICK_DIR}/rammeark-input.json (UiT-raden med kolonneetiketter), ${ASSUMPTIONS_FILE}, ${BRIDGE_INPUT} (UiT-siden ferdig), blått heftes forklaringssider og formatbeskrivelsen i ${SKILL}/references/scripts.md for harmonisering (brutto/netto studieplasser, pris inkludert videreført kompensasjon, kutt samlet, finansieringsflyttinger som egne rader).
1. Fyll forslagssiden i ${BRIDGE_INPUT} komponent for komponent med kildeside. Kjør ${PY} ${SCRIPTS}/reconcile_budget.py ${BRIDGE_INPUT} --output ${QUICK_DIR}/rammebro-kontroll.json. Rest i alle tre broer skal være 0; er den ikke det, vis resten som egen rad merket uforklart, aldri som et oppdiktet tiltak.
2. Legg "preliminary" inn i ${QUICK_DIR}/rammeark-input.json (source, expected_total, rows med tema, uit, forslag, kilde) og kjør ${PY} ${SCRIPTS}/build_frame_workbook.py ${QUICK_DIR}/rammeark-input.json --output ${WORKBOOK} på nytt, slik at arket "Mot foreløpig" finnes.
3. Oppdater ${QUICK_MD}: hovedtallene får UiTs foreløpige ramme og avvik; fyll seksjonen for komponenter mot foreløpig; oppdater "ikke kontrollert ennå". Behold resten.
Noter leste UiT-dokumenter i EXPOSURE_LOG.`,
      opts('deviation', { label: 'avvik', phase: 'Avvik', schema: DEVIATION_SCHEMA }))
    if (deviation) log(`AVVIK ${YEAR}: forslag ${deviation.proposed_nok_thousand ?? 'ukjent'} mot UiT foreløpig ${deviation.expected_nok_thousand ?? 'ukjent'} = ${deviation.difference_nok_thousand ?? 'ukjent'} tusen kr; bro ${deviation.bridge_status}`)
  } else if (quick) {
    log('Avvik mot foreløpig fordeling er ikke beregnet: UiTs forutsetninger mangler')
  }
}

return {
  workflow: 'codex-uit-ramme',
  run_id: RUN_ID,
  run_dir: RUN,
  phase_set: PHASE_SET,
  model_plan: PLAN,
  basis,
  assumptions,
  quick_answer: quick,
  workbook: quick ? quick.workbook : null,
  deviation,
}

}

if (isMain(import.meta.url)) await launch(run, process.argv.slice(2), "ramme")
