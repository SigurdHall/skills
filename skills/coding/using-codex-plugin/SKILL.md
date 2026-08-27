---
name: using-codex-plugin
description: Decide when to hand work to Codex (gpt-5.6-sol) from Claude Code, pick the right Codex operation, and know whether Claude should run it directly or leave it to the user. Use when stuck after repeated failed attempts, when a diff is ready for review before commit, when the approach or architecture is in doubt, when a bug resists diagnosis, when an independent or second opinion would help, or when the user mentions codex, sol, rescue, review, adversarial review, second opinion. Also Norwegian triggers: bruk codex, spør codex, hva sier codex, hva mener codex, gi meg en ny vurdering, se over dette, dobbeltsjekk dette, jeg står fast, dette funker ikke, kan noen andre se på det, er dette riktig tilnærming, andre øyne på dette.
---

# Using the Codex plugin

Codex is a tool inside Claude Code, not a second driver. Claude stays
responsible for the work and for reporting the outcome.

## Default delivery: direct `codex exec`

Prefer a direct `codex exec` call over the plugin. The plugin caps effort at
`xhigh` and exposes no service-tier flag, so `max`, `ultra` and fast mode are all
unreachable through it. Reach for `codex-companion.mjs` only when its background
job handling is the point (`--background`, `status`, `result`).

A direct call inherits nothing, so pass everything explicitly, and mind the two
footguns: there is **no `--effort` flag** (use `-c model_reasoning_effort=`), and
the process hangs on stdin without `< /dev/null`.

```bash
cd <repo> && codex exec -m <model> -c model_reasoning_effort=<effort> \
  --sandbox read-only "<prompt>" < /dev/null
```

Codex refuses to start outside a trusted directory, so `cd` into the repo first.

## What Claude can actually run

`disable-model-invocation: true` on most `/codex:` commands blocks the **slash
command**, not the capability. The companion script is plain Bash and Claude
can call every operation directly:

```bash
node "$CODEX_PLUGIN/scripts/codex-companion.mjs" <op> [flags]
```

where `$CODEX_PLUGIN` is the plugin install path for the current machine:

- Windows: `C:/Users/<user>/.claude/plugins/cache/openai-codex/codex/<version>`
- Sandbox container: `/home/vscode/.claude/plugins/cache/openai-codex/codex/<version>`

Read the real path from `~/.claude/plugins/installed_plugins.json` rather than
assuming either one.

**Green level-2 containers:** `installed_plugins.json` records the level-1
`/home/vscode` path, but `$HOME` is `/root` there and `/home/vscode` does not
exist — so the plugin never loads, and `/codex:*` and `codex:codex-rescue` are
absent from the session. The cache itself is intact under `/root/.claude`. Do not
rewrite `installPath`: `~/.claude` is bind-mounted and shared with level 1. Fix it
container-locally instead, then restart Claude Code:

```bash
mkdir -p /home/vscode && ln -sfn /root/.claude /home/vscode/.claude
ln -sfn /root/.codex /home/vscode/.codex
```

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

Every Codex call spends the user's subscription budget, but the amount depends
heavily on the model — Luna and Terra are far cheaper per task than Sonnet 5,
Sol is the expensive tier. So:

- Announce before running, in one line: what, why, and which model.
- Never run Codex silently, and never twice on the same unchanged diff.
- Reserve Sol for the cases that earn it. Routine delegation goes to Luna or
  Terra — see "Choosing the model".

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

## Standing rule: review Opus and Fable architecture work

When the planning or architectural decision was made by Opus or Fable, a Codex
review is mandatory, not optional. It covers target architecture, solution
design, technology and data-modelling choices, migration approach, and any
decision that is expensive to reverse. It does not cover routine implementation
inside an already-agreed design.

Run it with an adversarial prompt as a direct `codex exec` call, **with fast mode
on** — this is the case where the user is blocked waiting on the answer:

    cd <repo> && codex exec -m gpt-5.6-sol \
      -c model_reasoning_effort=xhigh \
      -c service_tier='"priority"' \
      --sandbox read-only "<adversarial prompt>" < /dev/null

Fast mode (`service_tier = "priority"` — 1.5x speed for increased usage) is not
reachable through the plugin, so this review must not go through `codex:rescue`.
`--sandbox read-only` is the direct-CLI equivalent of leaving `--write` off.

Sonnet and Haiku work does not trigger this rule on its own — use the judgement
in the table above.

## Choosing the model

Luna and Terra cost far less per task than Sonnet 5. That makes delegation the
cheap option, not the expensive one: work Claude would otherwise grind through
locally is often better sent down to Codex. Size the model to the difficulty.

