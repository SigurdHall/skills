export const meta = {
  name: 'uit-ramme',
  description: 'Workflow 1: UiT\'s frame in blått hefte as an Excel workbook (previous year adopted budget, price adjustment, bridge table), then the deviation against UiT\'s preliminary allocation',
  whenToUse: 'Started by /uit-statsbudsjett-proeve. phase_set grunnlag in September (previous year adopted budget and UiT assumptions), budsjettdag when the proposal is published',
  phases: [
    { title: 'Grunnlag', detail: 'fetch blått hefte for the previous year after vedtak, parse the UiT row; fetch UiT board case documents', model: 'sonnet' },
    { title: 'Forutsetninger', detail: 'document UiT preliminary allocation for the year (or reuse the prepared note)', model: 'opus' },
    { title: 'Hurtigsvar', detail: 'fetch blått hefte and KD, parse the table, check against the previous year, build the Excel workbook and hurtigsvar.md', model: 'opus' },
    { title: 'Avvik', detail: 'bridge proposal against the preliminary allocation; extend workbook and hurtigsvar', model: 'opus' },
  ],
}

// ---------------------------------------------------------------------------
// Arguments (JSON object in Workflow({args})). POSIX paths; from Windows pass
// unc_project and python_cmd ("wsl.exe -e <venv python>").
// phase_set: 'grunnlag' (September), 'budsjettdag' (the day the proposal is
// published; reuses the prepared basis), 'alt' (everything, for tests).
// ---------------------------------------------------------------------------
const a = args || {}
const PROJECT = a.project || '/home/sihal7953/repos/uit-statsbudsjett'
const UNC = a.unc_project || null
const SKILL = a.skill || '/home/sihal7953/repos/skills/skills/knowledge-management/uit-statsbudsjett-analyse'
const PY = a.python_cmd || a.python || '/home/sihal7953/.venvs/statsbudsjett/bin/python'
const CONFIG = a.config || 'arbeidsflyt/arbeidsdeling-2025.json'
const YEAR = a.budget_year || 2025
const PREV = YEAR - 1
const RUN_ID = a.run_id || `${YEAR}-claude-v1`
const STAGE = a.stage || 'regjeringens opprinnelige forslag'
const SOURCES_INPUT = a.sources_input || `analyse/kilder/${YEAR}/kilder-input.json`
const STARTED = a.run_started_utc || 'unknown (pass run_started_utc)'
const PHASE_SET = a.phase_set || 'alt'
const RUN_BASIS = ['grunnlag', 'alt'].includes(PHASE_SET)
const RUN_DAY = ['budsjettdag', 'alt'].includes(PHASE_SET)
const FORBIDDEN = Array.isArray(a.forbidden_dirs) ? a.forbidden_dirs : [`${YEAR}/`]

const PROFILE = a.profile || 'rask'
const PLAN_RASK = {
  prep: { model: 'sonnet', effort: 'low' },
  assumptions: { model: 'opus', effort: 'medium' },
  quick: { model: 'opus', effort: 'medium' },
  deviation: { model: 'opus', effort: 'medium' },
}
const PLAN_SESJON = { prep: { effort: 'low' }, assumptions: {}, quick: {}, deviation: {} }
const PLAN = Object.assign({}, PROFILE === 'sesjon' ? PLAN_SESJON : PLAN_RASK, a.models || {})
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

const ENV = UNC
  ? `Miljø: prosjektet ligger i WSL. Les og skriv filer med Read/Write/Glob på UNC-stien ${UNC} + samme relative sti som POSIX-stien. Kjør skript uten shell med PowerShell-verktøyet: ${PY} <skript> <argumenter>, eller Bash med MSYS_NO_PATHCONV=1 foran. Bruk POSIX-stier i alle skriptargumenter. Ikke bruk heredoc gjennom wsl.exe.`
  : `Miljø: kjør skript med ${PY} <skript> <argumenter>. Les og skriv filer direkte på POSIX-stiene.`

