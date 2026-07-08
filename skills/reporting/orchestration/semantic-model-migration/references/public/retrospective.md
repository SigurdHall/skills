# Retrospective

Lessons from an end-to-end legacy → clean semantic-model migration (Tableau-era finance model → import star schema, ~120 measures).

## What worked well
- **Fidelity-first sequencing** (physical cleanup → measures → govern). Clean star made the measure engine straightforward.
- **Porting a tested reference model** instead of translating messy auto-generated DAX. Biggest single quality lever.
- **Reconciliation after every batch** (additivity, segment sums, YTD == full-year). Caught real findings (e.g. an exclusion set that explained an "unclassified" residual) and prevented silent errors.
- **Canonical anchors + duplicate collapse.** Hundreds of catalog rows reduced to ~100 canonical measures with no duplicates.
- **Deterministic generators** for phases 3–6: read a column inventory, emit the edit/PQ payloads, apply in batches, diff the resulting M against the intended output. Repeatable and auditable.
- **Stopping for domain-critical decisions** (sign, budget-version selection, balance vs flow) rather than guessing. Two user questions uncovered a data-representation trap (opening balance in period month-00).
- **Session memory** capturing decisions, gotchas, and validated numbers — essential across a long, multi-session effort.
- **Sampling actual data before applying a name-based classification at scale** (see [ai-readiness.md](ai-readiness.md) §2) resolved most ambiguous summarizeBy/description cases without escalation, and caught cases where the literal pattern match was wrong (a `sum_*`-named column that was a status flag, a `*pris*`-named column that was a per-unit rate, not an amount).
- **A self-contained work-order document for cross-agent/cross-session handoff** (intent, principles, known gotchas, working pattern, precise per-task rules, verification queries) let a second, cheaper model execute complex judgment-heavy sub-tasks (a 150+ column classification pass, a 40+ measure disambiguation pass) unsupervised, including finding and transparently logging its own deviations from the literal spec. See `coding/agent-work-order-handoff`.
- **Backgrounding an independent, read-only sub-task** (generating description proposals into a new file) while the stateful model-editing work continued in the foreground avoided any risk of two agents writing to the same live model concurrently.

## What went badly / cost time
- **Losing unsaved in-memory MCP work** on a Desktop restart. Recovered only because the edits were scripted/deterministic. Save after every phase.
- **Trusting auto-translated catalog DAX** early — semantically wrong; had to switch to reference-porting.
- **Assuming time-intelligence worked** without marking the date table (`SAMEPERIODLASTYEAR` blank).
- **Assuming a data representation** for provisions (movement vs opening balance) — wrong until the actual periods were inspected.
- **Chasing objects MCP cannot create** (perspectives/synonyms are read-only via MCP) before checking capabilities.
- **Off-by-one name matching** for auto-date detection hid that the tables existed.
- **Discovering DMV unreliability reactively**, one bug at a time, each after an operation failed unexpectedly or a verification gave a surprising result (FormatString, then IsAvailableInMDX, then SummarizeBy, then the 100-row cap). A known-gotchas list existing up front (this file) removes this cost for the next migration.
- **Agent-permission setup friction** when the editing agent runs under a permission-gated harness (e.g. Claude Code): a live-model write to a shared/running Desktop instance can be blocked by a safety classifier by default, and the fix (adding a standing permission rule) can itself be blocked as "self-modification" — requiring the human to edit the permission config directly. Budget for this as a one-time per-project setup cost, and check settings-file validity (a copy/paste that leaves two JSON objects in one file invalidates the whole file silently).
- **A backgrounded sub-agent can be interrupted by an unrelated session/quota limit** mid-task. Resuming it (rather than restarting from scratch) preserved all its progress and context — worth doing before assuming the sub-task needs to be redone.

## Automation opportunities
- Auto-date detection + removal (rule-driven).
- Column inventory → datatype/summarizeBy/hide payloads (rule-driven, batchable, no refresh).
- Surrogate→natural mapping + PQ merge generation + orphan/uniqueness port templates.
- Reconciliation harness (parameterized additivity/segment/YTD checks).
- Catalog duplicate-collapse: cluster catalog rows by normalized logic/hash to surface canonical anchors.
- Best-Practice-Analyzer + acceptance-criteria check as a final gate.
- A generic "verify via TOM `Get`/`List`, never via `INFO.VIEW.*`" wrapper around every write, so the DMV-unreliability class of bug can't resurface silently.
- A character-budget validator for generated Copilot-facing descriptions (mechanical check, currently done by hand).
- A standard work-order template (intent/principles/gotchas/working-pattern/tasks/end-procedure sections) so cross-agent handoff doesn't need to be re-designed per project.

## What could be better next time
- Decide persistence/serialization cadence up front; script a snapshot after each phase.
- Inventory the target extract's **data availability** early (which facts/columns are populated) so blank-but-correct measures are expected, and out-of-scope areas (e.g. staffing) are flagged before building.
- Confirm capabilities of the editing bridge (MCP vs TMDL) before planning phase 8.
- Build the reconciliation harness before phase 7, not ad hoc.
- Have the known-gotchas list (this file + mcp-modeling-gotchas.md) in hand before starting the next migration, not assembled reactively during it.
- Ask "which parts of this are independent and read-only?" early in any multi-step model task, so delegation to a background agent is a deliberate up-front decision rather than something noticed partway through planning.

## Universal vs domain-specific (summary)
- **Universal:** phases 1–6 (star-schema hygiene), the measure-migration method, MCP/TMDL operating rules, phase-8 governance, the AI-readiness method (hierarchies, summarizeBy audit, description generation, measure-family disambiguation), the automation ideas, reconciliation discipline, the work-order/agent-delegation pattern.
- **Domain-specific (public-sector finance / BOTT):** chart-of-accounts string, balance-account exclusion, budget-version selection (dynamic code + as-of), provisions opening-balance handling, income/cost/net classification, publishing-date snapshot, the org-hierarchy rollup on the cost-center dimension. See finance-measure-patterns.
