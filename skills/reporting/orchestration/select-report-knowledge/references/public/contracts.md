# Selection contracts

## SelectionRequestV1

Required fields:

- `schemaVersion`: `1.0`.
- `requestId`: stable lowercase identifier.
- `domainRefs`: zero or more canonical `domain.*` IDs.
- `targets`: one or more of `powerbi`, `react`, or `html`.
- `recordTypes`: requested canonical record types.
- `tags`: optional narrowing tags.

An empty filter means "do not filter on this field". Use it intentionally; selecting every record
is rarely the smallest useful bundle.

## KnowledgeSelectionV1

The bundle includes the original request, targets, no-data policy, registry snapshot hash, selected
records with individual hashes, unresolved requirements, evidence advisories, status, and bundle
hash. Verification must recompute the complete deterministic selection against the current
registry. `unresolvedRequirements` blocks the requested scope. `evidenceAdvisories` records
candidate evidence or partial target adapters without pretending that the source is canonical.
`ready_for_authoring` means the deterministic selection succeeded; it does not assert that a
semantic model, real evidence, or target capability is ready.

## Downstream record

Every StoryFrame or target request grounded by the bundle should retain one
closed `knowledgeContext` block:

```text
selectionId
selectionSha256
registrySnapshotSha256
selectedDomainRefs
unresolvedKnowledgeRequirements
evidenceAdvisories
```

Do not embed the bundle as target geometry. Power BI, React, and HTML adapters own physical layout
and field binding independently.
