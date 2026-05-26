# Existing Skill Integration

## Power BI Og PBIP

Bruk `powerbi-pbip` når dokumentasjonen bygger på eller endrer:

- `.pbip`
- `.pbir`
- `definition/report.json`
- `definition/pages/**/page.json`
- `visual.json`
- `.SemanticModel/definition/*.tmdl`
- `.platform`
- themes, bookmarks, custom visuals eller templates

Bruk reglene derfra om UTF-8 uten BOM, JSON-validering, TMDL, relasjoner og PBIP-stioppsett.

## BOTT Og Økonomimodeller

Bruk `bott-semantic-model` og `uit-bott-okonomimodell` når dokumentasjonen gjelder:

- Unit4/BOTT økonomidata
- saldotabell, hovedbok, budsjett, faktura eller reskontro
- konto, koststed, prosjekt, delprosjekt, anlegg/ansatt eller bygg/arbeidspakke
- star schema for økonomistyring
- kontroll, avstemming, internregnskap, BOA, NFR, EU eller prosjektøkonomi

Behold BOTT-konteringsdimensjoner som faktiske koblingsfelt i fakta med mindre brukeren ber om fysisk lagerdesign som krever annet.

## UiT Rapportering

Bruk `uit-powerbi-reporting` når dokumentasjonen gjelder:

- `UiT/PowerBI/Tertialrapport`
- `UiT/PowerBI/templates`
- UiT-tema, farger, KPI-ikoner, rapporteringsenheter eller økonomirapportering

## DAX Og Finansmålinger

Bruk `finance-bi-dax-patterns` når dokumentasjonen beskriver:

- budsjett/regnskap/prognose-målinger
- avvik, prosentavvik, bullet charts eller akseberegninger
- blank-kategori og relasjonsmangler i Power BI
- Sum1-Sum5 eller andre drilldown-mønstre

## Tableau Til Fabric

Bruk `tableau-rest-api` når dokumentasjonen beskriver:

- Tableau Metadata API
- REST API
- `.tdsx`, `.tds` eller `.hyper`
- migrering fra Tableau til Fabric/Power BI

