# Reporting Skills

Top-level group for everything that turns Fabric/Power BI data into delivered
reporting: Power BI project files, semantic-model docs, HTML reports,
end-to-end orchestration, UiT norms, and private business data.

Categories:

- `powerbi/` — pure Power BI file skills (PBIP/PBIR/TMDL, metadata).
- `presentation/` — HTML/static report builders + slide decks.
- `orchestration/` — end-to-end processes that pull mechanics from
  `skills-for-fabric` and other skills into a full report.
- `fabric/` — Fabric documentation skills (architecture, model, lakehouse,
  data contract, cicd, delta-sharing).
- `norms/` — UiT + finance/BOTT conventions (model, DAX, theme, labels).
- `*/private/` — per-skill business data, **gitignored** (see Backup).

Current skills:

- powerbi: `powerbi-pbip`, `semantic-model-metadata`
- presentation: `html-report-builder`, `presentation-factory`, `uit-deck-generator`
- orchestration: `pbip-full-report`, `powerbi-report-production-loop`
- fabric: `fabric-documentation` (hub) + doc-type skills
- norms: `uit-powerbi-reporting`, `uit-bott-okonomimodell`, `bott-semantic-model`, `finance-bi-dax-patterns`

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
  rules from `norms/uit-powerbi-reporting`.
- Report layout, MCP/Desktop available → `powerbi-report-authoring` (Fabric) +
  UiT theme/labels from `norms/uit-powerbi-reporting`.
- Offline / no MCP, raw PBIP/PBIR/TMDL edit → `powerbi/powerbi-pbip` (fallback).
- Build a complete report end to end → `orchestration/pbip-full-report`, pulling
  mechanics from Fabric skills.
- Tableau → Power BI migration → `orchestration/powerbi-report-production-loop`.
- Static HTML report from YAML/SQL/Parquet → `presentation/html-report-builder`.
- Measure/column docs, lineage, annotations → `powerbi/semantic-model-metadata`
  (conventions) + `semantic-model-authoring` (edit).
- Any DAX/measure write → pair `semantic-model-authoring` (mechanics) with
  `powerbi/semantic-model-metadata` (description/lineage standard).
- Any UiT finance/økonomi specifics → `norms/uit-powerbi-reporting`.
- Finance/BOTT model semantics → `norms/uit-bott-okonomimodell`; star-schema →
  `norms/bott-semantic-model`; finance DAX → `norms/finance-bi-dax-patterns`.
- Write Markdown docs about a Fabric/Power BI item → `fabric/*` (hub:
  `fabric/fabric-documentation`), not the build skills above.
- Slide decks → `presentation/uit-deck-generator` (PPTX), `presentation/presentation-factory` (HTML).

Rule: generic Power BI mechanics → `skills-for-fabric`; this group stays focused
on UiT conventions, offline fallback, and orchestration.

## Private business data

Each skill may keep sensitive data under its own `private/` folder, e.g.
`reporting/<category>/<skill>/private/`. These folders are gitignored
(`skills/reporting/**/private/`) and never committed.

## Backup

Back up `private/` data into the UiT repo (`c:\repos\UiT`), the sanctioned store
for sensitive UiT material. Copy, do not symlink; keep skill folders portable.
Never commit private business data to this skills repo.
