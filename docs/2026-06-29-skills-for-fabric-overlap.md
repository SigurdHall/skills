# Skills For Fabric Overlap Review

Dato: 2026-06-29

## Kortversjon

Det er ingen direkte `name:`-kollisjoner mellom lokale skills i `C:\repos\skills\skills` og Microsoft `skills-for-fabric`, men det er tydelig trigger- og arbeidsflytkollisjon på Power BI/PBIP/Fabric-området.

Anbefaling:

- Behold dine lokale repo-managed skills som hovedlag for UiT, BOTT, PBIP-filer, dokumentasjon, DAX-forretningslogikk og Tableau->Power BI-migrering.
- Ikke ha hele `fabric-skills`-pakken aktiv som Codex skills til vanlig. Den er for bred og gjør skill-routing mer støyete.
- Behold Microsoft `semantic-model-consumption` og eventuelt `semantic-model-authoring` aktivt når `powerbi-modeling-mcp` skal brukes.
- Deaktiver Microsoft `powerbi-report-*`-skillene inntil `powerbi-report-author` og `powerbi-desktop` CLI faktisk finnes på PATH, eller bruk dem bare som referanse.
- Deaktiver workload-skills for Spark, SQL DW, Eventhouse, Eventstream, Activator, Fabric IQ, Dataflows, MLV og Azure-migrering med mindre en konkret oppgave handler om disse flatene.

## Kartlagt Grunnlag

Lokale repo-managed skills:

- Kilde: `C:\repos\skills\skills`
- Antall: 28
- Viktige grupper for dette spørsmålet:
  - `skills/fabric/*`
  - `skills/powerbi-local/*`
  - `skills/finance/*`
  - `skills/data-integration/*`

Microsoft skills-for-fabric:

- Kilde: `C:\repos\skills-for-fabric\skills`
- Aktivert som junctions:
  - `C:\repos\.agents\skills`
  - `C:\Users\sihal7953\.agents\skills`
- Antall aktive Microsoft-skills: 32

Toolingstatus i denne økten:

- `powerbi-modeling-mcp`: tilgjengelig og registrert i Codex.
- `powerbi-report-author`: ikke funnet på PATH.
- `powerbi-desktop`: ikke funnet på PATH.
- `az`: ikke funnet på PATH.
- `sqlcmd`: ikke funnet på PATH.
- `node`: tilgjengelig.
- `npm`: tilgjengelig.

Konsekvens: Microsofts semantic-model-skills kan være operative via MCP. De fleste Fabric workload- og report-authoring-skills er enten ikke relevante for dagens UiT/PBIP-arbeid eller mangler nødvendige CLI-forutsetninger i denne økten.

## Kollisjonsmatrise

