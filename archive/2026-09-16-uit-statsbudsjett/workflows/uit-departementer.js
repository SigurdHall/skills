export const meta = {
  name: 'uit-departementer',
  description: 'Workflow 2: departmental review of the state budget for UiT: fetch the remaining propositions, five specialist roles with memory, editor, deterministic checks',
  whenToUse: 'Started by /uit-statsbudsjett-proeve after uit-ramme has produced the quick answer in the same run',
  phases: [
    { title: 'Forbered', detail: 'fetch the remaining sources, extract text, prepare work orders', model: 'sonnet' },
    { title: 'Fagroller', detail: 'one agent per role; critical roles on opus, others on sonnet; optional duplicate and review', model: 'opus' },
    { title: 'Redaktør', detail: 'consolidated report, presentation spec, forwarding draft', model: 'opus' },
    { title: 'Kontroll', detail: 'structural check, bridge recomputation, workbook rebuild, manifest, exposure log', model: 'sonnet' },
  ],
}

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
const ROLES = Array.isArray(a.roles) ? a.roles : [
  { id: 'kd_ramme', parts: ['ramme', 'kd', 'fin'] },
  { id: 'helse_miljo', parts: ['hod', 'kld'] },
  { id: 'naring_arbeid_kultur', parts: ['nfd', 'aid', 'kud'] },
  { id: 'bygg_samisk_justis', parts: ['kdd', 'jd'] },
  { id: 'nordomraader_energi', parts: ['ud', 'oed'] },
]
const FORBIDDEN = Array.isArray(a.forbidden_dirs) ? a.forbidden_dirs : [`${YEAR}/`]

// Model plan: programmatic hits (extract_hits.py) are interpreted by every role on
// opus medium; the editor summarises everything on fable high; mechanical stages
// and duplicate drafts run on sonnet.
const PROFILE = a.profile || 'rask'
const PLAN_RASK = {
  prep: { model: 'sonnet', effort: 'low' },
  role_critical: { model: 'opus', effort: 'medium' },
  role_other: { model: 'opus', effort: 'medium' },
  duplicate: { model: 'sonnet', effort: 'medium' },
  review: { model: 'opus', effort: 'medium' },
  editor: { model: 'fable', effort: 'high' },
  check: { model: 'sonnet', effort: 'low' },
}
const PLAN_SESJON = { prep: { effort: 'low' }, role_critical: {}, role_other: {}, duplicate: {}, review: {}, editor: {}, check: { effort: 'low' } }
const PLAN = Object.assign({}, PROFILE === 'sesjon' ? PLAN_SESJON : PLAN_RASK, a.models || {})
const CRITICAL_ROLES = Array.isArray(a.critical_roles) ? a.critical_roles : ['kd_ramme', 'helse_miljo', 'naring_arbeid_kultur']
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

log(`uit-departementer. Modellplan (${PROFILE}): forbered ${describe('prep')}; kritiske roller ${describe('role_critical')}; øvrige roller ${describe('role_other')}; andreutkast ${describe('duplicate')}; review ${describe('review')}; redaktør ${describe('editor')}; kontroll ${describe('check')}`)

