---
name: uit-deck-generator
description: Create, improve, or regenerate UiT-branded PowerPoint decks from outlines, markdown notes, meeting narratives, data stories, Fabric/Power BI content, leadership briefings, or slide specs. Use when the user asks for UiT PowerPoint decks, slide decks in vault, UiT template/layout/background/color compliance, deck generation with python-pptx, or a workflow that routes rough content through narrative, review, domain, and meeting-prep skills before producing .pptx files.
---

# UiT Deck Generator

Use this skill to turn source material into UiT-branded `.pptx` decks with a
clear narrative, appropriate maturity checks, and reusable generation scripts.

## Workflow

1. Locate the deck source: outline, markdown, notes, existing deck, or user
   brief.
2. Read [content-maturity-and-skill-routing.md](references/content-maturity-and-skill-routing.md)
   and classify maturity before generating slides.
3. If the deck is not mature enough, use the routed skill first:
   - narrative/storyline: `thinking-planning/narrative-design`
   - hard challenge: `thinking-planning/grill-me`
   - Fabric documentation: `reporting/fabric/fabric-documentation`
   - BOTT/economy model: finance skills
   - Power BI local artifacts: `reporting/powerbi/*`, `reporting/orchestration/*`
   - missing recurring workflow: create/update a focused skill with
     `skill-creator` or `thinking-planning/skill-design`
4. Read [uit-visual-profile.md](references/uit-visual-profile.md) before
   styling. Use official UiT template layouts first; do not invent logo
   variants.
5. Check for a local template. Current known local template:
   `C:\repos\private\Vault\Topics\Fabric_og_okonomirapportering_UiT_mal.pptx`.
   If it is missing, tell the user and ask for a template or use the official
   UiT PowerPoint download source only with approval.
6. Write or derive a JSON deck spec. Use
   [deck-spec-schema.md](references/deck-spec-schema.md).
7. Choose slide types deliberately:
   - `bullets` only for short support points
   - `process` for flows, pipelines, roadmaps, and "from-to-through" logic
   - `hub` for operating models, roles, domains, and governance balances
   - `decision` for choices, trade-offs, and alternatives
   - `table` only when exact role/responsibility comparison is clearer
8. Generate `.pptx` with:

```powershell
python scripts/generate_uit_deck.py --spec deck.json --output output.pptx --template C:\path\to\UiT-template.pptx
```

9. Validate the generated deck:
   - PowerPoint opens with `python-pptx`.
   - no empty placeholders remain.
   - no duplicate zip members remain.
   - slide count and layout names match intent.
   - slides contain simple click animations where content is built up.
   - text does not obviously overflow dense slides.
10. Save generated decks where the user asked. For vault PowerPoint work, prefer:
   `private/Vault/PowerPoint-presentasjoner/<tema>/`.

## Script

Use `scripts/generate_uit_deck.py` for deterministic deck generation. It is a
generic version of the local `generate_decks.py` pattern and supports cover,
bullets, cards, two-column, table, timeline, quote, process, hub, and decision
slides. It also adds actual bullet characters, more line spacing, removes empty
placeholders, and writes simple click-to-appear animations.

Prefer the script for repeatable decks. For one-off manual deck repair, edit
the existing `.pptx` directly with `python-pptx`, but keep the same validation
checks.

## Assets

Official UiT assets bundled for local use:

- `assets/UiT_logo_Bokmaal.zip`
- `assets/UiT_fargekart_CMYK.pdf`
- `assets/uit-logo-bokmal/` extracted logo files

Use assets only according to the UiT visual profile reference. If the official
template already carries logo/master graphics, do not duplicate logos unless
the slide requires it.
