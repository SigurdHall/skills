# Fabric item lifecycle gates

Use the official pages below as live contracts. Microsoft Fabric item support,
identity support, preview status, and definition parts change over time.

## Required sequence

`DISCOVER -> CAPABILITY -> AUTHORITY -> SNAPSHOT -> DEPENDENCIES -> VALIDATE -> APPLY -> POLL -> VERIFY -> RECORD/RECOVER`

### 1. Discover and capability

- Resolve workspace and item IDs using a narrow search.
- Check the [item management overview](https://learn.microsoft.com/en-us/rest/api/fabric/articles/item-management/item-management-overview).
- Check the [item definition overview](https://learn.microsoft.com/en-us/rest/api/fabric/articles/item-management/definitions/item-definition-overview) and the item-specific definition page.
- Record unsupported operations, preview/beta status, and whether service
  principals or managed identities are supported.

### 2. Authority and privacy

- Confirm the least-privilege identity and required
  [scopes](https://learn.microsoft.com/en-us/rest/api/fabric/articles/scopes).
- Check [identity support](https://learn.microsoft.com/en-us/rest/api/fabric/articles/identity-support)
  and relevant [tenant developer settings](https://learn.microsoft.com/en-us/fabric/admin/service-admin-portal-developer).
- Keep secrets out of source files and command output.

### 3. Snapshot and dependencies

- Read item metadata and, where supported, the full definition before mutation:
  [Get item definition](https://learn.microsoft.com/en-us/rest/api/fabric/core/items/get-item-definition).
- Record [item connections](https://learn.microsoft.com/en-us/rest/api/fabric/core/items/list-item-connections), workspace, IDs, definition parts, and hashes.
- Inventory state that may live outside the item definition: sensitivity label,
  permissions, folder placement, schedules, identities, connection grants, and
  downstream references. Capture it where the current item APIs support it, or
  state explicitly that it cannot be reconstructed automatically.
- Resolve connection requirements against [supported connection types](https://learn.microsoft.com/en-us/rest/api/fabric/core/connections/list-supported-connection-types). Create connections only through the explicit [connection contract](https://learn.microsoft.com/en-us/rest/api/fabric/core/connections/create-connection).
- Order multi-item work by dependency; do not assume alphabetical deployment is safe.

### 4. Validate and apply

- Validate required definition parts, encoding, logical IDs, references, and
  environment-specific parameters before calling the API.
- Immediately before a complete-definition overwrite, read the current
  metadata/definition hash again and compare it with the snapshot. Abort on
  drift unless the user explicitly authorizes reconciliation against the new
  state; never overwrite a concurrent change silently.
- Use [Create item](https://learn.microsoft.com/en-us/rest/api/fabric/core/items/create-item)
  only for supported item types.
- Treat [Update item definition](https://learn.microsoft.com/en-us/rest/api/fabric/core/items/update-item-definition)
  as complete-definition replacement, not a patch. The `.platform` part changes
  only when `updateMetadata=true`; otherwise use [Update item](https://learn.microsoft.com/en-us/rest/api/fabric/core/items/update-item)
  for metadata such as name or description.
- Use the beta [bulk import](https://learn.microsoft.com/en-us/rest/api/fabric/core/items/bulk-import-item-definitions%28beta%29)
  only as an explicit opt-in. It can partially succeed.

### 5. Poll and verify

- A `202 Accepted` response is not completion. Persist the operation ID, honor
  `Retry-After`, and follow the [long-running operation](https://learn.microsoft.com/en-us/rest/api/fabric/articles/long-running-operation)
  protocol to a terminal state.
- Before starting a Pipeline job, check for an active or recently submitted
  equivalent run, define an idempotency/run-key policy for the workload, and
  persist the new job/run ID immediately. Never retry a write-producing
  pipeline blindly.
- Read back metadata, references, and connections. Read back the full definition
  when supported and required by the item-specific skill. If that skill
  explicitly treats a successful terminal `updateDefinition` LRO as sufficient
  and full read-back as optional or expensive, follow the narrower rule and
  record the exception.
- Run the item-specific smoke check: semantic query, report render, refresh/job
  status, KQL/SQL query, event flow, or notification canary as appropriate.
  For a Data Pipeline, verify the run reaches a terminal success state and then
  verify a job-correlated side effect, such as a recorded pipeline run ID,
  expected Delta version/change timestamp, or controlled before/after canary.
  Mere existence of an old table or Notebook output is insufficient.
- Apply narrow [pagination](https://learn.microsoft.com/en-us/rest/api/fabric/articles/pagination)
  and [throttling](https://learn.microsoft.com/en-us/rest/api/fabric/articles/throttling)
  handling. Use the [troubleshooting guide](https://learn.microsoft.com/en-us/rest/api/fabric/articles/get-started/fabric-api-troubleshooting)
  before retrying mutations.

### 6. Record and recover

- Record requested change, before/after hashes, API operation ID, terminal
  status, read-back evidence, runtime evidence, and known gaps.
- Recovery means reapplying a validated prior complete definition or a documented
  compensating action. It is not blind retry. Deletion recovery is materially
  different: a recreated item can receive a new ID and does not automatically
  restore permissions, labels, schedules, connection grants, or downstream
  references. Require a rebind/repermission plan and explicit confirmation
  before delete.

## Multi-item CI/CD

For repeated deployments, prefer:

- [Fabric CI/CD best practices](https://learn.microsoft.com/en-us/fabric/fundamentals/understand-best-practices-fabric-cicd)
- [`microsoft/fabric-cicd`](https://github.com/microsoft/fabric-cicd) and its
  [documentation](https://microsoft.github.io/fabric-cicd/latest/)
- [Fabric Git source format](https://learn.microsoft.com/en-us/fabric/cicd/git-integration/source-code-format)
  and [Git automation](https://learn.microsoft.com/en-us/fabric/cicd/git-integration/git-automation)

Pin tool and format versions. Git sync and deployment acceptance still require
item-specific read-back and runtime verification.

For test-to-production promotion, keep a reviewed environment mapping for
logical IDs, workspace/item IDs, connection IDs, parameters, and secret
references. Never store secret values in the mapping. Deploy in dependency
order and require test evidence before the production canary.

Use [deployment-promotion.md](deployment-promotion.md) for the operational
manifest and Pipeline-specific ID invariants.
