# Measure pattern library

This is a candidate checklist, not a formula catalog. Define each measure from
the decision and grain, then author it through the semantic-model workflow.

## Candidate families

| Family | Typical decision | Required semantic checks | Common failure |
|---|---|---|---|
| base amount/quantity | What happened? | fact grain, sign, currency/unit, additive dimensions | summing balances or mixed currencies |
| distinct entity count | How many entities? | entity key, unknowns, filter scope | counting rows instead of entities |
| average/rate | What is the typical level? | weighted vs unweighted denominator | average of averages |
| ratio/share/margin | How large relative to what? | numerator/denominator, zero/blank policy, sign | implicit division or mismatched filters |
| absolute variance | How far from plan/prior? | baseline version, direction, comparable scope | subtracting non-comparable periods |
| variance percent | How material is the gap? | denominator and zero policy | misleading infinity or wrong baseline |
| target attainment | Are we on track? | target grain, favorable direction, cap policy | mixing percent achieved and remaining |
| period-to-date/prior period | How is the period developing? | marked date table, fiscal calendar, completeness | comparing incomplete and complete periods |
| rolling window | Is the trend stable? | window length, inclusivity, missing dates | accidental partial windows |
| contribution/share of total | What drives the total? | filter-removal scope and hierarchy | removing intended slicers |
| rank/top-N | What needs attention first? | tie policy, population, blank handling | unstable rank across filter states |
| semi-additive snapshot | What was the balance/status then? | snapshot date and last-nonblank rule | summing across time |
| forecast/scenario | What may happen? | version, scenario, horizon, assumptions | presenting scenario as actual |
| freshness/quality/status | Can the evidence be trusted? | timestamp, SLA, completeness, rule owner | decorative status without action |

## Measure specification gate

Before authoring, record:

- stable semantic ID and human name
- business definition and decision served
- numerator/denominator or aggregation rule
- grain and allowed dimensions
- date role, calendar, period, and completeness rule
- filter-removal and relationship behavior
- additive, semi-additive, non-additive, or snapshot classification
- unit, format, favorable direction, target/baseline, and blank/zero policy
- owner, freshness expectation, quality tests, and caveats
- target bindings and fallback representation

## Selection rule

Start from the decision question. Use the corpus to suggest missing families,
then require domain evidence. A frequent function such as `CALCULATE`, `MAX`, or
`DIVIDE` says nothing by itself about whether a measure is valid for a given
model.

For finance/BOTT semantics, pair this library with
`reporting/norms/finance-bi-dax-patterns`, `bott-semantic-model`, and the relevant
domain catalog. For mechanics, use `semantic-model-authoring`; do not paste
unreviewed formulas from galleries.
