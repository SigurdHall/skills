---
name: uit-powerbi-reporting
description: Build or edit UiT Power BI finance/reporting artifacts, especially Tertialrapport, UiT/PowerBI templates, UiT økonomirapporter, finance dashboards, budget/accounting DAX, as-of reporting, report themes, color conventions, KPI card icons, reporting unit mappings, Rapporteringsenheter, cost center prefix logic, semantic model conventions, and user-facing labels for UiT finance dashboards. Also use before building or rebuilding any UiT økonomirapport page chrome (topptekst, filterlinje, valgknapper, KPI-kort, meny, «Sist oppdatert»): the Ledelsesrapport is the binding house-style reference. Use fabric-powerbi-report-doc instead when the task is to write Markdown documentation describing such a report rather than build or change it.
---

# UiT Power BI Reporting

Use this together with `powerbi-pbip` for UiT-specific Power BI work.

Mechanics (live model/report edits, MCP/Desktop, REST) belong to `skills-for-fabric` (`semantic-model-authoring`, `powerbi-report-authoring`). This skill supplies UiT input — brand, themes/labels, BOTT model, finance conventions — into those, and is not a tooling fallback.

## Scope

Typical repo paths:

- `uit-powerbi-okonomi/scripts/tertialrapport` (Ledelsesrapport generators, the style reference)
- `ws_okonomi_ppu_dev/verktoy/rapport` (Node report generators, render and click tests)
- `UiT/PowerBI/Tertialrapport`
- `UiT/PowerBI/templates`
- `UiT/PowerBI/templates/images`
- `UiT/PowerBI/Okonomi`

Prefer Norwegian user-facing labels in reports. Use English for technical file names only when established by the repo.

## References

For UiT økonomirapporter, budget/accounting DAX, kontorelasjon4 logic, BEVAAR budget versions, as-of dates, forecast logic, or result-area card filters, read the private business reference when it exists:

- `references/private/uit-okonomi-og-strategi-forretningslogikk.md`

Use this reference as the business definition source before changing measures, page filters, visual filters, or explanatory documentation in `UiT/PowerBI/Okonomi`. Do not copy private business content into committed skill files or public references.

## House Style: Ledelsesrapporten Is the Reference

For any new or rebuilt UiT økonomirapport (header, filter bar, choice buttons, KPI cards, panels, menu), read `references/public/husstil-ledelsesrapport.md` before writing a work order, a plan or any PBIR. It is binding and overrides generic design guidance from `powerbi-report-design`:

1. Clone the Ledelsesrapport visuals listed there and rebind fields. Do not redraw them from prose rules such as "follow VP12", and do not copy helpers from other report generators.
2. The header shows «Sist oppdatert» with date and time, never the period. A model without a timestamp gets `gold_status` through the model profile.
3. A functional deviation (Filtrer button, bookmark buttons) keeps the Ledelsesrapport look.
4. Before delivery, render the Ledelsesrapport and the new page at the same size and compare the top 340 px side by side. Static validation and click tests do not check style.

`references/public/okonomi-template-layouts-all.html` is the older layoutkatalog (template catalogue, `1600 x 900`). Use it only for page patterns the Ledelsesrapport does not have. Do not treat the HTML file as report data or as a generated report product.

## UiT Template Rules

1. Inspect the active PBIP project before editing: `.pbip`, `.Report/definition.pbir`, `.Report/definition/report.json`, page `visual.json`, semantic `model.tmdl`, `relationships.tmdl`, and relevant table TMDL files.
2. Keep UiT theme colors consistent across templates when the user asks for shared colors. Change only theme/default colors unless the user explicitly asks for layout or visual changes.
3. Preserve report navigation groups, bookmark names, visual IDs, and registered resource paths unless the task requires changing them.
4. Keep local or generated artefacts out of Git: `.env`, `__pycache__/`, `.pbi` cache/local settings, and `PowerBI/templates/images/.render/`.
5. Register new report pages in `.Report/definition/pages/pages.json`, not only by creating a page folder.
6. Validate changed report JSON with `ConvertFrom-Json`; for complex visuals, state clearly when Power BI Desktop manual validation is still needed.

## UiT Finance Semantic Model Rules

For UiT finance dashboards:

