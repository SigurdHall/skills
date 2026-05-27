# Fabric Skill Group

This folder groups Fabric documentation skills. Each child folder is intended to
behave as a standalone skill with its own `SKILL.md`.

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
