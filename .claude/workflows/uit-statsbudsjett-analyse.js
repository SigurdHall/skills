export const meta = {
  name: 'uit-statsbudsjett-analyse',
  description: 'Run the UiT state budget analysis: sources, role memories, five specialist roles, editor, deterministic checks',
  whenToUse: 'Started by the user-invoked skill /uit-statsbudsjett-proeve after the publication check has passed; runs one budget year end to end',
  phases: [
    { title: 'Forbered', detail: 'fetch sources, extract text, prepare work orders, open exposure log' },
    { title: 'Forutsetninger', detail: 'locate and document UiT preliminary allocation for the year' },
    { title: 'Fagroller', detail: 'one agent per role; optional independent duplicate and review per critical part' },
    { title: 'Redaktør', detail: 'consolidated report, presentation spec, forwarding draft' },
    { title: 'Kontroll', detail: 'structural check, bridge recomputation, manifest, exposure log' },
  ],
}

// ---------------------------------------------------------------------------
// Arguments. Pass as a JSON object in Workflow({args}). Script arguments use
// POSIX paths (the project lives in WSL). When Claude runs on Windows, files
// are read and written through the UNC path in unc_project, and scripts run
// through python_cmd, e.g. "wsl.exe -e /home/<user>/.venvs/statsbudsjett/bin/python".
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
const ROLES = Array.isArray(a.roles) ? a.roles : [
  { id: 'kd_ramme', parts: ['ramme', 'kd', 'fin'] },
  { id: 'helse_miljo', parts: ['hod', 'kld'] },
  { id: 'naring_arbeid_kultur', parts: ['nfd', 'aid', 'kud'] },
  { id: 'bygg_samisk_justis', parts: ['kdd', 'jd'] },
  { id: 'nordomraader_energi', parts: ['ud', 'oed'] },
]
const FORBIDDEN = Array.isArray(a.forbidden_dirs) ? a.forbidden_dirs : [`${YEAR}/`]

const RUN = `${PROJECT}/leveranser/${RUN_ID}`
const SCRIPTS = `${SKILL}/scripts`

const ENV = UNC
  ? `Miljø: prosjektet ligger i WSL. Les og skriv filer med Read/Write/Glob på UNC-stien ${UNC} + samme relative sti som POSIX-stien. Kjør skript uten shell med PowerShell-verktøyet: ${PY} <skript> <argumenter>, eller Bash med MSYS_NO_PATHCONV=1 foran. Bruk POSIX-stier i alle skriptargumenter. Ikke bruk heredoc gjennom wsl.exe.`
  : `Miljø: kjør skript med ${PY} <skript> <argumenter>. Les og skriv filer direkte på POSIX-stiene.`

const COMMON = `
Prosjekt: ${PROJECT}. Skill: ${SKILL}. Kjøring: ${RUN_ID}, budsjettår ${YEAR}, stadium: ${STAGE}. Startet ${STARTED} UTC.
${ENV}
Les først ${SKILL}/SKILL.md, ${SKILL}/references/agent-workflow.md og ${PROJECT}/arbeidsflyt/leveransekontrakt.md.
Forbudt å åpne eller liste: ${FORBIDDEN.map(d => `${PROJECT}/${d}`).join(', ')} og alle UiT-dokumenter om ${YEAR} datert etter framleggelsen. Alle lesinger av UiT-materiale skal noteres i ${RUN}/eksponeringslogg.md.
Prioritet 1 er korrekt informasjon, prioritet 2 ferdig leveranse. Aldri gjett et tall; skriv null og forklar. Skriv norsk i alle leveransefiler.
Returner bare det strukturerte resultatet; ikke skriv en melding til et menneske.`

// ---------------------------------------------------------------------------
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

