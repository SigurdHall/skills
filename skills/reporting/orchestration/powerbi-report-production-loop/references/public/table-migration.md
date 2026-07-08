# Table Migration

Use this reference when translating Tableau data sources, extracts, logical tables, joins, relationships, blends, and calculations into Power BI tables and semantic model objects.

## Migration Matrix Columns

| Column | Description |
| --- | --- |
| `source_workbook` | Tableau workbook or package name. |
| `source_data_source` | Tableau data source, extract, connection, or published source. |
| `source_object` | Tableau logical table, physical table, custom SQL, relationship, blend, parameter, set, or calculation. |
| `source_grain` | Row grain as observed or inferred. |
| `target_object_type` | `fact`, `dimension`, `bridge`, `parameter`, `helper`, `measure`, `power-query-step`, or `exclude`. |
| `target_table_or_measure` | Proposed Power BI table, column, measure, or query object. |
| `migration_decision` | `reuse-existing`, `create-new`, `merge-into-existing`, `replace-with-measure`, `manual-review`, or `exclude`. |
| `validation_rule` | Row count, sum, distinct count, filter scenario, or certified total. |
| `risk` | Data quality, ambiguity, privacy, performance, calculation, or refresh risk. |
| `status` | Use the status values from `output-artifacts.md`. |

## Decision Rules

1. Start from business grain. Do not mirror Tableau extracts if they mix incompatible grains.
2. Prefer star-schema fact and dimension tables over Tableau-specific wide tables or dashboard-only joins.
3. Translate Tableau row-level calculations to Power Query or calculated columns only when they define stable attributes.
4. Translate aggregations, LOD-style business measures, ratios, flags, and thresholds to DAX measures when they depend on filter context.
5. Treat Tableau parameters as disconnected parameter tables, field parameters, calculation groups, or report controls depending on behavior.
6. Treat Tableau sets/groups as dimensions or mapping tables when they encode business-managed categories.
7. Treat Tableau blends as a warning sign. Resolve them into explicit relationships, bridge tables, or separate visuals with documented limitations.
8. Do not silently drop hidden fields. Hidden fields can drive filters, calculations, actions, or tooltips.

## Calculation Translation Notes

| Tableau pattern | Power BI target | Check |
| --- | --- | --- |
| Simple row calculation | Power Query step or calculated column | Same row count and null behavior. |
| Aggregate calculation | DAX measure | Same filter scenario and total behavior. |
| Fixed LOD | DAX measure with explicit filter removal or dedicated aggregation table | Matches certified total across slicers. |
| Include/exclude LOD | DAX measure with explicit context handling | Matches detail and total rows. |
| Table calculation | DAX measure, visual calculation, or precomputed table | Sort/order and partition behavior documented. |
| Parameter-driven metric | Field parameter, disconnected table, or SWITCH measure | Selected value behavior matches Tableau. |
| Relative date filter | Date table and DAX/visual filter | Period boundary and timezone assumptions clear. |

## Validation Rules

- Validate row counts before totals.
- Validate totals before page visuals.
- Validate at least one default scenario and one filtered scenario for every critical measure.
- Record accepted variance for rounding, null handling, fiscal calendar differences, or source refresh timing.
- Keep privacy-sensitive sample data out of artifacts unless explicitly approved and sanitized.
