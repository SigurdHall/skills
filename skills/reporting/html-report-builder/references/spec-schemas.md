# HTML Report Builder Spec Schemas

Use these compact schemas as the starting point. Add fields only when the report needs them.

## `report.yaml`

```yaml
id: monthly-variance
title: Monthly Variance
purpose: Controller review of budget variance.
audience: Controller
data_contract: data_contract.yaml
output: monthly-variance.html

queries:
  summary:
    sql: sql/summary.sql

visuals:
  - id: variance-table
    title: Variance by unit
    type: table
    query: summary

evaluation:
  required_checks:
    - validate
    - render
```

Required top-level fields:

| Field | Meaning |
|---|---|
| `id` | Stable report identifier. |
| `title` | Human-readable title used in the HTML report. |
| `purpose` | Decision, review, or communication need the report supports. |
| `audience` | Primary reader or role. |
| `data_contract` | Relative path to `data_contract.yaml`. |
| `output` | Output HTML filename. |
| `queries` | Named SQL files. |
| `visuals` | Visual blocks bound to named queries. |
| `evaluation` | Checks required before completion. |

Current visual support:

| Type | Notes |
|---|---|
| `table` | Renders all rows/columns returned by the named query. |

## `data_contract.yaml`

```yaml
datasets:
  okonomi:
    path: data/okonomi.csv
    format: csv
    sensitivity: internal
    owner: Finance
    snapshot_date: "2026-06-15"
    columns:
      enhet: string
      regnskap: number
      budsjett: number
```

Required dataset fields:

| Field | Meaning |
|---|---|
| `path` | Relative path to local CSV or Parquet snapshot. |
| `format` | `csv` or `parquet`. |
| `columns` | Expected columns and simple types. |

Recommended dataset fields:

| Field | Meaning |
|---|---|
| `sensitivity` | Public/internal/confidential or local convention. |
| `owner` | Business/data owner. |
| `snapshot_date` | Date the local data snapshot was produced. |
| `checksums` | Manual or tool-produced totals for reconciliation. |

## SQL Rules

- Use table names matching dataset keys.
- Keep calculations in SQL, not YAML.
- Return stable column names suitable for display.
- Add comments for non-obvious business rules.
