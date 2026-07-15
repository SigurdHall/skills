# BI wireframe delivery template

Use this order so a later implementer can distinguish exploration, approved
design, generated files, and render evidence.

## 1. Status and assumptions

- status: `exploratory-pending-evidence`, `target-request-ready`,
  `approved-for-authoring`, or `implemented`
- data state: `synthetic`, `connected-sampled`, or `connected-live`
- audience, decision cadence, targets, data/model readiness, constraints
- explicit assumptions and decisions still required

Do not use `approved-for-authoring` while audience, page/section scope, filter
depth, required evidence, or semantic-model readiness is unresolved.

## 2. StoryFrame

Provide source refs/hashes and ordered frames with stable IDs, decision
questions, pending or supported claims, evidence needs, semantic roles, fact
refs, comparison context, caveats, freshness, and next action. Do not include
target geometry.

## 3. Measure decisions

For each semantic role, record definition status, grain, aggregation,
date/filter behavior, baseline, direction, blank/zero policy, format, quality
test, owner, and target bindings. Separate proposed, implemented, and certified
measures.

## 4. Target requests

Create a separate block for Power BI, React, and HTML as applicable:

- target/version and capability assumptions
- frame-to-page/route/section mapping
- component/visual/block roles and semantic bindings
- geometry/responsive/print rules owned by that target
- interactions and loading/empty/error/stale/partial states
- accessibility and fallback behavior
- traceability IDs
- implementation prerequisites and project-local test/render commands

For React, name the actual repository, framework, component system, data/query
boundary, test runner, accessibility check, and viewport set; do not invent a
generic authoring skill. For HTML, keep the target request separate from
`html-report-builder` YAML/data/query implementation inputs.

## 5. Inspiration ledger

For each selected source, record URL/commit, access date, license/terms, the
principle used, the transformation, attribution requirement, and excluded
material.

## 6. Gate status

| Gate | Status | Evidence | Gap/owner |
|---|---|---|---|
| Contract | | | |
| Story/evidence | | | |
| Capability/fallback | | | |
| Target-static | | | |
| Semantic parity | | | |
| Actual render | | | |
| Interaction/human | | | |

Allowed evidence labels: `not started`, `planned`, `statically validated`,
`rendered-synthetic`, `rendered-connected-sampled`, `rendered-connected-live`,
`parity-tested-synthetic`, `interaction tested`, and `human approved`. Always
pair render evidence with the data state; do not collapse it into a generic
`rendered` or `done`.
