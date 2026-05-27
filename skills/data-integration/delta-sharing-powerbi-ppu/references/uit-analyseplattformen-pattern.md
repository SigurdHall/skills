# UiT / Analyseplattformen Pattern

## Local Pattern

The local resource note `private/Vault/Resources/PowerBI/Delta Sharing fra Analyseplattformen til Power BI.md` summarizes a guide named `DK-Delta Sharing - PowerBI-260526-123528.pdf`.

The described flow is:

```text
Analyseplattformen / Databricks
  -> Delta Sharing endpoint
  -> Power BI Desktop
  -> OAuth with Entra ID
  -> imported Power BI tables
  -> semantic model/report
```

## Access Inputs

The guide expects access to be coordinated with the Analyseplattformen owner/contact. The practical inputs are:

- whether access is for a user or group,
- Entra ID object ID for that user or group,
- tenant ID,
- Delta Sharing Server URL returned through the provider flow.

Prefer group-based access for maintainability, audit, and role changes.

## Local Power BI Setup

The local guide uses:

- Power BI Desktop login with a user that has access,
- `Get data` -> `Delta Sharing`,
- `Delta Sharing Server URL`,
- `Row limit = 5000000`,
- OAuth sign-in,
- table selection,
- `Load` or `Transform data`.

Treat the 5 million row value as a local design choice, not a universal default.

## UiT Governance Interpretation

Direct Delta Sharing to Power BI should be treated as controlled access to data, not as automatic approval for official reporting.

Before broad publishing, document:

- source owner,
- table meaning and grain,
- access group,
- refresh owner,
- semantic model owner,
- relation to BOTT/UiT finance definitions,
- whether the output is pilot, internal working report, endorsed, or certified.

For financial management reports, combine this skill with `uit-bott-okonomimodell`, `bott-semantic-model`, and `finance-bi-dax-patterns`.