const prep = await agent(`${COMMON}
Oppgave: forbered kjøringen uten å analysere innholdet.
1. Hvis ${PROJECT}/${SOURCES_INPUT} finnes: kjør ${PY} ${SCRIPTS}/fetch_sources.py ${PROJECT}/${SOURCES_INPUT} ${PROJECT}/analyse/kilder/${YEAR}. Avvikende eksisterende filer skal ikke overskrives; rapporter dem.
2. For hver PDF i ${PROJECT}/analyse/kilder/${YEAR}/ uten tilhørende .txt: kjør ${PY} ${SCRIPTS}/extract_documents.py <pdf> --output <samme navn>.txt.
3. Kjør ${PY} ${SCRIPTS}/manage_workflow.py prepare ${PROJECT}/${CONFIG} --project ${PROJECT}.
4. Opprett eller utvid ${RUN}/eksponeringslogg.md med: forbudte mapper, dato ${STARTED}, kjøring ${RUN_ID}, og en seksjon "Lest UiT-materiale" som senere agenter fyller ut.
5. List hva som mangler for full analyse: kilder for departementer uten PDF (rollenes deler: ${ROLES.map(r => r.parts.join('/')).join(', ')}), manglende ${PROJECT}/analyse/uit-forutsetninger-${YEAR}.md, mal (${TEMPLATE || 'ikke oppgitt'}) og renderer (${LIBREOFFICE || 'ikke oppgitt'}).`,
  { label: 'forbered', phase: 'Forbered', effort: 'low', schema: PREP_SCHEMA })

if (!prep) throw new Error('Forberedelsen feilet; ingen agentresultat')
log(`Kilder hentet: ${prep.sources_fetched}, feilet: ${prep.sources_failed.length}, mangler: ${prep.missing.length}`)

// ---------------------------------------------------------------------------
phase('Forutsetninger')

const ASSUMPTIONS_SCHEMA = {
  type: 'object',
  properties: {
    found: { type: 'boolean' },
    file: { type: 'string' },
    board_case: { type: 'string' },
    decision_date: { type: 'string' },
    kd_frame_nok_thousand: { type: ['integer', 'null'] },
    sources: { type: 'array', items: { type: 'string' } },
    gaps: { type: 'array', items: { type: 'string' } },
  },
  required: ['found', 'file', 'sources', 'gaps'],
}

const assumptions = await agent(`${COMMON}
Oppgave: dokumenter UiTs forhåndsforutsetninger for budsjettåret ${YEAR}.
Hvis ${PROJECT}/analyse/uit-forutsetninger-${YEAR}.md allerede finnes og har KD-ramme med kilde: les den, kontroller kildene og returner uten å skrive om.
Ellers: bruk ${SKILL}/references/kildekart.md. Finn universitetsstyrets foreløpige fordeling for ${YEAR} (normalt junimøtet ${YEAR - 1}). Start med ${RUN}/kildesjekk.json hvis den finnes; den kan inneholde treff fra UiTs styreportal. Hent dokumentene med ${PY} ${SCRIPTS}/fetch_sources.py til ${PROJECT}/analyse/kilder/uit-forutsetninger-${YEAR}/ (lag en kilder-input.json der først). Lag tekstuttrekk med extract_documents.py. Skriv ${PROJECT}/analyse/uit-forutsetninger-${YEAR}.md med samme struktur som ${PROJECT}/analyse/uit-forutsetninger-2024.md: kilder og versjon, bro fra saldert ${YEAR - 1} til foreløpig ${YEAR} i 1 000 kroner, forutsetninger som skal prøves, resultatgrunnlag, planleggingsår, UiT-spesifikke forhold. Skriv også ${PROJECT}/analyse/${YEAR}-rammebro-input.json med UiT-siden fylt ut og forslagssiden null.
Ikke åpne UiTs analyse av statsbudsjettet ${YEAR}, endelig fordeling ${YEAR} eller tildelingsbrev. Noter alle åpnede UiT-dokumenter i ${RUN}/eksponeringslogg.md.`,
  { label: 'uit-forutsetninger', phase: 'Forutsetninger', schema: ASSUMPTIONS_SCHEMA })

if (!assumptions || !assumptions.found) {
  log('UiTs forhåndsforutsetninger ble ikke funnet; rollene fortsetter, men rammeavviket kan ikke beregnes')
}

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

