# StoryFrame and target adapters

## Boundary

Use this flow:

```text
StoryBrief + NarrativeEvidence + domain/measure knowledge + brand/taste
                                  |
                                  v
                             StoryFrameV1
              /            |             \
     Power BI request   React request   HTML request
           |                |              |
      PBIR/TMDL          DOM/app IR      document IR
```

`StoryFrameV1` is a target-independent draft story/evidence contract envelope.
It is not a layout schema and is not yet canonical. The sample in
`assets/story-frame-v1.example.json` is illustrative; promote a schema to a
canonical contract repository only after consumer tests exist.

Until then, treat these fields as the minimum draft envelope: contract/status,
data state (`knowledge_only_no_values`, `synthetic`, `connected-sampled`, or `connected-live`),
source references (including optional typed brand/taste refs), ordered frames,
stable frame IDs, decision questions,
claim refs, evidence needs, semantic-role refs, fact refs, comparison context,
caveats, freshness, next action, and frame-level trace refs. This checklist is
not a formal schema.

## StoryFrame content

Each ordered frame should contain:

- stable `frameId`, decision question, and `keyClaimRef`
- evidence needs with intent, priority, semantic-role references, and fact refs
- comparison context using the draft's small semantic key set and primitive
  values, driver status, string-only caveats, and freshness requirement
- intended decision or next action
- `traceRefs` that repeat every declared global source reference used by the
  frame: brief, narrative evidence, content hash, and optional brand/taste refs

Global `sourceRefs` use typed IDs: `brief:`, `evidence:`, `sha256:`, and, when
available, `brand:` and `taste:`. Brand and taste are target-independent intent
references; their concrete theme, component, CSS, or object-group realization
belongs only in a target adapter.

When a verified Report Knowledge Base selection is used, add one closed
`knowledgeContext` block containing `selectionId`, `selectionSha256`,
`registrySnapshotSha256`, `selectedDomainRefs`, and
`unresolvedKnowledgeRequirements`, and `evidenceAdvisories`. The block is
traceability metadata, never
target geometry or a substitute for evidence.

When the intent is `explain_change`, keep the verified `DiagnosticReportPlanV1`
as a separate companion contract. Map its ordered frames and measure roles into
StoryFrame decision/evidence semantics, and carry its plan ID/hash in the delivery
record and typed source refs. Do not add visual families or page-composition rules
to StoryFrame: apply them in each target adapter. Stop before target compilation
when the plan or a required measure role is blocked, a required planned frame has no safe
or conditional visual recommendation, or any plan gap has `blocking: true`.
Carry non-blocking conditions and advisories into the exploratory handoff.

Do not include:

- `x`, `y`, width, height, canvas size, or breakpoints
- chart/visual/component names
- CSS, DOM hierarchy, PBIR JSON, DAX, SQL, or target query syntax
- physical `Table[Field]` names or target-specific interactions

When no real evidence exists, use `status: exploratory-pending-evidence`, mark
every claim/fact ref as pending, use synthetic fixtures only for layout states,
and prohibit titles or narrative text that imply an observed result.
For the strict metadata-only Report Knowledge Base workflow, use
`dataState: knowledge_only_no_values` and do not create fixtures or values.

## Adapter mapping

| StoryFrame concept | Power BI | React | HTML |
|---|---|---|---|
| Frame/order | report page and reading order | route/section hierarchy | semantic section/print order |
| Evidence intent | visual-role and page-archetype rules | component-registry selection | chart/table/text block selection |
| Semantic role | physical semantic-model binding | typed view model/query binding | query result/column binding |
| Priority | canvas hierarchy and layout variant | responsive hierarchy | screen and print hierarchy |
| Comparison context | axes, small multiples, tooltip, drill | comparison component and state | adjacent table/chart and annotation |
| Brand intent | theme, taste profile, object groups | design tokens/component variants | CSS variables and print theme |
| Next action | button, bookmark, drillthrough, URL | route, command, filter state | link, details/summary, form if allowed |
| Traceability | page/visual metadata | `data-frame-id`, typed IDs | `data-frame-id` / `data-fact-id` |

## Target wireframe deliverables

### Power BI

- page archetype and purpose
- canvas grid and visual placeholders
- semantic bindings and measure dependencies
- slicers, filters, cross-highlighting, tooltips, bookmarks, and drillthrough
- accessibility order, mobile layout, theme/taste rules, and fallback visuals
- diagnostic frame-to-measure-role bindings plus satisfied visual and page conditions

### React

- route and component tree
- component contract, typed props/view models, loading/empty/error/stale states
- query/cache boundary and semantic-role binding
- CSS grid/flex hierarchy by breakpoint, tokens, keyboard behavior, and ARIA
- interaction state, URL/state persistence, observability, and export behavior
- diagnostic frame-to-view-model bindings plus satisfied visual and page conditions

### HTML

- semantic heading and section outline
- static data contract or server/client rendering boundary
- chart-to-table fallback, no-JavaScript behavior, and print/PDF layout
- CSS grid hierarchy, responsive order, accessibility, and provenance notes
- trace attributes for frames, claims, facts, and generated timestamp
- diagnostic frame-to-block bindings plus satisfied visual and page conditions

## Gates

1. **Draft contract:** `scripts/validate_story_frame.py` confirms required IDs,
   references, pending-evidence rules, unique frame IDs/orders, and absence of
   target geometry. This is minimum-envelope evidence, not canonical-schema or
   consumer-compatibility evidence.
2. **Story/evidence:** each important visual claim has an evidence need and each
   evidence block supports a decision.
3. **Capability/fallback:** every requested behavior is supported by that
   target or has an explicit fallback.
4. **Target-static:** target files/schema, lint, accessibility, and binding
   validation pass.
5. **Semantic parity:** definition, filters, grain, period, denominator, units,
   and direction match across targets. Run one shared synthetic golden-scenario
   package through the DAX, React, and SQL/HTML adapters; see
   [semantic-parity.md](semantic-parity.md).
6. **Actual render:** inspect Power BI Desktop/service, React at supported
   breakpoints, and HTML screen/print output. Static validation is not render
   evidence.
7. **Interaction/human:** verify navigation, filters, keyboard, empty/error
   states, decision usefulness, and unresolved caveats.

Pixel parity is not a goal. Decision, evidence, and semantic parity are.
