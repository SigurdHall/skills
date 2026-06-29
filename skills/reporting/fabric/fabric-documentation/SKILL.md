---
name: fabric-documentation
description: Main skill for creating, improving, or quality-checking Markdown documentation for Microsoft Fabric and Power BI. Use when the user asks to skrive Fabric-dokumentasjon, lage README/docs, document semantic models, lakehouse, warehouse, medallion, notebooks, pipelines, Git integration, CI/CD, governance, data products, runbooks, data contracts, star schema docs, PBIP/TMDL/Fabric item files, or when a Fabric documentation task does not clearly fit a narrower Fabric skill.
---

# Fabric Documentation

## Formål

Bruk denne hovedskillen til å lage praktiske, repo-vennlige Markdown-dokumenter for Fabric-løsninger. Skillen skal koordinere underskills for dokumenttype og hente inn eksisterende Power BI/BOTT-skills når domene eller modell krever det.

## Før Du Skriver

1. Finn målmappe og eksisterende dokumentasjonsstil.
2. Sjekk om dokumentet gjelder Fabric item definitions, repo-dokumentasjon eller begge deler.
3. Ikke legg frie `.md`-dokumenter inne i Fabric item-mapper hvis Git integration kan tolke mappen som et styrt item. Bruk normalt `docs/`, `architecture/` eller prosjektets etablerte dokumentmappe.
4. Les relevante Fabric item-filer før du dokumenterer dem:
   - `*.pbip`
   - `.Report/definition.pbir`
   - `.Report/definition/report.json`
   - `.SemanticModel/definition/model.tmdl`
   - `.SemanticModel/definition/relationships.tmdl`
   - `.SemanticModel/definition/tables/*.tmdl`
   - notebook-, pipeline- og lakehouse-definisjoner der de finnes i repoet
5. Hvis dokumentasjonen gjelder økonomi, BOTT eller UiT, bruk også `uit-bott-okonomimodell` og `bott-semantic-model`.
6. Hvis dokumentasjonen gjelder PBIP, TMDL, report JSON eller tema, bruk også `powerbi-pbip`.

## Velg Underskill

- Bruk `fabric-architecture-doc` for målarkitektur, løsningsdesign, plattformvalg, migrering og beslutningsnotater.
- Bruk `fabric-lakehouse-doc` for lakehouse, warehouse, medallion, datakilder, tabeller, pipelines, notebooks og databehandling.
- Bruk `fabric-delta-sharing-ingestion` for Delta Sharing til Fabric Dataflow Gen2, lakehouse/warehouse, gjenbrukbare data products og styrt overgang fra direkte Power BI-import til Fabric.
- Bruk `fabric-semantic-model-doc` for semantic model, TMDL, stjerneskjema, relasjoner, målinger, RLS/OLS og modellkvalitet.
- Bruk `fabric-powerbi-report-doc` for rapporter, sider, visuals, navigasjon, tema, KPI-er og rapportstandard.
- Bruk `fabric-cicd-governance-doc` for Git integration, deployment pipelines, miljøer, roller, publisering, drift, risiko og kontroll.
- Bruk `fabric-data-contract-doc` for datakontrakter, grensesnitt, tabellkrav, kvalitetssjekker og eierskap.

## Felles Dokumentstruktur

Start med denne strukturen og tilpass:

```markdown
# <Tittel>

## Kortversjon
## Formål og status
## Omfang
## Arkitektur / innhold
## Datagrunnlag
## Modell og relasjoner
## Drift, refresh og eierskap
## Sikkerhet, personvern og tilgang
## Kvalitetssjekker
## Kjente begrensninger
## Neste steg
## Kilder
```

For produksjonsnære dokumenter, inkluder alltid eier, miljø, kilde, refresh, tilgang, sensitivitet, avhengigheter og test-/kontrollpunkter.

## Ressurser

Les bare det som trengs:

- `references/microsoft-fabric-principles.md` for Microsoft-baserte prinsipper.
- `references/document-templates.md` for konkrete Markdown-maler.
- `references/existing-skill-integration.md` for når andre lokale skills skal brukes.
- `references/quality-checklist.md` før ferdigstilling.

## Validering

1. Sjekk at Markdown-filen ligger utenfor styrte Fabric item-mapper med mindre repoet eksplisitt bruker en annen standard.
2. Sjekk at dokumentet skiller fakta fra antakelser.
3. Sjekk at Fabric/Power BI-navn matcher filene eller kildene.
4. Sjekk at personvern, tilgang, refresh, lineage og eier er dekket der det er relevant.
5. For PBIP/TMDL-dokumentasjon, rapporter om du faktisk leste modellfilene eller bare jobbet fra antakelser.
