---
name: fabric-architecture-doc
description: Skriv Fabric arkitektur- og beslutningsdokumenter i Markdown. Use when documenting Microsoft Fabric solution architecture, target architecture, migration from Tableau/Databricks/SQL/Excel, workspace design, data product architecture, lakehouse vs warehouse, Direct Lake vs Import vs DirectQuery, environment strategy, governance choices, or architecture decision records.
---

# Fabric Architecture Doc

## Arbeidsflyt

1. Bruk `fabric-documentation` som hovedramme.
2. Les `../fabric-documentation/references/microsoft-fabric-principles.md` og `../fabric-documentation/references/document-templates.md`.
3. Kartlegg mål: rapportering, data product, migrering, governance, ytelse eller forvaltning.
4. Dokumenter minst tre lag når de finnes: datakilde, Fabric-lagring/transformasjon, semantic model/rapport.
5. Skill beslutning fra alternativer. Beskriv trade-offs, ikke bare valgt løsning.
6. Ta inn `tableau-rest-api` ved Tableau-migrering og `powerbi-pbip` ved PBIP/Fabric item-filer.

## Må Dekkes

- Formål, målgruppe og status.
- Datakilder og eierskap.
- Valg av lakehouse, warehouse, semantic model, report, notebook, dataflow eller pipeline.
- Lagringsmodus: Import, DirectQuery, Direct Lake eller hybrid.
- Dev/test/prod og Git/deployment-strategi.
- Sikkerhet, sensitivitet, RLS/OLS, personvern og tilgang.
- Drift, refresh, avhengigheter, feilhåndtering og support.
- Åpne risikoer og beslutninger.

## Output

Bruk malen `Architecture Decision Note` fra `document-templates.md` når dokumentet er et beslutningsnotat. Bruk full dokumentstruktur fra `fabric-documentation` når det er løsningsdokumentasjon.