const COMMON = `
Prosjekt: ${PROJECT}. Skill: ${SKILL}. Kjøring: ${RUN_ID}, budsjettår ${YEAR}, stadium: ${STAGE}. Startet ${STARTED} UTC.
${ENV}
Les først ${SKILL}/SKILL.md og ${SKILL}/references/hurtigsvar-format.md.
Forbudt å åpne eller liste: ${FORBIDDEN.map(d => `${PROJECT}/${d}`).join(', ')} og alle UiT-dokumenter om ${YEAR} datert etter framleggelsen. Alle lesinger av UiT-materiale skal noteres i ${RUN}/eksponeringslogg.md.
Prioritet 1 er korrekt informasjon: eksakte beløp i 1 000 kroner, riktig år og stadium, riktig PDF-side, tall kontrollert visuelt mot siden. Prioritet 2 er fart: skriv kort og bruk skriptene til alt som kan regnes eller kontrolleres maskinelt. Aldri gjett et tall; skriv null og forklar. Skriv norsk.
Returner bare det strukturerte resultatet; ikke skriv en melding til et menneske.`

log(`uit-ramme, fasesett ${PHASE_SET}. Modellplan (${PROFILE}): henting ${describe('prep')}; forutsetninger ${describe('assumptions')}; hurtigsvar ${describe('quick')}; avvik ${describe('deviation')}`)

let basis = null
let assumptions = null
let quickPrep = null
let quick = null
let deviation = null

