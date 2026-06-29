---
name: semantic-model-metadata
description: Conventions for documenting Power BI/Fabric semantic model measures and columns for distribution — description property (business meaning, vises i tooltip/Copilot/fabriciq), DAX comments (kun syntaks/hvorfor), and annotations (machine-readable lineage/governance). Use ALONGSIDE semantic-model-authoring whenever you write, add, edit, or refactor a measure/column/DAX: authoring does the edit, this defines the description/lineage standard. Empty is allowed; what is written must meet the standard. Triggers: add measure, edit measure, write DAX, refactor DAX, measure description, document measure, measure metadata, lineage, displayFolder, annotation owner/status, DAX comments, certified measure, distributable model docs, AI/Copilot readiness, dokumenter mål, beskrivelse, eierskap.
---

# Semantic Model Metadata

Conventions for where measure/column documentation goes in a distributable model.
Editing is done with `semantic-model-authoring` (Fabric); this skill defines the
standard it follows. No presence requirement — empty is fine; what is written
must meet the standard below.

## Three layers, one job each

1. `description` (TMDL) — business meaning, source of truth. Shows in tooltip,
   model view, Copilot, fabriciq. Write what the measure answers, grain, sign,
   one limitation. Not syntax.
2. DAX comments (`//`, `/* */`) — only what syntax cannot say: why a CALCULATE,
   KEEPFILTERS, edge cases, as-of logic. Never repeat the `description`.
3. `annotation` (TMDL) — machine-readable lineage/governance. Source, owner,
   status, last reviewed. Validatable and syncable; not shown to end users.

## Standard if written

- `description`: Norwegian, full sentence, business language. Include grain and
  sign when ambiguous. No DAX, no table.column refs.
- Comment: explains a choice, not the obvious. One line where possible.
- `displayFolder`: group visible measures; helpers in `_helpers`.
- Helpers: prefixed, `isHidden`, no end-user description needed.
- `lineageTag`: preserve; never regenerate.
- annotations use fixed keys: `kilde`, `eier`, `status`, `sist_gjennomgatt`.
  `status` ∈ {draft, review, certified}. `sist_gjennomgatt` = YYYY-MM.

## Example

```tmdl
measure 'Netto resultat' = [Inntekt] - [Kostnad]
    description = "Netto resultat per rapporteringsenhet. Grain: måned. Positiv = overskudd. Ekskluderer interne posteringer."
    displayFolder: Resultat
    formatString: #,0
    annotation kilde = BOTT/regnskap
    annotation eier = okonomi
    annotation status = certified
    annotation sist_gjennomgatt = 2026-06
    // CALCULATE-wrap nuller kontorelasjon4-filter; uten dette dobbeltteller helpers
```

## Rules

- Lineage goes in annotations, not comments — comments may be lost in
  optimization and cannot be validated.
- Skip rather than write filler. A weak description is worse than none.
- For UiT finance specifics defer to `uit-powerbi-reporting`.