// ---------------------------------------------------------------------------
phase('Forbered')
const PREP_SCHEMA = {
  type: 'object',
  properties: {
    quick_answer_present: { type: 'boolean' },
    sources_fetched: { type: 'integer' },
    sources_failed: { type: 'array', items: { type: 'string' } },
    extracts_written: { type: 'integer' },
    work_orders_written: { type: 'integer' },
    hits_per_part: { type: 'object', additionalProperties: { type: 'integer' } },
    exposure_log: { type: 'string' },
    missing: { type: 'array', items: { type: 'string' } },
  },
  required: ['quick_answer_present', 'sources_fetched', 'sources_failed', 'extracts_written', 'work_orders_written', 'hits_per_part', 'exposure_log', 'missing'],
}
const prep = await agent(`${COMMON}
Oppgave: forbered departementsgjennomgangen uten å analysere innholdet. Blått hefte, KD og hurtigsvaret (${QUICK_MD}, ${WORKBOOK}) skal finnes fra workflow uit-ramme i samme kjøring; rapporter om de gjør det. Andre filer for ${YEAR} som du ikke forventer, rapporteres i missing som "uventet rest".
1. Kjør ${PY} ${SCRIPTS}/fetch_sources.py ${PROJECT}/${SOURCES_INPUT} ${SOURCES_DIR}. Identiske filer som allerede finnes, beholdes av skriptet; avvikende eksisterende filer skal ikke overskrives; rapporter dem.
2. For hver PDF i ${SOURCES_DIR}/ uten tilhørende .txt: kjør ${PY} ${SCRIPTS}/extract_documents.py <pdf> --output <samme navn>.txt.
3. Kjør ${PY} ${SCRIPTS}/manage_workflow.py prepare ${PROJECT}/${CONFIG} --project ${PROJECT}.
4. Programmatisk søk: kjør ${PY} ${SCRIPTS}/extract_hits.py ${PROJECT}/${CONFIG} --sources-dir ${SOURCES_DIR} --output ${HITS_DIR} --year ${YEAR}. Det skriver <del>-treff.md og <del>-treff.json per del med hvert treffavsnitt pluss avsnittet før og etter, PDF-side og søkeord. Rapporter antall treff per del (hits_per_part, feltet total per del) og deler med manglende uttrekk.
5. Utvid ${RUN}/eksponeringslogg.md med fasesett departementer, dato ${STARTED}, og en seksjon "Lest UiT-materiale" som rollene fyller ut.
6. List hva som mangler: kilder for departementer uten PDF (rollenes deler: ${ROLES.map(r => r.parts.join('/')).join(', ')}), manglende ${ASSUMPTIONS_FILE}, mal (${TEMPLATE || 'ikke oppgitt'}) og renderer (${LIBREOFFICE || 'ikke oppgitt'}).`,
  opts('prep', { label: 'forbered', phase: 'Forbered', schema: PREP_SCHEMA }))
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
  const outDir = mode === 'duplicate' ? `${RUN}/kontroll/${role.id}` : `${RUN}/deler/${role.id}`
  const isolation = mode === 'duplicate'
    ? `Dette er et uavhengig andreutkast. Ikke les ${RUN}/deler/, ${QUICK_MD}, ${QUICK_DIR} eller andre agenters filer fra denne kjøringen. Skriv bare under ${outDir}/.`
    : `Ikke endre andre rollers filer.`
  return `${COMMON}
Du er fagrollen ${role.id} med delene ${parts}, og kjører som ${describe(roleStage(role, mode))}. Les oppdraget ${RUN}/oppdrag/${role.id}.md.
Avgjørende punkter først: for ramme den eksakte UiT-raden i blått hefte og begge broer uten rest; for hod, kud, nfd og kdd navngitte UiT-tilskudd med beløp, mottaker og vilkår (opptak, engangs, resultatandel); for alle deler finansieringsflyttinger som ikke er kutt. Deretter resten av delen, kort.
Før du åpner årets kilder: les ${PROJECT}/arbeidsminne/${role.id}/erfaringer-2018-2023.md og alle ${PROJECT}/arbeidsminne/${role.id}/erfaringer-*-proeve.md og erfaringer-review-*.md. Beregn SHA-256 av den historiske minnefilen (for eksempel med ${PY} -c) og skriv ${outDir}/minne-lest.json med feltene role, sha256, read_at_utc og memory.
Bruk ${ASSUMPTIONS_FILE} som UiT-side når den finnes. Kilder ligger i ${SOURCES_DIR}/ (PDF og .txt med sidemarkører "## PDF-side N").
Start med de programmatiske treffene ${HITS_DIR}/<del>-treff.md: hvert treff har avsnittet før og etter og PDF-side, og tabellen øverst viser treff per søkeord. Søkeord med hundrevis av treff (for eksempel departementets eget fagområde) er støy: skum dem etter UiT-nærhet og les bare de som nevner UiT, en UiT-enhet eller et navngitt tiltak. Tolk hvert relevant treff som relevant tiltak, rapportering av tidligere år, sektorpott, annen mottaker eller falskt treff, med én setning grunn. Les hele PDF-siden for treff du bekrefter, og let i tillegg etter tiltak uten UiT-navn (finansieringsmodell, programmer, generelle kutt) med søkeordene fra fagminnet. Treffene er ikke uttømmende; notater.md skal skille tolkede treff fra egne søk.
For hver del: skriv ${outDir}/<del>/notater.md (søkeord, treff, avviste treff med grunn, kildehull), ${outDir}/<del>/rapport.md og ${outDir}/<del>/funn.json i formatet fra agent-workflow.md. Ankeret skal inneholde funnets eget beløp; hvis bare et sammenligningstall kan markeres entydig, skal claim si det og et eget anker for beløpet legges til. Kjør ${PY} ${SCRIPTS}/build_evidence.py ${outDir}/<del>/funn.json --project ${PROJECT} --output ${outDir}/<del>/belegg og rett ankere til skriptet godtar dem. Tom funnliste gir et dokumentert negativt resultat, ikke en falsk kilde.
${mode === 'primary' && role.id === 'kd_ramme' ? `Rammen: hurtigsvaret ${QUICK_MD}, Excel-arket ${WORKBOOK} og ${QUICK_DIR}/rammebro-kontroll.json finnes fra samme kjøring. Kontroller hver komponent mot kildene på nytt i stedet for å kopiere; retter du noe, skriv hva og hvorfor i rapport.md, oppdater ${BRIDGE_INPUT} og ${QUICK_DIR}/rammeark-input.json, kjør ${PY} ${SCRIPTS}/reconcile_budget.py ${BRIDGE_INPUT} --output ${outDir}/ramme/rammebro-kontroll.json og bygg Excel-arket på nytt med build_frame_workbook.py.` : ''}
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
Du er redaktøren og kjører som ${describe('editor')}: du oppsummerer alt fra rammearket, hurtigsvaret, de programmatiske treffene og delrapportene. Les ${PROJECT}/arbeidsminne/redaktor/erfaringer-2018-2023.md, erfaringer-*-proeve.md og erfaringer-review-*.md først og skriv ${RUN}/minne-lest-redaktor.json med role, sha256, read_at_utc.
Delrapportene ligger i ${RUN}/deler/<rolle>/<del>/, de programmatiske treffene i ${HITS_DIR}/. Hurtigsvaret og Excel-arket fra samme kjøring ligger i ${QUICK_MD} og ${WORKBOOK}; der rammerapporten avviker fra dem, gjelder rammerapporten, og avviket skal nevnes. Kontroller at treff med UiT som mottaker i ${HITS_DIR} er behandlet i en delrapport; udekkede treff listes som åpne punkter. Roller uten leveranse: ${ROLES.filter(r => !delivered.find(d => d.role === r.id)).map(r => r.id).join(', ') || 'ingen'}. Rapporter manglende deler som manglende.
Skriv ${RUN}/samlet-rapport.md etter mønsteret i ${PROJECT}/leveranser/2024-v2/samlet-rapport.md: hovedvurdering, avvikstabell fra ${RUN}/deler/kd_ramme/ramme/rammebro-kontroll.json, prioriterte funn med kilde, samordning av kryssende tiltak (samme beløp i to departementer telles én gang), arbeidsdeling med lenker, erfaringer, videre arbeid. Skill rammetildeling, navngitt tilskudd, fellespott, kostnad og politisk føring. Kontroller at hvert beløp i den samlede rapporten står likt i delrapporten det kommer fra.
Skriv ${RUN}/presentasjon.json etter ${PROJECT}/leveranser/2024-v2/presentasjon.json og ${RUN}/videreformidling.md som tydelig usendt utkast med emne, mottakergruppe, hovedfunn, dokumentstatus og vedlegg (Excel-arket først).
Kjør ${PY} ${SCRIPTS}/assemble_evidence.py ${PROJECT}/${CONFIG} --project ${PROJECT} --output ${RUN}/kildepakke.pdf.
${TEMPLATE ? `Kjør ${PY} ${SCRIPTS}/build_presentation.py ${RUN}/presentasjon.json --template ${TEMPLATE} --output ${RUN}/statsbudsjettet-${YEAR}.pptx${LIBREOFFICE ? ` --libreoffice ${LIBREOFFICE}` : ''} og kontroller renderingen visuelt hvis den finnes.` : 'Ingen mal er oppgitt: lag ikke PowerPoint; skriv i rapporten at presentasjonen ikke er produsert.'}
Skriv ${PROJECT}/arbeidsminne/redaktor/erfaringer-${YEAR}-proeve.md med dato og modell/effort. Send ingenting til noen.`,
  opts('editor', { label: 'redaktor', phase: 'Redaktør', schema: EDITOR_SCHEMA }))
