---
name: agent-orchestration-sizing
description: Load before EVERY Agent tool call and EVERY Workflow script, and before loading workflow-authoring. Decides inline vs one subagent vs a workflow, and sets model and effort on every agent() and Agent call (Sonnet for work orders, builders, fixers, Fabric/query runners with a given plan, docs; Opus for open missions, judges, reviewers, synthesis). Use when spawning or fanning out subagents, writing or resuming a workflow script, setting agent() opts, when ultracode is on, for judge panels, build→review→fix loops, adversarial or production review, and when the user asks about model tier, effort, token cost, why agents ran on Opus, or why everything became a workflow. Norwegian triggers: subagent eller workflow, hvilken modell, Sonnet eller Opus, arbeidsordre, oppdrag, modellvalg, effort, «bare opus-agenter». Not for writing the work order text itself (agent-work-order-handoff) or choosing Codex (using-codex).
---

# Agent orchestration sizing

Orchestration is a cost, not a default. Prefer the smallest shape that meets the task: **inline → one subagent → workflow**. Escalate one step only when a criterion below holds, and say in one line which criterion it was.

## 1. Pick the shape

**Inline (no subagent)** when any of these holds:
- The answer is one lookup, one query or one known fact.
- The change is mechanical or touches one or two files (a colour, a title, a rename).
- The user has already made the decision; only execution remains.
- It is a narrow parameter search: a handful of candidates you can score with a script (for example three greens by contrast and ΔE).

**One subagent** when the task is one coherent job and at least one holds:
- Sequential steps that share context: build → test → fix.
- It must read a lot but return a short conclusion, and the main context should stay clean.
- It runs long and the main loop has other work meanwhile.
- It is the round's single runner for serialized side effects (Fabric, Desktop reloads, deploy checks; see `fabric-cu-glatting`).

**Workflow** only when at least one holds:
- **Parallel scale:** three or more genuinely independent units (per file, per dimension, per table) that can run at the same time.
- **Wide solution space:** a subjective or design choice where independent attempts plus judges beat one attempt iterated, and the user has not already narrowed the answer.
- **Irreversible or shared-production step:** independent adversarial reviewers before a deploy, schema change or migration are worth their cost.
- **Beyond one context:** the material cannot fit or be reasoned about in one agent.

**Not a workflow:**
- One build plus one review. Use one subagent, then one reviewer subagent.
- Work the user is steering turn by turn. Their next message will redirect it; wait for the decision, or run a short inline mock-up.
- Anything justified only by "ultracode is on".

**Ultracode** lowers the bar for the wide-solution-space and production criteria and asks for deeper verification. It does not turn single decisions, one-file edits or narrow searches into workflows. The user stated this on 30.09.2026.

## 2. Pick model and effort per agent

Allowed Claude tiers: **Opus 5.5** (`opus`) and **Sonnet 5.5** (`sonnet`).
- Do not use Haiku until it is on the same version level as Opus and Sonnet (user rule, 30.09.2026).
- Use Fable only when the user asks for it.

| Stage | Model | Effort |
|---|---|---|
| Mechanical execution: run tests or scripts, render mock-ups, regenerate files, collect outputs | sonnet | low–medium |
| Single external-system runner with a given query or deploy plan (Fabric DAX/SQL, REST) | sonnet | medium |
| Retrieval: docs lookup, schema or capability lookup, grep sweeps | sonnet | medium |
| Documentation in an existing house style (for example report guidelines) | sonnet | medium |
| Many parallel proposal generators in a judge panel | sonnet | medium–high |
| Implementation, arbeidsordre: the prompt gives files, method and acceptance criteria (generators, notebooks, TMDL, code) | sonnet | medium–high |
| Fixer in a build → review → fix loop | sonnet | medium–high |
| Implementation, oppdrag: goal and constraints only, the method is open | opus | default |
| Judges, adversarial review, verification before production | opus | high |
| Synthesis, design of a query plan or method, final decision | opus | high |
| Standing project rules that name a tier (for example powerbi-modeling-mcp through Opus subagents) | as the rule says | as the rule says |

Rules:
- **Arbeidsordre → Sonnet, oppdrag → Opus** (user rule, 01.10.2026).
  - An *arbeidsordre* (work order) is a direct change where the method is given. It goes to Sonnet.
  - An *oppdrag* (mission) is a goal with an open method that needs judgment. It goes to Opus.
  - A small oppdrag whose answer is a lookup also goes to Sonnet.
  - An arbeidsordre that touches shared production (a schema change or a migration) is built by Sonnet and gets one Opus check.
  - If Sonnet fails the same arbeidsordre twice, escalate to Opus and tell the user. It was probably an oppdrag.
  - Tell the user when the rule seems to give the wrong answer.
- Match the prompt to the tier. If you have already written the method (formulas, file list, exact steps), the judgment is done and what remains is mechanical, so use Sonnet. An Opus or Fable brief gives the goal, the constraints and the acceptance criteria, and leaves the method to the agent. A fully specified prompt on Opus pays for capability that is never used.
- The Agent tool takes `model` but no per-call effort. An agent started that way runs at the session effort. When effort matters, use a Workflow `agent()` call or an agent type whose definition sets it.
- **Never omit `model`.** Omitting it means a copy of the main model, which is Opus in these sessions. The Workflow tool's own guidance ("default to omitting it") does not apply here. On 01.10.2026, 23 of 33 workflow agents ran on Opus because builders, fixers and runners had no `model`, and about 14 of them were Sonnet work.
- Set `model` and `effort` explicitly on every `agent()` call. Set `model` on every Agent tool call. In a workflow, also add `model` to each phase in `meta.phases`.
- **Ultracode adds Opus reviewers and judges, not Opus builders.** It never turns an arbeidsordre into an Opus job.
- A detailed spec (exact files, formulas, item list such as C1–C8) is an arbeidsordre even when it is long. Length is not judgment.
- A fixer runs on Sonnet. Escalate the fixer to Opus only after two review rounds have failed, and tell the user.
- Cross-family review (Codex) goes through `using-codex`, not through this table.
- When a choice is uncertain and recurs, measure it instead of arguing it. The `workflows` repo binds roles to model and effort in profiles (ADR 0005), and its `benchmark` flow scores a model matrix against a hidden answer key.

## 3. Before launching

1. Name the shape and the criterion that justifies it.
2. Estimate agents and tokens. Keep a workflow under about 10 agents unless the user asked for scale.
3. Give each agent its tier and effort from the table, and write in each prompt whether it may call external systems and how many calls it gets. Before the Workflow or Agent call, write a short table in the message: agent, model, effort, arbeidsordre or oppdrag, and why. A builder or runner without `sonnet` needs a written reason.
4. For a proposal or judge round, check that the user is not mid-decision. If they are, show one inline mock-up first.
5. After the run, report agents used per model, tokens and what the verification found. Add a line to `references/evidence.md` when the outcome says something about sizing.

## 4. While a workflow runs

- Do not answer a workflow agent with SendMessage. It resumes the agent as a separate background copy, and the copy works in the same files as the original. Put the answer in the spec of the next run, or let the review and fix rounds handle it. If it has happened, find the copy with ListAgents and stop it with TaskStop.
- An agent inside a workflow sees the session's latest user message. If that message is unrelated (for example "er rc på?"), quote the user's actual request in the prompt, or the agent may refuse the task as unrequested.

See `references/evidence.md` for dated observations behind these rules.
