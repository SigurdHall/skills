# Tableau-Derived Report Templates

Use this when creating or adapting PBIP/PBIR reports from Tableau workbook
evidence, Tableau metadata, or migration mapping outputs.

## Inputs

- Tableau workbook/report evidence: workbook inventory, dashboards/views,
  filters, parameters, calculations, datasource bindings, permissions, refresh
  schedules, thumbnails, and known usage.
- Existing Tableau metadata: `.twb`/`.twbx` XML, `.tds` definitions, Metadata
  API/catalog exports, and normalized evidence CSV/JSON files.
- Table migration contracts: source-to-target table/column mappings, renamed
  fields, grain changes, retired objects, calculation ownership, and unresolved
  mapping gaps.
- Existing PBIP assets: semantic model, theme, page templates, bookmarks,
  registered resources, navigation patterns, and organizational report
  standards.

## Template Selection

- Treat Tableau dashboards as evidence of user questions, filters, and workflow;
  do not copy visual layout mechanically when Power BI has a clearer pattern.
- Reuse a Tableau-derived PBIP template only when its canvas, navigation,
  slicers, theme, and semantic model assumptions fit the target report.
- Reconcile every Tableau datasource/table/field used by a page against the
  migration contract before authoring visuals.
- Preserve audit needs from Tableau: drill paths, exports, row-level security
  signals, refresh timing, subscriptions, and owner/project context.
- Keep unresolved field, calculation, permission, or refresh differences visible
  in a report gap log or data quality page.

## Production Loop

1. Pick one Tableau dashboard/view or report decision area.
2. Map Tableau fields, filters, parameters, and calculations to the target
   semantic model using the migration contract.
3. Choose or adapt the nearest PBIP page template.
4. Implement the smallest coherent page/visual/theme/resource change.
5. Validate JSON, PBIR/PBIP/TMDL encoding, resource paths, and theme references.
6. Inspect the report in Power BI Desktop when visual semantics cannot be proven
   from JSON alone.
7. Record gaps, assumptions, and manual review items before moving to the next
   page.

Keep orchestration, sequencing across many reports, and migration program
management in the dedicated orchestration workflow. This reference only guides
PBIP report production from Tableau-derived evidence.
