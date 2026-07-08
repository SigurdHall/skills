---
name: fabric-lakehouse-doc
description: Document Fabric Lakehouse, Warehouse, medallion architecture, notebooks, pipelines, Dataflow Gen2, tables, datakorn, ingestion, transformations, Delta/Parquet, refresh, lineage, data quality, and data engineering workflows in Markdown. Use when the user asks for lakehouse docs, warehouse docs, Bronze/Silver/Gold, pipeline documentation, notebook documentation, table overview, data product before semantic model, or "dokumenter databehandlingen".
---

# Fabric Lakehouse Doc

## Arbeidsflyt

1. Bruk `fabric-documentation` som hovedramme.
2. Finn kilder, transformasjonssteg og lagringsmål før du skriver.
3. Dokumenter Bronze/Silver/Gold bare hvis løsningen faktisk bruker eller planlegger disse lagene.
4. Skill rådata, rensede data, forretningsklare tabeller og semantic model-kilder.
5. For økonomidata, bruk `uit-bott-okonomimodell` til å tolke korn, dimensjoner og kontrollrisiko.
6. For Tableau-uttrekk, bruk `tableau-rest-api` til å beskrive `.tdsx`/`.hyper`/metadataflyt korrekt.

## Tabellseksjon

For hver viktig tabell, dokumenter:

| Felt | Innhold |
| --- | --- |
| Tabell | Navn |
| Lag | Bronze/Silver/Gold eller annet |
| Korn | En rad per hva |
| Kilde | System/API/fil |
| Nøkkel | Primær/naturlig nøkkel |
| Partisjon | Dato/periode/annet |
| Refresh | Frekvens og metode |
| Kvalitet | Obligatoriske kontroller |
| Sensitivitet | Persondata/økonomi/annet |

## Kvalitet Og Kontroll

Dokumenter idempotens, duplikatregler, nullverdier, typekonvertering, avstemming, feillogging og hvordan endringer i kildeskjema håndteres.

## Output

Bruk `Lakehouse / Warehouse Data Product`-malen fra `../fabric-documentation/references/public/document-templates.md`.
