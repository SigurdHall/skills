export const meta = {
  name: 'uit-statsbudsjett-analyse',
  description: 'Run the UiT state budget analysis: sources, UiT assumptions, quick answer, five specialist roles, editor, deterministic checks',
  whenToUse: 'Started by the user-invoked skill /uit-statsbudsjett-proeve after the publication check has passed; runs one budget year in phase sets (forutsetninger, hurtig, full)',
  phases: [
    { title: 'Forbered', detail: 'fetch sources, extract text, prepare work orders, open exposure log', model: 'sonnet' },
    { title: 'Forutsetninger', detail: 'locate and document UiT preliminary allocation for the year', model: 'opus' },
    { title: 'Hurtigsvar', detail: 'UiT frame row, bridge against preliminary allocation, five items to follow up; fixed format', model: 'opus' },
    { title: 'Fagroller', detail: 'one agent per role; critical roles on opus, others on sonnet; optional duplicate and review', model: 'opus' },
    { title: 'Redaktør', detail: 'consolidated report, presentation spec, forwarding draft', model: 'opus' },
    { title: 'Kontroll', detail: 'structural check, bridge recomputation, manifest, exposure log', model: 'sonnet' },
  ],
}

// ---------------------------------------------------------------------------
// Arguments. Pass as a JSON object in Workflow({args}). Script arguments use
// POSIX paths (the project lives in WSL). When Claude runs on Windows, files
// are read and written through the UNC path in unc_project, and scripts run
// through python_cmd, e.g. "wsl.exe -e /home/<user>/.venvs/statsbudsjett/bin/python".
//
// phase_set selects what runs:
//   'forutsetninger' : Forbered (UiT documents only) + Forutsetninger. Run in
//                      September, before the proposal exists.
//   'hurtig'         : Forbered + Forutsetninger (skipped when the note exists)
//                      + Hurtigsvar. Budget day, first minutes.
//   'full'           : Fagroller + Redaktør + Kontroll. Continues the same run.
//   'alt'            : everything in one go.
// ---------------------------------------------------------------------------
const a = args || {}
const PROJECT = a.project || '/home/sihal7953/repos/uit-statsbudsjett'
const UNC = a.unc_project || null
const SKILL = a.skill || '/home/sihal7953/repos/skills/skills/knowledge-management/uit-statsbudsjett-analyse'
const PY = a.python_cmd || a.python || '/home/sihal7953/.venvs/statsbudsjett/bin/python'
const CONFIG = a.config || 'arbeidsflyt/arbeidsdeling-2025.json'
const YEAR = a.budget_year || 2025
const RUN_ID = a.run_id || `${YEAR}-claude-v1`
const STAGE = a.stage || 'regjeringens opprinnelige forslag'
const SOURCES_INPUT = a.sources_input || `analyse/kilder/${YEAR}/kilder-input.json`
const DUPLICATE_PARTS = Array.isArray(a.duplicate_parts) ? a.duplicate_parts.filter(p => p && p !== 'ingen') : ['ramme']
const TEMPLATE = a.template || null
const LIBREOFFICE = a.libreoffice || null
const STARTED = a.run_started_utc || 'unknown (pass run_started_utc)'
const PHASE_SET = a.phase_set || 'alt'
const RUN_PREP = ['forutsetninger', 'hurtig', 'alt'].includes(PHASE_SET)
const RUN_ASSUMPTIONS = ['forutsetninger', 'hurtig', 'alt'].includes(PHASE_SET)
const RUN_QUICK = ['hurtig', 'alt'].includes(PHASE_SET)
const RUN_FULL = ['full', 'alt'].includes(PHASE_SET)
const ROLES = Array.isArray(a.roles) ? a.roles : [
  { id: 'kd_ramme', parts: ['ramme', 'kd', 'fin'] },
  { id: 'helse_miljo', parts: ['hod', 'kld'] },
  { id: 'naring_arbeid_kultur', parts: ['nfd', 'aid', 'kud'] },
  { id: 'bygg_samisk_justis', parts: ['kdd', 'jd'] },
  { id: 'nordomraader_energi', parts: ['ud', 'oed'] },
]
const FORBIDDEN = Array.isArray(a.forbidden_dirs) ? a.forbidden_dirs : [`${YEAR}/`]

