# Fabric item routing matrix

This is a routing snapshot, not an API contract. Verify the installed skills and
the current Microsoft item-management matrix at the start of every authoring
run.

## Ownership rule

- This skill: item identification, capability gate, dependency order, mutation
  safety, verification, and recovery evidence.
- `skills-for-fabric`: current item-specific mechanics and API payloads.
- `reporting/fabric/*`: documentation artifacts, not live authoring.
- `reporting/orchestration/*`: report-domain workflows that compose mechanics.

## Coverage snapshot (2026-09-03)

Two versioned `skills-for-fabric` sources exist. Select one per run and record
its version and commit in the handoff.

- Claude Code (local and cloud): the vendored copy under `.claude/skills/`
  (26 skills, unprefixed names) with shared references under `.claude/common/`,
  pinned by `.claude/skills-for-fabric.vendor.json` (tag `v0.3.14`, commit
  `714ea2f...`). Refresh with `scripts/vendor_skills_for_fabric.py --tag <tag>`.
  The `fabric-collection` marketplace is declared in `.claude/settings.json`
  for on-demand plugin installs only; do not enable the plugins next to the
  vendored copy, because Claude Code loads the prefixed
  (`fabric-skills:<skill>`) and unprefixed skills side by side.
- Codex on Windows: the `C:\repos\skills-for-fabric` checkout exposed through
  `.agents/skills` junctions. Last recorded at `0.3.5` (`a2332f...`). Update it
  deliberately to the same tag before mixing outputs across tools.

Since `0.3.5`, upstream merged the separate authoring, consumption, and
operations skills into one `{item}-cli` skill per item with internal modes,
removed `check-updates` and `semantic-model-consumption`, and added skills for
SQL Database, Variable Library, Event Schema Set, deployment pipelines, and Git
integration. The names below are the `v0.3.14` names.

| Fabric item or task | Primary skill (plugin bundle) | Coverage note |
|---|---|---|
| Power BI report | `powerbi-report-planning`, `powerbi-report-design`, `powerbi-report-authoring`, `powerbi-report-management` (`powerbi-authoring`) | PBIR/PBIP file mechanics need the `powerbi-report-author` and `powerbi-desktop` CLIs; report item CRUD uses `az rest` |
| Semantic model | `semantic-model-authoring` (both bundles); `fabriciq` (`fabric-skills`) for read-only DAX and natural-language questions | Model changes via the modeling MCP or TMDL; read-back via DAX `INFO` functions |
| Notebook, Spark, Lakehouse engineering, Materialized Lake Views | `spark-cli` (authoring, consumption, operations modes) | MLV lifecycle is folded in; `mlv-operations-cli` no longer exists |
| Data Pipeline for Notebook/Spark orchestration | `spark-cli` plus `ITEM-DEFINITIONS-CORE.md` | Partial mutation route only for a bounded, documented `TridentNotebook` orchestration (and documented Variable Library references); other activity families remain plan-only until a dedicated skill exists |
| Warehouse, Lakehouse SQL analytics endpoint, Mirrored Database queries | `sqldw-cli` (authoring, consumption, operations modes) | Use the authoring mode only for write operations |
| SQL Database item | `sqldb-cli` (authoring, consumption, operations modes) | OLTP engine; distinct from Warehouse |
| Dataflow Gen2 | `dataflows-cli` (authoring, consumption, save-as upgrade modes) | Includes definitions, connections, and refresh monitoring |
| Eventstream | `eventstream-cli` (authoring, consumption modes) | Graph topology requires item-specific validation |
| Eventhouse / KQL Database | `eventhouse-cli` (authoring, consumption modes) | KQL commands and queries have different mutation boundaries |
| Event Schema Set | `eventschemaset-cli` | Preview delegated-identity constraints apply |
| Activator / Reflex | `activator-cli` (authoring, consumption modes) | Human confirmation is required for external notifications/actions |
| Fabric IQ ontology | `fabriciq-ontology-cli` (authoring, consumption modes) | Preview capability; verify current limits |
| Variable Library | `variable-library-cli` | Definitions, value sets, active value set |
| Deployment pipelines | `deployment-pipelines-authoring-cli` | Stage deploys are long-running operations; one operation per pipeline at a time |
| Workspace Git integration | `git-integration-operations-cli` | Connect, commit, update, status, conflicts; not `fabric-cicd` |
| Cross-workspace discovery | `search-consumption-cli` | Read-only discovery before routing |
| Azure Monitor telemetry into Fabric | `azmon-mirroredcatalogs-operations-cli` | Operations onboarding, not a generic item builder |
| Migration into Fabric (Databricks, Synapse, HDInsight, ADF pipelines) | `databricks-migration`, `synapse-migration`, `hdinsight-migration`, `pipeline-migration` | Not for Tableau to Power BI; use `reporting/orchestration/*` |
| Platform planning | `e2e-medallion-architecture`, `e2e-fabric-cost-estimation` | Planning skills, not item mutation |

## Definition references are not authoring skills

`skills-for-fabric/common/ITEM-DEFINITIONS-CORE.md` describes definition parts
for many item types, including notebooks, pipelines, reports, semantic models,
lakehouses, environments, variable libraries, event items, GraphQL, graph
models, mirrored databases, and Reflex. Use it after routing, but do not infer a
safe lifecycle workflow solely from a documented definition shape.

## Missing or thin dedicated coverage

As of this snapshot, treat these as capability-gated gaps rather than generic
REST work:

- Data Pipeline beyond Notebook/Spark orchestration, and Copy Job end-to-end authoring
- Environment item lifecycle
- KQL Dashboard and KQL Queryset authoring
- Mirrored database setup and validation
- GraphQL API and Graph Model lifecycle
- Machine learning and Data Agent items
- workspace, capacity, and tenant-admin orchestration

Create a narrow skill only when a recurring gap has an official, testable
contract. Keep the router small.

## Namespace hygiene

Plugin bundles namespace their skills (`fabric-skills:spark-cli`), while the
vendored copy, a loose checkout, or a junction exposes the unprefixed name.
Claude Code does not deduplicate across these, and both bundles carry
`semantic-model-authoring`. Select one versioned source per run and record its
tag or commit; duplicate discovery names are not additional capability. When
availability is uncertain, run `scripts/inventory_fabric_skills.py` against the
active source: pass an upstream checkout as the root, every agent/Claude
discovery root with `--junction-root`, and the vendored `.claude/skills` folder
or a plugin cache with `--additional-skills-root`.
