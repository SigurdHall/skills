# Cross-target semantic parity

Semantic parity needs executable evidence, not only a shared prose definition.
Use `assets/parity-scenarios.example.json` as an illustrative synthetic package
and create a project-owned package with the approved domain conventions.

## Required target adapters

Run the same named cases through:

1. the Power BI/DAX measure layer or a DAX test query;
2. pure React/TypeScript view-model or selector calculations;
3. the SQL/query calculation used by the HTML report.

Normalize decimals, currency/unit, blank/null, status codes, and rounding before
comparison. Target requests must name the repository-specific command that runs
each adapter test and the command that compares all outputs.

## Minimum finance scenarios

- actual versus baseline for cost and revenue direction
- absolute and percentage variance
- zero baseline/denominator
- incomplete period status
- driver contribution reconciliation and explicit residual
- blank/missing input where the domain permits it

The example fixes one convention solely for reproducibility:

- variance amount = actual - budget
- variance percent = variance / absolute budget, or null when budget is zero
- a non-positive cost variance is favorable; a non-negative revenue variance is
  favorable
- driver residual = variance - sum(driver contributions)

Replace these conventions only through an explicit versioned domain decision;
never let each target choose independently.

## Evidence levels

- `parity-tested-synthetic`: all target adapters pass shared synthetic cases.
- `parity-tested-connected-sampled`: sampled/aggregated connected queries also
  match certified expectations.
- `parity-tested-connected-live`: approved live connections and representative
  scenarios match; record dataset/model revision and timestamp.

Synthetic parity proves calculation alignment, not data-source correctness,
refresh behavior, security, or production readiness. Keep it separate from
actual render and live-data evidence.