// ---------------------------------------------------------------------------
// Model plan. Correctness on the few decisive items (frame bridge, named UiT
// grants with conditions, funding moves) and speed are the priorities, so the
// roles that own those items and every judging step run on opus at medium
// effort; mechanical stages and the remaining roles run on sonnet. Enable
// /fast in the session before starting if faster opus output is wanted; the
// script cannot toggle it. profile 'sesjon' inherits the session model instead.
// Override any stage with args.models, e.g. {"role_other": {"model": "opus"}}.
// ---------------------------------------------------------------------------
const PROFILE = a.profile || 'rask'
const PLAN_RASK = {
  prep: { model: 'sonnet', effort: 'low' },
  assumptions: { model: 'opus', effort: 'medium' },
  quick: { model: 'opus', effort: 'medium' },
  role_critical: { model: 'opus', effort: 'medium' },
  role_other: { model: 'sonnet', effort: 'medium' },
  duplicate: { model: 'sonnet', effort: 'medium' },
  review: { model: 'opus', effort: 'medium' },
  editor: { model: 'opus', effort: 'medium' },
  check: { model: 'sonnet', effort: 'low' },
}
const PLAN_SESJON = {
  prep: { effort: 'low' }, assumptions: {}, quick: {}, role_critical: {}, role_other: {}, duplicate: {}, review: {}, editor: {}, check: { effort: 'low' },
}
const PLAN = Object.assign({}, PROFILE === 'sesjon' ? PLAN_SESJON : PLAN_RASK, a.models || {})
const CRITICAL_ROLES = Array.isArray(a.critical_roles) ? a.critical_roles : ['kd_ramme', 'helse_miljo', 'naring_arbeid_kultur']

function opts(stage, extra) { return Object.assign({}, PLAN[stage], extra) }
function describe(stage) {
  const p = PLAN[stage] || {}
  return `${p.model || 'sesjonens modell'}, effort ${p.effort || 'sesjonens'}`
}

const RUN = `${PROJECT}/leveranser/${RUN_ID}`
const SCRIPTS = `${SKILL}/scripts`
const ASSUMPTIONS_FILE = `${PROJECT}/analyse/uit-forutsetninger-${YEAR}.md`
const BRIDGE_INPUT = `${PROJECT}/analyse/${YEAR}-rammebro-input.json`
const UIT_SOURCES_DIR = `${PROJECT}/analyse/kilder/uit-forutsetninger-${YEAR}`

const ENV = UNC
  ? `Miljø: prosjektet ligger i WSL. Les og skriv filer med Read/Write/Glob på UNC-stien ${UNC} + samme relative sti som POSIX-stien. Kjør skript uten shell med PowerShell-verktøyet: ${PY} <skript> <argumenter>, eller Bash med MSYS_NO_PATHCONV=1 foran. Bruk POSIX-stier i alle skriptargumenter. Ikke bruk heredoc gjennom wsl.exe.`
  : `Miljø: kjør skript med ${PY} <skript> <argumenter>. Les og skriv filer direkte på POSIX-stiene.`

const COMMON = `
Prosjekt: ${PROJECT}. Skill: ${SKILL}. Kjøring: ${RUN_ID}, budsjettår ${YEAR}, stadium: ${STAGE}. Startet ${STARTED} UTC.
${ENV}
Les først ${SKILL}/SKILL.md, ${SKILL}/references/agent-workflow.md og ${PROJECT}/arbeidsflyt/leveransekontrakt.md.
Forbudt å åpne eller liste: ${FORBIDDEN.map(d => `${PROJECT}/${d}`).join(', ')} og alle UiT-dokumenter om ${YEAR} datert etter framleggelsen. Alle lesinger av UiT-materiale skal noteres i ${RUN}/eksponeringslogg.md.
Prioritet 1 er korrekt informasjon på de avgjørende punktene: eksakte beløp med enhet, mottaker, år/stadium, nødvendige vilkår og riktig PDF-side. Prioritet 2 er rask, ferdig leveranse: skriv kort, ikke gjenta kildene, og bruk skriptene til alt som kan regnes eller kontrolleres maskinelt. Aldri gjett et tall; skriv null og forklar. Skriv norsk i alle leveransefiler.
Returner bare det strukturerte resultatet; ikke skriv en melding til et menneske.`

