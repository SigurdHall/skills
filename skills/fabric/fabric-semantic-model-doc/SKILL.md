---
name: fabric-semantic-model-doc
description: Write Markdown documentation that describes an existing Fabric/Power BI semantic model, including TMDL, star schema, fact tables, dimensions, relationships, DAX measures, RLS/OLS, Direct Lake, Import, DirectQuery, refresh, and model quality. Use when the user asks for semantic model docs, datamodell-dokumentasjon, TMDL documentation, star schema documentation, PBIP model docs, CSV star schema docs, or relationship/measure documentation. Use bott-semantic-model instead when the task is to design the model structure, and uit-bott-okonomimodell when the task is to interpret individual BOTT finance fields.
---

# Fabric Semantic Model Doc

## Arbeidsflyt

1. Bruk `fabric-documentation` som hovedramme.
2. Bruk `powerbi-pbip` før du leser eller endrer PBIP/TMDL.
3. Inspiser relevante filer:
   - `definition/model.tmdl`
   - `definition/relationships.tmdl`
   - `definition/tables/*.tmdl`
   - `definition/database.tmdl`
   - `definition.pbism`
4. Bruk `bott-semantic-model` og `uit-bott-okonomimodell` for BOTT/UiT økonomidata.
5. Bruk `finance-bi-dax-patterns` når målinger, budsjett/regnskap/prognose eller rapporteringslogikk skal forklares.
6. Dokumenter faktisk modelltilstand. Merk forslag og anbefalinger tydelig som forslag.

## Må Dekkes

- Modellformål og målgruppe.
- Kildegrunnlag og refresh/lagringsmodus.
- Faktatabeller med radkorn, beløpsfelt og degenerate dimensions.
- Dimensjoner med nøkler, hierarkier, SCD/historikk og beskrivelser.
- Relasjoner med kardinalitet, filterretning og aktive/inaktive relasjoner.
- Measures med forretningsdefinisjon, DAX-navn og eventuell avstemmingsregel.
- RLS/OLS, sensitivitet, sertifisering og eierskap.
- Modellkvalitet: blank relationship member, many-to-many, tvetydige relasjoner, ikke-additive felt og manglende dimensjonstreff.

## Star Schema-Regler

- Beskriv fakta som hendelser/observasjoner/målinger med dimensjonsnøkler.
- Beskriv dimensjoner som filtrerings- og grupperingsentiteter.
- Ikke bland brede rapporttabeller og semantic model-design uten å forklare hvorfor.
- For BOTT skal konteringsdimensjoner normalt beholdes som autoritative kodefelt i fakta og dimensjoner.
- Hvis surrogate keys brukes, forklar fysisk begrunnelse og historikk/SCD-behov.

## Output

Bruk `Semantic Model`-malen fra `../fabric-documentation/references/document-templates.md`. Ta med Mermaid ER-diagram når det gjør modellen lettere å kontrollere.
