---
name: present-complex-results
description: "Shapes the final response for complex work, in the same communication form as planf3. Use before the final response for every multi-step, tool-heavy, file-producing, high-impact, high-risk, partially complete, blocked, or decision-bearing process or delivery, even when the user did not explicitly request a summary. Also trigger when the user asks what changed, whether something is fixed or ready, for a delivery summary, or for next-step choices. Carries planf3's vocabulary into chat: purpose/problem/solution framing, phases with status markers, validation commands with what they prove, and questionables surfaced rather than silently decided. Do not use for simple factual answers, trivial edits, or one-step commands."
---

# Present Complex Results

Treat the final response as the user's remote control for the work. Make the
material outcome, evidence, limits, and next decision understandable without
requiring the user to open every file.

This is the presentation layer after the domain workflow. It does not replace
fresh verification, a domain skill, or a durable handoff.

**It is the conversational counterpart of a [planf3](../../thinking-planning/planf3/SKILL.md)
plan.** A planf3 plan is what gets built; this is how the build gets reported.
The two share one vocabulary so a reader moves between the HTML plan and the
chat response without re-learning terms. When a planf3 plan exists for the
work, report against its phases and reuse its names verbatim.

## Decide whether the result is complex

Apply this skill when one high-risk condition or at least two of these signals
are present:

- Complete several substantive steps or workstreams.
- Change multiple files, components, repositories, or live objects.
- Create artifacts whose purpose or relationship needs explanation.
- Use several tools, subagents, migrations, deployments, or external systems.
- Make a material design, architecture, business, governance, or scope choice.
- Leave manual verification, blockers, limitations, or follow-up work.
- Require the user to choose a direction or authorize a consequential action.
- Affect finance, compliance, privacy, production, or other high-risk work.

Do not invoke it for a simple answer, a trivial one-file edit, or a single
command whose outcome is self-explanatory.

## Use planf3's status markers

Report work with the same four markers the plan template uses, so a phase reads
identically in the plan and in chat:

- `[x]` complete — done and checked
- `[wip]` in progress — started, not finished
- `[]` idle — not started
- `[f]` failed or not possible — state the cause, then move on

Use them for phases and tasks, not for prose. A marker replaces a vague verb:
`[f] live-kjøring i Fabric` is honest where "mostly working" is not.

Alongside the markers, keep the distinctions that matter: `implemented`,
`inspected`, `tested`, `live-verified`, `not verified`. Never collapse these
into a generic claim that the work is done.

## Establish the actual status

Choose and state one primary status before drafting the rest:

- **Complete** — the requested scope is finished and the relevant checks pass.
- **Partial** — useful work delivered, but requested scope or meaningful
  verification is unfinished.
- **Blocked** — stopped on a specific missing input, authority, dependency, or
  external-state change.
- **Decision required** — a genuine fork where different choices change scope,
  risk, cost, or implementation.

## Translate evidence for a chat interface

The user sees the final response before any evidence file, test log, or earlier
commentary. Make technical status understandable in ordinary language before
presenting labels, counts, hashes, or gate names.

Whenever the result contains dense verification language:

1. **Plain-language meaning** — what works, where, and why it matters.
2. **Practical boundary** — what has not happened in the real system.
3. **Technical evidence** — test counts, digests, commands, gate status.
4. **Consequence** — whether the user can use, test, approve, or must wait.

Translate a term on first use when a reasonable user could misread it:
`offline smoke passed` means the package worked locally without contacting the
provider; `live smoke not run` means no real request was made; `parent gate
pending` means an independent review has not accepted the candidate.

Prefer a short "hva dette betyr i praksis" sentence over expecting the user to
infer meaning from `158 passed` or `overallRelease=not_authorized`. Treat
numbers as supporting evidence, not the explanation. Use a compact analogy only
when it clarifies the boundary, such as "benkprøvd, ikke kjørt på vei".

For unfamiliar systems, answer explicitly: what goes in, what comes out, what
is automatic, and what still needs a person, permission, or live connection.

## Meet the output contract

Mirror the planf3 section order. Write in the user's language, with headings to
match. Combine small sections when the work is light, but preserve this order.

1. **Result and status** — what the user now has, what it means in ordinary
   language, then the one primary status. Two to four concrete sentences. This
   is planf3's *Purpose* and *Solution* compressed into the lead.
2. **Problem** — only when the result is not self-explanatory: what was wrong,
   or what the work was for. Skip it when the user already knows.
3. **Phases and tasks** — each substantive workstream with its status marker,
   what it changed, and why that matters. Describe behaviour and decisions, not
   filenames and activity. When a planf3 plan governs the work, use its phase
   numbers and names.
4. **Artifacts** — tag each as `new` or `existing`, link the important ones,
   give each a one-sentence role. Name the source of truth when several
   overlap. Link only what matters; never dump a file inventory.
5. **Validation** — each command or manual check, its result, and **what it
   proves**. State what was not run and why. Never imply live success from
   syntax, schema, or static inspection alone.
6. **Questionables** — consequential assumptions, deviations, risks,
   out-of-scope items, blockers, and open faglige questions. Surface them
   rather than deciding silently. Do not omit a category because it weakens the
   success story. Number them when the user will need to answer them.
7. **Next step** — the most useful action. If none remains, say so explicitly.

When the user asks whether something is fixed, split the answer into diagnosis,
implemented change, and remaining verification.

## Honour the loop rule

planf3 says a phase is not complete until every box is checked. The reporting
equivalent: **do not present a phase as `[x]` while any of its validation
commands is unrun or failing.** If a check cannot be run in this environment,
mark it `[f]`, say why, and say what would make it runnable. An unrun check is
never silent.

## Keep a meaningful depth floor

Information coverage is the hard floor; word count is a diagnostic.

- Default to roughly 350–700 words for a complex result.
- Expand toward 700–1,200 for multi-repository, high-risk, partial, blocked, or
  decision-heavy work when the detail helps steering.
- Go below 350 only when the user asks for brevity or every required fact
  genuinely fits. Preserve the output contract even then.

Do not pad with a tool diary, implementation chronology, or repeated claims.
Prefer impact, evidence, decisions, consequences.

## Present useful next-step choices

When one natural action remains, recommend it directly instead of inventing a
menu. When a real fork exists:

1. Present two or three mutually distinct options.
2. Put the recommended one first and say why.
3. State the main consequence, trade-off, prerequisite, or risk for each.
4. State exactly what the user must decide or authorize.
5. Include stopping with the current result when that is reasonable.

Never end a complex delivery with only "what do you want to do next?".

## Enforce the remote-control rule

- Keep decision-relevant content in the conversation. Files hold durable detail
  and evidence, not the result summary.
- Never write only "details are in the files". Surface the findings, changes,
  risks, and choices, then link the artifact.
- Report deviations from the requested scope explicitly, and why they happened.
- Avoid generic offers of further help. End on the recommendation, the bounded
  options, the required decision, or a clear statement that nothing remains.

## Check before sending

The final response must let the user answer all of these without opening a file:

- What changed, and why does it matter?
- Can a non-specialist grasp the practical meaning before the technical evidence?
- What is the honest completion status, marker by marker?
- What evidence supports the claims, and what proves what?
- What remains uncertain, unverified, blocked, or out of scope?
- Which artifacts matter, and what is each for?
- What should happen next, and what choice or authority is needed?