log(`Fasesett ${PHASE_SET}. Modellplan (${PROFILE}): forbered ${describe('prep')}; forutsetninger ${describe('assumptions')}; hurtigsvar ${describe('quick')}; kritiske roller ${describe('role_critical')}; øvrige roller ${describe('role_other')}; andreutkast ${describe('duplicate')}; review ${describe('review')}; redaktør ${describe('editor')}; kontroll ${describe('check')}`)

let prep = null
let assumptions = null
let quick = null

// ---------------------------------------------------------------------------
if (RUN_PREP) {
  phase('Forbered')
  log(`Kjøring ${RUN_ID}: forbereder kilder og oppdrag`)

  const PREP_SCHEMA = {
    type: 'object',
    properties: {
      sources_fetched: { type: 'integer' },
      sources_failed: { type: 'array', items: { type: 'string' } },
      extracts_written: { type: 'integer' },
      work_orders_written: { type: 'integer' },
      exposure_log: { type: 'string' },
      missing: { type: 'array', items: { type: 'string' } },
    },
    required: ['sources_fetched', 'sources_failed', 'extracts_written', 'work_orders_written', 'exposure_log', 'missing'],
  }

  const onlyUit = PHASE_SET === 'forutsetninger'
  prep = await agent(`${COMMON}
Oppgave: forbered kjøringen uten å analysere innholdet. Kjøringen starter fra tom tilstand; launcheren har arkivert rester fra tidligere forsøk. Finner du likevel filer for ${YEAR} under ${PROJECT}/analyse/kilder eller ${RUN} som ikke er UiTs forutsetningsdokumenter, rapporter dem i missing som "uventet rest" og fortsett uten å bruke dem.
${onlyUit ? `Dette fasesettet gjelder bare UiTs forutsetninger; regjeringens kilder finnes ikke ennå. Hopp over punkt 1 og 2.` : ''}
1. Hvis ${PROJECT}/${SOURCES_INPUT} finnes: kjør ${PY} ${SCRIPTS}/fetch_sources.py ${PROJECT}/${SOURCES_INPUT} ${PROJECT}/analyse/kilder/${YEAR}. Hent blått hefte og KD først hvis rekkefølgen kan styres. Avvikende eksisterende filer skal ikke overskrives; rapporter dem.
2. For hver PDF i ${PROJECT}/analyse/kilder/${YEAR}/ uten tilhørende .txt: kjør ${PY} ${SCRIPTS}/extract_documents.py <pdf> --output <samme navn>.txt. Blått hefte og KD først.
3. Hvis ${UIT_SOURCES_DIR}/kilder-input.json finnes og ${ASSUMPTIONS_FILE} ikke finnes: kjør ${PY} ${SCRIPTS}/fetch_sources.py ${UIT_SOURCES_DIR}/kilder-input.json ${UIT_SOURCES_DIR} og lag .txt-uttrekk av hver PDF der.
4. Kjør ${PY} ${SCRIPTS}/manage_workflow.py prepare ${PROJECT}/${CONFIG} --project ${PROJECT}.
5. Opprett eller utvid ${RUN}/eksponeringslogg.md med: forbudte mapper, dato ${STARTED}, kjøring ${RUN_ID}, fasesett ${PHASE_SET}, og en seksjon "Lest UiT-materiale" som senere agenter fyller ut.
6. List hva som mangler for full analyse: kilder for departementer uten PDF (rollenes deler: ${ROLES.map(r => r.parts.join('/')).join(', ')}), manglende ${ASSUMPTIONS_FILE}, mal (${TEMPLATE || 'ikke oppgitt'}) og renderer (${LIBREOFFICE || 'ikke oppgitt'}).`,
    opts('prep', { label: 'forbered', phase: 'Forbered', schema: PREP_SCHEMA }))

  if (!prep) throw new Error('Forberedelsen feilet; ingen agentresultat')
  log(`Kilder hentet: ${prep.sources_fetched}, feilet: ${prep.sources_failed.length}, mangler: ${prep.missing.length}`)
}

