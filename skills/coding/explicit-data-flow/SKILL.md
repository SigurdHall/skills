---
name: explicit-data-flow
description: Write, rebuild or review table-transformation code (Spark, pandas or SQL notebooks, medallion layers, ETL scripts) as straight-line top-level chains, one per output table, with the read at the top, the write at the bottom, checks inline and no helper functions. Use when the user asks for readable transformations, ombygging, straight-line code, less indirection, fewer config dicts, or says "kode er billig, eierskap er dyrt". Not for application or library architecture, and never a reason to drop correctness checks.
---

# Explicit Data Flow

Code is cheap, ownership is expensive. The owner must be able to read every
table from source to output in one place, top to bottom, without entering a
function, following a loop, or opening a configuration object. Repeated code
is the accepted price. An abstraction is allowed only when it pays for itself
in a measured saving, never in fewer lines.

## The shape

One output table is one chain at top level, named for the table:

```python
# ## fak_regnskap
fak_regnskap = (
    spark.read.option("versionAsOf", silver_lock["fak_okonomi"]).table("lh_okonomi.silver_okonomi.fak_okonomi")
    .filter(F.col("kilde") == "regnskap")
    .drop("kilde", "belop_budsjett", "belop_valuta_budsjett", "timer_budsjett", "dato_fra", "dato_til")
    .withColumnRenamed("belop_regnskap", "belop")
    .withColumn("bilagsdato", F.col("bilagsdato").cast("date"))
    .join(dim_konto.select("zk_dim_konto", "konto_kode"), "zk_dim_konto", "left")
    .join(dim_koststed.select("zk_dim_koststed", "koststed_kode"), "zk_dim_koststed", "left")
)
# Stopper ved faktarader uten dimensjonstreff. Ukjent-raden -1 er et treff.
if fak_regnskap.where(F.col("konto_kode").isNull() | F.col("koststed_kode").isNull()).first():
    raise ValueError("fak_regnskap: faktarader uten dimensjonstreff.")
fak_regnskap = fak_regnskap.drop("zk_dim_konto", "zk_dim_koststed")
(fak_regnskap.write.format("delta").mode("overwrite").option("overwriteSchema", "true")
    .partitionBy("periode_aar").saveAsTable("gold_okonomi.fak_regnskap"))
```

Reading it answers, in order: where the rows come from and at which version,
which rows are kept, which columns are chosen, renamed and derived, which
lookups apply, what stops the run, where it is written and how. Nothing else
in the file is needed.

## Rules

1. **One chain per output table, at top level**, in build order, under a
   heading with the table name. No `def` around it.
2. **No helper functions in the notebook.** Reads, transformations, checks
   and writes are written out where they happen. A check is two or three
   lines after the chain: a filter or a groupBy, an `if`, a `raise` with the
   table name in the message. If the same check appears in twenty sections,
   it appears twenty times.
3. **Literal names everywhere.** The table read, the table written, the
   partition column, the join keys, the columns dropped. No name built from a
   prefix, a suffix, a string split or a dict lookup; `drop` lists the columns
   instead of matching `startswith`.
4. **Business rules sit in the chain that uses them.** A drop list, a rename,
   a date cast, a lookup belong to one table and are written in that table's
   chain, not in a cross-table dict. The one exception is the rule block of a
   uniform loop, defined under Loops; that block is the table's section.
5. **No dispatch on table name.** No `if table_name == ...`,
   `rules[table_name]`, kind flags or registries.
6. **Natural order inside the chain**: read, filter, select and rename,
   derive, join lookups, then checks, then write.
7. **Name an intermediate only when it carries business meaning** and is
   used again: `regnskap`, `budsjett_med_versjon`. Otherwise keep chaining.
8. **Comments are short working notes** on the line above the step they
   explain: why a column is dropped, why a check exists, which order matters.

## Loops

A loop is allowed for uniform mechanics that are identical for every item
and carry no per-item branch: locking a list of source tables at their
confirmed version, applying the same cleaning to a list of look-alike tables
with a rule block each, resolving where snapshot rows live for a list of
tables. The loop body is written out inline like any chain. The list it
iterates is a literal directly above it. A table that needs anything the
loop body does not do leaves the loop and gets its own chain.

A rule block inside such a loop is that table's section: all of its rules
(key, drops, casts, renames) in one dict literal, consumed in the same order
for every table. Ten dicts keyed by table name with one table's rules spread
across them is the pattern this skill removes.

## Failure and rollback

Do not wrap chains in functions to get a `try/except` around them. Each Delta
overwrite is atomic on its own; a failure stops the notebook at the failing
cell and leaves earlier tables written and later ones from the previous run.
Handle that outside the chains: write the status row last, and add a small
separate restore notebook as the next pipeline step that puts every table
back to the version it had at the last status write, drops tables created
after it, and does nothing after a successful run. A check that must not
leave a bad table visible does the same inline: note the version before the
write, and after a failed check restore or drop, then raise. Writing several
tables from one final cell is not atomic either; if readers must never see
mixed versions, that needs a publication pointer, not a staging schema.

## Rebuild procedure

1. **Inventory the contract** per output table from the old code: source and
   version, filter, columns kept, renames, derived columns, checks with their
   messages, write mode and partition. That is what must survive.
2. **Write each chain from the inventory.** Behaviour identical unless the
   review listed a defect, and then the change is named in the report.
3. **Delete every function, dispatcher, and dict that spreads one table's
   rules over several places or selects a code path.** Inline what they did,
   where it is used. Keep a loop only for uniform mechanics; its rule blocks
   stay.
4. **Prove equivalence** on a fixture: same columns and types, same rows,
   same checks firing with messages the tests match. Tests run the cells in
   order and inject failures between cells; tests of removed mechanics such
   as configuration validation or rollback are removed with them.

## Review procedure

For each output table, count the places a reader must visit to answer the
questions under The shape. More than one is a finding. List every function,
dict keyed by table name, name-derived behaviour, loop with a per-table
branch and configuration validator. Report per table: places visited, the
hidden rule, the proposed chain. Say which checks must survive.

## Completion report

- Tables and their chains. Source lines before and after, reported, not
  targeted.
- Loops kept, each with the uniform mechanic it covers.
- Behavioural differences, expected none unless a listed defect was fixed.
- Test evidence: which tests ran, on which runtime, what remains unverified.

Related: [readable-python-code](../readable-python-code/SKILL.md) for style,
naming and comment voice in the same notebooks.
