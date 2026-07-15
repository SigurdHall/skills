---
name: design-bi-report-wireframes
description: Use when designing or regenerating a BI report, dashboard, or analytical page for Power BI, React, or HTML from business questions, semantic-model knowledge, measure patterns, and visual references. Produces an evidence-led StoryFrame plus target-specific wireframes without forcing shared geometry across targets.
---

# Design BI Report Wireframes

Create one target-independent story contract, then compile it into separate
Power BI, React, and HTML wireframes. Reuse semantics, evidence, narrative, and
brand intent across targets; keep geometry, components, interactions, and
physical bindings target-specific.

## Workflow

1. Inspect available briefs, semantic metadata, narrative evidence,
   brand/taste rules, and target constraints. Read metadata before sampling
   data. A no-data output is an exploratory draft: mark claims
   `pending-evidence` and never write data-driven titles or conclusions as facts.
2. Invoke `select-report-knowledge` when the internal Report Knowledge Base is
   available. Build and verify a `KnowledgeSelectionV1` for the requested
   domains and targets. Carry the selection ID, both selection and registry
   hashes, selected domains, unresolved requirements, and evidence advisories
   in the StoryFrame `knowledgeContext` block. Fail closed on a stale, incomplete,
   unknown-version, or hash-invalid selection.
3. Select at most three relevant inspiration sources from the verified
   selection, supplementing it only when an explicit evidence gap remains. Use
   [gallery-catalog.md](references/public/gallery-catalog.md). Record source, license,
   borrowed principle, and what must not be copied.
4. Build a candidate measure set using business questions first, verified
   canonical definitions from the selection second, and
   [measure-pattern-library.md](references/public/measure-pattern-library.md) only as a
   fallback or inspiration prior.
   Use corpus prevalence only as an inspiration prior. Validate definition,
   grain, filter context, additivity, direction, baseline, format, and owner.
5. Draft `StoryFrameV1` from
   [story-frame-and-adapters.md](references/public/story-frame-and-adapters.md). Include
   ordered decisions, claims, evidence needs, caveats, freshness, and next
   actions. Use typed global source refs for brief/evidence/hash and optional
   brand/taste intent, then repeat every applicable ref in each frame's
   `traceRefs`. Exclude coordinates, visual types, CSS, DAX, SQL, and physical
   field names.
6. Compile a separate target request and wireframe for each requested target:
   - Power BI: for a conceptual wireframe, stop at the target request. After
     audience, page scope, filter depth, required evidence, and model readiness
     are locked, use `powerbi-report-design`; invoke `powerbi-report-authoring`
     only after the target request/design brief is approved.
   - React: define routes/sections, component registry, typed view models,
     responsive hierarchy, tokens, accessibility, interaction state, and a
     project-local implementation/test route. No canonical React authoring
     skill is assumed.
   - HTML: first define semantic sections, table/chart fallbacks, CSS/print
     behavior, and static-versus-interactive boundaries. Invoke
     `html-report-builder` after the target request is approved and either an
     identified/available data source or an approved synthetic fixture exists;
     that downstream skill owns creation and validation of report YAML, data
     contract, and SQL/query inputs.
7. Apply the seven gates in the adapter reference: contract, evidence,
   capability/fallback, target-static, semantic parity, actual render, and
   interaction/human review. Validate the draft envelope with
   `scripts/validate_story_frame.py` and use the shared synthetic cases in
   [semantic-parity.md](references/public/semantic-parity.md) for cross-target
   calculation tests.
8. Deliver the StoryFrame, target wireframes, measure decisions, inspiration
   ledger, validation evidence, and explicit gaps. Require semantic parity, not
   pixel parity, across targets. Use
   [delivery-template.md](references/public/delivery-template.md) for the handoff.

## Operating Rules

- Never create a universal layout schema spanning PBIR, React DOM, and HTML.
- Never consume a knowledge selection without verifying its bundle, record,
  and registry-snapshot hashes against the current canonical register.
- Never copy a gallery formula, layout, image, or asset without compatible
  licensing and attribution requirements.
- Never call a measure popular solely because it appears often in a biased
  public sample corpus. Say "widespread in this corpus" and report denominator,
  source spread, and bias.
- Never generate a measure until its business meaning and safe aggregation are
  known. Common is not the same as correct.
- Never advance an exploratory draft to authoring while required audience,
  scope, filter-depth, evidence, or model decisions remain unresolved.
- Keep report traceability through stable frame, claim, fact, and semantic-role
  IDs; bind those IDs differently in each target adapter.

## Resources

- [story-frame-and-adapters.md](references/public/story-frame-and-adapters.md): shared
  contract boundary, adapter mappings, and validation gates.
- [gallery-catalog.md](references/public/gallery-catalog.md): curated, license-aware
  visual and BI reference sources.
- [measure-corpus-method.md](references/public/measure-corpus-method.md):
  verifiable pinned snapshot, statistics, source manifest, and reconstruction
  limitation.
- [measure-pattern-library.md](references/public/measure-pattern-library.md): candidate
  measure families and semantic guardrails.
- [delivery-template.md](references/public/delivery-template.md): normalized
  StoryFrame, target-request, evidence, and gate-status handoff.
- [semantic-parity.md](references/public/semantic-parity.md): shared synthetic
  golden-scenario method for DAX, React, and SQL/HTML adapters.
- [measure-corpus-stats.json](references/public/measure-corpus-stats.json): generated
  aggregate output with no measure names or formulas; only approved public
  source labels and whitelisted built-in function tokens are exposed.
- [measure-corpus-manifest.json](references/public/measure-corpus-manifest.json):
  pinned public commits, licenses, and extracted-content hashes.
- [story-frame-v1.example.json](assets/story-frame-v1.example.json):
  illustrative, non-canonical StoryFrame instance.
- [parity-scenarios.example.json](assets/parity-scenarios.example.json):
  illustrative synthetic cross-target calculation cases.
- `scripts/analyze_measure_corpus.py`: metadata-only DAX/TMDL/BIM corpus
  analyzer; defaults source labels to anonymous, redacts unknown/user-defined
  call tokens, and never emits measure names or expressions.
- `scripts/validate_story_frame.py`: validates the minimum draft envelope,
  pending-evidence rules, unique frame IDs/orders, references, and absence of
  target geometry; it is not a canonical schema validator.
