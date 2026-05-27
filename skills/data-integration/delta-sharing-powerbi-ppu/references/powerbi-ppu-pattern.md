# Power BI PPU Pattern

## When PPU Fits

Use Premium Per User when the organization wants Premium-like Power BI capabilities for a bounded set of licensed users without moving the workspace to a full Premium/Fabric capacity.

PPU can fit:

- controller/analyst groups with limited audience,
- pilots before capacity decisions,
- models needing Premium features but not enterprise-wide distribution,
- management reports where all viewers already have PPU.

## Governance Rules

1. Do not publish Delta Sharing imports broadly before access, refresh, and semantic ownership are clear.
2. In PPU workspaces, plan for PPU licensing for viewers and collaborators unless the content is moved to Premium/Fabric capacity.
3. Assign owners for:
   - source access,
   - semantic model,
   - refresh credentials,
   - report/app,
   - data definitions.
4. Use Entra ID groups for workspace and app access where possible.
5. Mark status explicitly:
   - `prototype`,
   - `team report`,
   - `endorsed`,
   - `certified`,
   - `not official`.

## Refresh And Model Checks

Before production-like use:

- Confirm scheduled refresh works in Power BI Service.
- Verify gateway/cloud connection requirements for the chosen connector.
- Test token/OAuth renewal behavior.
- Check model size and refresh duration.
- Document the row limit and why it is acceptable.
- Compare totals with the source system or Databricks share.

## Upgrade Trigger To Fabric

Move from direct PPU consumption to Fabric ingestion when:

- the same tables feed many reports,
- definitions must be shared across units,
- data needs lakehouse/warehouse curation,
- lineage and data quality checks are required,
- the report becomes official styringsinformasjon,
- the semantic model should be certified or reused broadly.
