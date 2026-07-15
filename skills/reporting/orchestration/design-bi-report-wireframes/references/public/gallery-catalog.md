# BI gallery and design reference catalog

Use galleries to learn patterns, not to copy artifacts. Record the URL, access
date, license/terms, selected principle, and transformation in an inspiration
ledger.

## Structured or reusable sources

| Source | Best use | Rights/handling |
|---|---|---|
| [Microsoft SamplePBIP](https://github.com/microsoft/Analysis-Services/tree/master/pbidevmode/fabricps-pbip/SamplePBIP) | inspect PBIP/PBIR/TMDL structure and bindings | repository license applies; pin commit |
| [Power BI Desktop samples](https://github.com/microsoft/powerbi-desktop-samples) and [Learn sample datasets](https://learn.microsoft.com/en-us/power-bi/create-reports/sample-datasets) | official report/sample patterns | inspect per-sample terms; some linked samples have separate terms |
| [DAX Lib](https://github.com/daxlib/daxlib) | open DAX/TMDL function corpus and contribution patterns | MIT; UDFs are not ordinary measures |
| [Tabular Editor Scripts](https://github.com/TabularEditor/Scripts) | measure-generation automation patterns | MIT; generated output still needs semantic review |
| [Power BI theme JSON schema](https://github.com/microsoft/powerbi-desktop-samples/tree/main/Report%20Theme%20JSON%20Schema) | target-specific Power BI theme validation | official schema; do not treat it as cross-target design tokens |
| [Fluent UI](https://github.com/microsoft/fluentui), [Tremor](https://github.com/tremorlabs/tremor), [shadcn/ui dashboard blocks](https://ui.shadcn.com/blocks?category=dashboard), [Tabler](https://github.com/tabler/tabler), [AdminLTE](https://github.com/ColorlibHQ/AdminLTE) | React/HTML component, state, and responsive patterns | mostly MIT/Apache-2.0; check assets and current package license separately |
| [Apache Superset](https://github.com/apache/superset) | open analytical UI patterns and dashboard behavior | Apache-2.0 |

## Visual inspiration sources

The [Microsoft Fabric Community Galleries](https://community.fabric.microsoft.com/t5/Galleries/ct-p/PBI_Comm_Galleries)
are dynamic. Spot checks on 2026-07-14 showed approximately:

- Data Stories: 13.3k posts
- Themes: 5.6k posts
- Contests: 3.2k posts
- QuickViz: 1.2k posts
- [Quick Measures](https://community.fabric.microsoft.com/t5/Quick-Measures-Gallery/bd-p/QuickMeasuresGallery): 1.1k posts
- Notebook: about 190 posts
- Translytical Task Flow: about 30 posts
- Visual Calculations and [TMDL](https://community.fabric.microsoft.com/t5/TMDL-Gallery/bd-p/pbi_tmdlgallery): about 20 posts each

These are post counts, not unique, licensed, production-ready artifacts. There
is no blanket right to copy formulas, screenshots, themes, or attachments.
Counts are a dated discovery snapshot only. Refresh the live gallery before
citing them in a new delivery; never use count changes as design or popularity
evidence. Automated refresh is not implemented in this skill.

Also useful for visual study:

- [Maven Analytics Showcase](https://mavenshowcase.com/) and its
  [portfolio guidance](https://help.mavenanalytics.io/en/articles/6792558-what-makes-a-great-portfolio-project)
- [Dashboard Design Patterns](https://dashboarddesignpatterns.github.io/patterns.html),
  a research-derived pattern catalog based on 144 dashboards
- [Metabase examples](https://www.metabase.com/examples) for screenshot-level
  comparison only unless the underlying asset license is explicit

## Reference-only sources

- [DAX Patterns](https://www.daxpatterns.com/patterns/): use the taxonomy and
  concepts; do not reproduce protected prose or formulas.
- [`data-goblin/power-bi-agentic-development`](https://github.com/data-goblin/power-bi-agentic-development):
  GPL-3.0 repository metadata conflicts with restrictive README language. Use
  only aggregate observations unless rights are clarified.

## Selection rubric

Choose references by relevance, evidence quality, recency, machine readability,
license clarity, and diversity of source. Prefer two or three strong references
over a mood-board dump. GitHub sources should be accessed through supported API
or clone workflows, pinned to commits, and rate-limited; do not crawl search or
raw/tree pages against robots guidance.
