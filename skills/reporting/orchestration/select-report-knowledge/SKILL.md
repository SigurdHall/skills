---
name: select-report-knowledge
description: Use when a BI report, dashboard, StoryFrame, measure design, diagnostic explain-change request, or Power BI/React/HTML wireframe needs a governed subset of the internal Report Knowledge Base. Builds and verifies a deterministic, hash-locked DiagnosticReportPlanV1 and/or KnowledgeSelectionV1 containing only definitions, source metadata, empirical report-pattern evidence, and structural references; never report values or datasets.
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
4. For an explain-change request (for example, why receivables or FTE increased, or why sales
   decreased), write a `DiagnosticReportRequestV1` outside `catalog/`. Preserve the user's
   question and set the requested subject, direction, comparison, audience, domains, and targets.
   Read the canonical request and plan schemas under the product's `contracts/` directory; do not
   reconstruct their fields from memory. If the requested subject is not supported by the current
   request schema, return an explicit coverage gap instead of mapping it to the nearest subject.
   Build and immediately verify the plan before selecting records:

   ```powershell
   uv run --project C:\repos\bi-konsulent\leveranse\report-knowledge-base --python 3.12 report-knowledge-base plan-diagnostic --request <diagnostic-request.json> --output <diagnostic-plan.json>
   uv run --project C:\repos\bi-konsulent\leveranse\report-knowledge-base --python 3.12 report-knowledge-base verify-diagnostic-plan --plan <diagnostic-plan.json>
   ```

   Read the verified plan's measure roles, ordered frames, visual conditions, page-composition
   rules, evidence refs, and gaps. Stop before selection or wireframing when the plan status is
   `blocked`, any required measure role is `blocked`, a required planned frame has no safe or conditional
   visual recommendation, any gap has `blocking: true`, or verification fails. Treat a mismatch
   between the aggregate plan status and a blocking detail as a contract error. Preserve
   `severity: condition` and `severity: advisory` gaps with `blocking: false`, but do not let them
   trigger a hard stop. Return the exact gap reason and remediation; do not
   replace a blocked role or evidence link from memory. Treat a `conditional` plan as exploratory
   only and preserve every condition downstream.
5. Write a `SelectionRequestV1` outside the canonical `catalog/` directory. Start with
   `measure_definition`, `pattern_definition`, `report_definition`, and `decision_trace`.
   For a verified diagnostic plan, also request `diagnostic_pattern` and
   `pattern_observation`; use its exact domains and pattern trace rather than broadening the scope.
   Include `benchmark_definition` only for definition metadata.
6. Build and immediately verify the bundle:

   ```powershell
   uv run --project C:\repos\bi-konsulent\leveranse\report-knowledge-base --python 3.12 report-knowledge-base select --request <request.json> --output <selection.json>
   uv run --project C:\repos\bi-konsulent\leveranse\report-knowledge-base --python 3.12 report-knowledge-base verify-selection --bundle <selection.json> --require-ready
   ```

7. Fail closed when the selection is incomplete, has unresolved requirements, uses an unknown
   schema version, or no longer matches the current registry snapshot. Never hand-edit hashes.
8. Hand the verified bundle downstream with `selectionId`, `selectionSha256`,
   `registrySnapshotSha256`, selected domain/target scope, unresolved gaps, and the request path.
   For an explain-change request, also hand off the verified `planId`, `planSha256`,
   `diagnosticPatternRef`, plan status, complete gap list, and plan path as a companion contract.

## Selection Rules

- Select by decision need and domain before tags. Tags narrow a known scope; they do not establish
  business meaning.
- Preserve the full record and its `recordSha256`. Do not copy selected formulas or patterns into
  a second unversioned note and call that note canonical.
- Treat a `measure_candidate` as backlog, never as an authoring-ready measure.
- Treat `pattern_observation` as evidence. A `pattern_definition` is canonical only when its own
  evidence references satisfy the register's promotion gate.
- Treat `report_definition` as structural guidance. Text placeholders are roles, not values.
- Treat `DiagnosticReportPlanV1` as the authority for diagnostic measure bundles, usage
  conditions, ordered analysis steps, visual conditions, and page composition. Do not cherry-pick
  a visually convenient subset or invent a missing dependency.
- Treat `blocked` as a hard stop. A `conditional` plan may support an exploratory handoff, but it
  is never authoring-ready and every condition must remain visible.
- Preserve non-blocking condition and advisory gaps without promoting them to hard blockers.
- Keep a no-data StoryFrame exploratory and mark unsupported claims `pending-evidence`.
- If a task needs observed values, stop this skill at the selection handoff. A separate,
  explicitly authorized data workflow must supply them.

## Handoff Contract

Read [contracts.md](references/public/contracts.md) for the request fields, required verification
evidence, and downstream consumption rules.
