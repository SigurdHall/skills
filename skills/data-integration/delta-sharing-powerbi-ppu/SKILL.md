---
name: delta-sharing-powerbi-ppu
description: Connect, document, review, or troubleshoot Delta Sharing from Databricks/Analyseplattformen to Power BI Desktop, Power BI semantic models, Power BI dataflows, or Premium Per User workspaces. Use when the user mentions Delta Sharing, Delta Share, Power BI PPU, Premium Per User, Power Query Delta Sharing connector, Entra ID OAuth/OIDC, bearer token credentials, Databricks OIDC portal, Delta Sharing Server URL, row limit, refresh, publishing shared data to Power BI Service, or controlled data sharing from an analysis platform to Power BI. Use fabric-delta-sharing-ingestion instead when the goal is to land, transform, govern, or reuse the data inside Microsoft Fabric before reporting.
---

# Delta Sharing Power BI PPU

## Purpose

Use this skill for the direct Power BI path: a user or Power BI workspace consumes shared Delta tables through the Power Query Delta Sharing connector and then publishes or governs the result in Power BI Premium Per User.

Keep the distinction clear:

- Direct Power BI/PPU is good for controlled pilots, analyst work, small-to-medium imports, and early semantic model development.
- Fabric ingestion is better when the data should become a governed data product, reusable lakehouse/warehouse source, or certified enterprise semantic model. Use `fabric-delta-sharing-ingestion` for that pattern.

## Workflow

1. Classify the use case:
   - `Desktop prototype`: Power BI Desktop import for analysis or proof of concept.
   - `Team report`: semantic model published to a PPU workspace.
   - `Official reporting`: likely needs Fabric landing, shared definitions, endorsement, owner, refresh plan, and access model before broad use.
2. Check access prerequisites:
   - Delta Sharing Server URL or Databricks OIDC portal URL.
   - Entra tenant ID.
   - Entra object ID for user or group. Prefer groups.
   - Admin consent for the Databricks Delta Sharing multi-tenant app if OAuth/OIDC requires it.
   - Power BI Desktop version that supports the required connector/authentication flow.
3. Build the connection:
   - Power BI Desktop: `Get data` -> `Delta Sharing` -> Server URL -> optional row limit -> OAuth/OIDC or bearer token -> select tables -> `Load` or `Transform data`.
   - Power Query Online / dataflow: use the same connector only if the target surface supports it.
4. Decide the Power BI service pattern:
   - Publish only to a workspace whose license mode and audience fit the content.
   - In a PPU workspace, viewers and collaborators normally need PPU unless the content is moved to Premium/Fabric capacity.
   - Assign clear semantic model owner, refresh owner, and access group.
5. Document governance before calling the dataset official:
   - Source owner and data product owner.
   - Table list, grain, sensitivity, intended use, and refresh expectation.
   - Relationship to certified semantic models, star schema, and finance definitions when relevant.
   - Known limitations: import mode, row limit, memory pressure, duplicated logic in Power Query, and local model drift.

## References

Read only the relevant reference:

- `references/microsoft-power-query-delta-sharing.md` for connector behavior and setup.
- `references/powerbi-ppu-pattern.md` for PPU licensing and service governance.
- `references/uit-analyseplattformen-pattern.md` for the local UiT/Analyseplattformen pattern.
- `references/source-links.md` for official documentation links used by this skill.

## Use Other Skills

- Use `fabric-delta-sharing-ingestion` when a Fabric lakehouse, warehouse, Dataflow Gen2, or reusable data product is the target.
- Use `fabric-semantic-model-doc` or `bott-semantic-model` when the Delta Sharing data becomes a star schema or finance semantic model.
- Use `uit-bott-okonomimodell` for UiT/BOTT finance fields, accounting dimensions, Unit4 data, and controller-facing definitions.
- Use `powerbi-pbip` when editing local PBIP/PBIR/TMDL files created from the imported data.

## Output Checklist

For documentation or implementation notes, include:

- Connection pattern: Power BI Desktop, Power BI dataflow, semantic model, or PPU workspace.
- Authentication pattern: OAuth/OIDC or bearer token.
- Access holder: Entra group/user object ID, not personal names unless required by the task.
- Row limit and data volume assumption.
- Refresh and ownership plan.
- Licensing/audience impact for PPU.
- Whether the model is exploratory, endorsed, certified, or official reporting.
