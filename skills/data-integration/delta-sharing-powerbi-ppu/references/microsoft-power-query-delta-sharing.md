# Microsoft Power Query Delta Sharing

## Connector Scope

Microsoft documents Delta Sharing as a Power Query connector owned and provided by Databricks. It is available for Power BI semantic models, Power BI dataflows, and Fabric Dataflow Gen2. The connector supports import mode and authentication with bearer token credentials or OAuth/OpenID Connect.

Use the connector when the provider gives either:

- an activation/credential file with endpoint URL and bearer token, or
- a Databricks OIDC portal URL / serving endpoint for OAuth sign-in.

## Power BI Desktop Flow

1. Open Power BI Desktop.
2. Use `Get data` and search for `Delta Sharing`.
3. Enter the Delta Sharing Server URL.
4. Set `Row Limit` deliberately. Microsoft documents 1 million rows as the default; UiT's local guide uses 5 million for its example.
5. Choose authentication:
   - bearer token from the credential file, or
   - OAuth/OIDC and sign in with the organization's identity provider.
6. Select tables in Navigator.
7. Choose `Load` for quick import or `Transform data` when shaping is needed.

## Power Query Online / Fabric Flow

Power Query Online surfaces the same general connection pattern: choose Delta Sharing, enter server URL, choose bearer token or OAuth/OIDC, select tables, and transform data.

For Fabric-specific work, use `fabric-delta-sharing-ingestion` because destination, ownership, refresh, and governance matter more than the connector click path.

## OIDC Notes

Databricks documents a user-to-machine OIDC flow for tools such as Power BI. For Entra ID, providers may need issuer URL, subject claim, subject value, and the Databricks multi-tenant app audience. The tenant admin may need to grant admin consent to the Databricks Delta Sharing app before users can sign in.

Power BI Desktop version requirements have changed over time. Check the current Databricks OIDC page before troubleshooting OAuth failures.

## Main Risks

- Import mode can create large local semantic models.
- Row limit can silently shape the data available to the model if set too low.
- Business rules in Power Query can drift if many users build separate reports.
- Bearer token patterns require secure distribution and rotation.
- OAuth/OIDC patterns require correct Entra ID group/user object IDs and admin consent.
