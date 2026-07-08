# Fabric Governed Ingestion Pattern

## Architecture

Use this pattern for recurring or official reporting:

```text
Source owner: Analyseplattformen / Databricks
  -> Delta Sharing access contract
  -> Fabric Dataflow Gen2 ingestion
  -> Lakehouse/Warehouse curated tables
  -> Semantic model following star schema
  -> Power BI report/app
  -> endorsement/certification and monitoring
```

## Why Use Fabric Instead Of Direct Desktop Import

Fabric adds value when the goal is governance and reuse:

- one shared ingestion path instead of many local Power Query copies,
- lineage from source to report,
- managed refresh and monitoring,
- quality checks before reporting,
- reusable semantic model,
- clearer data product ownership,
- better fit for data mesh and domain ownership.

## Minimum Documentation For A Data Product

Document:

- source share and owner,
- Fabric workspace and item owner,
- table list and grain,
- keys and expected uniqueness,
- refresh cadence and acceptable delay,
- sensitivity and access groups,
- data quality checks,
- semantic model status,
- known limitations and escalation contact.

## Finance And Virksomhetsstyring Rules

For finance data:

- Preserve BOTT/UiT accounting dimensions as business keys where needed for reconciliation.
- Model reportable data as facts and dimensions before broad Power BI use.
- Keep measure definitions in the semantic model, not scattered across reports.
- Use certified/endorsed status only after reconciliation and ownership are documented.

## Adjacent Patterns

Delta Sharing is not the only Fabric integration route. Evaluate alternatives when the source already exposes governed storage or compute:

- ADLS/OneLake shortcuts for file/table references where permissions and storage layout fit.
- Azure Databricks connector when querying Databricks SQL warehouses is a better fit.
- Lakehouse/warehouse ingestion from supported connectors when copy semantics are required.

Shortcuts are references to external or internal data, not copies. Their security depends on both shortcut path and target path permissions.
