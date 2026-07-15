# Fabric- og BI-rapportbygging: skills, kilder, measures og wireframes

Dato: 2026-07-14
Status: implementert skill- og kunnskapsgrunnlag; ingen live Fabric-mutasjoner

## Resultat

To nye repo-forvaltede skills dekker hvert sitt tydelige ansvar:

1. `fabric-item-authoring` ruter opprettelse, oppdatering, deploy og sletting av
   Fabric-items til riktig spesialskill og legger på faste livssyklusporter.
2. `design-bi-report-wireframes` lager én målplattformuavhengig StoryFrame og
   kompilerer deretter separate wireframes for Power BI, React og HTML.

Den viktigste arkitekturavgjørelsen er at vi **ikke** lager ett universelt
layoutformat. Vi deler beslutningsspørsmål, evidens, semantiske roller, measures,
prioritet, merkevareintensjon og sporings-ID-er. Koordinater, visuals,
komponenter, DOM, CSS, interaksjoner og fysiske feltbindinger eies av hver
målplattform.

## 1. Fabric-item-authoring

### Hva som finnes

Den lokale `C:\repos\skills-for-fabric`-arbeidskopien er versjon `0.3.5`. En
read-only fetch viste upstream `main` på `0.3.7`, ni commits foran. Det lokale
settet har god dedikert dekning for blant annet:

- Power BI-rapporter og semantiske modeller
- Notebook, Spark og Lakehouse-relaterte arbeidsflyter
- Warehouse/SQL-endepunkt
- Dataflow Gen2
- Eventstream og Eventhouse/KQL Database
- Activator
- Fabric IQ Ontology
- Materialized Lake View-operasjoner

Upstream `0.3.7` legger blant annet til en SQL Database-skillfamilie og endrer
Power BI-authoring/design. Oppdatering bør gjøres kontrollert som en egen
endring. Plugin-cachen kan samtidig eksponere identiske Power BI-skills med både
prefikset og uprefikset navn; én versjonert kilde må velges per kjøring.

Det nye inventarskriptet verifiserte den lokale, rene committen
`a2332f8fbe3993c445cf0c1d58465bc05d5dce14`: 32 skills fordelt på 10 authoring,
9 consumption, 3 operations, 4 migration og 6 øvrige. Alle 32 har korrekt
junction i `C:\repos\.agents\skills`; ingen av upstream-skillene er junction-
eksponert i `C:\repos\.claude\skills`. Claude-ruten bør derfor velge enten
plugin-installasjon eller junctions i en egen kontrollert endring, ikke begge.

Sammenligning med den aktive Power BI-plugin-cachen fant seks duplikatnavn:
`check-updates`, `powerbi-report-authoring`, `powerbi-report-design`,
`powerbi-report-management`, `powerbi-report-planning` og
`semantic-model-authoring`. De to nye lokale skillene er derimot eksplisitt
wired til både `.agents` og `.claude`.

### Hva som mangler eller er tynt

Følgende områder bør fortsatt capability-gates og eventuelt få smale egne
skills når de blir gjentakende behov:

- Data Pipeline og Copy Job end-to-end authoring
- Environment og Variable Library
- KQL Dashboard og KQL Queryset
- Event Schema Set
- mirrored databases
- GraphQL API og Graph Model
- ML/Data Agent-items
- workspace-, capacity-, tenant-admin-, deployment-pipeline- og Git-orkestrering

`ITEM-DEFINITIONS-CORE.md` i `skills-for-fabric` er verdifull som formatreferanse,
men et definisjonsformat er ikke i seg selv en sikker authoring-workflow.

### Standard livssyklus

```text
DISCOVER
  -> CAPABILITY
  -> AUTHORITY
  -> SNAPSHOT
  -> DEPENDENCIES
  -> VALIDATE
  -> APPLY
  -> POLL
  -> VERIFY
  -> RECORD / RECOVER
```

Viktige regler:

