---
name: finance-bi-dax-patterns
description: Write, review, debug, or explain finance BI DAX measures and Power BI semantic model patterns. Use when the user asks for DAX, measure, budsjett/regnskap/prognose, avvik, prosentavvik, finance dashboard calculations, bullet chart axis scaling, blank category handling, Sum1-Sum5 drilldown, common maximum calculations, Norwegian public-sector finance reporting terms, or why a Power BI finance measure behaves wrong.
---

# Finance BI DAX Patterns

Use this for DAX work in finance/accounting Power BI models.

## Principles

1. Separate visible business measures from helper measures used for scale, axis, filters, or visual behavior.
2. Preserve external slicers such as period, organization, project, and funding unless the user explicitly asks to ignore them.
3. Be explicit about hierarchy filters when working with drilldown fields.
4. Use `ABS()` only when the visual needs comparable magnitudes; do not change accounting signs unless intended.

## Common Terms

Norwegian finance BI terms often map as:

- `Regnskap hittil i år`: actuals year to date
- `Budsjett hittil i år`: budget year to date
- `Årsbudsjett`: annual budget
- `Prognose` / `Årsprognose`: forecast
- `Avvik`: variance
- `Restbudsjett`: remaining budget
- `Nettobidrag`: net contribution
- `Avsetninger`: provisions/reserves depending on context

## Bullet Chart Common Axis

When a bullet chart must have comparable axes across categories, create a helper maximum measure. It should:

- Iterate over the intended comparison grain, often `Sum1`.
- Remove the visual's category/drill filters, often `Sum1` to `Sum5` and `Konto_tekst`.
- Reapply the iterated grain.
- Return `BLANK()` for blank category members.
- Be placed in the visual's `Maximum` field and colored white/transparent if necessary.

Pattern:

```DAX
VAR Sum1Categories =
    FILTER(
        CALCULATETABLE(
            VALUES('Dim'[Sum1]),
            ALLSELECTED('Dim'),
            REMOVEFILTERS('Dim'[Sum1]),
            REMOVEFILTERS('Dim'[Sum2]),
            REMOVEFILTERS('Dim'[Sum3]),
            REMOVEFILTERS('Dim'[Sum4]),
            REMOVEFILTERS('Dim'[Sum5]),
            REMOVEFILTERS('Dim'[Konto_tekst])
        ),
        NOT ISBLANK('Dim'[Sum1])
    )
VAR CommonAxisMaximum =
    MAXX(
        Sum1Categories,
        VAR CurrentSum1 = 'Dim'[Sum1]
        VAR CurrentSum1Filter =
            FILTER(ALL('Dim'[Sum1]), 'Dim'[Sum1] = CurrentSum1)
        VAR Actuals =
            ABS(
                CALCULATE(
                    [Regnskap hittil],
                    REMOVEFILTERS('Dim'[Sum1]),
                    REMOVEFILTERS('Dim'[Sum2]),
                    REMOVEFILTERS('Dim'[Sum3]),
                    REMOVEFILTERS('Dim'[Sum4]),
                    REMOVEFILTERS('Dim'[Sum5]),
                    REMOVEFILTERS('Dim'[Konto_tekst]),
                    CurrentSum1Filter
                )
            )
        VAR BudgetYtd = ABS(CALCULATE([Budsjett hittil], CurrentSum1Filter))
        VAR AnnualBudget = ABS(CALCULATE([Årsbudsjett], CurrentSum1Filter))
        VAR Forecast = ABS(CALCULATE([Prognose], CurrentSum1Filter))
        RETURN MAX(MAX(Actuals, BudgetYtd), MAX(AnnualBudget, Forecast))
    )
VAR IsBlankCategory =
    (
        HASONEVALUE('Dim'[Sum1])
            && ISBLANK(SELECTEDVALUE('Dim'[Sum1]))
    )
RETURN
    IF(IsBlankCategory, BLANK(), CommonAxisMaximum)
```

Adapt every `CALCULATE` consistently. If only one variable removes hierarchy filters, blank or row-specific behavior can leak back into the visual.

## Blank Categories

If `(blank)` appears:

1. Check whether the dimension column actually has blanks.
2. Check for unmatched fact rows that create Power BI's automatic blank relationship member.
3. Check whether a helper measure returns non-blank for blank category context.
4. Add `BLANK()` logic to helper measures or a visual filter such as `is not blank`.

With field parameters, `ISINSCOPE()` may not catch the active blank member reliably. Prefer explicit checks using `HASONEVALUE()` and `SELECTEDVALUE()` for each possible drill field.

## Validation

- Add the helper measure to a table with the category hierarchy to confirm one common maximum.
- Drill `Sum1` to `Sum5` and confirm the maximum remains common where intended.
- Confirm blank categories disappear or show no value.
- Compare against a grouped bar chart if the goal is matching axis length.
