# AI / Copilot readiness — depth beyond phase 8

Phase 8 (finish & govern) names "AI-ready" as a goal but only lists
perspectives/synonyms/status/BPA. This is the method for the four items that
most affect what Copilot for Power BI can actually do with the model, learned
while preparing a migrated model for Copilot after phases 1–8 were already
complete. Mechanics (create hierarchy, update column, update measure) are
`skills-for-fabric/semantic-model-authoring`; the vendor skill's own
`semantic-model-ai-readiness.md` reference covers the full checklist (naming,
descriptions, AI instructions, AI schema, verified answers) — this file is the
execution method for the four TOM-metadata items on that checklist that
involve the most judgment at scale.

**Gate to add to phase 8:** hierarchies exist on every dimension with a
natural drill path; 0 visible numeric columns summed without business
justification; every "family" of similarly-named measures has an
unambiguous, front-loaded routing sentence in its description.

## 1. Building hierarchies

For each candidate hierarchy (typically a date dimension and any dimension
with a natural rollup, e.g. cost-center → department → division):

1. Confirm each level column exists and check `isAvailableInMDX` before
   attempting `Create` (see gotchas: fix this first, not after a failure).
2. Pick the leaf level by checking, not assuming: `DISTINCTCOUNT` of the
   candidate leaf column against total row count. If it isn't unique, check
   whether a sibling "name" column is unique instead; use whichever actually
   satisfies the leaf's uniqueness requirement.
3. Run a non-blocking data-quality check before finalizing multi-level
   hierarchies: does every child in level N roll up to exactly one parent in
   level N-1? (`SUMMARIZE` the child, count `DISTINCTCOUNT` of the parent per
   child, filter for >1). Report violations; build the hierarchy anyway
   unless the user wants to fix the source data first — a hierarchy with a
   few dirty rows is still far better than no hierarchy.

## 2. summarizeBy classification at scale

North star: **no visible numeric column should auto-sum unless the sum has
business meaning.** Patterns are a heuristic starting point, not a rule to
apply blindly — verify against the data before applying at scale, especially
at the boundary:

- **Keep `Sum`:** genuine amounts and counts — currency amounts, quantities,
  countable units (FTE, units delivered/ordered/invoiced).
- **Set `None`:** IDs, sequence/line numbers, codes, date-part numbers
  (year/month/quarter number), rates, percentages, thresholds/limits,
  per-unit multipliers or unit prices, technical/checksum fields.
- **Escalate, don't guess:** when the column is blank in the current extract
  (can't be resolved from data) or the name is genuinely ambiguous even after
  sampling.

Resolve ambiguous names by sampling before deciding, not by pattern alone —
`TOPN(n, VALUES(col))`, `DISTINCTCOUNT`, or `CONCATENATEX(TOPN(...), ..., ", ")`
to batch several columns' samples into one query. This single step resolved
the large majority of ambiguous cases in practice (e.g. a column that reads
like a count but samples as 0/1/-1 is a flag, not a quantity; a column that
reads like a monetary rate but samples as classic multi-year duration values
in whole numbers is an object lifetime, not an additive amount). Only true
name+data ambiguity (e.g. the column is entirely blank in this extract)
should reach the user.

When a literal pattern match conflicts with what the data shows (a column
named like an amount that samples as a small constant status code, or a
column named with a cost/price stem that is actually a per-unit rate), follow
the data and log the override explicitly — don't apply the pattern silently,
and don't apply the override silently either.

## 3. Column descriptions at scale

Copilot reads only the **first ~200 characters** of a description — front-load
the single most useful sentence (preferred usage, disambiguation, unit,
grain). Never write a description for a hidden column; Copilot never sees it,
so the effort is wasted. Generate in three tiers:

1. **Hidden columns:** no descriptions. Skip entirely.
2. **Pattern-generated (bulk):** code/name sibling pairs, calendar-dimension
   columns, status/type columns (sample distinct values with
   `TOPN`+`DISTINCTCOUNT` and list them in the description rather than
   guessing their meaning), fact-table date/timestamp columns tied to a named
   event. Route anything that doesn't cleanly match a rule to a
   needs-review bucket rather than emitting a weak guess — a missing
   description is recoverable, a wrong one is not.
3. **Curated (manual):** the columns that drive the model's core business
   logic (chart-of-accounts hierarchy fields, version/status codes, key
   dates, amount fields) — write these with domain input, not generation.

Mechanically verify the 200-character budget on every generated description
before applying — do not rely on eyeballing it.

## 4. Disambiguating measure-name families

Legacy/migrated models routinely end up with two (or more) measures that
answer a similar question differently — e.g. one that follows whatever date
filter is on the visual, and one pinned to an explicit year/month selection
regardless of visual filter context. Copilot cannot tell them apart from the
name alone, and will pick the wrong one.

1. Identify the families by listing all measures whose name matches the
   ambiguous term (get the live list — measure sets drift between sessions,
   don't rely on an earlier inventory) and grouping by which behavior each
   one actually implements (read the DAX, don't guess from the name).
2. Give each family one short, consistent routing sentence, and put it
   **first** in the description (front-load, per the 200-char budget above).
3. Check whether the routing concept already exists somewhere later in the
   description before adding a new one — if so, move it to the front instead
   of duplicating it.
4. Re-fetch the live measure list at the start of this step even if an
   earlier phase already inventoried it — measures are edited across
   sessions and a stale list produces updates against measures that no
   longer exist under that name, or misses new ones.