- Sjekk den levende [item management-matrisen](https://learn.microsoft.com/en-us/rest/api/fabric/articles/item-management/item-management-overview)
  og [definition-oversikten](https://learn.microsoft.com/en-us/rest/api/fabric/articles/item-management/definitions/item-definition-overview)
  før hver kjøring.
- `UpdateDefinition` er en full erstatning, ikke en patch. Ta full snapshot med
  hashes og avhengigheter først.
- `202 Accepted` betyr at en long-running operation er startet, ikke at itemet
  virker. Poll til terminal status og kjør målspesifikk smoke-test.
- Bruk [`fabric-cicd`](https://github.com/microsoft/fabric-cicd) for repeterbare
  multi-item deployments; bruk direkte REST for avgrensede, eksplisitt støttede
  enkeltoperasjoner.

Den detaljerte portlisten og offisielle kildene ligger i skillens referanser.

## 2. Gallerier og inspirasjonskilder

Kildene er delt i tre bruksnivåer:

1. **Strukturerte/gjenbrukbare:** Microsoft SamplePBIP, Power BI Desktop samples,
   DAX Lib, Tabular Editor Scripts og åpne React/HTML-systemer med tydelig
   MIT/Apache-lisens.
2. **Visuell inspirasjon:** Fabric Community Galleries, Maven Showcase og
   Dashboard Design Patterns. Her hentes prinsipper, ikke kopier.
3. **Referanse-only:** kilder med opphavsrettslig eller lisensmessig uklarhet,
   blant annet DAX Patterns-formler og data-goblin-repoet.

Fabric Community Galleries viste ved spot checks 2026-07-14 omtrent 13,3k Data
Stories, 5,6k Themes, 3,2k Contests, 1,2k QuickViz og 1,1k Quick Measures.
Siden endres fortløpende, så eksakte tall skal hentes på nytt når de siteres.
Dette er posttall, ikke unike eller fritt lisensierte rapporter. Tallene kan
brukes til å prioritere hvor vi leter, ikke som dokumentasjon på utbredelse.

Hver wireframe bør ha en liten inspirasjonslogg:

| Felt | Innhold |
|---|---|
| kilde | URL + pinned commit når relevant |
| rettigheter | lisens/terms og eventuelle asset-unntak |
| lånt prinsipp | for eksempel sammenligningshierarki eller tomtilstand |
| transformasjon | hvordan prinsippet er tilpasset eget domene og target |
| ikke kopiert | formel, layout, bilde, tema eller tekst som er utelatt |

## 3. Measure-korpus og statistikk

Et metadata-only pilotskript analyserte et verifiserbart, pinned snapshot av
seks offentlige kilde-røtter. Snapshotet er ikke fullt rekonstruerbart fra
repoet alene fordi den kuraterte include-/filelisten og acquisition-scriptet
ikke er del av denne leveransen. Ingen PBIX
ble åpnet eller refreshet, ingen datakilder ble kontaktet, og repoet inneholder
verken målnavn eller DAX-formler.

### Korpus

- 351 measure-forekomster
- 314 unike normaliserte DAX-uttrykk
- 25 artefaktgrupper, som inkluderer både komplette modeller og enkeltstående
  eksempler
- 74 calculation items, 98 calculated columns, 34 calculated tables/partitions
  og 61 TMDL UDF-definisjoner eksplisitt utelatt
- 0 lese-/decode-unntak i 149 gjenkjente kandidatfiler; parseren er ikke en
  komplett DAX-grammatikkvalidator

### Mest utbredt i dette korpuset

| Funksjon/token | Andel av 314 unike uttrykk |
|---|---:|
| `CALCULATE` | 44,6 % |
| `MAX` | 22,6 % |
| `DIVIDE` | 18,5 % |
| `IF` | 16,6 % |
| `HASONEVALUE` | 11,5 % |
| `DATEADD` | 9,2 % |
| `SUMX` | 8,0 % |
| `ALL` | 7,6 % |
| `SUM` | 6,7 % |
| `COUNTROWS` | 6,4 % |

Mønsterfamilier: context/filtering 46,5 %, base aggregation 43,6 %, time
intelligence 26,1 %, `VAR`-basert 25,5 %, safe ratio 18,5 %, conditional logic
17,2 %, iteratorer 13,7 % og selection/filter state 13,4 %.

Dette er ikke global popularitet. Én kilde bidrar med 212 av 314 unike uttrykk,
og korpuset er skjevt mot AdventureWorks, SpaceParts, usage-metrics og SVG-
eksempler. Offentlig sektor, økonomistyring, governance, HR, helse,
tilgjengelighet og produksjonsfeil er underrepresentert. Statistikken brukes som
en prior for ideer; forretningsdefinisjon, grain, additivitet, baseline,
retning, datokontekst og datakvalitet avgjør om et measure skal bygges.

Neste forskningsnivå bør kreve minst 30 uavhengige modeller og 100 measures,
stratifisere på domene, deduplisere forks/template-familier og skille mellom:

- uttrykksprevalens
- mønsterprevalens
- modell-/kildeforekomst
- faktisk visualbruk

## 4. Wireframes for Power BI, React og HTML

### Felles kunnskap

```text
Domain/measure catalog + StoryBrief + NarrativeEvidence + brand/taste
                                |
                                v
                           StoryFrameV1
                    /           |           \
              Power BI       React          HTML
             target IR      target IR      target IR
                 |              |             |
             PBIR/TMDL       app/DOM       document/CSS
```

StoryFrame-utkastet inneholder beslutningsspørsmål, påstander, evidensbehov, semantiske
roller, prioritet, sammenligningskontekst, caveats, freshness, neste handling,
typede globale kildereferanser for brief/evidens/hash og valgfrie brand/taste-intent,
samt frame-spesifikke `traceRefs` tilbake til disse kildene.
Den inneholder ikke koordinater, chart types, komponentnavn, breakpoints, DAX,
SQL eller fysiske feltnavn.

### Målspesifikke wireframes

- **Power BI:** sidearketype, canvas/grid, visuals, slicers, cross-filtering,
  tooltips, bookmarks, drillthrough, theme/taste, mobil og bindinger.
- **React:** route/component tree, typed view models, query/cache-grense,
  responsive hierarchy, tokens, loading/empty/error/stale state, keyboard/ARIA
  og URL/state.
- **HTML:** semantisk dokumentstruktur, chart/table-fallback, no-JS, CSS-grid,
  print/PDF, statisk/interaktiv grense og provenance.

Målet er semantisk og beslutningsmessig parity, ikke pixel parity.

### Bruk av eksisterende report-factory-kunnskap

`C:\repos\bi-konsulent\leveranse\fundament\report-factory` har allerede nyttige
byggesteiner:

- domene- og measure-katalog
- `ReportBlueprintV1`
- object groups og taste profiles
- generering av PBIR/TMDL og en HTML-lookbook

Anbefalt bruk:

- domene-/measure-katalog, story/evidence og brand/taste er gjenbrukbar input;
- `ReportBlueprintV1` forblir Power BI-target-IR;
- HTML-lookbooken forblir en Power BI-designpreview, ikke en generell
  React/HTML-renderer;
- en framtidig kanonisk `StoryFrameV1` bør ligge i fabrikkens contracts-lag og
  få consumer/contract-tester før den blir autoritativ. Skillens JSON-fil er kun
  et illustrativt eksempel.

Dette følger den eksisterende arkitekturregelen om at felles kontrakter stopper
ved fakta, story og brand, mens target-spesifikk geometri og interaksjon blir i
target request/IR.

## 5. Valideringsporter

En rapportleveranse er ikke ferdig før relevant evidens finnes for:

1. kontrakt og sporings-ID-er
2. story/evidence-dekning
3. target capability og fallback
4. statisk fil/schema/lint/accessibility
5. semantisk parity for measure, filter, grain, periode, enhet og retning
6. faktisk render i Power BI, React-breakpoints og HTML screen/print
7. interaksjon, tom-/feiltilstander og menneskelig beslutningsnytte

## 6. Anbefalt videre arbeid

1. Kjør de nye skillene på ett syntetisk økonomistyringscase og produser tre
   target-wireframes fra samme StoryFrame.
2. Etter consumer-testen: foreslå kanonisk `StoryFrameV1` i report-factorys
   contract-lag, ikke i skills-repoet.
3. Oppdater `skills-for-fabric` fra `0.3.5` til `0.3.7` i en egen kontrollert
   endring og rydd eventuell prefikset/uprefikset discovery-duplisering.
4. Utvid measure-korpuset domenevis med lisensklare modeller, særlig offentlig
   økonomi, forecast/budsjett, kvalitet/freshness og internkontroll.
5. Skill corpus-maintenance ut i egen skill når innhenting, deterministisk
   include-/filemanifest, pinning, lisensregister og periodisk reanalyse blir en
   selvstendig gjentakende jobb. Før det skal snapshotet kalles verifiserbart,
   ikke fullt reproducerbart.
