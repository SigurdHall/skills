import { isMain, launch, modelPlan } from '../../skills/knowledge-management/uit-statsbudsjett-analyse/scripts/codex_launch.mjs'
import { prepareDepartments } from '../../skills/knowledge-management/uit-statsbudsjett-analyse/scripts/codex_steps.mjs'

// Codex-variant av uit-departementer.js ved 0fbd0f6. Kjøres med Node, uten Claude Workflow-verktøyet.
export const meta = {
  name: 'codex-uit-departementer',
  description: 'Workflow 2: departmental review of the state budget for UiT: fetch the remaining propositions, five specialist roles with memory, editor, deterministic checks',
  whenToUse: 'Started by $codex-uit-statsbudsjett-proeve after uit-ramme has produced the quick answer in the same run',
  phases: [
    { title: 'Forbered', detail: 'fetch the remaining sources, extract text, prepare work orders', model: null },
    { title: 'Fagroller', detail: 'Luna per role; independent draft and review on Astra', model: 'gpt-5.6-luna' },
    { title: 'Redaktør', detail: 'consolidated report, presentation spec, forwarding draft', model: 'gpt-6-astra' },
    { title: 'Kontroll', detail: 'structural check, bridge recomputation, workbook rebuild, manifest, exposure log', model: null },
  ],
}

