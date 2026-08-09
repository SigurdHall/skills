---
name: present-complex-results
description: "Present complex work in a remote-control-friendly final response with a minimum information and detail floor. Use before the final response for every multi-step, tool-heavy, file-producing, high-impact, high-risk, partially complete, blocked, or decision-bearing process or delivery, even when the user did not explicitly request a detailed summary. Also trigger when the user asks what changed, whether something is fixed or ready, for a delivery summary, or for next-step choices. Do not use for simple factual answers, trivial edits, or one-step commands."
---

# Present Complex Results

Treat the final response as the user's remote control for the work. Make the
material outcome, evidence, limits, and next decision understandable without
requiring the user to open every file.

Use this as the presentation layer after completing the domain workflow. Do
not replace fresh verification, a domain-specific skill, or a durable handoff
when one is required.

## Decide whether the result is complex

Apply this skill when either one high-risk condition or at least two of these
signals are present:

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

## Establish the actual status

Choose and state one primary status before drafting the rest:

- **Complete** — finish the requested scope and pass the relevant checks.
- **Partial** — deliver useful work, but leave requested scope or meaningful
  verification unfinished.
- **Blocked** — stop on a specific missing input, authority, dependency, or
  external-state change.
- **Decision required** — reach a genuine fork where different choices change
  scope, risk, cost, or implementation.

Distinguish `implemented`, `inspected`, `tested`, `live-verified`, and `not
verified`. Never collapse these into a generic claim that the work is done.

## Translate evidence for a chat interface

Assume the user sees the final response before any evidence file, test log, or
earlier commentary. Make technical status understandable in ordinary language
before presenting labels, counts, hashes, or gate names.

Use this sequence whenever the result contains dense verification language:

1. **Plain-language meaning** — say what works, where it works, and why the
   user should care.
2. **Practical boundary** — say what has not happened in the real system.
3. **Technical evidence** — then give test counts, digests, commands, and gate
   status.
4. **Consequence** — state whether the user can use, test, approve, or must
   wait for the result.

Translate a term on first use when a reasonable user could otherwise
misinterpret it. For example:

- `offline smoke passed` means the package worked locally without connecting
  to the provider;
- `live smoke not run` means no real sandbox or service request was made;
- `parent gate pending` means an independent final review has not accepted the
  candidate yet.

Prefer a short “What this means in practice” sentence over expecting the user
to infer meaning from `158 passed`, `replayed_identical`, or
`overallRelease=not_authorized`. Treat numbers as supporting evidence, not the
main explanation. Use a compact analogy only when it materially clarifies the
boundary, such as “bench-tested, not road-tested.”

For unfamiliar systems, explicitly answer:

- What goes in?
- What comes out?
- What is automatic?
- What still needs a person, permission, or live connection?

## Meet the output contract

Use headings appropriate to the user's language. Preserve this information
order even when combining small sections:

1. **Result, meaning, and status** — lead with what the user now has, explain
   its practical meaning in ordinary language, and then state the primary
   status. Use two to four concrete sentences.
2. **Delivered or changed** — summarize each material workstream and why it
   matters. Describe behavior and decisions, not only filenames or activity.
3. **Important artifacts** — when files exist, link the important ones and
   give each a one-sentence role. Identify the source of truth when several
   artifacts overlap.
4. **Verification and evidence** — name each relevant command or manual check,
   its result, and what it proves. State what was not run and why. Do not imply
   live success from syntax, schema, or static inspection alone.
5. **Decisions, limitations, and remaining work** — expose consequential
   assumptions, deviations, risks, out-of-scope items, blockers, and manual
   checks. Do not omit a category merely because it weakens the success story.
6. **Next step** — recommend the most useful action. If no action remains, say
   so explicitly.

When the user asks whether something is fixed, separate the answer into the
diagnosis, the implemented change, and the remaining verification.

## Keep a meaningful depth floor

Use information coverage as the hard floor and word count as a diagnostic:

- Default to roughly 350–700 words for a complex result.
- Expand toward 700–1,200 words for multi-repository, high-risk, partial,
  blocked, or decision-heavy work when the extra detail helps steering.
- Go below 350 words only when the user explicitly requests brevity or every
  required fact genuinely fits. Preserve the output contract even then.

Do not pad the response with a tool diary, obvious implementation chronology,
or repeated claims. Prefer impact, evidence, decisions, and consequences.

## Present useful next-step choices

When one natural action remains, recommend it directly instead of inventing a
menu. When a real fork exists:

1. Present two or three mutually distinct options.
2. Put the recommended option first and explain why it is recommended.
3. State the main consequence, trade-off, prerequisite, or risk for each.
4. State exactly what the user needs to decide or authorize.
5. Include stopping with the current result when that is a reasonable choice.

Never end a complex delivery with only "What do you want to do next?"

## Enforce the remote-control rule

- Keep decision-relevant content in the conversation. Use files for durable
  detail and evidence, not as a substitute for the result summary.
- Never write only "details are in the files." Surface the important findings,
  changes, risks, and choices, then link the supporting artifact.
- Link only the important files; do not dump generated-file inventories.
- Report deviations from the requested scope explicitly and explain why they
  occurred.
- Avoid generic offers for more help. End on the recommendation, bounded
  options, required decision, or a clear statement that no action remains.

## Check before sending

Confirm that the final response lets the user answer all of these without
opening a file:

- What changed, and why does it matter?
- Can a non-specialist understand the practical meaning before reading the
  technical evidence?
- What is the honest completion status?
- What evidence supports the claims?
- What remains uncertain, unverified, blocked, or out of scope?
- Which artifacts matter, and what is each for?
- What should happen next, and what choice or authority is needed?
