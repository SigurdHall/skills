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

1. `description` (TMDL `///` line above the object) — business meaning, source of
   truth. People see it as the tooltip in the Data pane, Model Explorer, DAX query
   view and model view. DAX query view Copilot reads only the first 200 characters.
   Copilot data questions work from Prep data for AI (AI data schema, AI
   instructions, verified answers), and they and the Fabric data agent accept
   English only. Not syntax.
2. DAX comments (`//`, `/* */`) — only what syntax cannot say: why a CALCULATE,
   KEEPFILTERS, edge cases, as-of logic. Never repeat the `description`.
   Copilot's description generator ignores comments.
3. `annotation` (TMDL) — machine-readable lineage/governance. Source, owner,
   status, last reviewed. Validatable and syncable; never shown to users and not
   read by any AI feature.

## Description template

One `///` line, Norwegian bokmål, plain statements, parts in this order:

1. Definisjon (required on visible measures, max 120 characters): what the number
   is. Start with the thing measured, give sign or unit when ambiguous. Never a
   question, never the name repeated.
2. Tid: which time table changes the value, e.g. `Følger dim_periode, ikke dim_dato.`
   or `Følger bare år i dim_periode, ikke dim_dato.` Generate it from a live
   grouping test when one exists.
3. Omfang: `Blank per …` (dimensions a guard blanks), `Summerer ikke over …`
   (members double count), `Deles ikke på …` (dimensions the value ignores). At
   most four business names, then `med flere`, so a short list never reads as
   complete. Generate from the test when one exists.
4. Bruk (optional): which sibling measure to use, and when. Starts `Bruk` or
   `Standardmål for`.
5. Innhold (optional): inclusions, exclusions, versions, codes staff use.
6. Merk (optional): one temporary data problem, stated as its consequence.

Definisjon, Tid and the first Omfang sentence end within 200 characters; the whole
line stays within 400. Write a TMDL description as one line: serializers rewrap
long `///` blocks at 80 characters.

## Standard if written

- No DAX, brackets, quoted names or table.column refs. Exception: when a model has
  both a period table and a date table with overlapping columns (år, tertial,
  periode), name the two tables in the Tid phrase, because users see those table
  names in the Data pane.
- If the DAX removes all filters (`REMOVEFILTERS ( )`), say `du har tilgang til`:
  RLS still applies.
- A measure that reaches a dimension through only some of its facts shows a
  misleading number there. Blank it on that dimension (`ISFILTERED` guard, not
  `ISCROSSFILTERED`, which also fires on dimensions that other dimensions filter)
  and state it in Omfang.
- Comment: explains a choice, not the obvious. One line where possible.
- `displayFolder`: group visible measures; helpers in `_helpers`.
- Helpers: `_` prefix, `isHidden`, one sentence starting `Hjelpemål:`. DAX query
  view Copilot reads hidden objects too.
- `lineageTag`: preserve; never regenerate. New objects get new GUIDs.
- annotations use fixed keys: `kilde` (the fact tables the DAX reads), `status` ∈
  {draft, review, certified}, `sist_gjennomgatt` = YYYY-MM, and `eier` once on the
  model, repeated on a measure only when it differs.

## Example

```tmdl
	/// Budsjett minus driftsregnskap. Positivt tall er mindreforbruk. Følger dim_periode, ikke dim_dato. Blank per budsjettprofil, leverandør, kunde med flere. Standardmål for budsjettavvik.
	measure Avvik =
			// Budsjett og regnskap deler ikke leverandør eller budsjettprofil; blank heller enn feil tall.
			IF (
				NOT [_Budsjett og regnskap utenfor omfang],
				[Budsjett] - [Driftsregnskap]
			)
		formatString: #,##0
		displayFolder: _Measures\Budsjett\Avvik
		lineageTag: 414eaaab-2e2b-46f0-8b48-96e726c6b9aa

		annotation kilde = fak_budsjett, fak_regnskap
		annotation status = review
		annotation sist_gjennomgatt = 2026-09
```

## Rules

- Lineage goes in annotations, not comments — comments may be lost in
  optimization and cannot be validated.
- Skip rather than write filler. A weak description is worse than none.
- For UiT finance specifics defer to `uit-powerbi-reporting`.
