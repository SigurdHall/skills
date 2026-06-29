# Power BI Local Skills

Skills in this folder support local Power BI/Fabric project files, PBIP/PBIR,
TMDL, report JSON, themes, bookmarks, templates, and UiT-specific report
standards.

Use these skills when editing or documenting local Power BI projects before
publishing to Power BI Service or Fabric.

Current skills:

- `pbip-full-report`
- `powerbi-pbip`
- `powerbi-report-production-loop`
- `uit-powerbi-reporting`

## Ownership boundary (avoid two truths)

- **Mechanics (live tooling) → `skills-for-fabric`.** Use the Microsoft skills
  for MCP-driven model edits, PBIR/report-author CLI, Power BI Desktop
  reload/screenshot, and workspace REST. Do not re-document these here.
  Relevant: `semantic-model-authoring`, `semantic-model-consumption`,
  `powerbi-report-authoring`, `powerbi-report-planning`, `powerbi-report-design`,
  `powerbi-report-management`.
- **UiT domain + offline fallback → this group.** Finance conventions, BOTT
  model, themes/labels, encoding/BOM rules, and pure-file PBIP editing when no
  MCP/Desktop bridge is available.

## Routing

- Model / measures, MCP available → `semantic-model-authoring` (Fabric) + UiT
  rules from `uit-powerbi-reporting`.
- Report layout, MCP/Desktop available → `powerbi-report-authoring` (Fabric) +
  UiT theme/labels from `uit-powerbi-reporting`.
- Offline / no MCP, raw PBIP/PBIR/TMDL edit → `powerbi-pbip` (fallback).
- Build a complete report end to end → `pbip-full-report` for UiT structure,
  delegating mechanics to the Fabric skills.
- Tableau → Power BI migration → `powerbi-report-production-loop`.
- Any UiT finance/økonomi specifics → always `uit-powerbi-reporting`.

Rule: if a step is generic Power BI mechanics, prefer the `skills-for-fabric`
skill; keep local skills focused on UiT conventions and offline fallback.
