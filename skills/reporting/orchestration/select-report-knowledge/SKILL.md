---
name: select-report-knowledge
description: Use when a BI report, dashboard, StoryFrame, measure design, or Power BI/React/HTML wireframe needs a governed subset of the internal Report Knowledge Base. Builds and verifies a deterministic, hash-locked KnowledgeSelectionV1 containing only definitions, source metadata, empirical report-pattern evidence, and structural references; never report values or datasets.
---

# Select Report Knowledge

Build the smallest traceable knowledge bundle that can ground a report-design task. Treat the
bundle as an input contract: downstream work may refine target bindings, but must not silently
change definitions, provenance, or empirical evidence.

## Workflow

1. Locate the canonical product at
   `C:\repos\bi-konsulent\leveranse\report-knowledge-base`. Stop and report a missing
   dependency if its manifest or CLI is unavailable; do not reconstruct the register from memory.
2. Read the report brief and identify requested targets, decision domains, record types, and
   optional tags. Use domain IDs from the current explorer projection or domain partition. Do not
   infer a broad domain when a narrower registered domain satisfies the brief.
3. Run the registry and no-data gates before selecting:

   ```powershell
   uv run --project C:\repos\bi-konsulent\leveranse\report-knowledge-base --python 3.12 report-knowledge-base validate
   uv run --project C:\repos\bi-konsulent\leveranse\report-knowledge-base --python 3.12 report-knowledge-base audit-no-data
   ```

   Both commands must return a valid status. The policy must be `knowledge_only_no_values`.
4. Write a `SelectionRequestV1` outside the canonical `catalog/` directory. Start with
   `measure_definition`, `pattern_definition`, `report_definition`, and `decision_trace`.
   Include `pattern_observation` when the task needs to inspect the empirical basis, and include
   `benchmark_definition` only for definition metadata.
5. Build and immediately verify the bundle:

   ```powershell
   uv run --project C:\repos\bi-konsulent\leveranse\report-knowledge-base --python 3.12 report-knowledge-base select --request <request.json> --output <selection.json>
   uv run --project C:\repos\bi-konsulent\leveranse\report-knowledge-base --python 3.12 report-knowledge-base verify-selection --bundle <selection.json> --require-ready
   ```

6. Fail closed when the selection is incomplete, has unresolved requirements, uses an unknown
   schema version, or no longer matches the current registry snapshot. Never hand-edit hashes.
7. Hand the verified bundle downstream with `selectionId`, `selectionSha256`,
   `registrySnapshotSha256`, selected domain/target scope, unresolved gaps, and the request path.

## Selection Rules

- Select by decision need and domain before tags. Tags narrow a known scope; they do not establish
  business meaning.
- Preserve the full record and its `recordSha256`. Do not copy selected formulas or patterns into
  a second unversioned note and call that note canonical.
- Treat a `measure_candidate` as backlog, never as an authoring-ready measure.
- Treat `pattern_observation` as evidence. A `pattern_definition` is canonical only when its own
  evidence references satisfy the register's promotion gate.
- Treat `report_definition` as structural guidance. Text placeholders are roles, not values.
- Keep a no-data StoryFrame exploratory and mark unsupported claims `pending-evidence`.
- If a task needs observed values, stop this skill at the selection handoff. A separate,
  explicitly authorized data workflow must supply them.

## Handoff Contract

Read [contracts.md](references/public/contracts.md) for the request fields, required verification
evidence, and downstream consumption rules.
