# Content Maturity And Skill Routing

Use this before producing a deck. The goal is to avoid generating polished
slides from immature thinking.

## Maturity Levels

| Level | Input state | Agent action | Skills to use before `.pptx` |
| --- | --- | --- | --- |
| 0. Raw intent | Loose idea, unclear audience, no ask | Clarify decision, audience, tension, and constraints | `grill-me` if stakes are high; `narrative-design` |
| 1. Source pile | Notes, links, research, local files, mixed facts | Extract claims, evidence, assumptions, and gaps | Domain skill if available; web/official docs if current facts matter |
| 2. Narrative draft | Main message exists, but flow is weak | Build red thread and slide-headline storyboard | `narrative-design`; load presentation reference |
| 3. Slide outline | Slides A-Z are named with message/bullets | Convert to deck spec; check brand/visual constraints | `uit-deck-generator`; domain skill for factual review |
| 4. Generated deck | `.pptx` exists but may be rough | Validate layout, placeholders, contrast, density, and narrative | `grill-me` for challenge; `narrative-design` for revision |
| 5. Meeting-ready | Deck supports a specific meeting decision | Prepare talk track, objections, and decision ask | `narrative-design` meeting-prep reference |

## Routing Algorithm

1. If the user asks for a deck but provides only a topic, do not start with
   PowerPoint. First create a one-sentence narrative contract:
   `Because [pressure], [audience] must decide/do [action].`
2. If the source contains technical claims, route to the relevant domain skill
   before writing slide assertions.
3. If there is no relevant skill and the need is recurring, create or update a
   focused skill before continuing. If the need is one-off, write a short local
   reference note instead.
4. If the deck is for leaders, make the first three slides establish:
   - why this matters now
   - what decision is needed
   - what risk/opportunity the leader owns
5. If the content is already a slide outline, use the generator script and keep
   body text short. Put nuance in speaker notes, appendix, or pre-read.
6. If the generated deck has more than one purpose, split it into a main deck
   and support decks instead of making one over-broad deck.

## Skill Creation Rule

Create a missing skill only when all are true:

- the workflow will recur
- local standards or domain knowledge matter
- the task needs more than ordinary reasoning
- a compact `SKILL.md` plus references/scripts can improve future execution

Do not create a skill just to solve one isolated deck.
