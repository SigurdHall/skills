---
name: agent-work-order-handoff
description: Use when delegating a complex, judgment-heavy task to a cheaper/different model, a background sub-agent, or a future session — writing a self-contained work order that preserves intent across the handoff, deciding what to background vs keep in the main thread, resuming an interrupted delegate, and receiving/consuming a handoff written by another agent or tool. Triggers: write a work order, delegate to a cheaper model, hand off to Sonnet/Haiku, spec for a subagent, background an independent task, resume an interrupted agent, cross-session handoff, multi-agent delegation, receive a handoff, locate a chat log/session transcript, cross-tool handoff (Claude Code/Codex/Copilot).
---

# Agent Work-Order Handoff

The receiving agent (a different model, a subagent, a future session) shares
none of your context. A short task description loses the *why*; the receiver
either re-derives it (slow, sometimes wrong) or executes the letter of the
instruction past the point where it stops making sense. A work order is a
self-contained document that survives the handoff.

## What a work order needs

1. **Intent** — why this work matters and what it's part of, in 1–3
   sentences. Not "do X" but "X because Y, so when in doubt prefer Y."
2. **Principles to preserve** — the constraints that must survive even where
   the literal task description doesn't cover a case (don't guess domain
   facts, don't touch objects outside a named boundary, escalate rather than
   assume). State these before the tasks, not buried inside them.
3. **Setup/connection procedure** — exactly how to reach the resource being
   worked on, including how to pick the right one when several similar
   candidates exist (name matching, not positional assumption).
4. **Known pitfalls** — every gotcha you already hit, as a symptom → fix
   table. This is the highest-leverage section: it is pure rediscovery cost
   avoided. Update it as new pitfalls surface, even mid-task.
5. **Working pattern** — the loop the delegate should run per unit of work
   (typically: pull real state → act → verify against real state → report),
   stated once so it doesn't need repeating per task.
6. **Precise per-task rules** — concrete decision criteria (classification
   buckets, exact thresholds, naming templates), not vague direction. Where
   real judgment is required, say so explicitly and give an escalation path
   instead of pretending a rule covers it.
7. **End procedure** — what "done" looks like: verification steps, what to
   remind the human of (e.g. persistence/save steps the delegate cannot do
   itself), and how to report deviations.
8. **Source reference** — the originating tool, session id (or human-readable
   thread/chat title), and file path if known. Lets the receiver — another
   agent, a future session, or the human — locate the original conversation
   when the work order's summary doesn't cover something. See "Locating
   source chat logs" below for where each tool stores these.

## Locating source chat logs

Every major agent tool persists its own session transcripts locally. Citing
the source session in a work order lets anyone go back to the original
conversation instead of re-deriving context from a summary alone. Don't read
a full log into context to do this — these files commonly run into single-
or double-digit MB — grep for a keyword/date, or use the lightweight index
where one exists.

- **Claude Code** —
  `%USERPROFILE%\.claude\projects\<sanitized-cwd>\<session-uuid>.jsonl`
  (`<sanitized-cwd>` is the working directory path with separators/drive-colon
  replaced by `-`, e.g. `C:\repos` → `c--repos`). One JSONL file per session,
  named by session UUID. Large offloaded tool outputs live alongside it in
  `<session-uuid>/tool-results/`. No separate title index — use file mtime,
  or grep the first lines for the initial user message, to identify a
  session.
- **Codex CLI** —
  `%USERPROFILE%\.codex\sessions\YYYY\MM\DD\rollout-<timestamp>-<session-id>.jsonl`.
  Check the lightweight index at `%USERPROFILE%\.codex\session_index.jsonl`
  first — one line per session with `id`, human-assigned `thread_name`, and
  `updated_at` — to find the right session id/date before opening a rollout
  file.
- **GitHub Copilot Chat (VS Code)** —
  `%APPDATA%\Code\User\workspaceStorage\<workspace-hash>\chatSessions\<session-uuid>.jsonl`.
  Find `<workspace-hash>` by checking `workspace.json` in each
  `workspaceStorage\*` folder for the target path (e.g.
  `{"folder":"file:///c%3A/repos"}`). Each session file's first record has a
  `customTitle` (the human-readable chat name) and `sessionId`.

## Deciding what to background vs. keep sequential

- **Background it** when the sub-task is read-only, or writes to a new/
  independent artifact that nothing else touches. Concurrent reads (or reads
  alongside foreground writes) are safe; concurrent writes to the same shared
  live resource are not.
- **Keep it in the main thread, sequential** when the sub-task writes to the
  same stateful shared resource the main thread is also editing — two
  connections issuing writes against the same live object can race or
  transaction-poison each other. Don't parallelize writes just because the
  tasks are logically separable; check whether they share a write target.
- Ask "is this independent and non-conflicting?" **before** starting a
  multi-step task, not partway through — it's a planning decision, not an
  afterthought.

## Resuming an interrupted delegate

If a background delegate stops mid-task for a reason unrelated to the task
itself (a transient quota/session limit, an infra hiccup), resume it by
messaging its existing identity rather than restarting fresh. A resumed agent
keeps its transcript and partial progress; a fresh one re-derives everything
already done and can silently duplicate or skip work.

## Receiving a handoff

The receiver's job is to end up talking about the same thing the sender was —
not just executing the same task description in isolation.

- Keep the source reference (tool, session id/title, path) as given — don't
  discard it once work starts. If you produce your own handoff later
  (chained delegation, or reporting back to the human), carry the same
  reference forward instead of inventing a new one, so the chain stays
  traceable back to the original conversation even across tools (e.g. a
  Claude Code session handing off to Codex or Copilot).
- If the work order's summary leaves a real question unanswered — a
  decision's rationale, an exact value, why an option was rejected — look it
  up in the referenced source log before guessing. Grep for a keyword or date
  range rather than reading the whole file.
- If the human refers to "that session" / "what we discussed earlier" by
  title rather than id, resolve it via the relevant index (Codex's
  `session_index.jsonl`, Copilot's `customTitle` field, Claude Code file
  mtimes) before assuming it's inaccessible.
- If something in the work order conflicts with what the source log actually
  shows, say so explicitly rather than silently trusting either one — this is
  a deviation to log, per Guardrails below.

## Guardrails

- Instruct the delegate to **log every deviation from the literal spec**,
  with the reason — both overrides ("the pattern said X, the data showed Y,
  I did Y") and open questions it couldn't resolve. Silent compliance with a
  wrong literal rule and silent judgment calls are both worse than a visible,
  reasoned deviation.
- Don't over-specify to the point of removing useful judgment. A sharp set of
  principles plus concrete rules for the common cases, with an explicit
  escalation path for the genuinely ambiguous ones, outperforms an attempt to
  enumerate every case in advance.
- Re-fetch live state at the start of delegated work even if an earlier
  phase already inventoried it — the resource may have changed since, and a
  stale inventory produces confidently wrong actions.
