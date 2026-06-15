---
name: html-report-builder
description: Use when Codex needs to interview for, specify, validate, or generate static HTML reports from YAML report specs, SQL files, and local Parquet/CSV data snapshots using the html-report-toolkit CLI.
---

# HTML Report Builder

## Overview

Use this skill to turn a reporting need into a reproducible static HTML report. The skill owns the agent workflow; `html-report-toolkit` owns deterministic validation, SQL execution, and rendering.

## Hard Rules

- Do not invent report logic in chat only. Put report intent in `report.yaml`, data assumptions in `data_contract.yaml`, and calculations in SQL.
- Do not edit the HTML output by hand. Change the spec, SQL, data contract, template, or tool code and regenerate.
- Do not commit real source data, snapshots, or generated reports containing sensitive data.
- Run validation before saying the report is finished.

## Workflow

1. Interview the user for purpose, audience, decisions supported, data sources, measures, filters, layout, sensitivity, and acceptance checks.
2. Create or update:
   - `report.yaml`
   - `data_contract.yaml`
   - one or more `sql/*.sql` files
3. Keep YAML thin: metadata, data references, visuals, filters, output name, and evaluation checks. Keep business calculations in SQL.
4. Validate the spec:
   ```powershell
   html-report validate report.yaml
   ```
5. Render the report:
   ```powershell
   html-report render report.yaml --output reports
   ```
6. Run the full check before completion:
   ```powershell
   html-report check report.yaml
   ```
7. Summarize the generated file, input specs, validation result, and any unresolved assumptions.

## Tool Contract

Default toolkit location: `C:\repos\html-report-toolkit`.

CLI commands:

| Command | Purpose |
|---|---|
| `html-report validate <report.yaml>` | Validate spec, data contract, dataset files, SQL files, and visual/query references. |
| `html-report render <report.yaml> --output reports` | Execute SQL and generate static HTML output. |
| `html-report check <report.yaml>` | Validate and execute queries without claiming completion from spec-only checks. |

If `html-report` is not on PATH, run from the toolkit repo with:

```powershell
python -m html_report_toolkit check path\to\report.yaml
```

## Spec Details

Read `references/spec-schemas.md` when creating or reviewing `report.yaml` or `data_contract.yaml`.

Minimum report contents:

- purpose and audience
- local Parquet/CSV datasets
- SQL query files
- visuals tied to named queries
- evaluation checks that define when the report is usable

## Completion Criteria

A report-building task is complete only when:

- `html-report validate` succeeds
- `html-report render` produces the expected HTML file
- `html-report check` succeeds
- sensitive data and generated outputs are excluded from git when required
- assumptions are documented in the spec or decision log

## Common Mistakes

| Mistake | Fix |
|---|---|
| Putting calculations in YAML | Move them to explicit SQL. |
| Treating the first report as the product | Keep the reusable skill/tool workflow primary. |
| Hand-editing generated HTML | Regenerate from source specs. |
| Skipping data sensitivity | Add sensitivity and owner fields to `data_contract.yaml`. |