if (!editor) log('Redaktøren leverte ikke; kontrollen kjører likevel og rapporterer manglende leveranser')

// ---------------------------------------------------------------------------
phase('Kontroll')
const CHECK_SCHEMA = {
  type: 'object',
  properties: {
    ready: { type: 'boolean' },
    issues: { type: 'array', items: { type: 'string' } },
    bridge_status: { type: 'string' },
    workbook_checked: { type: 'boolean' },
    manifest: { type: 'string' },
    exposure_log_complete: { type: 'boolean' },
    verification_file: { type: 'string' },
  },
  required: ['ready', 'issues', 'bridge_status', 'workbook_checked', 'manifest', 'exposure_log_complete', 'verification_file'],
}
const check = await agent(`${COMMON}
Sluttkontroll uten faglig omskriving.
1. Kjør ${PY} ${SCRIPTS}/manage_workflow.py check ${PROJECT}/${CONFIG} --project ${PROJECT} --output ${RUN}/kontroll.json. Returkode 2 betyr ufullstendig; list hver issue.
2. Les ${RUN}/deler/kd_ramme/ramme/rammebro-kontroll.json og ${QUICK_DIR}/rammebro-kontroll.json; oppgi status og rest for begge og om totalene er like. Kjør ${PY} ${SCRIPTS}/build_frame_workbook.py ${QUICK_DIR}/rammeark-input.json --output ${QUICK_DIR}/kontroll-uit-ramme.xlsx og bekreft returkode 0.
3. Kontroller at alle relative Markdown-lenker i ${RUN}/*.md og ${RUN}/deler/**/rapport.md peker til eksisterende filer.
4. Skriv ${RUN}/manifest.json med SHA-256 for alle filer under ${RUN} og for ${SKILL}/SKILL.md, med created_at_utc og modellplanen: ${JSON.stringify(PLAN)}.
5. Kontroller at ${RUN}/eksponeringslogg.md har oppføringer fra hurtigsvar, avvik, alle roller og redaktør, og at ingen forbudt mappe er nevnt som lest. Legg til en avsluttende linje om at loggen er fryst før fasit.
6. Skriv ${RUN}/verifikasjon.md med kjørte kommandoer, resultater og hva kontrollen ikke beviser (faglig riktighet, visuell kvalitet).`,
  opts('check', { label: 'kontroll', phase: 'Kontroll', schema: CHECK_SCHEMA }))

return {
  workflow: 'uit-departementer',
  run_id: RUN_ID,
  run_dir: RUN,
  model_plan: PLAN,
  preparation: prep,
  roles: delivered.map(r => ({ role: r.role, parts: r.primary.parts, reviews: r.reviews.length })),
  editor,
  check,
  not_delivered: ROLES.filter(r => !delivered.find(d => d.role === r.id)).map(r => r.id),
}
