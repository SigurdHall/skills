# Fabric Skill Group

This folder groups Fabric documentation skills. Each child folder is intended to
behave as a standalone skill with its own `SKILL.md`.

## Group Routing

Use `fabric-documentation` as the hub and main framing for any Fabric
documentation task. Route to a narrower skill when the task clearly fits one:

- [fabric-architecture-doc](fabric-architecture-doc/SKILL.md): architecture, target architecture, ADR/decision notes, migration plans, lakehouse vs warehouse, storage-mode choices.
- [fabric-semantic-model-doc](fabric-semantic-model-doc/SKILL.md): semantic models, TMDL, star schema, fact/dimension, relationships, measures, RLS/OLS.
- [fabric-powerbi-report-doc](fabric-powerbi-report-doc/SKILL.md): PBIR/PBIP report definitions, pages, visuals, navigation, slicers, bookmarks, report standards.
- [fabric-lakehouse-doc](fabric-lakehouse-doc/SKILL.md): lakehouse/warehouse, medallion, notebooks, pipelines, Dataflow Gen2, tables, ingestion, data engineering.
- [fabric-data-contract-doc](fabric-data-contract-doc/SKILL.md): data contracts, table/interface contracts, field definitions, quality rules, SLA, ownership.
- [fabric-cicd-governance-doc](fabric-cicd-governance-doc/SKILL.md): Git integration, CI/CD, deployment pipelines, environments, permissions, release, governance, runbooks.
- [fabric-delta-sharing-ingestion](fabric-delta-sharing-ingestion/SKILL.md): landing Delta Sharing data in Fabric (Dataflow Gen2, lakehouse, warehouse, governed data product) before reporting.

Use Norwegian for user-facing documentation unless the target repository or
user asks for English. Keep technical identifiers, filenames, Power BI object
names, TMDL, DAX, SQL, and config keys in their natural language.

Do not duplicate large rules from related skills. Reference and use these
existing skills when relevant:

- `powerbi-pbip`
- `bott-semantic-model`
- `uit-bott-okonomimodell`
- `uit-powerbi-reporting`
- `finance-bi-dax-patterns`
- `tableau-rest-api`
- `delta-sharing-powerbi-ppu`

Use `fabric-delta-sharing-ingestion` when Delta Sharing data should land in
Fabric Dataflow Gen2, lakehouse, warehouse, or a governed data product before
Power BI reporting. Use `delta-sharing-powerbi-ppu` for direct Power BI
Desktop/PPU consumption.
