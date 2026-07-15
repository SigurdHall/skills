# Test-to-production promotion contract

This is a tool-neutral control manifest, not a claimed native `fabric-cicd`
file format. Keep it in source control next to deployment automation and map it
to the selected, version-pinned deployment tool.

## Required manifest content

For every item, record:

- stable logical ID, item type, source path/definition hash, and dependencies
- source and target workspace logical names and resolved IDs
- source and target item IDs, or the rule for creating the target
- logical connection references and target connection IDs
- allowed environment transforms and a deny-list of source-environment IDs
- pre-deploy validation, runtime canary, and recovery action
- prior target definition/metadata hash and snapshot location

Never put secret values in this manifest. Reference a managed secret or
connection identity instead.

## Promotion sequence

1. Pin and record the `skills-for-fabric`, `fabric-cicd`, definition-format, and
   automation versions.
2. Resolve the target workspace, capacity, identity, item support, connections,
   and existing items.
3. Build a static deployment plan from the dependency graph. If the selected
   tool has no true dry-run, do not label static validation as a dry-run.
4. Snapshot existing target metadata/definitions and validate recovery before
   mutation.
5. Apply environment transforms and fail if any forbidden source workspace,
   item, or connection ID remains.
6. Deploy to test in dependency order, poll each operation/job, and collect
   runtime evidence.
7. Promote the identical reviewed source revision to production with only the
   approved environment mapping changed.
8. Run a bounded production canary. Recover from the snapshot or execute the
   documented compensating action if it fails.

## Data Pipeline invariants

For each `TridentNotebook` activity, decode and inspect the item definition and
verify that `typeProperties.workspaceId` and `typeProperties.notebookId` resolve
to the approved target workspace and Notebook. Fail promotion when a source
environment GUID remains or the referenced Notebook is missing.

Before executing the Pipeline:

- establish an idempotent workload/run key;
- check active/recent equivalent jobs;
- save the returned job/run ID immediately;
- correlate terminal job status with a new output version, timestamp, audit row,
  or controlled canary produced by that exact run.

## Handoff evidence

Report source revision, tool versions, deployment plan, before/after hashes,
environment mapping checksum, operation/job IDs, terminal states, canary result,
and recovery readiness. Keep `planned`, `mutated`, `API accepted`, `read back`,
and `runtime verified` as separate statuses.