1. Prefer generic base measures for `Regnskap`, `Budsjett`, `Avvik`, ratio, percent variance, and forecast logic. Use visual filters for result areas such as inntekter, kostnader, nettobidrag, and total instead of duplicating the same measure set per area.
2. Never use raw `SUM(fak_okonomi[belop_budsjett])` in visible measures. Budget measures must explicitly select a budget basis/version, for example current `BEVAAR<år>` or approved `BEVAAR<år>_M1`.
3. Apply excluded account logic consistently to both accounting and budget base measures when the report is about operating follow-up. Do not include balance, settlement, tax, bank, receivable/payable, or provision accounts in ordinary result follow-up unless the user asks for a balance/provision analysis.
4. Use `dim_konto[kontorelasjon4]` or `dim_konto[kontorelasjon4_kode]` for result-area filters. Use `dim_prosjekt[prosjekttype_kode]` only when the business definition requires project type scope, such as the nettobidrag BOA/BEV view. BEV (appropriation-funded) project types are `A1`/`A2`/`I1`/`I2`/`I3`; BOA (externally funded) project types share the `Z*` prefix — filter with `prosjekttype_kode IN {...}` for BEV and `LEFT(prosjekttype_kode, 1) = "Z"` for BOA rather than hardcoding the full list in more than one place (centralize as dimension flags if the same filter appears in many measures).
5. Keep page-specific helper measures in a dedicated display folder with a clear numeric prefix, for example `Measures\08 Økonomiutvikling`.
6. Put page-specific as-of assumptions in a small helper measure, for example `Økonomiutvikling as-of dager = 20`, so the assumption can be changed in one place.
7. For disconnected axis, slicer, or legend tables, create separate TMDL table files and register them in `model.tmdl` with both `ref table` and query order when the model uses `PBI_QueryOrder`.
8. `dim_koststed` typically carries the full org rollup as sibling text columns — `fakultet` → `institutt` → `seksjon` (seksjon is a faggruppe-level unit *under* institutt, not a peer of institutt) → `koststed`. Build a user hierarchy on these directly rather than assuming new columns are needed; pick the coded `koststed` column (code + name combined) as the leaf, not the plain name column, since the plain name is not always unique at full grain.
9. "Hittil"-named measures commonly split into two families that look interchangeable but answer different questions: one follows whatever date filter the visual applies (`TOTALYTD`-style), the other is pinned to an explicit valgt år/valgt måned selection independent of visual context (built on a publiseringsdag/as-of cutoff). Disambiguate both families' descriptions explicitly — front-load which one to use in a visual vs. a KPI card — rather than relying on the name to carry the distinction; see `orchestration/semantic-model-migration`'s `ai-readiness.md` for the method.

## UiT Finance Report Patterns

Use these defaults unless the report or user request says otherwise:

- Use a `1920 x 960` canvas with FitToPage for UiT finance reports. Older `1600 x 900` templates are not the target size.
- Keep Norwegian labels in report visuals, page names, slicers, and card titles.
- Colors follow UiT's graphic profile only: yellow `#F2A900` is regnskap and merforbruk, dark blue `#003349` is budsjett hittil, blue `#007396` is årsbudsjett and mindreforbruk, light blue `#59BEC9` is prognose. Red `#CB333B` is reserved for Investeringer - KD and is not a budget or warning color.
- Keep main trend graphs free of result-area filters when they are intended to show total selected report context; put kontorelasjon4 filters on cards or area-specific visuals.
- For card groups showing result areas, make filters explicit on the visual and verify them statically in JSON.
- Update the business logic documentation when DAX or report behavior changes the interpretation of accounting, budget, forecast, as-of dates, account exclusions, or filter semantics.

## Reporting Units

For UiT finance reporting, a common mapping table is `Rapporteringsenheter`:

- Key: `Koststed`
- Identifier: `Rapporteringsenhet`
- Text: `Rapporteringsenhet_tekst`
- Supporting descriptions: `Koststed_tekst`, `Fakultet_tekst`

Common rule pattern:

- Match the longest approved `Koststed` prefix first.
- Assign `Rapporteringsenhet` and `Rapporteringsenhet_tekst` from the local mapping table.
- Fall back to `[Fak]` / `[Fakultet_tekst]` only when no specific reporting-unit mapping exists.

Use prefix logic when the user says cost centers are "under" a code. Do not interpret that as `Fak = <code>` unless the user explicitly says the faculty field should drive it.

Exact internal mapping examples, if needed locally, belong in `references/private/reporting-units.md`.

## KPI Icons

UiT KPI/card icon style:

- Small square icon tile, about 48x48.
- Light background, subtle border, rounded corners.
- Thin black line icon, no heavy fill.
- Use SVG originals for scalability and PNG copies when Explorer thumbnails are needed.
- Store reusable icons under `UiT/PowerBI/templates/images`.
- Keep a manifest with source file and display name when generating many icons.

Recommended validation:

```powershell
$failed = @()
Get-ChildItem -LiteralPath "UiT/PowerBI/templates/images" -Filter *.svg |
  ForEach-Object {
    try { [xml](Get-Content -Raw -LiteralPath $_.FullName) | Out-Null }
    catch { $failed += $_.Name }
  }
if ($failed.Count -eq 0) { "SVG XML: OK" } else { $failed }
```

## Before Finishing

- Run JSON validation for changed report JSON files.
- Run BOM check for `.json`, `.tmdl`, `.pbip`, `.pbir`, `.platform`, and theme files.
- For semantic model edits, check that calculated tables are registered in `model.tmdl`.
- For new pages, check that the page is registered in `pages/pages.json`.
- For visual filters, statically verify the expected fields and values in `visual.json`.
- Run `git diff --check` on changed PBIP/PBIR/TMDL/JSON and documentation files.
- Check `git status --short` and make sure secrets, local caches, and generated render folders are not staged.