// ---------------------------------------------------------------------------
if (RUN_BASIS) {
  phase('Grunnlag')
  const BASIS_SCHEMA = {
    type: 'object',
    properties: {
      vedtatt_pdf: { type: ['string', 'null'] },
      vedtatt_total_nok_thousand: { type: ['integer', 'null'] },
      table_pdf_page: { type: ['integer', 'null'] },
      column_count: { type: ['integer', 'null'] },
      basis_json: { type: ['string', 'null'] },
      uit_documents_fetched: { type: 'integer' },
      problems: { type: 'array', items: { type: 'string' } },
    },
    required: ['vedtatt_pdf', 'vedtatt_total_nok_thousand', 'table_pdf_page', 'column_count', 'basis_json', 'uit_documents_fetched', 'problems'],
  }
  basis = await agent(`${COMMON}
Oppgave: skaff grunnlaget for neste års bro, uten å analysere.
1. Hvis ${BASIS_DIR}/kilder-input.json finnes (skrevet av launcheren fra publiseringssjekken for ${PREV} etter vedtak): kjør ${PY} ${SCRIPTS}/fetch_sources.py ${BASIS_DIR}/kilder-input.json ${BASIS_DIR}, lag .txt-uttrekk av PDF-en med ${PY} ${SCRIPTS}/extract_documents.py <pdf> --output <samme navn>.txt, og kjør ${PY} ${SCRIPTS}/parse_blaatt_hefte_table.py <txt> --output ${BASIS_JSON}. UiT-radens siste tall er vedtatt budsjett ${PREV} i 1 000 kroner. Rapporter det, PDF-siden og antall kolonner. Mangler filen, rapporter at grunnlaget for ${PREV} ikke er tilgjengelig.
2. Hvis ${UIT_SOURCES_DIR}/kilder-input.json finnes og ${ASSUMPTIONS_FILE} ikke finnes: kjør ${PY} ${SCRIPTS}/fetch_sources.py ${UIT_SOURCES_DIR}/kilder-input.json ${UIT_SOURCES_DIR} og lag .txt-uttrekk av hver PDF der.
3. Opprett eller utvid ${RUN}/eksponeringslogg.md med forbudte mapper, dato ${STARTED}, kjøring ${RUN_ID}, fasesett ${PHASE_SET}, og hvilke UiT-dokumenter som ble hentet (ikke lest).`,
    opts('prep', { label: 'grunnlag', phase: 'Grunnlag', schema: BASIS_SCHEMA }))
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
Oppgave: dokumenter UiTs forhåndsforutsetninger for budsjettåret ${YEAR}. Det avgjørende er den eksakte KD-rammen i 1 000 kroner og hver linje i broen fra saldert ${PREV}; kontroller tabellen visuelt mot PDF-siden (render siden til PNG med ${PY} og pymupdf) før du skriver tallene. Vedtatt ${PREV} fra blått hefte etter vedtak står i ${BASIS_JSON} (UiT-radens siste tall); UiTs bro skal starte på samme tall, ellers forklar avviket.
Hvis ${ASSUMPTIONS_FILE} allerede finnes og har KD-ramme med kilde: les den, kontroller at kildene og ${BRIDGE_INPUT} finnes, sett reused_existing_note true og returner uten å skrive om.
Ellers: bruk ${RUN}/kildesjekk.json og ${SKILL}/references/kildekart.md. Dokumentene og .txt-uttrekkene ligger i ${UIT_SOURCES_DIR}/. Skriv ${ASSUMPTIONS_FILE} med samme struktur som ${PROJECT}/analyse/uit-forutsetninger-2024.md, og ${BRIDGE_INPUT} i formatet fra ${SKILL}/references/scripts.md med UiT-siden fylt ut (opening, expected per rad, expected_total) og forslagssiden null.
Ikke åpne UiTs analyse av statsbudsjettet ${YEAR}, endelig fordeling ${YEAR} eller tildelingsbrev. Noter alle åpnede UiT-dokumenter i ${RUN}/eksponeringslogg.md.`,
    opts('assumptions', { label: 'uit-forutsetninger', phase: 'Forutsetninger', schema: ASSUMPTIONS_SCHEMA }))
  if (assumptions && assumptions.found) log(`UiTs forutsetninger: ${assumptions.board_case || 'sak ukjent'} ${assumptions.decision_date || ''}, KD-ramme ${assumptions.kd_frame_nok_thousand ?? 'ukjent'} tusen kr${assumptions.reused_existing_note ? ' (forberedt notat gjenbrukt)' : ''}`)
  else log('UiTs forhåndsforutsetninger ble ikke funnet')
}

// ---------------------------------------------------------------------------
if (RUN_DAY) {
  phase('Hurtigsvar')
  const PREP_QUICK_SCHEMA = {
    type: 'object',
    properties: {
      blaatt_hefte_pdf: { type: 'string' },
      blaatt_hefte_sha256: { type: 'string' },
      table_json: { type: 'string' },
      table_pdf_page: { type: ['integer', 'null'] },
      uit_row_found: { type: 'boolean' },
      column_count: { type: ['integer', 'null'] },
      basis_available: { type: 'boolean' },
      assumptions_available: { type: 'boolean' },
      problems: { type: 'array', items: { type: 'string' } },
    },
    required: ['blaatt_hefte_pdf', 'blaatt_hefte_sha256', 'table_json', 'table_pdf_page', 'uit_row_found', 'column_count', 'basis_available', 'assumptions_available', 'problems'],
  }
  quickPrep = await agent(`${COMMON}
Oppgave: skaff bare det hurtigsvaret trenger, så fort som mulig. Ikke analyser.
1. Les ${PROJECT}/${SOURCES_INPUT} og skriv en filtrert kopi med bare postene med id blaatt-hefte-forslag-${YEAR} og kd-prop-${YEAR} til ${QUICK_DIR}/kilder-hurtig.json. Kjør ${PY} ${SCRIPTS}/fetch_sources.py ${QUICK_DIR}/kilder-hurtig.json ${SOURCES_DIR}.
2. Kjør ${PY} ${SCRIPTS}/extract_documents.py ${SOURCES_DIR}/blaatt-hefte-forslag-${YEAR}.pdf --output ${SOURCES_DIR}/blaatt-hefte-forslag-${YEAR}.txt, deretter samme for KD-PDF-en.
3. Kjør ${PY} ${SCRIPTS}/parse_blaatt_hefte_table.py ${SOURCES_DIR}/blaatt-hefte-forslag-${YEAR}.txt --output ${QUICK_DIR}/blaatt-hefte-tabell.json. Returkode 2 betyr at UiT-raden ikke ble funnet; rapporter header_lines og siden du mener tabellen står på.
4. Rapporter om ${BASIS_JSON} og ${ASSUMPTIONS_FILE} finnes. Les SHA-256 for blått hefte fra ${SOURCES_DIR}/sources.json. Opprett eller utvid ${RUN}/eksponeringslogg.md med forbudte mapper, dato ${STARTED}, kjøring ${RUN_ID} og fasesett ${PHASE_SET}.`,
    opts('prep', { label: 'hurtig-kilder', phase: 'Hurtigsvar', schema: PREP_QUICK_SCHEMA }))
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
Noter i ${RUN}/eksponeringslogg.md hvilke dokumenter du leste. Ikke åpne fagproposisjonene.`,
    opts('quick', { label: 'hurtigsvar', phase: 'Hurtigsvar', schema: QUICK_SCHEMA }))
  if (quick) {
    log(`HURTIGSVAR ${YEAR}: UiT forslag ${quick.proposed_nok_thousand ?? 'ukjent'} tusen kr, saldert ${PREV} ${quick.saldert_nok_thousand ?? 'ukjent'} (vedtatt ${PREV} ${quick.vedtatt_prev_nok_thousand ?? 'ukjent'}, rest ${quick.previous_year_residual ?? '?'}), endring ${quick.change_pct ?? '?'} % (sektor ${quick.sector_change_pct ?? '?'} %), prissats ${quick.price_rate_pct ?? '?'} %; bro-rest ${quick.bridge_residual_nok_thousand ?? '?'}; visuelt kontrollert: ${quick.visually_verified}. Excel: ${quick.workbook}`)
  } else {
    log('Hurtigsvaret feilet; ingen agentresultat')
  }

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
Grunnlag: ${QUICK_DIR}/rammeark-input.json (UiT-raden med kolonneetiketter), ${ASSUMPTIONS_FILE}, ${BRIDGE_INPUT} (UiT-siden ferdig), blått heftes forklaringssider og ${PROJECT}/analyse/2024-rammebro-kontroll.json som mønster for harmonisering (brutto/netto studieplasser, pris inkludert videreført kompensasjon, kutt samlet, finansieringsflyttinger som egne rader).
1. Fyll forslagssiden i ${BRIDGE_INPUT} komponent for komponent med kildeside. Kjør ${PY} ${SCRIPTS}/reconcile_budget.py ${BRIDGE_INPUT} --output ${QUICK_DIR}/rammebro-kontroll.json. Rest i alle tre broer skal være 0; er den ikke det, vis resten som egen rad merket uforklart, aldri som et oppdiktet tiltak.
2. Legg "preliminary" inn i ${QUICK_DIR}/rammeark-input.json (source, expected_total, rows med tema, uit, forslag, kilde) og kjør ${PY} ${SCRIPTS}/build_frame_workbook.py ${QUICK_DIR}/rammeark-input.json --output ${WORKBOOK} på nytt, slik at arket "Mot foreløpig" finnes.
3. Oppdater ${QUICK_MD}: hovedtallene får UiTs foreløpige ramme og avvik; fyll seksjonen for komponenter mot foreløpig; oppdater "ikke kontrollert ennå". Behold resten.
Noter leste UiT-dokumenter i ${RUN}/eksponeringslogg.md.`,
      opts('deviation', { label: 'avvik', phase: 'Avvik', schema: DEVIATION_SCHEMA }))
    if (deviation) log(`AVVIK ${YEAR}: forslag ${deviation.proposed_nok_thousand ?? 'ukjent'} mot UiT foreløpig ${deviation.expected_nok_thousand ?? 'ukjent'} = ${deviation.difference_nok_thousand ?? 'ukjent'} tusen kr; bro ${deviation.bridge_status}`)
  } else if (quick) {
    log('Avvik mot foreløpig fordeling er ikke beregnet: UiTs forutsetninger mangler')
  }
}

return {
  workflow: 'uit-ramme',
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