export async function run(a, runtime, steps = { prepareDepartments }) {
const { agent, parallel, log, phase } = runtime
const PROJECT = a.project
const SKILL = a.skill
const PY = "'" + a.python.replaceAll("'", "'\\''") + "'"
const CONFIG = a.config
const YEAR = a.budget_year
const RUN_ID = a.run_id
const STAGE = a.stage || 'regjeringens opprinnelige forslag'
const SOURCES_INPUT = a.sources_input || `analyse/kilder/${YEAR}/kilder-input.json`
const DUPLICATE_PARTS = Array.isArray(a.duplicate_parts) ? a.duplicate_parts.filter(p => p && p !== 'ingen') : ['ramme']
const TEMPLATE = a.template || null
const LIBREOFFICE = a.libreoffice || null
const STARTED = a.run_started_utc
const ROLES = a.roles
const FORBIDDEN = Array.isArray(a.forbidden_dirs) ? a.forbidden_dirs : [`${YEAR}/`]

// Skript henter og kontrollerer; Luna tolker fagområdene med høyere effort på kritiske roller.
const PROFILE = 'codex-rask'
const PLAN = modelPlan('departementer', a.models)
const CRITICAL_ROLES = ['kd_ramme', 'helse_miljo', 'naring_arbeid_kultur']
function opts(stage, extra) { return Object.assign({}, PLAN[stage], extra) }
function describe(stage) { const p = PLAN[stage] || {}; return `${p.model || 'sesjonens modell'}, effort ${p.effort || 'sesjonens'}` }

const RUN = `${PROJECT}/leveranser/${RUN_ID}`
const SCRIPTS = `${SKILL}/scripts`
const SOURCES_DIR = `${PROJECT}/analyse/kilder/${YEAR}`
const ASSUMPTIONS_FILE = `${PROJECT}/analyse/uit-forutsetninger-${YEAR}.md`
const BRIDGE_INPUT = `${PROJECT}/analyse/${YEAR}-rammebro-input.json`
const QUICK_DIR = `${RUN}/hurtigsvar`
const WORKBOOK = `${RUN}/uit-ramme-${YEAR}.xlsx`
const QUICK_MD = `${RUN}/hurtigsvar.md`
const HITS_DIR = `${RUN}/treff`

const ENV = `Miljø: kjør skript med ${PY} <skript> <argumenter>. Les og skriv filer direkte på POSIX-stiene. Siter alle stier som separate shell-argumenter.`

const COMMON = `
Prosjekt: ${PROJECT}. Skill: ${SKILL}. Kjøring: ${RUN_ID}, budsjettår ${YEAR}, stadium: ${STAGE}. Startet ${STARTED} UTC.
${ENV}
Les først ${SKILL}/SKILL.md, ${SKILL}/references/agent-workflow.md og ${PROJECT}/arbeidsflyt/leveransekontrakt.md.
Forbudt å åpne eller liste: ${FORBIDDEN.map(d => `${PROJECT}/${d}`).join(', ')} og alle UiT-dokumenter om ${YEAR} datert etter framleggelsen. Alle lesinger av UiT-materiale skal noteres i EXPOSURE_LOG.
Prioritet 1 er korrekt informasjon på de avgjørende punktene: eksakte beløp med enhet, mottaker, år/stadium, nødvendige vilkår og riktig PDF-side. Prioritet 2 er rask, ferdig leveranse: skriv kort, ikke gjenta kildene, og bruk skriptene til alt som kan regnes eller kontrolleres maskinelt. Ukjent beløp er JSON null eller «ukjent» i tekst, aldri tallet 0. Skriv norsk i alle leveransefiler.
Returner bare det strukturerte resultatet; ikke skriv en melding til et menneske.`

log(`codex-uit-departementer. Modellplan (${PROFILE}): forbered og kontroll med skript; kritiske roller ${describe('role_critical')}; øvrige roller ${describe('role_other')}; andreutkast ${describe('duplicate')}; review ${describe('review')}; redaktør ${describe('editor')}`)

// ---------------------------------------------------------------------------
phase('Forbered')
const prep = await steps.prepareDepartments(a)
if (!prep) throw new Error('Forberedelsen feilet; ingen agentresultat')
log(`Kilder hentet: ${prep.sources_fetched}, feilet: ${prep.sources_failed.length}, mangler: ${prep.missing.length}; hurtigsvar til stede: ${prep.quick_answer_present}; treff per del: ${JSON.stringify(prep.hits_per_part)}`)

// ---------------------------------------------------------------------------
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
  const history = ROLES.find(r => r.id === role.id).history
  const outDir = mode === 'duplicate' ? `${RUN}/kontroll/${role.id}` : `${RUN}/deler/${role.id}`
  const isolation = mode === 'duplicate'
    ? `Dette er et uavhengig andreutkast. Ikke les ${RUN}/deler/, ${QUICK_MD}, ${QUICK_DIR} eller andre agenters filer fra denne kjøringen. Skriv bare under ${outDir}/.`
    : `Ikke endre andre rollers filer.`
  return `${COMMON}
Du er fagrollen ${role.id} med delene ${parts}, og kjører som ${describe(roleStage(role, mode))}. Les oppdraget ${RUN}/oppdrag/${role.id}.md.
Avgjørende punkter først: for ramme den eksakte UiT-raden i blått hefte og begge broer uten rest; for hod, kud, nfd og kdd navngitte UiT-tilskudd med beløp, mottaker og vilkår (opptak, engangs, resultatandel); for alle deler finansieringsflyttinger som ikke er kutt. Deretter resten av delen, kort.
Før du åpner årets kilder: les ${PROJECT}/${history} og bare tidligere års prøveminner som er oppført i ${RUN}/minnegrunnlag.json. Ikke les årets prøveminner eller review-minner som ikke er godkjent i denne listen. Beregn SHA-256 av den historiske minnefilen (for eksempel med ${PY} -c) og skriv ${outDir}/minne-lest.json med feltene role, sha256, read_at_utc og memory.
Bruk ${ASSUMPTIONS_FILE} som UiT-side når den finnes. Kilder ligger i ${SOURCES_DIR}/ (PDF og .txt med sidemarkører "## PDF-side N").
Start med de programmatiske treffene ${HITS_DIR}/<del>-treff.md: hvert treff har avsnittet før og etter og PDF-side, og tabellen øverst viser treff per søkeord. Søkeord med hundrevis av treff (for eksempel departementets eget fagområde) er støy: skum dem etter UiT-nærhet og les bare de som nevner UiT, en UiT-enhet eller et navngitt tiltak. Tolk hvert relevant treff som relevant tiltak, rapportering av tidligere år, sektorpott, annen mottaker eller falskt treff, med én setning grunn. Les hele PDF-siden for treff du bekrefter, og let i tillegg etter tiltak uten UiT-navn (finansieringsmodell, programmer, generelle kutt) med søkeordene fra fagminnet. Treffene er ikke uttømmende; notater.md skal skille tolkede treff fra egne søk.
For hver del: skriv ${outDir}/<del>/notater.md (søkeord, treff, avviste treff med grunn, kildehull), ${outDir}/<del>/rapport.md og ${outDir}/<del>/funn.json i formatet fra agent-workflow.md. Ankeret skal inneholde funnets eget beløp; hvis bare et sammenligningstall kan markeres entydig, skal claim si det og et eget anker for beløpet legges til. Kjør ${PY} ${SCRIPTS}/build_evidence.py ${outDir}/<del>/funn.json --project ${PROJECT} --output ${outDir}/<del>/belegg og rett ankere til skriptet godtar dem. Tom funnliste gir et dokumentert negativt resultat, ikke en falsk kilde.
${mode === 'primary' && role.id === 'kd_ramme' ? `Rammen: hurtigsvaret ${QUICK_MD}, Excel-arket ${WORKBOOK} og ${QUICK_DIR}/rammebro-kontroll.json finnes fra samme kjøring. Kontroller hver komponent mot kildene på nytt i stedet for å kopiere; retter du noe, skriv hva og hvorfor i rapport.md, oppdater ${BRIDGE_INPUT} og ${QUICK_DIR}/rammeark-input.json, kjør ${PY} ${SCRIPTS}/reconcile_budget.py ${BRIDGE_INPUT} --output ${outDir}/ramme/rammebro-kontroll.json og bygg Excel-arket på nytt med build_frame_workbook.py.` : ''}
${mode === 'duplicate' && role.id === 'kd_ramme' ? `Rammen: bygg broen selv fra kildene og ${ASSUMPTIONS_FILE}; skriv egen input til ${outDir}/ramme/rammebro-input.json og kjør ${PY} ${SCRIPTS}/reconcile_budget.py på den med --output ${outDir}/ramme/rammebro-kontroll.json.` : ''}
${mode === 'duplicate' ? '' : `Etterpå: skriv ${PROJECT}/arbeidsminne/${role.id}/erfaringer-${YEAR}-proeve.md, merket prøve uten fasit, med dato og modell/effort (${describe(roleStage(role, mode))}). Ikke endre historiske minnefiler.`}
${isolation} Noter hvert åpnet UiT-dokument i EXPOSURE_LOG.`
}