| Work | Model | Effort |
|---|---|---|
| Easy for Sonnet 5 — mechanical, bounded, obvious shape | `gpt-5.6-luna` | `max` |
| Harder than that, still a contained problem | `gpt-5.6-terra` | `max` |
| Planning or architecture by Opus or Fable | `gpt-5.6-sol` | `xhigh` + fast mode |

The saving comes from the model tier, not from thinking less — so Luna and Terra
run at `max`, the highest effort they support. Buying more thinking on a cheap
tier is cheap. Sol stays at `xhigh` because it is the expensive tier and `max`
there is a real cost; raise it only when a problem has already resisted `xhigh`.

Examples of Luna work: rename and mechanical refactors, adding tests to an
existing pattern, tracing a specific call path, checking a claim against the
code, cleaning up a diff. Examples of Terra work: diagnosing a bug that resists
one reading, reviewing a non-trivial implementation, unpicking an unfamiliar
subsystem, work with several plausible approaches.

If the difficulty is genuinely unclear, use Terra. The cost gap between Luna and
Terra is small next to the cost of a second run.

Model names must be passed in full — `spark` is the only alias
`codex-companion.mjs` resolves, and the plugin caps effort at `xhigh`, so
Codex's own `max` and `ultra` tiers are unreachable through it.

`ultra` is a **distinct tier, not merely more effort** — Sol and Terra describe it
as "maximum reasoning with automatic task delegation". Luna has no `ultra` at all;
`max` is its ceiling. The CLI does not validate effort against the model's
supported list, so `ultra` on Luna is accepted and echoed back for a tier that
model does not have — a typo will look like it worked. Judge whether effort landed
by `reasoning_output_tokens` in the rollout, never by the startup header: trivial
prompts log 0 reasoning tokens at every tier.

## Reviewing things that are not a diff

`review` only handles git diffs. For plans, architecture, solution choices,
completion claims, and documents, use `task` **without `--write`** — it runs
read-only on the same path as `adversarial-review`, gets subagents, and unlike
`adversarial-review` it accepts `--effort`.

Call `codex exec --sandbox read-only` directly rather than the rescue agent, so
write access is provably absent. Prompt patterns:
[review-prompts.md](references/review-prompts.md).

## When not to use Codex

- Edits Claude can finish in the next tool call. Anything larger is a candidate
  for Luna, which is cheaper than grinding it out locally.
- Documentation, markdown, config-only changes.
- Before Claude has made a real attempt.
- Outside a git repository — the review operations require one.

## Runtime facts that change the advice

- The plugin passes `null` for model and effort unless told otherwise, so both
  come from `~/.codex/config.toml`. On Windows that file sets `gpt-5.6-sol` at
  `high`. **The sandbox container has no `config.toml`**, so an unset call there
  falls back to Codex's own built-in default. Pass `--model` and `--effort`
  explicitly when the values matter.
- The only model alias the plugin resolves is `spark` -> `gpt-5.3-codex-spark`
  (`codex-companion.mjs`, `MODEL_ALIASES`). Any other model must be given as its
  full name and is passed straight through to Codex.
- `review` and `adversarial-review` accept `--model` but have **no effort
  flag**. They cannot be tuned per call.
- `task` accepts `--effort` up to `xhigh`. The plugin rejects `ultra`.
- `adversarial-review` runs subagents (`max_threads = 12`); `review` uses
  Codex's built-in reviewer and does not.

## Sessions and `--ephemeral`

Every plain `codex exec` creates a new thread and writes the conversation to three
places under `~/.codex`: `sessions/YYYY/MM/DD/rollout-<ts>-<id>.jsonl`,
`thread_history_1.sqlite` and `state_5.sqlite`. Continue one with
`codex exec resume --last|<id>`, branch it with `codex exec fork <id>`. Note that
`resume --last` filters by cwd — pass `--all` to reach other directories.

Persist by default, so a follow-up turn stays possible. Reserve `--ephemeral` for
throwaway side questions and one-shot lookups that would never be resumed; it
leaves no trace on disk, but ephemeral threads cannot be resumed or forked, so
capture anything worth keeping with `-o <file>` or `--json`.

Two traps. `history.persistence = "none"` is **not** an off switch — it governs
only the TUI composer history and leaves all three files intact. And `--ephemeral`
is local-only: `disable_response_storage` no longer exists in the binary, so
nothing in the CLI controls server-side retention.

Never read a rollout file whole — they run 50KB–800KB and will flood the context
window. Extract the field needed with `jq` or `grep`.

## Reporting back

Codex output is evidence, not a verdict. Relay its findings, state plainly
which ones Claude agrees with, and never present an unverified Codex claim
as confirmed.
