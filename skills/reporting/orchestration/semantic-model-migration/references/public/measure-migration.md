# Measure migration — logic-layer method

How to rebuild the DAX measure layer during a semantic-model migration. Universal method; domain content lives in [finance-measure-patterns.md](finance-measure-patterns.md).

## Source of truth: port vs translate

Legacy models usually give you two candidate sources:

1. **A tested reference model** (a working report's model with the same fact/source) — clean, validated DAX.
2. **An auto-generated catalog** of the legacy tool's calculations (e.g. exported Tableau formulas) — messy, "literal", often semantically wrong in DAX.

**Rule:** port the *logic* from the reference model where it exists (it is tested truth); translate the catalog only for what the reference does not cover. Reference = DAX logic, **not** structure — do not copy its scaffolding (a single `_Measures` table, report-only slicer/snapshot tables). Place measures on their home fact table.

The auto-translated catalog DAX is a decoding aid, not something to bulk-apply. Typical breakage: a row-level `IF(col <= param, value)` is **not** an aggregating measure in DAX — it must become filter context (`CALCULATE(base, dim[period] <= SELECTEDVALUE(...))`).

## Dependency layers (build bottom-up)

Logic is a tree, not a flat list. Build lowest layer first; a higher measure references only measures below it, never base columns directly.

1. **Selection helpers** — `Valgt År`/`Valgt Mnd`-style measures from the date dim (replace legacy tool parameters), `COALESCE(SELECTEDVALUE(...), fallback)`.
2. **Base amounts** — raw `SUM(col)` (hidden), then the canonical filtered base (e.g. an operational-account exclusion).
3. **Version/segment-filtered** — `CALCULATE(base, KEEPFILTERS(...))`.
4. **Aggregates** — null-protected component sums (`COALESCE(x,0)`).
5. **Periodised (YTD / as-of)** — period-window + publishing/as-of cutoffs.
6. **Variance / share** — differences and ratios over the layers below.

Mark a date table as a **date table** before using time-intelligence — `TOTALYTD` is forgiving, but `SAMEPERIODLASTYEAR` returns blank without it.

## Canonical anchors + duplicate collapse

Legacy catalogs explode a handful of real measures into dozens of copies, fixed-date snapshots, graph-variants, and parameter-variants. Do **not** recreate them.

- Identify the ~10 canonical anchors and build those.
- Map every duplicate's hash/id to its canonical name; mark it **replaced** in the catalog status (phase 8).
- Fixed-date snapshots (`... per 30.09.YY`) collapse into one period-slicer-driven measure.
- Parameter-variants collapse to the canonical selection-helper measures.
- Result: hundreds of catalog rows → ~100 canonical measures. No duplicate-named measures (a phase-8 acceptance criterion).

## Validation by reconciliation

Every batch, validate with the consumption side, not by eyeballing DAX:

- **Additivity:** components sum to the total (e.g. income + cost + net + unclassified = base). A large "unclassified" residual usually means a classification/data gap — investigate, it often reveals a real finding.
- **Cross-check reformulations:** a full-year YTD equals the full-year base; last-year-same-period equals the prior year's base.
- **Segment reconciliation:** segment splits sum to the parent (BEV + BOA + outside = base), to the øre/cent.
- **Empty is a valid result** when the test extract lacks that data (e.g. budget rows) — verify the measure *evaluates* without error and is structurally correct; note it as evaluation-only validation.

## Naming, format, documentation (apply as you build)

- Every measure: `formatString`, a `///` description (business rule + when-vs-alternative + basis + catalog hash), a display folder, and a catalog-hash annotation.
- Organize display folders under one top folder per fact table (e.g. `_Measures\<area>`); a leading underscore sorts it to the top of the field list.
- Keep raw/base helpers hidden; expose only the canonical measures.

## What worked / what did not

- **Worked:** porting the tested reference engine (huge fidelity win over translating catalog DAX); reconciliation-per-batch (caught the account-exclusion finding); canonical-anchor collapse (hundreds → ~100); stopping for domain-critical sign/version decisions.
- **Did not / cost time:** trusting auto-translated catalog DAX; assuming time-intelligence works without a marked date table; assuming a data representation (movement vs opening-balance) — always inspect the actual periods/values first.
