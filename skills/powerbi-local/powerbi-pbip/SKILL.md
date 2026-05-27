---
name: powerbi-pbip
description: Safely edit, inspect, validate, or explain local Power BI/Fabric PBIP/PBIR projects, report JSON, semantic model TMDL, relationships, measures, calculated tables, themes, bookmarks, groups, visual containers, templates, and .pbit preparation. Use when the user mentions PBIP, PBIR, TMDL, .platform, definition.pbir, report.json, visual.json, Power BI project files, page sizes, visual positions, UTF-8 BOM errors, or asks to modify a local Power BI report/model.
---

# Power BI PBIP

## Core Rules

1. Treat PBIP/PBIR files as structured project files. Inspect relevant `*.pbip`, `definition.pbir`, `definition/report.json`, `definition/pages/**/page.json`, `visual.json`, bookmarks, and theme files before changing them.
2. Preserve existing IDs, bookmark targets, visual names, group names, and relative paths unless the task explicitly requires changing them.
3. Save JSON, TMDL, PBIP, PBIR, `.platform`, and theme files as UTF-8 without BOM. Power BI can fail on BOM-prefixed files.
4. Validate JSON after edits. Do not rely only on visual inspection.
5. For copied PBIP templates, keep `.pbip` report paths and `definition.pbir` dataset paths relative and consistent with the new location.
6. Check semantic model `definition/database.tmdl` compatibility level when copying models between PBIP projects. Do not request a lower compatibility level than the local Power BI database/cache already has.
7. For semantic model edits, inspect `definition/model.tmdl`, `definition/relationships.tmdl`, and relevant `definition/tables/*.tmdl` before changing measures, calculated tables, or relationships.
8. Before committing PBIP work, check that local artefacts are ignored: `.env`, `__pycache__/`, `*.py[cod]`, `.pbi/cache.abf`, `.pbi/localSettings.json`, generated render/cache folders, and any temporary export folders.

## Encoding

PowerShell 5.1 `Set-Content -Encoding UTF8` and `Out-File -Encoding utf8` can write UTF-8 with BOM. Avoid them for PBIP/PBIR/JSON/TMDL/`.platform` files.

Use one of these instead:

```powershell
$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
[System.IO.File]::WriteAllText($path, $content, $utf8NoBom)
```

or, if PowerShell 7+ is confirmed:

```powershell
Set-Content -LiteralPath $path -Value $content -Encoding utf8NoBOM
```

For manual edits, prefer `apply_patch`; after any PowerShell rewrite, explicitly scan for BOM.

## BOM Check

Run this after editing PBIP/PBIR/JSON/TMDL/`.platform` files:

```powershell
Get-ChildItem -Recurse -File |
  Where-Object { $_.Extension -in @(".json", ".pbip", ".pbir", ".tmdl") -or $_.Name -eq ".platform" } |
  ForEach-Object {
    $bytes = [System.IO.File]::ReadAllBytes($_.FullName)
    if ($bytes.Length -ge 3 -and $bytes[0] -eq 0xEF -and $bytes[1] -eq 0xBB -and $bytes[2] -eq 0xBF) {
      $_.FullName
    }
  }
```

If any paths are returned, rewrite those files as UTF-8 without BOM:

```powershell
$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
Get-ChildItem -Recurse -File |
  Where-Object { $_.Extension -in @(".json", ".pbip", ".pbir", ".tmdl") -or $_.Name -eq ".platform" } |
  ForEach-Object {
    $bytes = [System.IO.File]::ReadAllBytes($_.FullName)
    if ($bytes.Length -ge 3 -and $bytes[0] -eq 0xEF -and $bytes[1] -eq 0xBB -and $bytes[2] -eq 0xBF) {
      $text = [System.IO.File]::ReadAllText($_.FullName)
      [System.IO.File]::WriteAllText($_.FullName, $text, $utf8NoBom)
    }
  }
```

## JSON Validation

Validate changed JSON files:

```powershell
$failed = @()
Get-ChildItem -Recurse -Filter *.json |
  ForEach-Object {
    try { Get-Content -Raw -LiteralPath $_.FullName | ConvertFrom-Json | Out-Null }
    catch { $failed += $_.FullName }
  }
if ($failed.Count -eq 0) { "OK all JSON files parsed" } else { $failed }
```

## TMDL Model Edits

When editing semantic models:

1. Add calculated tables as separate `definition/tables/<TableName>.tmdl` files.
2. Register every table in `definition/model.tmdl` with `ref table <TableName>`.
3. Add relationships in `definition/relationships.tmdl` using stable GUIDs and existing naming style.
4. Keep `sourceColumn` aligned with calculated table output column names.
5. Use `summarizeBy: none` for identifier columns that should not aggregate.
6. Preserve lineage tags in existing objects. For new objects, create new GUIDs and do not reuse IDs.
7. After TMDL edits, run BOM checks on `.tmdl`, `.pbip`, `.pbir`, `.json`, and `.platform`.

Common calculated table pattern:

```DAX
VAR Base =
    SUMMARIZE(
        DimensionTable,
        DimensionTable[Key],
        "Label", MAX(DimensionTable[Label])
    )
RETURN
    SELECTCOLUMNS(
        ADDCOLUMNS(Base, "DerivedColumn", <expression>),
        "Key", [Key],
        "Label", [Label],
        "DerivedColumn", [DerivedColumn]
    )
```

For custom visuals and field parameters:

- Inspect the visual `queryState` and `fieldParameters` in `visual.json`.
- Do not assume a field well name matches the UI label. Confirm fields under roles such as `Category`, `Value`, `TargetValue`, `VeryGood`, or `Maximum`.
- If a measure is used only to control scale/axis, keep it semantically separate from visible business measures.

## PBIP Template Checklist

When copying or moving a Power BI template:

1. Move or copy the `.pbip`, `.Report`, and `.SemanticModel` together.
2. Update `.pbip`:
   - `artifacts[0].report.path`
3. Update `.Report/definition.pbir`:
   - `datasetReference.byPath.path`
4. Update `.Report/.platform` and `.SemanticModel/.platform` display names if creating a distinct template.
5. Keep theme references aligned between:
   - `.Report/definition/report.json`
   - `.Report/StaticResources/RegisteredResources/*.json`
6. Check page size in every `page.json`.
7. If scaling layout, scale visual and group `position.x`, `position.y`, `position.width`, and `position.height` consistently.
8. Validate bookmarks after renaming groups or filter panels.
9. Check `SemanticModel/definition/database.tmdl`. If Power BI reports `PFE_IMBI_DB_COMPLEVEL_DOWNGRADE` or says current `CompatibilityLevel` is higher than requested, raise the requested level in `database.tmdl` to the current level, for example from `1600` to `1601`.
10. Run JSON validation and BOM check before reporting completion.

## Power BI Layout Notes

For UiT finance/reporting templates:

- Use `1600 x 900` unless the user requests another canvas.
- Keep red and orange out of automatic `dataColors` unless they are intentionally semantic.
- Use red/orange for deviations, risk, warning, and threshold breaches.
- Preserve filter-menu buttons, bookmark actions, and hidden panel states when changing layout.