function rolePrompt(role, mode) {
  const parts = role.parts.join(', ')
  const outDir = mode === 'duplicate' ? `${RUN}/kontroll/${role.id}` : `${RUN}/deler/${role.id}`
  const isolation = mode === 'duplicate'
    ? `Dette er et uavhengig andreutkast. Ikke les ${RUN}/deler/ eller andre agenters filer fra denne kjøringen. Skriv bare under ${outDir}/.`
    : `Ikke endre andre rollers filer.`
  return `${COMMON}
Du er fagrollen ${role.id} med delene ${parts}. Les oppdraget ${RUN}/oppdrag/${role.id}.md.
Før du åpner årets kilder: les ${PROJECT}/arbeidsminne/${role.id}/erfaringer-2018-2023.md og alle ${PROJECT}/arbeidsminne/${role.id}/erfaringer-*-proeve.md og erfaringer-review-*.md. Beregn SHA-256 av den historiske minnefilen (for eksempel med ${PY} -c) og skriv ${outDir}/minne-lest.json med feltene role, sha256, read_at_utc og memory.
Bruk ${PROJECT}/analyse/uit-forutsetninger-${YEAR}.md som UiT-side når den finnes. Kilder ligger i ${PROJECT}/analyse/kilder/${YEAR}/ (PDF og .txt med "=== PDF-side N ===").
For hver del: skriv ${outDir}/<del>/notater.md (søkeord, treff, avviste treff med grunn, kildehull), ${outDir}/<del>/rapport.md og ${outDir}/<del>/funn.json i formatet fra agent-workflow.md. Ankeret skal inneholde funnets eget beløp; hvis bare et sammenligningstall kan markeres entydig, skal claim si det og et eget anker for beløpet legges til. Kjør ${PY} ${SCRIPTS}/build_evidence.py ${outDir}/<del>/funn.json --project ${PROJECT} --output ${outDir}/<del>/belegg og rett ankere til skriptet godtar dem. Tom funnliste gir et dokumentert negativt resultat, ikke en falsk kilde.
Rollen kd_ramme skal i tillegg fylle forslagssiden i ${PROJECT}/analyse/${YEAR}-rammebro-input.json og kjøre ${PY} ${SCRIPTS}/reconcile_budget.py ${PROJECT}/analyse/${YEAR}-rammebro-input.json --output ${outDir}/ramme/rammebro-kontroll.json; resten må være null.
${mode === 'duplicate' ? '' : `Etterpå: skriv ${PROJECT}/arbeidsminne/${role.id}/erfaringer-${YEAR}-proeve.md, merket prøve uten fasit, med dato, modell og effort du kjørte med. Ikke endre historiske minnefiler.`}
${isolation} Noter hvert åpnet UiT-dokument i ${RUN}/eksponeringslogg.md.`
}

const roleResults = await pipeline(
  ROLES,
  role => agent(rolePrompt(role, 'primary'), { label: `rolle:${role.id}`, phase: 'Fagroller', schema: ROLE_SCHEMA }),
  async (primary, role) => {
    if (!primary) return { role: role.id, primary: null, reviews: [] }
    const dup = role.parts.filter(p => DUPLICATE_PARTS.includes(p))
    if (!dup.length) return { role: role.id, primary, reviews: [] }
    const second = await agent(rolePrompt({ id: role.id, parts: dup }, 'duplicate'),
      { label: `andreutkast:${role.id}`, phase: 'Fagroller', schema: ROLE_SCHEMA })
    const reviews = await parallel(dup.map(part => () => agent(`${COMMON}
Sammenlignende kontroll av delen ${part} for rollen ${role.id}. Les begge uavhengige utkast: ${RUN}/deler/${role.id}/${part}/ og ${RUN}/kontroll/${role.id}/${part}/, og de samme primærkildene. Kontroller uenigheter mot kildene, og kontroller dekning mot temalisten i ${PROJECT}/arbeidsminne/${role.id}/erfaringer-2018-2023.md, også temaer begge har utelatt. Skriv ${RUN}/deler/${role.id}/${part}/kontroll.md med hver forskjell, hvilket utkast som har kildebelegg, og hvilke vilkår som må inn. Rett bare ${RUN}/deler/${role.id}/${part}/rapport.md og funn.json der du har kildebelegg, og kjør build_evidence.py på nytt hvis funn.json endres. Enighet er ikke godkjenning.`,
      { label: `kontroll:${part}`, phase: 'Fagroller', schema: REVIEW_SCHEMA })))
    return { role: role.id, primary, second, reviews: reviews.filter(Boolean) }
  },
)

const delivered = roleResults.filter(Boolean).filter(r => r.primary)
log(`Roller levert: ${delivered.length} av ${ROLES.length}`)
const lostConditions = delivered.flatMap(r => r.reviews.flatMap(v => v.conditions_lost))
if (lostConditions.length) log(`Vilkår som måtte gjenopprettes i review: ${lostConditions.length}`)

