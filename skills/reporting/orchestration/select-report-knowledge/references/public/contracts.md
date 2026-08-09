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

## DiagnosticReportPlanV1

Use this companion contract first when the intent is `explain_change`. Build it from a
`DiagnosticReportRequestV1`, then verify its hash before selecting knowledge or designing a page.
It binds one empirical diagnostic pattern to measure roles, ordered frames, conditional visual
families, page-composition rules, an exploratory story, and explicit gaps. It contains no observed
values.

Stop when `status` is `blocked`, a required measure role is `blocked`, a required planned frame has no safe
or conditional visual recommendation, any gap has `blocking: true`, or plan verification fails.
Treat any mismatch between the aggregate status and a blocking detail as a contract error.
Preserve gaps with `blocking: false`: `severity: condition` constrains an exploratory handoff and
`severity: advisory` documents remaining scope, but neither is a hard stop.
Keep a `conditional` plan exploratory and preserve its complete `gaps` list. Only
`ready_for_wireframing` may proceed as a diagnostic wireframe input without a knowledge blocker.
`frame.required` and `page.required` distinguish the minimum diagnostic path from optional
branches that may be omitted when their measures are not ready.

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

For an explain-change handoff, keep the verified plan as a separate companion and retain:

```text
planId
planSha256
registrySnapshotSha256
diagnosticPatternRef
status
gaps
planPath
```

Do not add these fields to the closed `knowledgeContext` block. Reference the plan through the
StoryFrame source refs and delivery record until the StoryFrame draft contract is versioned to
carry a dedicated diagnostic context.
