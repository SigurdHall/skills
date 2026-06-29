# Fabric Dataflow Gen2 Delta Sharing

## Supported Surface

Microsoft documents Delta Sharing support in Fabric Data Factory through Dataflow Gen2 as a source connector. Supported authentication is bearer token (`Key`) and OAuth/OIDC. Gateway is documented as not required for the connector overview.

Do not assume Delta Sharing support in Fabric pipelines or copy jobs. Microsoft currently documents Dataflow Gen2 support and states that Data Factory pipelines do not support Delta Sharing.

## Fabric Setup Flow

1. Open a Fabric-enabled workspace.
2. Create `New` -> `Dataflow Gen2`.
3. In Power Query, choose `Get data`.
4. Search for `Delta Sharing`.
5. Enter the Server URL from the provider credential/profile flow.
6. Choose authentication:
   - bearer token from credential file, or
   - OAuth/OIDC with organizational sign-in.
7. Select tables.
8. Transform in Power Query.
9. Load to an agreed destination, typically lakehouse/warehouse tables or a semantic-model-ready curated layer.

## Limitations To State Explicitly

- Import is the connector capability.
- Row limits and memory pressure still matter.
- Fabric pipeline support should not be assumed.
- OAuth/OIDC may require Entra ID admin consent and correct Databricks policy setup.
- A dataflow output is not automatically a governed data product; it still needs ownership, tests, and publication rules.

## Validation

After building the dataflow:

- Run refresh manually once.
- Compare row counts and key totals against source.
- Record refresh duration and failure behavior.
- Confirm destination table names and schema.
- Test that downstream users can access only what they should.
