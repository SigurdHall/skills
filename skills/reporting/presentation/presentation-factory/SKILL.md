---
name: presentation-factory
description: Use this skill when creating premium HTML-first presentations, PowerPoint/PPTX exports, visual slide decks, branded or non-work presentation systems, image-led decks, or reusable presentation workflows with staged outline, visual direction, layout review, controlled image generation, HTML build, hybrid PPTX export, and QA.
---

# Presentation Factory

Use the local presentation factory at `C:\repos\presentation-factory`.

## Trigger Scope

Use for:

- premium visual presentations
- HTML-first slide decks
- branded or non-work slide decks
- existing PowerPoint decks used as content sources
- image-led presentation design
- hybrid PPTX export from structured sources
- reusable presentation workflows with stage gates

Use `uit-deck-generator` instead when the user specifically asks for UiT-branded PowerPoint template compliance.

## Workflow

1. Read `C:\repos\presentation-factory\AGENTS.md`.
2. Work from source files in:
   - `content/deck.yaml`
   - `content/visuals.yaml`
   - `themes/*/theme.json`
   - `src/`
3. Follow the staged workflow:
   - import existing PPTX text when a source deck is provided
   - outline
   - visual direction
   - visual plan
   - layout plan
   - slide-by-slide form review
   - approved image prompts
   - low/high HTML build
   - HTML preview rendering
   - HTML visual QA before calling high-fidelity HTML finished
   - PPTX export from HTML snapshots when visual parity matters
   - PPTX preview export
   - HTML/PPTX parity QA
   - final preview QA
4. Use the project-local skills under `.agents/skills/` when their trigger scope matches the task.
5. Use `$imagegen` only after form review approves generated visual assets and safe zones exist.

## Do Not

- Do not treat generated HTML, PPTX, PDF, screenshots or generated images as source of truth.
- Do not generate final images before the high-fidelity gate passes.
- Do not put confidential data, personal data, exact internal cases, official logos, exact chart values or slide text into image prompts.
- Do not use a heavy frontend framework unless the user explicitly changes the setup goal.

## Commands

Run from `C:\repos\presentation-factory`:

```powershell
python scripts/import_pptx_text.py --input "C:\path\to\source.pptx" --markdown "output\imported-outline.md" --yaml "output\imported-deck-draft.yaml" --title "Draft title"
npm install
npm run validate
npm run html:low
npm run html:high
npm run previews
npm run qa:html
npm run build
npm run previews:pptx
npm run qa:pptx
npm run check
```

If Node/npm or preview tools are missing, report the exact skipped command and the reason.

## PPTX Visual Parity

When the user expects the PowerPoint file to match the high-fidelity HTML:

1. Build HTML first.
2. Render per-slide HTML screenshots with `npm run previews`.
3. Run `npm run qa:html` and fix high-fidelity HTML overflow or safe-zone issues before continuing.
4. Build PPTX with `npm run build`.
5. Export PPTX slides with `npm run previews:pptx`.
6. Compare HTML and PPTX with `npm run qa:pptx`.

If `npm run build` reports `native_hybrid_fallback`, do not claim the PPTX matches HTML. Re-run the workflow so HTML slide screenshots exist before the PPTX build.