// ---------------------------------------------------------------------------
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

if (RUN_ASSUMPTIONS) {
  phase('Forutsetninger')
  assumptions = await agent(`${COMMON}
Du kjører som ${describe('assumptions')}.
Oppgave: dokumenter UiTs forhåndsforutsetninger for budsjettåret ${YEAR}. Det avgjørende er den eksakte KD-rammen i 1 000 kroner og hver linje i broen fra saldert ${YEAR - 1}; kontroller tabellen visuelt mot PDF-siden (render siden til PNG med ${PY} og pymupdf om nødvendig) før du skriver tallene.
Hvis ${ASSUMPTIONS_FILE} allerede finnes og har KD-ramme med kilde (forberedt i september): les den, kontroller at kildene og ${BRIDGE_INPUT} finnes, sett reused_existing_note true og returner uten å skrive om.
Ellers: bruk ${RUN}/kildesjekk.json (feltet uit_forelopig_fordeling) og ${SKILL}/references/kildekart.md. Dokumentene og .txt-uttrekkene ligger i ${UIT_SOURCES_DIR}/ (hentet i Forbered); mangler de, hent med ${PY} ${SCRIPTS}/fetch_sources.py ${UIT_SOURCES_DIR}/kilder-input.json ${UIT_SOURCES_DIR} og lag uttrekk. Skriv ${ASSUMPTIONS_FILE} med samme struktur som ${PROJECT}/analyse/uit-forutsetninger-2024.md: kilder og versjon, bro fra saldert ${YEAR - 1} til foreløpig ${YEAR} i 1 000 kroner, forutsetninger som skal prøves, resultatgrunnlag, planleggingsår, UiT-spesifikke forhold. Skriv også ${BRIDGE_INPUT} i formatet fra ${SKILL}/references/scripts.md med UiT-siden fylt ut (expected, opening, expected_total) og forslagssiden null.
Ikke åpne UiTs analyse av statsbudsjettet ${YEAR}, endelig fordeling ${YEAR} eller tildelingsbrev. Noter alle åpnede UiT-dokumenter i ${RUN}/eksponeringslogg.md.`,
    opts('assumptions', { label: 'uit-forutsetninger', phase: 'Forutsetninger', schema: ASSUMPTIONS_SCHEMA }))

  if (!assumptions || !assumptions.found) {
    log('UiTs forhåndsforutsetninger ble ikke funnet; rammeavviket kan ikke beregnes')
  } else {
    log(`UiTs forutsetninger: ${assumptions.board_case || 'sak ukjent'} ${assumptions.decision_date || ''}, KD-ramme ${assumptions.kd_frame_nok_thousand ?? 'ukjent'} tusen kr${assumptions.reused_existing_note ? ' (forberedt notat gjenbrukt)' : ''}`)
  }
}

// ---------------------------------------------------------------------------
const QUICK_SCHEMA = {
  type: 'object',
  properties: {
    file: { type: 'string' },
    proposed_nok_thousand: { type: ['integer', 'null'] },
    expected_nok_thousand: { type: ['integer', 'null'] },
    difference_nok_thousand: { type: ['integer', 'null'] },
    bridge_status: { type: 'string' },
    follow_up: { type: 'array', items: { type: 'string' } },
    not_checked: { type: 'array', items: { type: 'string' } },
    source_pages: { type: 'array', items: { type: 'string' } },
  },
  required: ['file', 'proposed_nok_thousand', 'expected_nok_thousand', 'difference_nok_thousand', 'bridge_status', 'follow_up', 'not_checked', 'source_pages'],
}