| Flate | Lokale skills | Microsoft skills | Vurdering | Anbefaling |
| --- | --- | --- | --- | --- |
| Lokal PBIP/PBIR/TMDL-filredigering | `powerbi-pbip`, `pbip-full-report`, `uit-powerbi-reporting` | `semantic-model-authoring`, `powerbi-report-authoring` | Reell arbeidsflytkollisjon. Lokal skill er fil-first og bevarer eksisterende PBIP/PBIR/TMDL-kontrakter. Microsoft `semantic-model-authoring` er MCP-first og sier at TMDL-filer er stale når MCP er koblet. | Lokal `powerbi-pbip` skal være default for repo/PBIP-filendringer. Microsoft `semantic-model-authoring` brukes bare når oppgaven eksplisitt er live model/MCP/Fabric semantic model authoring. |
| UiT økonomirapporter | `uit-powerbi-reporting`, `finance-bi-dax-patterns`, `bott-semantic-model`, `uit-bott-okonomimodell` | `semantic-model-authoring`, `powerbi-report-design`, `powerbi-report-planning` | Microsoft-skills mangler UiT/BOTT-regler, norsk økonomisemantikk og etablerte 1600x900/overlay-filtermeny-regler. | Behold lokale UiT/finance-skills som autoritative. Ikke la Microsoft report-design/planning overstyre lokale UiT-layoutregler. |
| DAX og modellmetadata | `finance-bi-dax-patterns`, `powerbi-pbip` | `semantic-model-consumption` | Komplementært. Lokal skill forklarer og feilsøker finans-DAX. Microsoft-skill kjører live DAX/INFO-spørringer via MCP. | Behold `semantic-model-consumption` aktiv hvis live DAX/metadata-spørringer er ønsket. |
| Semantic model authoring | `powerbi-pbip`, `bott-semantic-model`, `fabric-semantic-model-doc` | `semantic-model-authoring` | Delvis overlapp. Microsoft-skill er sterk på MCP/Fabric authoring og Direct Lake. Lokale skills er sterkere på repo/PBIP-kontroll, BOTT og dokumentasjon. | Behold Microsoft-skill som eksplisitt MCP-verktøy, men ikke som default for alle TMDL/PBIP-oppgaver. |
| Report authoring/design | `pbip-full-report`, `powerbi-pbip`, `uit-powerbi-reporting` | `powerbi-report-planning`, `powerbi-report-design`, `powerbi-report-authoring`, `powerbi-report-management` | Stor trigger-overlapp. Microsoft-skillene forutsetter `powerbi-report-author`, `powerbi-desktop`, ofte `az`; disse mangler nå. De bruker også generiske designkontrakter som kan kollidere med UiT-standardene. | Deaktiver Microsoft `powerbi-report-*` aktivt inntil CLI-ene er installert eller bruk kun ved eksplisitt "Microsoft report authoring CLI"-arbeid. |
| Fabric dokumentasjon og governance | `fabric-documentation`, `fabric-architecture-doc`, `fabric-lakehouse-doc`, `fabric-semantic-model-doc`, `fabric-powerbi-report-doc`, `fabric-data-contract-doc`, `fabric-cicd-governance-doc` | Flere workload-skills, `e2e-medallion-architecture` | Liten direkte kollisjon. Lokale skills er dokumentasjons- og governance-orienterte. Microsoft-skillene er operativ CLI/API-workflow. | Behold lokale Fabric-dokumentasjonsskills. Microsoft workload-skills trengs ikke aktivt for dokumentasjon. |
| Delta Sharing | `delta-sharing-powerbi-ppu`, `fabric-delta-sharing-ingestion` | `dataflows-authoring-cli`, `spark-authoring-cli`, `e2e-medallion-architecture` | Delvis overlapp på Fabric ingestion, men lokale skills dekker Databricks/Analyseplattformen/PPU og governance-presisjonen bedre. | Behold lokale Delta Sharing-skills. Microsoft workload-skills aktiveres bare ved konkret Dataflow/Spark/Fabric API-implementasjon. |
| Tableau->Power BI-migrering | `tableau-rest-api`, `powerbi-report-production-loop` | `databricks-migration`, `pipeline-migration`, `synapse-migration`, `hdinsight-migration` | Ikke egentlig samme migreringstype. Lokale skills dekker Tableau-workbook/PBIP/parity. Microsoft migration-skills dekker Azure/Data engineering-migrering. | Microsoft migration-skills er ikke nødvendige aktivt for UiT/Tableau->Power BI. |
| Fabric workloads uten dagens behov | Ingen lokale direkte match for Eventhouse, Eventstream, Activator, Fabric IQ, MLV, SQL DW | `eventhouse-*`, `eventstream-*`, `activator-*`, `fabriciq*`, `mlv-operations-cli`, `sqldw-*`, `spark-*`, `search-consumption-cli` | Disse kan være nyttige senere, men de øker støy i skill discovery nå. Flere krever `az`, `sqlcmd` eller Fabric API-tilgang som ikke er validert. | Deaktiver som aktive Codex-skills nå; behold repoet som referanse. |

