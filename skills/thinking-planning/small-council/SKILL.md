---
name: small-council
description: Use when the user asks for Small Council, council brief, daily intelligence council, source/news/RSS intelligence, or wants Codex to gather, sort, rank, evaluate, recommend, and operationalize information into the private vault.
---

# Small Council

Use this when the user asks for `Small Council` or equivalent council wording.

Small Council is the user's personal information intelligence system. It should
collect and evaluate information, maintain RSS/source coverage, curate vault
notes, recommend what to read and do next, and identify skills/workflows that
increase the user's capacity.

It is not a general-purpose review crew. For ordinary code review, planning, or
debugging, use the relevant non-council workflow unless the user explicitly asks
for Small Council.

## Core Rule

When Small Council is called, use the whole council operationally:

- Tyrion / King's Hand stays in the main thread.
- Dispatch every available council seat as a subagent when subagent tools are
  available.
- If runtime thread limit prevents full parallel dispatch, run the council in
  waves until all seats have been attempted.
- If a seat cannot be spawned, report that honestly. Do not imply it ran.
- Close stale council agents before dispatch when the tool runtime exposes agent
  cleanup. If cleanup is unavailable, proceed and state the limitation only if it
  affects the result.

## Seat-Only Mode

When a dispatched prompt says `You are [Name] / [Title] in the Small Council`,
that agent is already inside a council run. It should answer only within that
seat mandate and must not start a new full council run, dispatch other council
seats, or run Spider scouts unless Tyrion explicitly asks for it.

Seat agents should complete the assigned mandate, not switch into generic skill
self-review. If the prompt is read-only, do not write files, reports, inbox
entries, or skill-improvement suggestions; return suggested changes in the
response instead.

## Council Seats

Use names and titles as labels, not as character imitation.

| Seat | Title | Mandate |
| --- | --- | --- |
| Tyrion | King's Hand | Main-thread coordinator. Clean up old agents when possible, dispatch seats, manage wave execution, synthesize final brief, and decide practical next actions. |
| Varys | Master of Whispers | Find sources, RSS feeds, watch pages, source gaps, weak signals, similar feeds, and information the user may need soon. Separate confirmed sources from candidates. |
| Samwell Tarly | The Forvalter | Manage vault quality: filenames, frontmatter, metadata, source history, backlinks, indexes, duplicates, retention, and curation status. |
| Baelish | Master of Coin | Evaluate value, cost, prioritization, finance/BI/productivity implications, corporate-finance logic, and practical return on attention. |
| Renly | Master of Laws | Review privacy, licensing, governance, security, Git risk, e-mail risk, UiT/internal-content constraints, and public-sector suitability. |
| Pycelle | Grand Maester | Maintain documentation, runbooks, skill analysis, capacity upgrades, and reusable workflow recommendations. |

## Agent Budget Rule

Use model capacity deliberately when the subagent runtime supports model
selection.

- Tyrion / King's Hand stays in the main thread and uses the current main model.
- Varys / Master of Whispers should normally inherit the main model when acting
  as source strategist, scout-swarm planner, or evidence coordinator.
- Baelish / Master of Coin and Renly / Master of Laws should normally inherit the
  main model, because value, finance, governance, privacy, licensing, and risk
  decisions are high-leverage.
- Varys may recommend narrower source scouts for routine data collection. These
  scout subagents are the only agents that should use `Spider 1`, `Spider 2`,
  ... `Spider N` labels. They may use a cheaper or faster available model for
  bounded read-only collection tasks.
- Samwell Tarly / The Forvalter and Pycelle / Grand Maester may use a cheaper or
  faster available model for routine read-only RSS metadata checks, vault hygiene,
  backlinks, runbooks, and documentation summaries.
- Escalate any downgraded seat back to the main model when the task involves
  unclear source rights, UiT/internal or employee-facing content, persondata,
  secrets, e-mail sending, Git publication risk, finance/governance judgment,
  code changes, conflicting evidence, or recommendations that may affect work
  decisions.
- If model override is unavailable or uncertain, do not block the work. Use the
  default inherited model and report only material limitations.

## Varys Scout Swarm

For larger collection tasks, Varys may propose a scout swarm but should not run
unbounded nested agents.

Varys stays on the main model as source strategist, scout-swarm planner, and
evidence coordinator. The council seats keep their council names; `Spider N`
labels are reserved only for narrow data-gathering scouts created from Varys'
recommendations.

Varys returns:

- source categories
- proposed `Spider 1`, `Spider 2`, ... `Spider N` scout tasks
- expected output
- risk level
- recommended model tier

Tyrion dispatches the Spider scouts when useful. Default scout scopes:

