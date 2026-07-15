# Measure corpus pilot

## Result

The 2026-07-14 pilot scanned six public source roots. A pinned manifest verifies
repository commits, licenses, and deterministic hashes of the extracted input
trees; the generated JSON also records manifest and analyzer hashes. This is a
verifiable snapshot, not a fully reconstructible corpus: the temporary roots
were curated sparse extracts, and this delivery does not include their exact
include-path/file manifest or an acquisition script.

- 351 measure instances
- 314 unique normalized DAX expressions
- 25 artifact groups across five measure-bearing sources
- 74 calculation items, 98 calculated columns, 34 calculated tables/partitions,
  and 61 TMDL UDF definitions excluded
- zero read/decode exceptions across 149 recognized candidate files

`artifact_group` is deliberately not called an independent model. The corpus
mixes complete semantic models, alternative serializations, and standalone
measure examples.

## Observed function prevalence

Denominator: 314 unique normalized expressions. The table exposes only a
conservative whitelist of built-in DAX call tokens. Unknown and user-defined
call identifiers are counted but redacted; the current corpus contains 43
redacted unique tokens across 27 unique expressions.

| Token | Unique expressions | Share | Source roots |
|---|---:|---:|---:|
| `CALCULATE` | 140 | 44.6% | 4 |
| `MAX` | 71 | 22.6% | 4 |
| `DIVIDE` | 58 | 18.5% | 4 |
| `IF` | 52 | 16.6% | 4 |
| `HASONEVALUE` | 36 | 11.5% | 3 |
| `DATEADD` | 29 | 9.2% | 2 |
| `SUMX` | 25 | 8.0% | 5 |
| `ALL` | 24 | 7.6% | 2 |
| `SUM` | 21 | 6.7% | 5 |
| `COUNTROWS` | 20 | 6.4% | 3 |

## Observed pattern prevalence

| Pattern | Unique expressions | Share | Source roots |
|---|---:|---:|---:|
| context/filtering | 146 | 46.5% | 4 |
| base aggregation | 137 | 43.6% | 5 |
| time intelligence | 82 | 26.1% | 4 |
| `VAR`-based | 80 | 25.5% | 3 |
| safe ratio (`DIVIDE`) | 58 | 18.5% | 4 |
| conditional logic | 54 | 17.2% | 4 |
| iterators | 43 | 13.7% | 5 |
| selection/filter state | 42 | 13.4% | 3 |

Measure-name proxies found 57 ratio/percent/margin, 54 YTD/MTD/QTD, 50
target/budget/forecast, 28 total/sum, and 21 variance/change/growth expressions.
Names are weak evidence and are never used to infer business meaning alone.

Complexity for unique expressions: median 81 characters, four lines, and two
function calls; 90th percentile 543 characters, 19 lines, and 13 calls.

## Source manifest

| Source | Pinned commit | License/handling | Measures / unique within source |
|---|---|---|---:|
| [`SuperUser-Gump/adventureworks-bi-dashboard`](https://github.com/SuperUser-Gump/adventureworks-bi-dashboard) | `c488693ee8ce7ccbccdf2779866cb9338d73a2ae` | MIT | 41 / 41 |
| [`Mofaji/Agentic-PBIP-Template`](https://github.com/Mofaji/Agentic-PBIP-Template) | `195760f4e863c45337b5fba04beadf46275256a1` | MIT; zero-measure control | 0 / 0 |
| [`microsoft/Analysis-Services`](https://github.com/microsoft/Analysis-Services) | `d3ccb5032c9029b097276b88412f7b61df6e73b8` | MIT | 70 / 56 |
| [`pbi-tools/pbi-tools`](https://github.com/pbi-tools/pbi-tools) | `71681a4542216decc1a4d647fa6c4c56a447990c` | AGPL-3.0; aggregate analysis only | 11 / 5 |
| [`RuiRomano/pbip-demo-agentic`](https://github.com/RuiRomano/pbip-demo-agentic) | `2c573dfeb90a4d9983ebcbc340642a8126597605` | MIT | 15 / 15 |
| [`data-goblin/power-bi-agentic-development`](https://github.com/data-goblin/power-bi-agentic-development) | `7de813c1a531da4f62f3b2fcfaa68a096423be5b` | GPL-3.0 plus conflicting README restrictions; aggregate only | 214 / 212 |

No PBIX file was opened, refreshed, or connected. Raw clones and text extracts
stayed in a temporary folder; no measure names, DAX expressions, or source
artifacts are committed to this skill. Approved public repository labels and
pinned provenance are intentionally present.

## Method

`scripts/analyze_measure_corpus.py` reads `.bim`, `.tmdl`, pbi-tools measure
JSON/DAX, and standalone files named as measure examples. It:

1. verifies every source root against `measure-corpus-manifest.json`;
2. extracts explicit measures and counts excluded object kinds;
3. strips comments only outside protected DAX tokens, normalizes case and
   insignificant spacing in code, and preserves double-quoted strings,
   single-quoted identifiers, and bracketed identifiers exactly;
4. hashes normalized expressions for exact-expression deduplication;
5. emits whitelisted built-in-function, pattern, name-proxy, approved source,
   artifact, co-occurrence, duplicate, and complexity aggregates;
6. redacts unknown/user-defined call tokens and never emits measure names or
   expressions.

## Interpretation limits

- One reference source contributes 212 of 314 unique expressions; SpaceParts
  and SVG/usage examples skew the distribution.
- Public sample repositories underrepresent public-sector finance, governance,
  HR, health, audit, accessibility, and production failure handling.
- Repository stars, gallery views, forks, and post counts do not measure measure
  adoption.
- Exact-expression duplicates are not semantic equivalence, and structurally
  equivalent formulas may remain separate.
- `read_parse_errors: 0` is not proof that every DAX construct was understood.
  The parser recognizes BIM, TMDL, and pbi-tools/standalone measure candidates;
  it is not a complete DAX grammar validator.

Use the phrase **"widespread in this corpus"**, never global popularity. For a
future benchmark, stratify by domain and model family, deduplicate forks and
templates, add structure hashes, and require at least 30 independent models and
100 measures before publishing even a provisional prevalence claim.

Before treating a later corpus as reproducible, add a licensed acquisition
workflow with pinned commits, deterministic include/exclude paths or a complete
file manifest, byte verification, and the exact regenerate command. Until then,
the checked JSON can be regenerated only when the matching temporary snapshot
is still available.
