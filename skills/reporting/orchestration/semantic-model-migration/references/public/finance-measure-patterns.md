# Finance / BOTT measure patterns

Domain-specific measure patterns discovered during a public-sector finance (BOTT / UiT) semantic-model migration. Patterns only — concrete account codes, version codes, and source paths are project data (`references/private/` or the project repo). Pair with `norms/finance-bi-dax-patterns`, `norms/bott-semantic-model`, `norms/uit-bott-okonomimodell`.

## Sign convention: keep source sign, classify by account type
- Keep the ledger's source sign; classify by **account type**, not by debit/credit. A credit on a cost account is a reversed cost, not income.
- Income (credit) stays negative, cost (debit) positive, unless a report explicitly flips income for presentation. Decide the flip once, at the report layer, not per measure.

## Canonical `[Regnskap]`: operational base excludes balance accounts
- The operational P&L base (`[Regnskap]`) excludes balance-sheet, settlement, and interim accounts via a curated exclusion set (`CALCULATE([raw], KEEPFILTERS(FILTER(ALL(dim_konto[code]), NOT CONTAINSROW(exclusions, code))))`).
- Keep a separate unfiltered `[... totalt]` for ledger reconciliation, and a hidden raw `SUM`.
- The exclusion typically resolves most of an apparent "unclassified" residual (those rows are balance accounts that were never meant to be in operational follow-up).

## Chart-of-accounts hierarchy drives result areas
- Use the account-relation hierarchy (not raw class/group numbers) for the income/cost/net split. The relation code (e.g. income/cost/net) filters the totals: `CALCULATE([... total], KEEPFILTERS(dim_konto[relation_code] = "<code>"))`.
- Rewrite any legacy class/group-based logic onto this hierarchy.

## Budget version = dynamic code + as-of, never literal `LEFT()`
- The applicable ("gjeldende") budget version is a **dynamically constructed code** for the selected year (`"<FAMILY>" & FORMAT([Valgt År],"0")`), plus an **as-of date cutoff** on transaction date — not a `LEFT(code, n)` prefix match or a literal equality.
- Approved ("godkjent") version appends a milestone suffix; different budget families (appropriation vs external-funded) use different family codes and different project-type filters.
- Version code encodes family + year + milestone/revision suffix; a transaction-type marker flags the base version per family/year.

## Provisions / carryover: opening balance is period month-00
- Balance-account provisions are stored as an **opening balance on period month 00** (`year*100 + 0`) **plus** monthly movement. The cumulative year-end balance = months 00–12, i.e. filter `period >= year*100` (include month 00) — not `>= year*100 + 1` (which captures only the movement and misses the opening balance).
- This is a data-representation trap: always inspect the actual periods on the balance accounts before choosing the window.
- Result-disposition accounts (year-result → provisions) are a **separate** account from the balance provisions — do not fold them into the balance total.

## Publishing-date snapshot ("hittil valgt måned")
- Period-to-date measures pinned to a selected year/month use a publishing cutoff: only rows updated by the publishing date (day-N of month+1) are included, so the figure reflects the ledger as published, not later corrections. Expect the as-of snapshot to differ from the final restated figure.
- This produces **two "period-to-date" measure families that look interchangeable but aren't**: one follows whatever date filter the visual applies (standard time-intelligence, e.g. `TOTALYTD`), the other is pinned to an explicit year/month selection independent of visual context (built from the publishing-cutoff logic above). Copilot and new report authors alike will pick the wrong one from the name alone — disambiguate both families' descriptions explicitly (see [ai-readiness.md](ai-readiness.md) §4) rather than relying on naming convention to carry the distinction.

## Organizational hierarchy on the cost-center dimension
- The cost-center/department dimension typically carries a full org rollup (e.g. faculty/division → institute/department → sub-unit → cost center) as sibling text columns even when no user hierarchy has been built on them — check for this before assuming a hierarchy needs new columns, not just a `Create` call.
- Pick the leaf level by uniqueness, not by which column looks most complete: the "coded name" column (code + name combined) is often unique across the full grain where the plain name column has a handful of duplicates.
- Validate the rollup is clean before finalizing (every child rolls up to exactly one parent) — report violations but build the hierarchy regardless; a few dirty rows do not justify skipping it.

## Year-end forecast
- `Årsprognose = actuals-to-date + remaining-year budget`; at month 12 the remaining budget is 0, so forecast equals actuals. Split by result area and segment mirrors the base measures.

## Data-availability caveats (test extracts)
- Budget rows, external-funded project types, and staffing/FTE data are often **absent** in a test/gold extract. Measures on them are structurally correct but blank — validate by evaluation, not value. Staffing measures may require a separate HR/DBH source not present in the finance gold model; defer them.
