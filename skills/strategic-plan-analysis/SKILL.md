---
name: strategic-plan-analysis
description: Analyze an organization's strategy, long-term plans, operating model, and governance documents. Use when Codex should research current public or internal strategy documents, compare strategy with operational plans, assess implementation quality, create critical Markdown notes, build topic pages in an Obsidian vault, or evaluate whether plans translate into priorities, resources, indicators, risk management, reporting, and accountability.
---

# Strategic Plan Analysis

## Goal

Turn strategy and planning documents into practical, critical knowledge artifacts. Prefer clear synthesis over document summaries. Separate documented facts from analysis, criticism, assumptions, and follow-up questions.

## When The Task Involves A Vault

If the target is `private/Vault`, also use the `vault-forvalter` skill if available.

Before editing vault files, read:

1. `private/Vault/_principal.md`
2. `private/Vault/_forvalter.md`
3. `private/Vault/_kontekst.md`

Place source-oriented notes under a suitable `Resources/<organization>/` folder. Place synthesis/navigation pages under `Topics/`.

## Source Workflow

1. Identify the latest strategy document and its official source.
2. Identify the latest operational plan, long-term plan, annual plan, development agreement, budget document, or equivalent implementation document.
3. Look for earlier versions to compare maturity, continuity, and changes.
4. Prefer official and primary sources. For public-sector entities, prioritize official websites, board papers, annual reports, budget documents, allocation letters, and governance instructions.
5. Download or archive PDFs locally when the vault or repository is intended to preserve the evidence base.
6. Record retrieval date and source URLs in Markdown frontmatter or a `Kilder` section.

Use web browsing when information may have changed or the user asks for current/latest information.

## Analysis Frame

Assess whether the plan actually operationalizes the strategy:

- **Strategic fit:** Does the plan preserve the strategy's main priorities and logic?
- **Prioritization:** Does it make hard choices, or mostly list initiatives?
- **Resource linkage:** Are budget, people, capacity, and investment consequences visible?
- **Accountability:** Are responsible levels, owners, and decision arenas clear?
- **Indicators:** Do measures capture outcomes/effects, or mostly activity and volume?
- **Risk:** Are risks linked to concrete mitigations, budget choices, and reporting?
- **Reporting:** Is there a clear loop through annual plans, tertial/quarterly reports, annual reports, and management dialogue?
- **Learning:** Does weak performance trigger review, reprioritization, or corrective action?
- **Version change:** What changed from earlier plans, and does the newest version improve execution?
- **Governance quality:** Is the document useful for managers and controllers, or mainly communicative?

## Recommended Artifacts

Create separate notes when the work has more than one layer:

1. `Resources/<organization>/<strategy-title> - operasjonalisering.md`
2. `Resources/<organization>/<plan-title> - kritisk vurdering.md`
3. `Topics/<organization> strategi og virksomhetsstyring.md`

For the topic page, put critical questions first, then a summary, then an overview of the strategy and plan.

## Markdown Structure

Use this structure for a strategy operationalization note:

```markdown
---
created: YYYY-MM-DD
status: arbeidsnotat
tags:
  - strategi
  - virksomhetsstyring
kilder:
  - https://...
---

# <Organization> strategi - operasjonalisering

## Kortversjon
## Strategiens kjerne
## Innsatsområder / hovedmål
## Hvordan strategien operasjonaliseres
## Styringskjeden i praksis
## Vurdering
## Kilder
## Videre arbeid
```

Use this structure for a long-term-plan critique:

```markdown
---
created: YYYY-MM-DD
status: arbeidsnotat
tags:
  - langtidsplan
  - strategi
  - virksomhetsstyring
  - kritisk-vurdering
kilder:
  - https://...
relatert:
  - "[[Related note]]"
---

# <Organization> <plan> - kritisk vurdering

## Kortversjon
## Hva planen er ment å gjøre
## Vurdert dokument
## Sammenheng med strategien
## Hva som er nytt eller tydeligere enn tidligere
## Kritisk vurdering mot strategien
## Vurdering per strategisk område
## Samlet konklusjon
## Spørsmål å følge opp
## Kilder
```

Use this structure for a topic page:

```markdown
---
created: YYYY-MM-DD
status: arbeidsnotat
tags:
  - strategi
  - virksomhetsstyring
---

# <Organization> strategi og virksomhetsstyring

## Spørsmål og kritikk
## Sammendrag
## Oversikt over strategien
## Oversikt over overordnet plan
## Styringskjeden
## Noter
## Videre analyse
## Kilder
```

## Writing Rules

- Be direct and critical, but evidence-based.
- Do not overstate. Use "framstår som", "tyder på", or "basert på dokumentene" when making inferences.
- Preserve Norwegian for explanations and note text unless the user asks for English.
- Use English for filenames only when that is the existing convention.
- Avoid long quotes from sources; paraphrase and cite.
- Make limitations explicit when PDFs could not be parsed completely or sources are missing.
- For public-sector and finance contexts, call out governance, auditability, internal control, risk, reporting, and accountability.

## Validation

Before finishing:

1. Verify the Markdown files exist in the intended folder.
2. Check that wikilinks point to actual note basenames when practical.
3. Check git status and report unrelated local changes separately.
4. If asked to commit, stage only files created or intentionally changed for this task unless the user explicitly asks for more.
