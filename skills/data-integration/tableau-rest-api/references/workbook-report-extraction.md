# Workbook And Report Extraction

Use this when Tableau workbook/report evidence is needed for analysis,
migration, or Power BI rebuilds.

## Evidence To Capture

- Workbook: `id`, `name`, `contentUrl`, project, owner, created/updated dates,
  tags, description, size, show tabs flag, and permissions summary.
- Views/sheets/dashboards: view IDs, names, content URLs, parent workbook,
  thumbnails or preview images when allowed, and view usage statistics when
  available.
- Datasources/connections: published datasource IDs, embedded datasource names,
  connection type/server/database/schema, extract/live mode, refresh schedule,
  and datasource-to-workbook bindings.
- Fields: physical fields, calculated fields, captions, aliases, default
  aggregations, folders, hidden flags, and field roles.
- Report behavior: filters, parameters, sets, groups, actions, navigation,
  tooltips, subscriptions, alerts, and export/download requirements.
- Governance: permissions, row-level security indicators, project/site context,
  refresh owner, certification/warnings, and known limitations.

## Extraction Sequence

1. Sign in with PAT and capture site/user IDs without logging secrets.
2. List projects, workbooks, views, datasources, schedules, and permissions via
   REST API where endpoints exist.
3. Download workbook or datasource files only when allowed; store them as raw
   evidence and record source URL, API version, timestamp, and checksum.
4. Use existing Tableau metadata first: `.twb`/`.twbx` XML, `.tds` definitions,
   Metadata API results, catalog exports, and previously exported inventories.
5. Parse workbook XML or metadata to build a normalized evidence table for
   workbooks, dashboards/views, datasources, fields, calculations, filters, and
   parameters.
6. Join datasource/table/field evidence to table migration contracts when they
   exist. Do not guess mappings from display names when contract fields are
   missing; emit unresolved mappings for review.
7. Produce compact CSV/JSON artifacts that future report builders can inspect
   without opening Tableau Desktop.

## Output Artifacts

Prefer these names unless the repo already has conventions:

```text
tableau_workbooks.csv
tableau_views.csv
tableau_datasources.csv
tableau_fields.csv
tableau_calculations.csv
tableau_filters_parameters.csv
tableau_permissions.csv
tableau_migration_mapping_gaps.csv
```

Keep raw downloaded Tableau files separate from normalized outputs. Do not
commit credentials, extracts, screenshots, or sensitive workbook contents unless
the repository policy explicitly permits it.