if (RUN_QUICK) {
  phase('Hurtigsvar')
  quick = await agent(`${COMMON}
Du kjører som ${describe('quick')}. Dette er hurtigsvaret på budsjettdagen; det skal være ferdig på minutter og riktig på hovedtallene.
Kilder: ${PROJECT}/analyse/kilder/${YEAR}/blaatt-hefte-forslag-${YEAR}.txt (og PDF), KD Prop. 1 S i samme mappe, og ${ASSUMPTIONS_FILE}. Les ${SKILL}/references/hurtigsvar-format.md og følg det formatet nøyaktig.
1. Finn UiT-raden i blått heftes hovedtabell (linjen som begynner med "UiT" og kolonnene for saldert ${YEAR - 1}, prisjustering, studieplasser, resultat, kutt, andre endringer og sum). Kontroller kolonneoverskriftene på samme PDF-side; kolonnene endrer seg mellom år. Kontroller raden visuelt (render PDF-siden til PNG) før tallene brukes.
2. Fyll forslagssiden i ${BRIDGE_INPUT} med harmoniserte komponenter (samme grupperingsregler som i ${PROJECT}/analyse/2024-rammebro-kontroll.json: brutto/netto, pris inkludert videreført kompensasjon, kutt samlet). Kjør ${PY} ${SCRIPTS}/reconcile_budget.py ${BRIDGE_INPUT} --output ${RUN}/hurtigsvar/rammebro-kontroll.json. Rest skal være 0; ellers vis resten som uforklart.
3. Skriv ${RUN}/hurtigsvar.md i det faste formatet: hovedtall, komponenter, fem punkter å følge opp fra blått hefte og KD (beløp, mottaker, vilkår, PDF-side), ikke kontrollert ennå, kilder og status.
Skriv i ${RUN}/eksponeringslogg.md hvilke dokumenter du leste. Ikke åpne fagproposisjonene; det gjør rollene.`,
    opts('quick', { label: 'hurtigsvar', phase: 'Hurtigsvar', schema: QUICK_SCHEMA }))

  if (quick) {
    log(`HURTIGSVAR ${YEAR}: forslag ${quick.proposed_nok_thousand ?? 'ukjent'}, UiT foreløpig ${quick.expected_nok_thousand ?? 'ukjent'}, avvik ${quick.difference_nok_thousand ?? 'ukjent'} tusen kr; bro ${quick.bridge_status}. Fil: ${quick.file}`)
  } else {
    log('Hurtigsvaret feilet; ingen agentresultat')
  }
}

// ---------------------------------------------------------------------------
let delivered = []
let editor = null
let check = null