const roleResults = await parallel(ROLES.map(role => async () => {
    const dup = role.parts.filter(p => DUPLICATE_PARTS.includes(p))
    // Begge utkast starter med samme minnegrunnlag før review får lese dem.
    const [primary, second] = await Promise.all([
      agent(rolePrompt(role, 'primary'), opts(roleStage(role, 'primary'), { label: 'rolle:' + role.id, phase: 'Fagroller', schema: ROLE_SCHEMA })),
      dup.length ? agent(rolePrompt({ id: role.id, parts: dup }, 'duplicate'), opts('duplicate', { label: 'andreutkast:' + role.id, phase: 'Fagroller', schema: ROLE_SCHEMA })) : Promise.resolve(null),
    ])
    if (!primary) return { role: role.id, primary: null, reviews: [] }
    if (!dup.length) return { role: role.id, primary, reviews: [] }
    const reviews = await parallel(dup.map(part => () => agent(`${COMMON}
Du kjører som ${describe('review')}. Sammenlignende kontroll av delen ${part} for rollen ${role.id}. Les begge uavhengige utkast: ${RUN}/deler/${role.id}/${part}/ og ${RUN}/kontroll/${role.id}/${part}/, og de samme primærkildene. Kontroller uenigheter mot kildene, og kontroller dekning mot temalisten i ${PROJECT}/arbeidsminne/${role.id}/erfaringer-2018-2023.md, også temaer begge har utelatt. Skriv ${RUN}/deler/${role.id}/${part}/kontroll.md med hver forskjell, hvilket utkast som har kildebelegg, og hvilke vilkår som må inn. Rett bare ${RUN}/deler/${role.id}/${part}/rapport.md og funn.json der du har kildebelegg, og kjør build_evidence.py på nytt hvis funn.json endres. For ramme: hvis rettelsen endrer et beløp, oppdater også ${BRIDGE_INPUT} og ${QUICK_DIR}/rammeark-input.json med kilde, kjør reconcile_budget.py til begge kontrollfiler, bygg arbeidsboken og oppdater hurtigsvar.md. Ingen annen rolle får skrive disse felles filene. Enighet er ikke godkjenning.`,
      opts('review', { label: `kontroll:${part}`, phase: 'Fagroller', schema: REVIEW_SCHEMA }))))
    return { role: role.id, primary, second, reviews: reviews.filter(Boolean) }
  }))
const delivered = roleResults.filter(Boolean).filter(r => r.primary)
log(`Roller levert: ${delivered.length} av ${ROLES.length}`)
const lostConditions = delivered.flatMap(r => r.reviews.flatMap(v => v.conditions_lost))
if (lostConditions.length) log(`Vilkår som måtte gjenopprettes i review: ${lostConditions.length}`)

