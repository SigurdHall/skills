---
name: fabric-powerbi-report-doc
description: Write Markdown documentation that describes Power BI/Fabric reports, PBIR/PBIP report definitions, pages, visuals, navigation, slicers, filter panels, bookmarks, themes, KPI cards, report standards, and QA checks. Use when the user asks to dokumentere rapport, Power BI report docs, report pages, visual layout, rapportnormer, testpunkter, or user-facing report documentation. Use uit-powerbi-reporting instead when the task is to build or edit the UiT report itself rather than document it; this skill still uses uit-powerbi-reporting for UiT templates, colors, and KPI conventions.
---

# Fabric Power BI Report Doc

## Arbeidsflyt

1. Bruk `fabric-documentation` som hovedramme.
2. Bruk `powerbi-pbip` før du leser eller endrer PBIP/PBIR/report JSON.
3. Bruk `uit-powerbi-reporting` for UiT-maler, farger, KPI-ikoner og rapporteringsenheter.
4. Inspiser relevante filer:
   - `.pbip`
   - `.Report/definition.pbir`
   - `.Report/definition/report.json`
   - `.Report/definition/pages/pages.json`
   - `.Report/definition/pages/**/page.json`
   - `.Report/definition/pages/**/visuals/**/visual.json`
   - bookmarks og registered resources der relevant
5. Dokumenter rapporten fra brukerens perspektiv, men forankre tekniske detaljer i filene.

## Må Dekkes

- Formål, målgruppe og beslutninger rapporten støtter.
- Rapportens sider, navigasjon, slicere og bokmerker.
- Hvilken semantic model rapporten bruker.
- Viktige målinger og definisjoner.
- Visuelle normer: farger, KPI-bruk, terskler, avvik, sortering og skala.
- Tilgang, RLS-effekt og eksport-/delingbegrensninger.
- Testpunkter etter endring: navigasjon, slicere, bokmerker, refresh, visual rendering og filterlogikk.

## UiT/Økonomi-Normer

- Bruk norske brukerrettede etiketter når rapporten er for UiT/økonomibrukere.
- Rød/oransje skal reserveres for avvik, risiko, advarsel og terskelbrudd.
- Forklar rapporteringsenheter og koststedslogikk hvis rapporten grupperer økonomiansvar.
- Ta inn `finance-bi-dax-patterns` når DAX-målinger er sentrale.

## Output

Bruk `Power BI Report`-malen fra `../fabric-documentation/references/document-templates.md`.
