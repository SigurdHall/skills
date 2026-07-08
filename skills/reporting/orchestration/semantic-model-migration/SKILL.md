---
name: semantic-model-migration
description: Use when migrating or refactoring a legacy/Tableau-era Power BI or Fabric semantic model into a clean import star schema — removing auto-date tables, dropping unused/firma/surrogate columns, fixing datatypes and summarizeBy, converting dimensions to natural keys, merging natural codes into facts via Power Query, rebuilding the DAX measure layer, and preparing the finished model for Copilot/AI consumption (hierarchies, summarizeBy audit, column-description generation at scale, measure-family disambiguation). Covers the end-to-end work-order process, MCP-vs-TMDL operating rules, measure porting/translation, and finishing (perspectives, discourageImplicitMeasures, catalog status, BPA validation, AI readiness). Not for report/visual layout (use powerbi-report-production-loop) and not for generic MCP mechanics (use skills-for-fabric).
---

# Semantic Model Migration

Orchestrates migration of a messy legacy semantic model (typically Tableau-era, or an auto-generated import model) into a clean, documented, import star-schema model with a curated DAX measure layer. This skill owns the **process, sequencing, validation gates, and refactoring decisions** — not generic tooling.

**MECHANICS:** Delegate live model edits to `skills-for-fabric` (`semantic-model-authoring` for MCP measure/column/table/relationship/partition ops, `semantic-model-consumption` for DAX/INFO queries). Use `powerbi/powerbi-pbip` for offline TMDL edits when no MCP bridge exists. This skill layers process + gotchas on top; see [mcp-modeling-gotchas.md](references/public/mcp-modeling-gotchas.md).

**DELEGATE:** report/visual migration → `orchestration/powerbi-report-production-loop`. Finance/BOTT semantics → `norms/uit-bott-okonomimodell`, star-schema design → `norms/bott-semantic-model`, finance DAX → `norms/finance-bi-dax-patterns`. Measure documentation standard → `powerbi/semantic-model-metadata`.

## Core principle

Fidelity and traceability beat performance. The **logic layer (measures) is the deliverable**, not physical table tidiness. Do physical cleanup first (so measures build on a clean star), then port the logic durably, then finish/govern.

## Phased process (work orders)

Run in order; each phase has a **validation gate** — do not advance on a failed gate. Detail, edge-cases, and universal-vs-domain notes in [migration-phases.md](references/public/migration-phases.md).

1. **Baseline & setup** — connect tooling, snapshot counts (tables/columns/relationships), take a file copy.
2. **Remove auto-date** — delete LocalDateTable/DateTableTemplate + variations; turn off auto date/time.
3. **Remove dead columns** — single-value/tenant/audit columns (e.g. a constant `firma`/company id). **Gate: stop if a "constant" column is not actually constant.**
4. **Datatypes / summarizeBy / hide** — fix double→decimal/int, `summarizeBy=none` on IDs/codes, hide technical columns. Pure TOM metadata, durable, no refresh.
5. **Dimensions → natural keys** — collapse SCD, drop surrogate (`zk_*`) + SCD-window columns, expose natural key, build hierarchies. **Gate: uniqueness port per dim.**
6. **Facts → natural keys** — merge natural codes into each fact via Power Query, re-point relationships to natural keys, drop surrogates. **Gate: 0 orphans per conformed dim.**
7. **Measure layer** — build/port the DAX engine bottom-up (see [measure-migration.md](references/public/measure-migration.md)). **Gate: reconciliation vs source + 0 leftover auto-translation artifacts.**
8. **Finish & govern** — perspectives, `discourageImplicitMeasures=true`, synonyms, catalog status, Best-Practice-Analyzer validation, serialize. For real Copilot/AI readiness (hierarchies, `summarizeBy` at scale, front-loaded descriptions, measure-name disambiguation) see [ai-readiness.md](references/public/ai-readiness.md). When Copilot/conversational-BI consumption is in scope, this phase also covers AI readiness: hierarchies, a summarizeBy audit, column-description generation at scale, and measure-family disambiguation — see [ai-readiness.md](references/public/ai-readiness.md) for the method (gate, decision rules, escalation criteria).

## Operating rules

- **Persistence is not automatic.** MCP edits the *in-memory* model; nothing hits disk until saved. Save (or serialize) after every phase — an unsaved restart loses everything. See gotchas.
- **Durable cleanup = metadata + Power Query together.** Deleting a column only in the model re-adds it on refresh; also remove it in the M partition.
- **Validate every phase with the consumption side** (row counts, DISTINCTCOUNT, orphan checks, reconciliation) before advancing.
- **Prefer a tested reference model over auto-translated catalog DAX.** If a clean, tested implementation of the same logic exists, port its logic (not its structure); translate a messy catalog only for what the reference does not cover. See measure-migration.
- **Collapse duplicates to canonical anchors.** Legacy catalogs are full of copies/snapshots/parameter-variants of a handful of real measures; build the canon and mark the rest replaced — do not recreate duplicate-named measures.
- **Stop for genuinely ambiguous or domain-critical decisions** (sign conventions, version selection, balance vs flow accounts) instead of guessing; record the decision.
- **Keep domain concretes out of committed files.** Account-code lists, org codes, source URLs, local paths, and reference-model locations are project data → `references/private/` or the project repo, never public skill files.

## What is universal vs domain-specific

- **Universal:** phases 1–6 (star-schema hygiene), the measure-migration *method* (reference-port vs translate, dependency layers, canonical anchors, reconciliation), the MCP/TMDL operating rules, phase-8 governance.
- **Domain-specific (here: public-sector finance / BOTT):** which columns are the chart-of-accounts string, the balance-account exclusion set, budget-version selection, provisions (opening-balance) handling, income/cost classification. Kept in [finance-measure-patterns.md](references/public/finance-measure-patterns.md) as patterns and in `references/private/` as concretes.

## References

- [migration-phases.md](references/public/migration-phases.md): per-phase goals, steps, validation gates, edge-cases, automation notes.
- [measure-migration.md](references/public/measure-migration.md): logic-layer method (port vs translate, dependency layers, canonical anchors, reconciliation).
- [ai-readiness.md](references/public/ai-readiness.md): phase-8 depth for Copilot/AI consumption — hierarchies, summarizeBy audit, column-description generation at scale, measure-family disambiguation.
- [mcp-modeling-gotchas.md](references/public/mcp-modeling-gotchas.md): operational supplements to `skills-for-fabric` (persistence, partial updates, batching, reconnect, DMV quirks, TMDL boundaries).
- [finance-measure-patterns.md](references/public/finance-measure-patterns.md): finance/BOTT-specific measure patterns discovered during migration.
- [ai-readiness.md](references/public/ai-readiness.md): AI/Copilot-readiness depth for phase 8 (hierarchies, summarizeBy at scale, description tiers, measure-name family disambiguation).
- [retrospective.md](references/public/retrospective.md): what worked, what did not, automation opportunities, improvements.

For multi-session or multi-agent delegation of this process (e.g. a planning
model specifying a batch for a cheaper execution model, or an independent
read-only sub-task run in the background), see
`coding/agent-work-order-handoff`.