// ---------------------------------------------------------------------------
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
const editor = await agent(`${COMMON}
Du er redaktøren og kjører som ${describe('editor')}: du oppsummerer alt fra rammearket, hurtigsvaret, de programmatiske treffene og delrapportene. Les ${PROJECT}/arbeidsminne/redaktor/erfaringer-2018-2023.md, bare tidligere års prøveminner oppført i ${RUN}/minnegrunnlag.json først og skriv ${RUN}/minne-lest-redaktor.json med role, sha256, read_at_utc.
Delrapportene ligger i ${RUN}/deler/<rolle>/<del>/, de programmatiske treffene i ${HITS_DIR}/. Hurtigsvaret og Excel-arket fra samme kjøring ligger i ${QUICK_MD} og ${WORKBOOK}; der rammerapporten avviker fra dem, gjelder rammerapporten, og avviket skal nevnes. Kontroller at treff med UiT som mottaker i ${HITS_DIR} er behandlet i en delrapport; udekkede treff listes som åpne punkter. Roller uten leveranse: ${ROLES.filter(r => !delivered.find(d => d.role === r.id)).map(r => r.id).join(', ') || 'ingen'}. Rapporter manglende deler som manglende.
Skriv ${RUN}/samlet-rapport.md etter leveransekontrakten: hovedvurdering, avvikstabell fra ${RUN}/deler/kd_ramme/ramme/rammebro-kontroll.json, prioriterte funn med kilde, samordning av kryssende tiltak (samme beløp i to departementer telles én gang), arbeidsdeling med lenker, erfaringer, videre arbeid. Skill rammetildeling, navngitt tilskudd, fellespott, kostnad og politisk føring. Kontroller at hvert beløp i den samlede rapporten står likt i delrapporten det kommer fra.
Skriv ${RUN}/presentasjon.json i formatet fra build_presentation.py og skillens references/scripts.md og ${RUN}/videreformidling.md som tydelig usendt utkast med emne, mottakergruppe, hovedfunn, dokumentstatus og vedlegg (Excel-arket først).
Kjør ${PY} ${SCRIPTS}/assemble_evidence.py ${PROJECT}/${CONFIG} --project ${PROJECT} --output ${RUN}/kildepakke.pdf.
${TEMPLATE ? `Kjør ${PY} ${SCRIPTS}/build_presentation.py ${RUN}/presentasjon.json --template ${TEMPLATE} --output ${RUN}/statsbudsjettet-${YEAR}.pptx${LIBREOFFICE ? ` --libreoffice ${LIBREOFFICE}` : ''} og kontroller hvert rendret lysark visuelt. Etter faktisk visuell kontroll, skriv ${RUN}/visuell-kontroll.json med {"pptx":"statsbudsjettet-${YEAR}.pptx","inspected_slide_images":["relativ/sti/til/lysark-01.png"],"approved":true}. Listen skal inneholde alle de faktiske lysarkbildene du inspiserte. Uten rendering eller ved uløste feil: approved false; ikke attester en kontroll du ikke utførte.` : 'Ingen mal er oppgitt: lag ikke PowerPoint; skriv i rapporten at presentasjonen ikke er produsert.'}
Skriv ${PROJECT}/arbeidsminne/redaktor/erfaringer-${YEAR}-proeve.md med dato og modell/effort. Send ingenting til noen.`,
  opts('editor', { label: 'redaktor', phase: 'Redaktør', schema: EDITOR_SCHEMA }))
if (!editor) log('Redaktøren leverte ikke; kontrollen kjører likevel og rapporterer manglende leveranser')

// ---------------------------------------------------------------------------
phase('Kontroll')
const check = null // Launcher utfører sluttkontrollen etter at alle modellkall er avsluttet.

return {
  workflow: 'codex-uit-departementer',
  run_id: RUN_ID,
  run_dir: RUN,
  model_plan: PLAN,
  preparation: prep,
  roles: delivered.map(r => ({ role: r.role, parts: r.primary.parts, reviews: r.reviews.length })),
  editor,
  check,
  not_delivered: ROLES.filter(r => !delivered.find(d => d.role === r.id)).map(r => r.id),
}

}

if (isMain(import.meta.url)) await launch(run, process.argv.slice(2), "departementer")
