---
name: fabric-delta-sharing-ingestion
description: Plan, document, review, or troubleshoot Microsoft Fabric ingestion of Delta Sharing data from Databricks/Analyseplattformen into Dataflow Gen2, lakehouse, warehouse, semantic model, or governed data product workflows. Use when the user mentions Delta Sharing in Fabric, Dataflow Gen2 Delta Sharing connector, Fabric data platform, lakehouse ingestion, reusable Power BI/Fabric semantic models, data product governance, OneLake, Fabric capacity, or when a direct Power BI Delta Sharing import may need to be elevated into a governed Fabric pattern. Use delta-sharing-powerbi-ppu for direct Power BI Desktop/PPU consumption without Fabric landing.
---

# Fabric Delta Sharing Ingestion

## Purpose

Use this skill when Delta Sharing data should become part of a governed Fabric workflow before reporting. The main supported Fabric pattern is Dataflow Gen2 as a source connector for Delta Sharing, then loading curated outputs to Fabric items for reuse.

This skill is not a generic Fabric documentation skill. Use it to decide and document how shared Delta data moves into Fabric and how the result becomes trustworthy for Power BI and virksomhetsstyring.

## Decision Tree

1. If the task is a single analyst pulling tables into Power BI Desktop, use `delta-sharing-powerbi-ppu`.
2. If the data will be reused by several reports, units, or semantic models, prefer Fabric ingestion.
3. If the data is official styringsinformasjon, require documented owner, grain, refresh, access model, quality checks, and semantic model governance.
4. If the required workflow is a Fabric pipeline/copy job, verify connector support first. Delta Sharing is supported for Fabric Dataflow Gen2 as source; do not assume pipeline support.
5. If the source is already available as ADLS/OneLake/Databricks tables through another governed route, compare Delta Sharing with shortcuts, Databricks connector, or lakehouse/warehouse loading before recommending duplication.

## Standard Pattern

Use this pattern unless local constraints say otherwise:

```text
Databricks / Analyseplattformen
  -> Delta Sharing endpoint or OIDC portal
  -> Fabric Dataflow Gen2 using Delta Sharing connector
  -> Lakehouse/Warehouse staging or curated tables
  -> Star schema / semantic model
  -> Power BI report package
  -> endorsed/certified content for leaders
```

For finance and virksomhetsstyring, document the semantic boundary:

- Raw shared tables are not automatically official definitions.
- Curated tables should have grain, keys, owners, quality checks, and known limitations.
- Semantic models should follow star schema and Power BI norms before broad publishing.

## Implementation Notes

1. Start with a minimal table set that proves refresh, access, and model grain.
2. Use OAuth/OIDC when available for user/group-governed access. Use bearer tokens only when that is the approved provider pattern and token rotation is documented.
3. In Fabric, create a Dataflow Gen2 connection to Delta Sharing, select tables, and transform/load to the agreed destination.
4. Keep transformation logic close to the data product when it is shared by multiple reports. Avoid duplicating business rules in several report-level Power Query queries.
5. Publish reports from a governed semantic model, not directly from raw imported tables, when the output is used for management control.
6. Validate row counts, refresh duration, schema drift, source update timing, and access behavior before promoting content.

## References

Read only what is needed:

- `references/public/fabric-dataflow-gen2-delta-sharing.md` for connector support and limitations.
- `references/public/fabric-governed-ingestion-pattern.md` for the recommended governed architecture.
- `references/public/source-links.md` for official documentation links used by this skill.
- `references/private/local-source-links.md` when local UiT source notes are needed and the file exists.

## Use Other Skills

- Use `fabric-documentation` as the parent skill when writing Markdown documentation for a Fabric solution.
- Use `fabric-lakehouse-doc` for lakehouse/warehouse/table documentation.
- Use `fabric-semantic-model-doc` for semantic model, relationship, Direct Lake/Import/DirectQuery, and star schema documentation.
- Use `fabric-cicd-governance-doc` for deployment pipelines, workspace governance, endorsement, environments, and release control.
- Use `delta-sharing-powerbi-ppu` when the deliverable is direct Power BI Desktop/PPU consumption rather than Fabric ingestion.
- Use `uit-bott-okonomimodell`, `bott-semantic-model`, and `finance-bi-dax-patterns` for UiT/BOTT finance models and DAX.

## Validation Checklist

- Connector surface confirmed: Dataflow Gen2, Power Query Online, Power BI Desktop, or another route.
- Authentication and admin consent documented.
- Destination item named: dataflow, lakehouse, warehouse, semantic model, or report.
- Refresh plan and owner documented.
- Data quality checks defined before reporting.
- Access model covers source, Fabric item, semantic model, and report/app.
- Official-reporting status is explicit: prototype, endorsed, certified, or not approved for broad use.
