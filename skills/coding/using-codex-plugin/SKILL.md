---
name: using-codex-plugin
description: Decide when to hand work to Codex (gpt-5.6-sol) from Claude Code, pick the right Codex operation, and know whether Claude should run it directly or leave it to the user. Use when stuck after repeated failed attempts, when a diff is ready for review before commit, when the approach or architecture is in doubt, when a bug resists diagnosis, when an independent or second opinion would help, or when the user mentions codex, sol, rescue, review, adversarial review, second opinion. Also Norwegian triggers: bruk codex, spør codex, hva sier codex, hva mener codex, gi meg en ny vurdering, se over dette, dobbeltsjekk dette, jeg står fast, dette funker ikke, kan noen andre se på det, er dette riktig tilnærming, andre øyne på dette.
---

# Using the Codex plugin

Codex is a tool inside Claude Code, not a second driver. Claude stays
responsible for the work and for reporting the outcome.

## What Claude can actually run

`disable-model-invocation: true` on most `/codex:` commands blocks the **slash
command**, not the capability. The companion script is plain Bash and Claude
can call every operation directly:

```bash
node "$CODEX_PLUGIN/scripts/codex-companion.mjs" <op> [flags]
```

where `$CODEX_PLUGIN` is
`C:/Users/<user>/.claude/plugins/cache/openai-codex/codex/<version>`.

| Operation | Claude runs it | Notes |
|---|---|---|
| `review [--background]` | Yes — announce first | Read-only. Requires a git repo. |
| `adversarial-review` | Yes — announce first | Heavier: runs subagents. |
| `status` / `result` | Yes, freely | Cheap, read-only. Job state is per-workspace. |
| `task` (rescue) | Via `Agent(subagent_type: "codex:codex-rescue")` | **Write-capable by default.** |
| `transfer` | No — leave to the user | Hands the session elsewhere; their call. |

This skill is the user's standing authorization for the above, including the
`codex:codex-rescue` agent. No other agent gains proactive-spawn permission.

## Quota discipline

Every Codex call spends the user's subscription budget. So:

- Announce before running, in one line: what and why.
- Never run Codex silently, and never twice on the same unchanged diff.
- Skip it entirely for trivial edits — see the exclusions below.

## When to reach for Codex

| Situation | Operation |
|---|---|
| Substantive change complete, before commit | `review --background` |
| Real doubt about approach, design, tradeoffs | `adversarial-review` |
| Two attempts at the same problem have failed | rescue agent |
| Root cause needs code reading that would burn remaining context | rescue agent |
| Reviewing a plan, approach, claim, or document | `task` — see below |
| User asked for a second opinion | match to the four above |

Before a rescue run, confirm the branch or worktree if the working tree holds
unrelated changes — rescue writes.

## Reviewing things that are not a diff

`review` only handles git diffs. For plans, architecture, solution choices,
completion claims, and documents, use `task` **without `--write`** — it runs
read-only on the same path as `adversarial-review`, gets subagents, and unlike
`adversarial-review` it accepts `--effort`.

Call the script directly rather than the rescue agent, so `--write` is
provably absent. Prompt patterns: [review-prompts.md](references/review-prompts.md).

## When not to use Codex

- Small, bounded edits Claude can finish now.
- Documentation, markdown, config-only changes.
- Before Claude has made a real attempt.
- Outside a git repository — the review operations require one.

## Runtime facts that change the advice

- Default is `gpt-5.6-sol` at `high` effort, from `~/.codex/config.toml`.
  The plugin passes `null` and inherits it.
- `review` and `adversarial-review` accept `--model` but have **no effort
  flag**. They cannot be tuned per call.
- `task` accepts `--effort` up to `xhigh`. The plugin rejects `ultra`.
- `adversarial-review` runs subagents (`max_threads = 12`); `review` uses
  Codex's built-in reviewer and does not.

## Reporting back

Codex output is evidence, not a verdict. Relay its findings, state plainly
which ones Claude agrees with, and never present an unverified Codex claim
as confirmed.