## Anbefalt Aktivt Sett Nå

For daglig UiT/Power BI/PBIP-arbeid:

- Alle lokale repo-managed skills i `C:\repos\skills\skills` beholdes.
- Microsoft skills som kan være aktive:
  - `semantic-model-consumption`
  - `semantic-model-authoring` hvis MCP-first live model authoring er ønsket
  - `check-updates` bare som støtte for Microsoft-skills

Microsoft skills som ikke trenger å være aktive nå:

- `activator-authoring-cli`
- `activator-consumption-cli`
- `databricks-migration`
- `dataflows-authoring-cli`
- `dataflows-consumption-cli`
- `dataflows-save-as-authoring-cli`
- `e2e-medallion-architecture`
- `eventhouse-authoring-cli`
- `eventhouse-consumption-cli`
- `eventstream-authoring-cli`
- `eventstream-consumption-cli`
- `fabriciq`
- `fabriciq-ontology-authoring-cli`
- `fabriciq-ontology-consumption-cli`
- `hdinsight-migration`
- `mlv-operations-cli`
- `pipeline-migration`
- `powerbi-report-authoring`
- `powerbi-report-design`
- `powerbi-report-management`
- `powerbi-report-planning`
- `search-consumption-cli`
- `spark-authoring-cli`
- `spark-consumption-cli`
- `spark-operations-cli`
- `sqldw-authoring-cli`
- `sqldw-consumption-cli`
- `sqldw-operations-cli`
- `synapse-migration`

## Routingregler Som Bor Gjelde

1. Når oppgaven handler om lokale PBIP/PBIR/TMDL-filer i repoet:
   - Bruk `powerbi-pbip`.
   - Bruk `uit-powerbi-reporting` for UiT økonomi/rapportering.
   - Ikke la Microsoft `semantic-model-authoring` overstyre fil-first PBIP-kontroll med mindre brukeren eksplisitt ber om MCP/live model workflow.

2. Når oppgaven handler om live semantic model metadata, DAX query eller MCP:
   - Bruk `semantic-model-consumption` for read-only DAX/metadata.
   - Bruk `semantic-model-authoring` for live authoring når MCP skal være kilde til sannhet.

3. Når oppgaven handler om UiT/BOTT økonomi:
   - Bruk `uit-bott-okonomimodell`, `bott-semantic-model`, `finance-bi-dax-patterns` og `uit-powerbi-reporting`.
   - Microsoft skills kan supplere teknisk MCP/Fabric-operasjon, men ikke definere forretningslogikken.

4. Når oppgaven handler om generisk Fabric workload-implementasjon:
   - Aktiver Microsoft workload-skill eksplisitt for den aktuelle flaten.
   - Ikke behold hele `fabric-skills` aktivt til vanlig.

## Oppryddingsstrategi

Ikke slett `C:\repos\skills-for-fabric`. Behold repoet som upstream-referanse.

Rydd bare i aktive junctions under:

- `C:\repos\.agents\skills`
- `C:\Users\sihal7953\.agents\skills`

Sikker strategi:

1. Flytt/deaktiver alle Microsoft workload-junctions som er listet som "ikke nødvendig nå".
2. Behold bare `semantic-model-consumption`, `semantic-model-authoring` og `check-updates` aktivt.
3. Start ny Codex-økt og bekreft at skill-listen er mindre støyete.
4. Reaktiver spesifikke Microsoft-skills ved behov, ikke hele pakken.

## Notater

- Dette er en routing- og discovery-vurdering, ikke en vurdering av kvaliteten på Microsoft-skillene.
- Microsoft-pakken er nyttig som referanse og for Copilot CLI, men full aktiv Codex-discovery gir for mye overlapp mot lokale UiT/PBIP-skills.
- Den mest alvorlige kollisjonen er `powerbi-pbip` vs. `semantic-model-authoring`: fil-first repoarbeid og MCP-first live authoring må skilles eksplisitt.
