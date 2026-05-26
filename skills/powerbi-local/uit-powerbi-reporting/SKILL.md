---
name: uit-powerbi-reporting
description: Use for UiT Power BI finance/reporting work, especially Tertialrapport and templates under UiT/PowerBI, UiT color/theme conventions, KPI card icons, reporting unit mappings, and semantic model conventions for UiT finance dashboards.
---

# UiT Power BI Reporting

Use this together with `powerbi-pbip` for UiT-specific Power BI work.

## Scope

Typical repo paths:

- `UiT/PowerBI/Tertialrapport`
- `UiT/PowerBI/templates`
- `UiT/PowerBI/templates/images`

Prefer Norwegian user-facing labels in reports. Use English for technical file names only when established by the repo.

## UiT Template Rules

1. Inspect the active PBIP project before editing: `.pbip`, `.Report/definition.pbir`, `.Report/definition/report.json`, page `visual.json`, semantic `model.tmdl`, `relationships.tmdl`, and relevant table TMDL files.
2. Keep UiT theme colors consistent across templates when the user asks for shared colors. Change only theme/default colors unless the user explicitly asks for layout or visual changes.
3. Preserve report navigation groups, bookmark names, visual IDs, and registered resource paths unless the task requires changing them.
4. Keep local or generated artefacts out of Git: `.env`, `__pycache__/`, `.pbi` cache/local settings, and `PowerBI/templates/images/.render/`.

## Reporting Units

For UiT finance reporting, a common mapping table is `Rapporteringsenheter`:

- Key: `Koststed`
- Identifier: `Rapporteringsenhet`
- Text: `Rapporteringsenhet_tekst`
- Supporting descriptions: `Koststed_tekst`, `Fakultet_tekst`

Common rule pattern:

```DAX
LEFT(FORMAT([Koststed], "0"), 6) = "340320" -> 340320 / "BFE-fartøydrift"
LEFT(FORMAT([Koststed], "0"), 4) = "2627" -> 2627 / "BEA"
else -> [Fak] / [Fakultet_tekst]
```

Use prefix logic when the user says cost centers are "under" a code. Do not interpret that as `Fak = <code>` unless the user explicitly says the faculty field should drive it.

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
- Check `git status --short` and make sure secrets, local caches, and generated render folders are not staged.
