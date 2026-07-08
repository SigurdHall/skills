# Subagents And Four Waves

Use these subagents as role definitions. Dispatch only the roles needed for the current migration slice, but keep the four-wave sequence intact.

## Subagent Definitions

| Subagent | Primary job | Inputs | Outputs |
| --- | --- | --- | --- |
| Migration Orchestrator | Own the loop, scope, sequencing, and final synthesis. | User request, source/target paths, constraints, prior outputs. | Migration brief, decisions, risks, next actions. |
| Tableau Inventory Analyst | Inspect Tableau workbook behavior and document sheets, dashboards, fields, parameters, filters, actions, extracts, and visible business logic. | Tableau workbook/package exports, screenshots, metadata, extracts, user notes. | Workbook inventory, dashboard/page map, calculation and filter catalog, parity questions. |
| Data And Table Migration Analyst | Map Tableau extracts, logical tables, joins, relationships, blends, parameters, and calculations to Power BI tables and model decisions. | Tableau inventory, source data extracts, target model files. | Table migration matrix, grain decisions, relationship candidates, Power Query/TMDL notes. |
| Semantic Model And DAX Architect | Design or adapt the Power BI semantic model, translate calculations to measures, and keep business logic auditable. | Table migration matrix, source calculations, target TMDL/model. | Star-schema proposal, DAX measure catalog, calculation translation notes, model blockers. |
| Report Production Builder | Rebuild pages, visuals, navigation, filters, tooltips, and bookmarks in PBIP/PBIR using local Power BI project conventions. | Parity contract, page map, model, theme, assets. | PBIP/PBIR change plan or edits, page production notes, visual mapping. |
| Parity And QA Reviewer | Test Power BI outputs against Tableau behavior and certified totals. | Tableau screenshots/exports, Power BI outputs, model measures, test data. | Parity test log, mismatches, accepted variances, release blockers. |
| Governance And Release Reviewer | Check privacy, access, refresh, lineage, documentation, known limitations, and handover readiness. | All artifacts, deployment context, data sensitivity notes. | Governance checklist, release note, owner review items. |

## Four Migration Waves

### Wave 1: Inventory And Parity Contract

Goal: define what must be equivalent before any build work expands.

1. Migration Orchestrator records source workbook, target PBIP/report location, audience, decisions supported, and release boundary.
2. Tableau Inventory Analyst inventories dashboards, sheets, fields, calculations, parameters, filters, actions, extracts, joins, and known workbook quirks.
3. Parity And QA Reviewer proposes measurable parity checks: totals, row counts, filter scenarios, time periods, rounding, and accepted differences.
4. Output gate: migration brief, workbook inventory, page map, calculation catalog, and parity contract.

### Wave 2: Table And Semantic Migration

Goal: convert Tableau data behavior into a durable Power BI semantic model.

1. Data And Table Migration Analyst maps each Tableau data source/logical table to Power BI fact, dimension, bridge, parameter, or helper table.
2. Semantic Model And DAX Architect translates calculations into model measures, calculated columns only where justified, and Power Query/TMDL changes.
3. Governance And Release Reviewer flags sensitive fields, row-level security needs, refresh risks, and lineage gaps.
4. Output gate: table migration matrix, relationship plan, DAX measure catalog, data quality checks, and unresolved model blockers.

### Wave 3: Report Production

Goal: rebuild the user-facing report in Power BI without copying Tableau design mistakes.

1. Report Production Builder maps Tableau dashboards to Power BI pages, visuals, slicers, navigation, tooltips, and drill paths.
2. Semantic Model And DAX Architect supports production with helper measures for sorting, formatting, conditional colors, and visual scale.
3. Migration Orchestrator keeps scope tight: one completed page or control surface at a time.
4. Output gate: PBIP/PBIR edits or implementation plan, visual mapping, page notes, screenshots/export instructions, and open production issues.

### Wave 4: Validation, Governance, And Release

Goal: prove what matches, disclose what does not, and prepare handover.

1. Parity And QA Reviewer executes parity scenarios and records evidence.
2. Governance And Release Reviewer checks privacy, access control, refresh, ownership, retention, and known limitations.
3. Migration Orchestrator produces final status: complete, partial, blocked, or needs user review.
4. Output gate: parity log, blocker list, release note, owner review checklist, and next migration slice.

## Loop Control

- Repeat Waves 2-4 for each report slice until the parity contract is satisfied or a blocker is explicit.
- If a wave discovers a source ambiguity, return to Wave 1 and update the contract before continuing.
- If a Power BI limitation changes report behavior, document the accepted variance and reviewer approval needed.
