# MCP modeling gotchas

Operational supplements to `skills-for-fabric/semantic-model-authoring`. These are recurring traps when editing a live semantic model via the modeling MCP — things the generic mechanics docs do not warn about. Not a replacement for that skill.

## Persistence (the expensive one)
- MCP edits the **in-memory** model in the running Desktop instance. Nothing is written to the project (`.pbip`/TMDL) until someone saves.
- Closing/restarting Desktop without saving **loses all MCP work**; the on-disk model reverts to the last save. This can silently discard hours of edits.
- Save (or serialize) after every phase. Do not defer persistence to the end.
- `model_operations ExportTMDL` returns the full live model as text (useful snapshot/verification) but does **not** write the project files — real persistence is the user's save.

## Partial updates & batching
- `measure_operations Update` with only `{name, tableName, displayFolder}` is a **partial** update — it preserves expression/format/description. Safe for bulk folder reorganization.
- Use `Options {ContinueOnError:true, UseTransaction:false}` for bulk create/update to avoid whole-batch rollback.
- Very large batches can fail transiently (relationships above ~15–17; giant single calls). Split into smaller batches.
- `column_operations`/`partition_operations` create/update take `Definitions` (not `columns`); relationship/column delete references use `{tableName, name}` (not `table`).

## The rollback-poison + reconnect fix
- A rolled-back transaction (e.g. a hierarchy `Create` that failed on a name collision with `useTransaction:true`) can poison the engine's impact-analysis baseline. Subsequent deletes then fail with a "base version must not be negative" error and retries do not help.
- **Fix:** `connection_operations` Disconnect + Connect (re-attach to the same DB). Then operations work again. Prefer `useTransaction:false` for batch deletes to avoid the poison.

## IsAvailableInMDX blocks hierarchies and sortByColumn
- Creating a user hierarchy level or setting `sortByColumn` on a column fails if that column has `isAvailableInMDX: false` (attribute hierarchy disabled) — the error differs by call site ("ugyldig kolonne-ID" for sort, "Attributthierarkiet ... er deaktivert" for hierarchy `Create`) but the fix is the same: `column_operations Update {isAvailableInMDX: true}` on the source column in its own call, then retry. This is common on hidden low-cardinality columns (e.g. a hidden `aar`/year column used as a hierarchy's top level) since hiding a column does not by itself disable its attribute hierarchy, but some import paths do.

## Refresh & durability
- Deleting a column only in the model re-adds it on the next refresh. For durable removal, also add `Table.RemoveColumns(..., MissingField.Ignore)` to the M partition.
- Datatype / `summarizeBy` / hide are **pure TOM metadata**: durable, no refresh, no M edit, batchable. They convert the storage type on next refresh but do not revert.
- A merge/partition change fails to refresh with "column X not in the rowset" if the table object columns do not match the M output — fix the table object (drop/create columns) **before** refreshing.
- A calculated column is empty until a `{RefreshType:"Calculate"}` refresh populates it.
- Refresh pulls from the real source (can be heavy) — avoid unnecessary refreshes; metadata edits usually do not need one.

## DMV / query quirks
- `INFO.VIEW.MEASURES()` exposes `[Name]`/`[Table]`/`[DisplayFolder]`/`[Expression]` but **not** a populated `[FormatString]` (returns blank even when the measure has a format) — verify format on disk (TMDL), not via this DMV.
- `INFO.MEASURES()` lacks a friendly display-folder column; use `INFO.VIEW.MEASURES()`.
- `INFO.VIEW.COLUMNS()[IsAvailableInMDX]` can read `True` when the column's real value is `False` — this surfaces as a confusing failure on a later operation (see "IsAvailableInMDX blocks hierarchies/sort", below), not as a wrong-looking read. Verify with `column_operations Get`/`List` (reads TOM directly) whenever a hierarchy or `sortByColumn` operation fails with an unexplained "attribute hierarchy disabled"-style error, even if the DMV says the column should already work.
- `INFO.VIEW.COLUMNS()[SummarizeBy]` can read the **pre-update** value after a successful batch write (the write did commit — confirmed via `column_operations List`). Do not use this DMV to verify a `summarizeBy` change; re-read via `column_operations Get`/`List`.
- `SEARCH(find, text, 1, BLANK())` returns BLANK when not found, and `ISERROR(BLANK())` is FALSE — a `NOT(ISERROR(SEARCH(...)))` "contains" test then matches everything. Use `NOT(ISBLANK(SEARCH(...)))` instead.
- `GROUPBY`'s expression argument must be an aggregate function applied to `CURRENTGROUP()`. A `SUMMARIZE(base, [Col], "N", COUNTROWS(preFilteredVar))` pattern does **not** error — it silently returns the same ungrouped total for every group, which is more dangerous than a hard failure. Use `GROUPBY(filtered, [Col], "N", COUNTX(CURRENTGROUP(), 1))` for a correct per-group count.
- `dax_query_operations` results are capped at 100 rows **on disk, in the returned resource file itself** — confirmed by direct row-count on the CSV with `maxRows` set to both 100 and 500 (both produced exactly 100 data rows). This contradicts an earlier read of this behavior as "not truncated"; treat the 100-row cap as real and version-dependent, and re-verify against your own server build before assuming either way. When more than 100 rows are needed: get an exact per-group count first (`GROUPBY(..., COUNTX(CURRENTGROUP(), 1))`), diff it against what the first capped batch actually returned to find incomplete/missing groups, then fetch those groups explicitly with `[Col] IN {...}`. Do not paginate with a `>= "X"` filter on a name column — it re-includes the boundary group's rows and produces overlap rather than a clean continuation.

## MCP vs TMDL boundary
- Some objects are **not creatable via MCP** — `perspective_operations` is read-only (list/get/export). Perspectives, linguistic synonyms, and native DAX line-formatting must be done in TMDL.
- TMDL editing is only safe when **disk == memory**: have the user save first, then edit the TMDL files, then reload the project (do not save over from Desktop, which would overwrite the file edits). If disk is behind the live model, do everything via MCP instead.
- `discourageImplicitMeasures` is set via `model_operations Update {Definition:{DiscourageImplicitMeasures:true}}`.