if (RUN_FULL) {
  phase('Fagroller')

  const ROLE_SCHEMA = {
    type: 'object',
    properties: {
      role: { type: 'string' },
      memory_sha256: { type: 'string' },
      parts: {
        type: 'array',
        items: {
          type: 'object',
          properties: {
            part: { type: 'string' },
            findings: { type: 'integer' },
            evidence_built: { type: 'boolean' },
            source_missing: { type: 'boolean' },
          },
          required: ['part', 'findings', 'evidence_built', 'source_missing'],
        },
      },
      experience_file: { type: 'string' },
      open_questions: { type: 'array', items: { type: 'string' } },
    },
    required: ['role', 'memory_sha256', 'parts', 'experience_file', 'open_questions'],
  }

  const REVIEW_SCHEMA = {
    type: 'object',
    properties: {
      part: { type: 'string' },
      differences: { type: 'integer' },
      corrections_with_source: { type: 'integer' },
      conditions_lost: { type: 'array', items: { type: 'string' } },
      file: { type: 'string' },
    },
    required: ['part', 'differences', 'corrections_with_source', 'conditions_lost', 'file'],
  }

  function roleStage(role, mode) {
    if (mode === 'duplicate') return 'duplicate'
    return CRITICAL_ROLES.includes(role.id) ? 'role_critical' : 'role_other'
  }

  function rolePrompt(role, mode) {
    const parts = role.parts.join(', ')
    const outDir = mode === 'duplicate' ? `${RUN}/kontroll/${role.id}` : `${RUN}/deler/${role.id}`
    const isolation = mode === 'duplicate'
      ? `Dette er et uavhengig andreutkast. Ikke les ${RUN}/deler/, ${RUN}/hurtigsvar.md eller andre agenters filer fra denne kjøringen. Skriv bare under ${outDir}/.`
      : `Ikke endre andre rollers filer.`
    return `${COMMON}
Du er fagrollen ${role.id} med delene ${parts}, og kjører som ${describe(roleStage(role, mode))}. Les oppdraget ${RUN}/oppdrag/${role.id}.md.
Avgjørende punkter først: for ramme den eksakte UiT-raden i blått hefte og begge broer uten rest; for hod, kud, nfd og kdd navngitte UiT-tilskudd med beløp, mottaker og vilkår (opptak, engangs, resultatandel); for alle deler finansieringsflyttinger som ikke er kutt. Deretter resten av delen, kort.
Før du åpner årets kilder: les ${PROJECT}/arbeidsminne/${role.id}/erfaringer-2018-2023.md og alle ${PROJECT}/arbeidsminne/${role.id}/erfaringer-*-proeve.md og erfaringer-review-*.md. Beregn SHA-256 av den historiske minnefilen (for eksempel med ${PY} -c) og skriv ${outDir}/minne-lest.json med feltene role, sha256, read_at_utc og memory.
Bruk ${ASSUMPTIONS_FILE} som UiT-side når den finnes. Kilder ligger i ${PROJECT}/analyse/kilder/${YEAR}/ (PDF og .txt med "=== PDF-side N ===").
For hver del: skriv ${outDir}/<del>/notater.md (søkeord, treff, avviste treff med grunn, kildehull), ${outDir}/<del>/rapport.md og ${outDir}/<del>/funn.json i formatet fra agent-workflow.md. Ankeret skal inneholde funnets eget beløp; hvis bare et sammenligningstall kan markeres entydig, skal claim si det og et eget anker for beløpet legges til. Kjør ${PY} ${SCRIPTS}/build_evidence.py ${outDir}/<del>/funn.json --project ${PROJECT} --output ${outDir}/<del>/belegg og rett ankere til skriptet godtar dem. Tom funnliste gir et dokumentert negativt resultat, ikke en falsk kilde.
${mode === 'primary' && role.id === 'kd_ramme' ? `Rammen: hurtigsvaret i ${RUN}/hurtigsvar.md og ${RUN}/hurtigsvar/rammebro-kontroll.json finnes fra samme kjøring. Kontroller hver komponent mot kildene på nytt i stedet for å kopiere; retter du noe, skriv hva og hvorfor i rapport.md, oppdater ${BRIDGE_INPUT} og kjør ${PY} ${SCRIPTS}/reconcile_budget.py ${BRIDGE_INPUT} --output ${outDir}/ramme/rammebro-kontroll.json.` : ''}
${mode === 'duplicate' && role.id === 'kd_ramme' ? `Rammen: bygg broen selv fra kildene og ${ASSUMPTIONS_FILE}; skriv egen input til ${outDir}/ramme/rammebro-input.json og kjør ${PY} ${SCRIPTS}/reconcile_budget.py på den med --output ${outDir}/ramme/rammebro-kontroll.json.` : ''}
${mode === 'duplicate' ? '' : `Etterpå: skriv ${PROJECT}/arbeidsminne/${role.id}/erfaringer-${YEAR}-proeve.md, merket prøve uten fasit, med dato og modell/effort (${describe(roleStage(role, mode))}). Ikke endre historiske minnefiler.`}
${isolation} Noter hvert åpnet UiT-dokument i ${RUN}/eksponeringslogg.md.`
  }

  const roleResults = await pipeline(
    ROLES,
    role => agent(rolePrompt(role, 'primary'), opts(roleStage(role, 'primary'), { label: `rolle:${role.id}`, phase: 'Fagroller', schema: ROLE_SCHEMA })),
    async (primary, role) => {
      if (!primary) return { role: role.id, primary: null, reviews: [] }
      const dup = role.parts.filter(p => DUPLICATE_PARTS.includes(p))
      if (!dup.length) return { role: role.id, primary, reviews: [] }
      const second = await agent(rolePrompt({ id: role.id, parts: dup }, 'duplicate'),
        opts('duplicate', { label: `andreutkast:${role.id}`, phase: 'Fagroller', schema: ROLE_SCHEMA }))
      const reviews = await parallel(dup.map(part => () => agent(`${COMMON}
Du kjører som ${describe('review')}. Sammenlignende kontroll av delen ${part} for rollen ${role.id}. Les begge uavhengige utkast: ${RUN}/deler/${role.id}/${part}/ og ${RUN}/kontroll/${role.id}/${part}/, og de samme primærkildene. Kontroller uenigheter mot kildene, og kontroller dekning mot temalisten i ${PROJECT}/arbeidsminne/${role.id}/erfaringer-2018-2023.md, også temaer begge har utelatt. Skriv ${RUN}/deler/${role.id}/${part}/kontroll.md med hver forskjell, hvilket utkast som har kildebelegg, og hvilke vilkår som må inn. Rett bare ${RUN}/deler/${role.id}/${part}/rapport.md og funn.json der du har kildebelegg, og kjør build_evidence.py på nytt hvis funn.json endres. Enighet er ikke godkjenning.`,
        opts('review', { label: `kontroll:${part}`, phase: 'Fagroller', schema: REVIEW_SCHEMA }))))
      return { role: role.id, primary, second, reviews: reviews.filter(Boolean) }
    },
  )

  delivered = roleResults.filter(Boolean).filter(r => r.primary)
  log(`Roller levert: ${delivered.length} av ${ROLES.length}`)
  const lostConditions = delivered.flatMap(r => r.reviews.flatMap(v => v.conditions_lost))
  if (lostConditions.length) log(`Vilkår som måtte gjenopprettes i review: ${lostConditions.length}`)

  // -------------------------------------------------------------------------
  // The editor needs every departmental report; this is the one real barrier.
  phase('Redaktør')

  const EDITOR_SCHEMA = {
    type: 'object',
    properties: {
      report: { type: 'string' },
      presentation_spec: { type: 'string' },
      pptx: { type: ['string', 'null'] },
      forwarding_draft: { type: 'string' },
      evidence_pack: { type: ['string', 'null'] },
      frame_difference_nok_thousand: { type: ['integer', 'null'] },
      experience_file: { type: 'string' },
      unresolved: { type: 'array', items: { type: 'string' } },
    },
    required: ['report', 'presentation_spec', 'pptx', 'forwarding_draft', 'evidence_pack', 'frame_difference_nok_thousand', 'experience_file', 'unresolved'],
  }

  editor = await agent(`${COMMON}
Du er redaktøren og kjører som ${describe('editor')}. Les ${PROJECT}/arbeidsminne/redaktor/erfaringer-2018-2023.md, erfaringer-*-proeve.md og erfaringer-review-*.md først og skriv ${RUN}/minne-lest-redaktor.json med role, sha256, read_at_utc.
Delrapportene ligger i ${RUN}/deler/<rolle>/<del>/. Hurtigsvaret fra samme kjøring ligger i ${RUN}/hurtigsvar.md; der rammerapporten avviker fra hurtigsvaret, gjelder rammerapporten, og avviket skal nevnes. Roller uten leveranse: ${ROLES.filter(r => !delivered.find(d => d.role === r.id)).map(r => r.id).join(', ') || 'ingen'}. Rapporter manglende deler som manglende.
Skriv ${RUN}/samlet-rapport.md etter mønsteret i ${PROJECT}/leveranser/2024-v2/samlet-rapport.md: hovedvurdering, avvikstabell fra ${RUN}/deler/kd_ramme/ramme/rammebro-kontroll.json, prioriterte funn med kilde, samordning av kryssende tiltak (samme beløp i to departementer telles én gang), arbeidsdeling med lenker, erfaringer, videre arbeid. Skill rammetildeling, navngitt tilskudd, fellespott, kostnad og politisk føring. Kontroller at hvert beløp i den samlede rapporten står likt i delrapporten det kommer fra.
Skriv ${RUN}/presentasjon.json etter ${PROJECT}/leveranser/2024-v2/presentasjon.json og ${RUN}/videreformidling.md som tydelig usendt utkast med emne, mottakergruppe, hovedfunn, dokumentstatus og vedlegg.
Kjør ${PY} ${SCRIPTS}/assemble_evidence.py ${PROJECT}/${CONFIG} --project ${PROJECT} --output ${RUN}/kildepakke.pdf.
${TEMPLATE ? `Kjør ${PY} ${SCRIPTS}/build_presentation.py ${RUN}/presentasjon.json --template ${TEMPLATE} --output ${RUN}/statsbudsjettet-${YEAR}.pptx${LIBREOFFICE ? ` --libreoffice ${LIBREOFFICE}` : ''} og kontroller renderingen visuelt hvis den finnes.` : 'Ingen mal er oppgitt: lag ikke PowerPoint; skriv i rapporten at presentasjonen ikke er produsert.'}
Skriv ${PROJECT}/arbeidsminne/redaktor/erfaringer-${YEAR}-proeve.md med dato og modell/effort. Send ingenting til noen.`,
    opts('editor', { label: 'redaktor', phase: 'Redaktør', schema: EDITOR_SCHEMA }))

  if (!editor) log('Redaktøren leverte ikke; kontrollen kjører likevel og rapporterer manglende leveranser')

  // -------------------------------------------------------------------------
  phase('Kontroll')

  const CHECK_SCHEMA = {
    type: 'object',
    properties: {
      ready: { type: 'boolean' },
      issues: { type: 'array', items: { type: 'string' } },
      bridge_status: { type: 'string' },
      manifest: { type: 'string' },
      exposure_log_complete: { type: 'boolean' },
      verification_file: { type: 'string' },
    },
    required: ['ready', 'issues', 'bridge_status', 'manifest', 'exposure_log_complete', 'verification_file'],
  }

  check = await agent(`${COMMON}
Sluttkontroll uten faglig omskriving.
1. Kjør ${PY} ${SCRIPTS}/manage_workflow.py check ${PROJECT}/${CONFIG} --project ${PROJECT} --output ${RUN}/kontroll.json. Returkode 2 betyr ufullstendig; list hver issue.
2. Les ${RUN}/deler/kd_ramme/ramme/rammebro-kontroll.json og ${RUN}/hurtigsvar/rammebro-kontroll.json; oppgi status og rest for begge og om totalene er like.
3. Kontroller at alle relative Markdown-lenker i ${RUN}/*.md og ${RUN}/deler/**/rapport.md peker til eksisterende filer.
4. Skriv ${RUN}/manifest.json med SHA-256 for alle filer under ${RUN} og for ${SKILL}/SKILL.md, med created_at_utc og modellplanen: ${JSON.stringify(PLAN)}.
5. Kontroller at ${RUN}/eksponeringslogg.md har oppføringer fra hurtigsvar, alle roller og redaktør, og at ingen forbudt mappe er nevnt som lest. Legg til en avsluttende linje om at loggen er fryst før fasit.
6. Skriv ${RUN}/verifikasjon.md med kjørte kommandoer, resultater og hva kontrollen ikke beviser (faglig riktighet, visuell kvalitet).`,
    opts('check', { label: 'kontroll', phase: 'Kontroll', schema: CHECK_SCHEMA }))
}

return {
  run_id: RUN_ID,
  run_dir: RUN,
  phase_set: PHASE_SET,
  model_plan: PLAN,
  preparation: prep,
  assumptions,
  quick_answer: quick,
  roles: delivered.map(r => ({ role: r.role, parts: r.primary.parts, reviews: r.reviews.length })),
  editor,
  check,
  not_delivered: RUN_FULL ? ROLES.filter(r => !delivered.find(d => d.role === r.id)).map(r => r.id) : [],
}
