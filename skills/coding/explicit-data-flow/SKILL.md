---
name: explicit-data-flow
description: Write, rebuild or review table-transformation code (Spark, pandas or SQL notebooks, medallion layers, ETL scripts) as explicit straight-line data flow with one section per output table, literal source and output, and business rules placed where they are used. Use when the user asks for readable transformations, ombygging, less indirection, fewer config dicts, or says "kode er billig, eierskap er dyrt". Not for application or library architecture, and never a reason to drop correctness guards.
---

# Explicit Data Flow

Code is cheap, ownership is expensive. The owner must be able to read every
table from source to output without tracing a loop, a configuration object or
a helper whose behaviour depends on the table name. An abstraction is allowed
only when it pays for itself in a measured saving or a removed defect, never
in fewer lines.

## The reader test

Pick any output table. Reading one section top to bottom, the reader answers:

1. Where do the rows come from, and at which version or filter?
2. Which rows are kept?
3. Which columns are selected, renamed or derived, and by which rule?
4. Which checks apply, and what stops the run?
5. Where is it written, in which mode, with which partition?

If answering needs a second place in the file, that is a finding. Count the
places per table when reviewing; more than two is a defect.

## Rules

1. **One section per output table**, in build order. The heading is the table
   name. Dependencies sit above their users.
2. **Source and output are literal** inside the section: the read at the top,
   the write at the bottom, both with the table name spelled out. No output
   name derived from string splitting, suffix stripping or prefix tests.
3. **Name an intermediate when it has business meaning**: `regnskap`,
   `regnskap_med_koder`, `budsjett_med_versjon`. Not `df2`, `tmp`, `out`.
4. **Column choices and business rules live in the section that uses them.**
   A column list for one table sits in that table's section, not in a
   cross-table dict keyed by table name.
5. **No dispatch on table name.** No `if table_name == ...`, no
   `rules[table_name]`, no `kind` or `slag` discriminator, no behaviour from
   a name prefix. Two tables needing the same operation call the same
   function twice with explicit arguments.
6. **Transformations in natural order**: filter, select and rename, join
   lookups, derive, check, write. The order a person would describe it.
7. **Guards are part of the flow.** Call `require_unique(...)` right after
   the step that can break uniqueness, inside the section. Do not centralise
   checks in a `check_configuration()` that validates dicts.
8. **No metaprogramming.** No `getattr`, `globals()`, generated expressions
   from name patterns, decorators, registries or builder dicts.

## What shared code may look like

Shared functions are mechanics that are identical for every caller and carry
no per-table branch: read at a locked version, write with a mode, unique
check, reconciliation, status row. Each takes its inputs as arguments, does
one thing, has a verb name, and stays short enough to read in one screen.
A function that takes `table_name` and looks something up with it is a
dispatcher, not a mechanic.

Inline versus extract: if inlining costs at most five lines and at most three
copies, inline. Extract only identical mechanics. An extraction justified by
efficiency must state the measured saving in a comment; an unmeasured
efficiency claim does not buy indirection.

## Loops

A loop is allowed for uniform work: every iteration is the same operation on
the same shape, and the body has no branch on which table it is. The list it
iterates is a literal directly above it. The moment one table needs a
different operation, it leaves the loop and gets its own section.

Per-table rule blocks are acceptable inside such a loop when all three hold:
every rule is a column list consumed by the same uniform step, all rules for
a table sit together in one block, and the loop body has no table-name
branch. Ten dicts each keyed by table name, where one table's rules are
spread across all ten, is the pattern this skill removes.

## Rollback, locking and status

Run-level mechanics stay in one clearly marked run section as straight-line
code: lock sources, remember previous versions, try the sections in order,
reconcile, write status, on failure restore. When every table must be written
under one rollback, write each table section as a function named for the
table, body straight-line, and call them in an explicit ordered list in the
run section. One level of indirection, named, no dispatcher.

## Example

Before, the reader visits `bygg`, `fakta`, `build_fact`, `fakta_koder`,
`with_natural_keys` and `write_gold` to learn what `fak_regnskap` is:

```python
fakta = {"fak_regnskap": {"kilde": "regnskap", "nye_navn": {...}, "fjern": [...], "datoer": [...]}}
for table_name in bygg:
    if table_name in fakta:
        df = build_fact(table_name)
```

After, one section answers all five questions:

```python
# ## fak_regnskap
def bygg_fak_regnskap():
    regnskap = silver("fak_okonomi").where(F.col("kilde") == "regnskap")
    regnskap = regnskap.drop("kilde", "belop_budsjett", "belop_valuta_budsjett", "timer_budsjett", ...)
    regnskap = (regnskap.withColumnRenamed("belop_regnskap", "belop")
                        .withColumnRenamed("belop_valuta_regnskap", "belop_valuta")
                        .withColumn("bilagsdato", F.col("bilagsdato").cast("date")))
    # Naturlige nøkler fra dimensjonene. Surrogatene slippes etterpå.
    regnskap_med_koder = with_code(regnskap, gold("dim_konto"), "zk_dim_konto", "konto_kode")
    regnskap_med_koder = with_code(regnskap_med_koder, gold("dim_koststed"), "zk_dim_koststed", "koststed_kode")
    require_all_matched(regnskap_med_koder, ["konto_kode", "koststed_kode"], "fak_regnskap")
    fak_regnskap = regnskap_med_koder.drop(*[c for c in regnskap_med_koder.columns if c.startswith("zk_dim_")])
    return write_gold(fak_regnskap, "fak_regnskap", partition="periode_aar")
```

## Rebuild procedure

1. **Inventory the contract.** For every output table, from the existing
   dicts and dispatcher: source, filter, columns kept, renames, derived
   columns, checks, write mode and partition. This is the behaviour to keep.
2. **Write each section from the inventory.** Behaviour identical unless the
   review listed a defect, and then the change is named in the report.
3. **Keep only mechanics.** Move them to one short cell near the top. Delete
   config dicts, dispatchers, discriminators and the functions that validated
   them.
4. **Prove equivalence** on a fixture: same columns and types, same rows,
   same guards firing with the same messages. Rewrite tests to call sections
   and mechanics directly; tests of the removed configuration layer are
   removed with it.

## Review procedure

For each output table, count the places visited to answer the reader test.
List every dispatcher, dict keyed by table name, name-derived behaviour, loop
with a per-table branch, helper with a hidden lookup, and configuration
validator. Report per table: places visited, the hidden rule, the proposed
section. Say which guards must survive the rebuild.

## Completion report

- Tables and their sections. Source lines before and after, reported, not
  targeted.
- Shared functions kept, each with its justification.
- Behavioural differences, expected none unless a listed defect was fixed.
- Test evidence: which tests ran, on which runtime, what remains unverified.

Related: [readable-python-code](../readable-python-code/SKILL.md) for style,
naming and comment voice in the same notebooks.