// ---------------------------------------------------------------------------
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

const editor = await agent(`${COMMON}
Du er redaktøren. Les ${PROJECT}/arbeidsminne/redaktor/erfaringer-2018-2023.md, erfaringer-*-proeve.md og erfaringer-review-*.md først og skriv ${RUN}/minne-lest-redaktor.json med role, sha256, read_at_utc.
Delrapportene ligger i ${RUN}/deler/<rolle>/<del>/. Roller uten leveranse: ${ROLES.filter(r => !delivered.find(d => d.role === r.id)).map(r => r.id).join(', ') || 'ingen'}. Rapporter manglende deler som manglende.
Skriv ${RUN}/samlet-rapport.md etter mønsteret i ${PROJECT}/leveranser/2024-v2/samlet-rapport.md: hovedvurdering, avvikstabell fra ${RUN}/deler/kd_ramme/ramme/rammebro-kontroll.json, prioriterte funn med kilde, samordning av kryssende tiltak (samme beløp i to departementer telles én gang), arbeidsdeling med lenker, erfaringer, videre arbeid. Skill rammetildeling, navngitt tilskudd, fellespott, kostnad og politisk føring.
Skriv ${RUN}/presentasjon.json etter ${PROJECT}/leveranser/2024-v2/presentasjon.json og ${RUN}/videreformidling.md som tydelig usendt utkast med emne, mottakergruppe, hovedfunn, dokumentstatus og vedlegg.
Kjør ${PY} ${SCRIPTS}/assemble_evidence.py ${PROJECT}/${CONFIG} --project ${PROJECT} --output ${RUN}/kildepakke.pdf.
${TEMPLATE ? `Kjør ${PY} ${SCRIPTS}/build_presentation.py ${RUN}/presentasjon.json --template ${TEMPLATE} --output ${RUN}/statsbudsjettet-${YEAR}.pptx${LIBREOFFICE ? ` --libreoffice ${LIBREOFFICE}` : ''} og kontroller renderingen visuelt hvis den finnes.` : 'Ingen mal er oppgitt: lag ikke PowerPoint; skriv i rapporten at presentasjonen ikke er produsert.'}
Skriv ${PROJECT}/arbeidsminne/redaktor/erfaringer-${YEAR}-proeve.md. Send ingenting til noen.`,
  { label: 'redaktor', phase: 'Redaktør', schema: EDITOR_SCHEMA })

if (!editor) log('Redaktøren leverte ikke; kontrollen kjører likevel og rapporterer manglende leveranser')

// ---------------------------------------------------------------------------
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

const check = await agent(`${COMMON}
Sluttkontroll uten faglig omskriving.
1. Kjør ${PY} ${SCRIPTS}/manage_workflow.py check ${PROJECT}/${CONFIG} --project ${PROJECT} --output ${RUN}/kontroll.json. Returkode 2 betyr ufullstendig; list hver issue.
2. Les ${RUN}/deler/kd_ramme/ramme/rammebro-kontroll.json og oppgi status og rest. Hvis filen mangler, si det.
3. Kontroller at alle relative Markdown-lenker i ${RUN}/*.md og ${RUN}/deler/**/rapport.md peker til eksisterende filer.
4. Skriv ${RUN}/manifest.json med SHA-256 for alle filer under ${RUN} og for ${SKILL}/SKILL.md, med created_at_utc.
5. Kontroller at ${RUN}/eksponeringslogg.md har oppføringer fra alle roller og redaktør og at ingen forbudt mappe er nevnt som lest. Legg til en avsluttende linje om at loggen er fryst før fasit.
6. Skriv ${RUN}/verifikasjon.md med kjørte kommandoer, resultater og hva kontrollen ikke beviser (faglig riktighet, visuell kvalitet).`,
  { label: 'kontroll', phase: 'Kontroll', effort: 'low', schema: CHECK_SCHEMA })

return {
  run_id: RUN_ID,
  run_dir: RUN,
  preparation: prep,
  assumptions,
  roles: delivered.map(r => ({ role: r.role, parts: r.primary.parts, reviews: r.reviews.length })),
  editor,
  check,
  not_delivered: ROLES.filter(r => !delivered.find(d => d.role === r.id)).map(r => r.id),
}
