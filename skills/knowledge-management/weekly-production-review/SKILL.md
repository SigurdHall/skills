---
name: weekly-production-review
description: On-demand weekly rollup of the past 7 days of production (pushes + accomplishment-log entries) into a Summary note with per-item comments and an overall meta-comment. Not scheduled/automatic yet — invoked manually. Not a full-career summary (see accomplishment-log Mode 2). Triggers: weekly review, oppsummer uken, produksjon denne uken, ukentlig gjennomgang, friday review.
---

# Weekly Production Review

## Scope

A weekly meta-summary of "what got produced" — reads the last 7 days, not
the whole career (that's `accomplishment-log` Mode 2). Invoked on request;
not scheduled or automatic in this version (see "Trigger mechanism" below).

## Inputs

1. `private/Vault/Journal/Entries/*.md` for the past 7 days — the
   `## 📦 Leveranser` sections written by `coding/git-push-daily-log`.
2. `private/Vault/Notes/Career/career-log-YYYY.md` — any entries dated in
   the past 7 days.
3. Optional: `git log --since=7.days` across the known repos under
   `C:\repos`, **only** as a completeness cross-check — did anything get
   pushed that wasn't logged anywhere? Flag the gap explicitly; don't
   silently backfill an entry the user hasn't seen.

## Output

`private/Vault/Summaries/weekly-YYYY-Www.md` (ISO week number — matches the
Journal footer's existing `Uke [[YYYY-[W]WW]]` link convention), containing:

- Per-day/per-item short comments (what happened)
- An overall **meta-comment**: themes across the week, net direction, and
  anything notably absent (e.g. a week with many small commits but no
  forward-moving deliverable). This must be genuinely evaluative, not
  reflexively positive — per `_forvalter.md`'s own requirement to
  "utfordre en antakelse ... ved hver sesjon."

## Trigger mechanism

Not solved in this version. `CronCreate` (session-scoped, expires after 7
days) cannot deliver a standing weekly job. The user has explicitly chosen
**manual invocation only** for now — no Windows Task Scheduler entry or
other automatic trigger has been set up. Future option, not built: a
Windows Task Scheduler entry either running the Claude Code CLI headlessly,
or just sending a reminder notification that prompts the user to invoke
this skill themselves.

## Pairs with

- `coding/git-push-daily-log` — source of the per-push Journal entries this
  skill reads.
- `knowledge-management/accomplishment-log` — source of curated entries;
  also the skill to use for a longer-period (multi-week/year) summary
  instead of this weekly one.