- AI, OpenAI, GitHub, and developer practice
- BI, Fabric, Power BI, Databricks, and semantic models
- Data engineering, podcasts, and practitioner resources
- UiT, public sector, governance, and working-life sources
- RSS candidates, stale sources, and source-quality gaps

## Intelligence Pipeline

Run this cycle for RSS, information, news, and vault tasks:

1. Collect
   - Read activated RSS feeds and known watch pages.
   - Prefer existing local scripts before inventing new workflow.
   - Do not scrape full text by default.

2. Refresh
   - Identify sources not documented or verified in the last 120 days.
   - Check failing feeds, disabled candidates, and watch pages.
   - Keep Gartner/licensed sources and UiT/employee-facing content as link-only
     or human-review unless policy explicitly allows more.

3. Rank
   - Rank by freshness, source quality, relevance, category, expected value,
     noise level, and usefulness for the user's current work.
   - Prioritize finance, management control, BI/Fabric/Power BI, data
     engineering, AI practice, public-sector governance, UiT-relevant work, and
     skills that improve capacity.

4. Store
   - Save Markdown notes in the private vault with stable readable filenames.
   - Include frontmatter, source link, digest link, run ID, source policy,
     relevance, domain, backlinks, and curation status.
   - Do not store secrets, personal data, real invoices/vouchers, internal
     documents, or licensed full text without explicit policy.

5. Brief
   - Produce a short decision-oriented Small Council brief.
   - Recommend what to read, what to do next, how to implement the useful parts,
     source gaps, skill/workflow upgrades, and immediate watchlist.

6. Recommend
   - Suggest new feeds, source candidates, scripts, skills, tests, or vault
     structures that increase the user's capacity.
   - Anticipate near-future needs from the user's stated interests and current
     files, but label assumptions clearly.

## Standard Command

Prefer the existing local command for RSS/intelligence intake:

```powershell
cd C:\repos\private\rss-intake
.\start-small-council-intake.ps1
```

Useful variants:

```powershell
.\start-small-council-intake.ps1 --refresh-stale-sources
.\start-small-council-intake.ps1 --brief-only
.\start-small-council-intake.ps1 --max-age-days 45 --limit 40 --email-preview
```

Default outputs:

- `Resources/RSS/Reports/YYYY-MM-DD-small-council-briefing.md`
- `Resources/RSS/Reports/YYYY-MM-DD-source-candidates.md`
- `Resources/RSS/Reports/YYYY-MM-DD-skill-capacity-review.md`
- `Resources/RSS/Articles/...`
- `Resources/RSS/Podcasts/...`
- `Resources/RSS/Index.md`

## Brief Format

Small Council's final user-facing brief should use this short format:

```md
## Small Council Called
- Seats attempted:
- Seats completed:
- Wave fallback used:
- Sources/files used:

## Most Important
- ...

## Look At
- ...

## Do Next
- ...

## How To Implement
- ...

## Source Gaps
- ...

## Skill/Workflow Upgrades
- ...

## Immediate Future Watchlist
- ...

## Residual Risk
- ...
```

Keep the final synthesis shorter than raw council notes. Link to generated vault
reports instead of pasting long lists.

## Dispatch Prompt Template

Use this shape for each dispatched seat:

```md
You are [Name] / [Title] in the Small Council.

Mission:
- Support the user's personal information intelligence system.
- Work on your council mandate only.

Scope:
- [RSS run, vault reports, source config, files, or question]

Constraints:
- Work read-only unless explicitly assigned a disjoint write scope.
- Read-only includes not writing skill-improvement inbox entries, reports, or
  generated notes.
- Separate facts, assumptions, and recommendations.
- Do not inspect or expose secrets, persondata, real invoices/vouchers, licensed
  full text, or employee-facing content beyond the stated scope.
- Do not switch into generic skill self-review unless explicitly requested.
- Keep output short and actionable.

Return:
- Key findings
- Evidence or files/sources
- Gaps/risks
- Recommendations
- One concrete next action
```

## Safety Defaults

- No full-text scraping by default.
- No Gartner/licensed content automation beyond links and metadata.
- No UiT/employee-facing content storage beyond links and user-approved notes
  without human review.
- E-mail is preview-only unless the user explicitly requests sending and the
  environment is configured safely.
- Generated RSS output must be safe for local vault storage and Git-aware: no
  secrets, personal data, or sensitive internal records.

## Renly Gate

For recurring intelligence automation, Renly / Master of Laws should verify:

- `content_policy` is documented and technically respected.
- E-mail is preview-only unless explicitly approved for sending.
- UiT/internal or employee-facing content is link-only/manual-review by default.
- Licensed sources are metadata/link-only unless policy allows more.
- Git ignore rules protect generated RSS output, caches, secrets, and volatile
  plugin state.
