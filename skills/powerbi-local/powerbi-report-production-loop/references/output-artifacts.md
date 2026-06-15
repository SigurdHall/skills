# Output Artifacts

Keep outputs concise and versionable. Store them where the target repository already keeps migration notes, docs, or report implementation records. Do not create extra files unless the user asks or the repo pattern supports it.

## Required Artifacts

| Artifact | Purpose | Minimum contents |
| --- | --- | --- |
| Migration brief | Align scope and decisions. | Source workbook, target report, audience, release boundary, assumptions, non-goals. |
| Workbook inventory | Capture Tableau behavior. | Dashboards, sheets, data sources, extracts, calculations, parameters, filters, actions. |
| Page and visual map | Guide Power BI production. | Tableau dashboard/sheet to Power BI page/visual mapping, visual purpose, filter behavior. |
| Table migration matrix | Control data model migration. | Source table/extract, grain, target Power BI table, decision, owner, status, notes. |
| Calculation catalog | Preserve business logic. | Tableau calculation, business meaning, target DAX/Power Query location, validation scenario. |
| Parity contract | Define success before build. | Certified totals, filter scenarios, row counts, date periods, rounding, accepted variance. |
| Parity test log | Prove behavior. | Scenario, Tableau result, Power BI result, variance, status, evidence, reviewer. |
| Blocker and decision log | Keep unresolved items visible. | Issue, impact, options, decision, owner, due date. |
| Release note | Prepare handover. | Completed scope, known limitations, refresh/access notes, validation status, next steps. |

## Completion Gates

### Ready For Semantic Migration

- Workbook inventory exists.
- Tableau data sources, extracts, joins, relationships, blends, and key calculations are identified.
- Parity contract names the totals and scenarios that matter.
- Sensitive fields and access-control concerns are flagged.

### Ready For Report Production

- Target table roles and grain decisions are documented.
- Relationships and DAX translation approach are clear.
- Required measures have validation scenarios.
- Known source ambiguities are either resolved or listed as blockers.

### Ready For Validation

- Power BI pages or PBIP edits are complete for the migration slice.
- Visual mappings, filters, and navigation are documented.
- Test data, periods, and slicer scenarios are available.
- Open production issues are not hidden in implementation notes only.

### Ready For Release Review

- Parity test log is complete for agreed scenarios.
- Variances are accepted, explained, or blocked.
- Refresh, ownership, privacy, RLS/access, and retention notes are explicit.
- The user or report owner can see what remains manual or uncertain.

## Status Values

Use these statuses consistently:

- `not-started`
- `in-progress`
- `needs-source-clarification`
- `needs-model-change`
- `needs-user-review`
- `validated`
- `accepted-variance`
- `blocked`
- `released`
