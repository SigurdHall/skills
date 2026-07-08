---
name: pbip-full-report
description: Use when creating, scaffolding, or substantially adapting complete Power BI reports as local PBIP/PBIR projects, including report purpose, semantic model fit, page structure, visual selection, themes, navigation, bookmarks, images, custom visuals, validation, and governance.
---

# PBIP Full Report

## Overview

Build Power BI reports as maintainable PBIP/PBIR projects. Treat the report as a product: define the decision it supports, confirm the semantic model, design page flows, choose visuals deliberately, then edit PBIP files with validation.

**MECHANICS:** Delegate live model and report editing to `skills-for-fabric` (`semantic-model-authoring`, `powerbi-report-authoring`) when MCP/Desktop is available. This skill owns UiT report structure and decisions, not generic PBIR/TMDL tooling.

**REQUIRED SUB-SKILL:** Use `powerbi-pbip` before reading or editing PBIP/PBIR/TMDL/report JSON files offline. Use `uit-powerbi-reporting` as well for UiT finance/reporting reports.

When rebuilding from Tableau evidence, read
`references/public/tableau-derived-templates.md` and use Tableau artifacts as design
evidence, not as an instruction to clone every visual.

## Report Workflow

1. Clarify the report job:
   - Primary audience and decisions.
   - Reporting period, grain, and refresh expectations.
   - Required filters, drill paths, and export needs.
   - Definitions that must be visible for auditability.

2. Inspect the project before design:
   - `.pbip`, `.Report/definition.pbir`, `.Report/definition/report.json`
   - `.Report/definition/pages/**/page.json`
   - existing `visual.json`, bookmarks, registered resources, and theme files
   - `.SemanticModel/definition/model.tmdl`, `relationships.tmdl`, and relevant table TMDL files

3. Choose the base:
   - Prefer an existing PBIP template when layout, navigation, theme, or model wiring already fits.
   - For Tableau-derived rebuilds, prefer a PBIP template derived from the
     Tableau evidence only when the semantic model, page intent, and migration
     contracts fit.
   - Copy `.pbip`, `.Report`, and `.SemanticModel` together if creating a new report from a template.
   - Keep paths, dataset references, display names, theme references, bookmarks, and resource names aligned.

4. Confirm the semantic model before visuals:
   - Use a star schema where possible.
   - For Tableau migrations, reconcile datasource/table/field usage against the
     table migration contract before creating visuals.
   - Put business logic in measures, not in visual-only calculations.
   - Separate visible business measures from helper measures for sorting, scale, color, or conditional formatting.
   - Hide technical columns and set identifier columns to non-summarizing behavior.
   - Add source, refresh, and limitation fields when the report will be used for governance or control.

5. Design the page architecture:
   - Overview page: status, key measures, trend, main deviations, last refresh, and navigation.
   - Analysis pages: one decision area per page, with consistent filters and comparison logic.
   - Detail page: table/matrix for traceability, drillthrough, or export.
   - Data quality page: source status, missing values, unmapped keys, refresh timestamp, and known limitations.

6. Select visuals by question:

| Question | Prefer | Avoid |
| --- | --- | --- |
| Current status | Cards, KPI cards, gauges only with clear target | Decorative cards without definition |
| Trend over time | Line chart, small multiples | Pie/donut over time |
| Variance to budget/target | Bar chart, waterfall, matrix with conditional formatting | Random category colors for risk |
| Composition | Stacked bar, treemap only for broad scanning | Too many slices |
| Ranking | Sorted bar chart, table with rank | Unsigned columns with unclear sort |
| Audit trail | Matrix/table with drillthrough | Over-aggregated visuals without details |

7. Apply layout and interaction standards:
   - Use a stable canvas, normally `1600 x 900` for local UiT/reporting templates unless the project uses another size.
   - Keep slicers consistent across pages; use bookmarks for collapsible filter panels only when the existing report pattern supports it.
   - Use semantic color: red/orange for risk, deviations, warnings, and threshold breaches, not ordinary categories.
   - Keep titles action-oriented and labels business-facing.
   - Use tooltip pages for definitions and secondary context instead of crowding the main page.
   - Do not add custom visuals unless native visuals cannot answer the question.

8. Add visual assets safely:
   - Store reusable icons/images under the report's registered resources or the established template asset folder.
   - Prefer SVG for scalable icons and PNG only when Power BI or Explorer previews need it.
   - Register image resources consistently in report metadata.
   - Do not embed sensitive screenshots, personal data, secrets, or internal extracts as images.

9. Govern custom visuals:
   - Prefer certified or organizational visuals.
   - Check whether AppSource or `.pbiviz` use is allowed by tenant policy.
   - Document why the custom visual is needed, what data it receives, and what replacement exists if it is blocked.

10. Implement PBIP changes conservatively:
   - Prefer Power BI Desktop for complex new visual authoring when exact report JSON is unknown.
   - Use PBIP edits for repeatable layout changes, theme updates, resource registration, page metadata, bookmarks, and known visual patterns.
   - Preserve existing IDs, visual names, bookmark targets, group names, and relative paths unless intentionally replacing them.
   - Write JSON, TMDL, PBIP, PBIR, `.platform`, and theme files as UTF-8 without BOM.

For Tableau-derived production loops, keep one concise evidence-to-report
iteration: map evidence to page intent, implement the smallest PBIP change,
validate files, inspect the report, record gaps, then repeat. Do not duplicate a
separate migration orchestration workflow inside this skill.

## Report Quality Checklist

- Purpose and audience are explicit.
- Every page supports a decision, control activity, or traceability need.
- Measures have business definitions and consistent formatting.
- Slicers, navigation, and interactions are predictable.
- Colors carry meaning and meet contrast needs.
- Report includes source, last refresh, and known limitations.
- Detail or drillthrough exists for numbers that require follow-up.
- Data quality issues are visible rather than hidden.
- Custom visuals and embedded assets have a governance rationale.
- JSON parses, BOM check passes, and local artefacts are not staged.

## Validation

Use `powerbi-pbip` validation commands after edits:

- JSON validation for changed report JSON files.
- BOM check for `.json`, `.pbip`, `.pbir`, `.tmdl`, `.platform`, and theme files.
- Git status check to avoid staging `.env`, `.pbi` cache/local settings, generated render folders, or downloaded data.

For finance, public-sector, HR, personal-data, or internal-control reports, also check privacy, access control, retention, traceability, and human review needs before publishing.
