---
name: mcp-context-hygiene
description: Enforce narrow, filtered MCP tool calls to prevent context/cost blowup in long agent sessions. Use whenever calling ANY MCP server's tools (not just Power BI/Fabric) — before List/Get/Export/Query-style operations, when working alongside semantic-model-authoring, semantic-model-consumption, or any skill layering on MCP mechanics, and in any long session doing repeated MCP round-trips. Triggers: MCP tool, MCP server, List operation, Get operation, ExportTMDL, unfiltered query, full schema dump, context usage, token budget, large tool result, "list all tables/measures/columns".
---

# MCP Context Hygiene

Tool call *results* land in the conversation's message history and stay there
for the rest of the session — they are not shrunk by summarizing them
afterward. An unfiltered `List` call across many objects sits in context at
full size regardless of how briefly it is described in the reply that follows.

## MUST

- Before any List/Get/Export-style MCP call, scope it: filter by name/table/
  folder, cap the result count, or request a single named object. Never call
  "list everything" as the default.
- Use a narrower existence/name check ("Find"-style) instead of a full-object
  listing when the task only needs to confirm something exists or get a count.
- Extract the answer (count, verdict, specific value) from a large result
  immediately, in the same turn, and do not re-fetch the same data again later
  in the session "to double check" — re-use the earlier extraction instead.
- Route anticipated large exports (whole-model/schema dumps) through a
  mechanism that offloads to a file, then pull only the needed slice via
  grep/script. Do not read a full large export into working context "to be
  safe."

## AVOID

- Calling `List`/`Get` with no filter as a default habit, even when a
  narrower call answers the same question.
- Requesting full descriptive detail (all properties/descriptions) when only
  a name or count is needed for the current step.
- Treating "the result was useful" as justification for having fetched more
  than the task needed — usefulness does not offset cost.

## Escalation ladder for data (not just metadata)

Row-level data reads are allowed — this skill does not ban them — but they
are never the first move.

1. **Metadata/schema first.** Table, column, measure, relationship listings;
   counts; aggregates. Almost every question ("does X exist", "how many
   rows", "which tables reference Y") is answerable here.
2. **Sampled/aggregated queries next**, if metadata alone cannot answer it —
   `TOPN`, `DISTINCTCOUNT`, `GROUP BY`-style summaries. Still not full rows.
3. **Row-level reads, only once 1–2 are tried and insufficient.** Escalating
   straight to raw rows as a first attempt is the failure mode this skill
   exists to prevent, not row-level access itself.
4. **When row-level reads are genuinely needed:** prefer a script/query that
   writes results to a file over an inline dump into the conversation, then
   extract only the needed slice via grep/read-with-offset. After a large
   pull like this, consider whether the session is at a natural point to
   compact context (`/compact` or equivalent) rather than carrying the full
   result forward for the rest of the session.

## Why this is a hard rule, not a preference

Verified in a live session (2026-07-08, Power BI semantic-model work):
unfiltered MCP `List`/`Export` calls (a full measure list with descriptions,
repeated full table listings) drove the conversation's message-history
context to 337.9k/967k tokens (34.9%) in a single session — while the MCP
tool *schemas themselves* cost a flat, fixed amount regardless of call
volume. Schema cost does not grow with usage; unfiltered call results do,
and never shrink back once returned.

## Scope note

Orthogonal to `semantic-model-consumption`'s "use `INFO.VIEW.*` before data
queries" rule (DAX-query-specific, lives in `skills-for-fabric`, not
duplicated here). This skill covers MCP tool-call scoping generally — across
any MCP server, including `semantic-model-authoring`'s own table/measure/
relationship/column operations, which are not DAX queries and are not
covered by the consumption skill's pointer.
