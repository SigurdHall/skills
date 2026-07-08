# Migration phases — detailed process

Universal work-order skeleton for legacy → clean import star-schema semantic model. Each phase: **goal → steps → validation gate → edge-cases**. Mechanics via `skills-for-fabric/semantic-model-authoring`.

## Phase 1 — Baseline & setup
- **Goal:** known starting point + safety net.
- **Steps:** connect tooling to the live model or the project folder; record counts (tables, columns, relationships, rows on the big fact); take a file copy of the project.
- **Gate:** baseline numbers captured; working copy exists.
- **Edge-cases:** an "import" model auto-built from a lakehouse/warehouse often carries a huge auto-date subgraph (one hidden date table per date column) — the raw table count can be 3–4× the "real" table count.

## Phase 2 — Remove auto-date
- **Goal:** kill auto date/time bloat.
- **Steps:** turn off the model's auto date/time; delete every LocalDateTable + the DateTableTemplate; remove dangling `variation` on date columns.
- **Gate:** 0 auto-date tables; model still loads.
- **Edge-cases:** auto-date variation relationships inflate the relationship count — deleting the tables drops them too. When detecting by name, match the full prefix length (an off-by-one `LEFT()` returns 0 hits and hides that they exist).

## Phase 3 — Remove dead / tenant / audit columns
- **Goal:** drop columns that carry no analytical value.
- **Steps:** verify a suspected constant with `DISTINCTCOUNT`; if constant, delete it (model + M partition) and drop its relationships; also drop audit timestamps and internal attribute ids not used downstream.
- **Gate:** target columns gone; **stop if a "constant" column has >1 value** (it may encode something).
- **Edge-cases:** a stray mapping/bridge table can still hold the "constant" column with other values — decide per table, do not blanket-drop.

## Phase 4 — Datatypes / summarizeBy / hide
- **Goal:** correct storage + stop implicit numeric aggregation of ids/codes.
- **Steps:** from a column inventory, set double→decimal (currency) or double→int; set `summarizeBy=none` on all ids/codes/keys; hide technical columns (`isHidden` + `isAvailableInMdx=false`). Batch it.
- **Gate:** 0 `double` left; 0 `sum` on id/code; protected natural keys stay visible.
- **Edge-cases:** this is **pure model metadata** — durable, needs **no refresh**, does not edit M, does not mark the table incomplete. Keep a short protect-list of natural keys that must stay visible/`summarizeBy=none` so a blanket rule does not hide them.

## Phase 5 — Dimensions → natural keys (type-1)
- **Goal:** one row per natural key, natural key as the relationship key, hierarchies built.
- **Steps:** per dim, collapse SCD history in Power Query to one row per natural key; **uniqueness port** (`COUNTROWS` vs `DISTINCTCOUNT` of the key); drop surrogate (`zk_*`) + SCD-window (valid-from/to) columns; expose the natural key (`summarizeBy=none`, not `isKey`); build user hierarchies.
- **Gate:** unique natural PK per dim (port passes); **stop per dim on a uniqueness break**.
- **Edge-cases:** a hierarchy cannot take a name that collides with an existing column. A dimension may have an SCD-window even when "not versioned" — always test uniqueness, never assume. Hierarchy `Create` that fails rolls back the transaction and can poison the engine baseline (see gotchas — reconnect).

## Phase 6 — Facts → natural keys (Power Query merge)
- **Goal:** facts join dimensions on natural codes; surrogates gone.
- **Steps (order matters):**
  1. Delete the old surrogate relationships first (they block re-pointing / cause ambiguity).
  2. Merge M: `Table.NestedJoin(fact, {surrogate}, dim, {surrogate}, ...)` → expand only the natural code → `Table.RemoveColumns` the surrogate.
  3. In the model: delete the surrogate column, create the natural code column (`SourceColumn` = M output name).
  4. Refresh **after** the table object matches the M output (else "column X not in the rowset").
  5. Create natural 1:* relationships (single direction; fact-side key hidden).
- **Gate:** 0 conformed-dimension surrogates in facts; orphan rate 0 against every conformed dim; relationships active and unambiguous.
- **Edge-cases:**
  - A fact that already has the natural code needs **no refresh** — just drop the surrogate + create the relationship. Only merge-facts need a full refresh.
  - Active **both-directions 1:1** relationships create path ambiguity that blocks activating others — delete all old surrogate relationships before creating single-direction natural ones.
  - Snowflake vs star: when a fact reaches a dimension both directly and via another dim, deactivate the direct edge for grain-appropriate facts before activating the snowflake edge.
  - Relationship-create batches above ~15–17 sometimes fail transiently — split into smaller batches.

## Phase 7 — Measure layer
- See [measure-migration.md](measure-migration.md). **Gate:** core measures reconcile to source for representative slices; 0 leftover auto-translation artifacts (`Calculation_*`, `(copy)_*`); every visible measure has format + description + display folder.

## Phase 8 — Finish & govern
- **Goal:** distributable, AI-ready, traceable target model.
- **Steps:** `discourageImplicitMeasures=true`; perspectives per work area; synonyms/linguistic metadata; set status on every catalog row (implemented / replaced / excluded / deferred); run a Best-Practice-Analyzer pass; serialize to the project folder.
- **Gate:** 0 critical BPA findings; all catalog rows have status; each visible table/column has a description.
- **Edge-cases:** perspectives and synonyms are often **not creatable via MCP** (read-only) — write them in TMDL after a save, then reload. Perspectives are low-value for standard report authoring (they only scope Excel/Q&A/Copilot/personalize surfaces), so weigh effort vs payoff.

## Automation opportunities
- Phases 3–6 are **deterministic from a column inventory** — generate the model/PQ edit payloads with a script, apply in batches, then diff the resulting M against the intended output byte-for-byte.
- Uniqueness ports, orphan checks, and reconciliation are all parameterizable query templates.
- Auto-date detection, datatype/hide rules, and surrogate→natural mapping are rule-driven and portable across models.
