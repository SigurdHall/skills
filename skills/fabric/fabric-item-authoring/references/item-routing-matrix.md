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

## Coverage snapshot (2026-07-14)

The local `C:\repos\skills-for-fabric` checkout is package version `0.3.5`
(`a2332f...`). A read-only fetch showed upstream `main` at `0.3.7`
(`b961296...`), nine commits ahead. Version `0.3.7` adds the SQL Database skill
family and updates Power BI authoring/design. Update deliberately; do not mix
files from two versions in one run.

| Fabric item or task | Primary skill family | Coverage note |
|---|---|---|
| Power BI report | `powerbi-report-authoring`, `powerbi-report-management` | PBIR/PBIP mechanics and workspace lifecycle |
| Semantic model | `semantic-model-authoring`, `semantic-model-consumption` | Model changes and DAX/metadata read-back |
| Notebook, Spark, Lakehouse engineering | `spark-authoring-cli`, `spark-consumption-cli`, `spark-operations-cli` | Authoring, query, and diagnosis are separate |
| Data Pipeline for Notebook/Spark orchestration | `spark-authoring-cli` plus `ITEM-DEFINITIONS-CORE.md` | Partial mutation route only for a bounded, documented `TridentNotebook` orchestration (and documented Variable Library references); other activity families remain plan-only until a dedicated skill exists |
| Warehouse / SQL endpoint | `sqldw-authoring-cli`, `sqldw-consumption-cli`, `sqldw-operations-cli` | Use the authoring skill only for write operations |
| SQL Database item | `sqldb-*` in upstream `0.3.7+` | Not present in the local `0.3.5` checkout |
| Dataflow Gen2 | `dataflows-authoring-cli`, `dataflows-consumption-cli` | Includes definitions, connections, and refresh monitoring |
| Eventstream | `eventstream-authoring-cli`, `eventstream-consumption-cli` | Graph topology requires item-specific validation |
| Eventhouse / KQL Database | `eventhouse-authoring-cli`, `eventhouse-consumption-cli` | KQL commands and queries have different mutation boundaries |
| Activator / Reflex | `activator-authoring-cli`, `activator-consumption-cli` | Human confirmation is required for external notifications/actions |
| Fabric IQ ontology | `fabriciq-ontology-authoring-cli`, `fabriciq-ontology-consumption-cli` | Preview capability; verify current limits |
| Materialized Lake View operations | `mlv-operations-cli` | Schedule and job operations, not a generic item builder |
| Cross-workspace discovery | `search-consumption-cli` | Read-only discovery before routing |

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
- Environment and Variable Library lifecycle
- KQL Dashboard and KQL Queryset authoring
- Event Schema Set lifecycle
- Mirrored database setup and validation
- GraphQL API and Graph Model lifecycle
- Machine learning and Data Agent items
- workspace, capacity, tenant-admin, deployment-pipeline, and Git orchestration

Create a narrow skill only when a recurring gap has an official, testable
contract. Keep the router small.

## Namespace hygiene

The Power BI authoring plugin cache and `skills-for-fabric` checkout may expose
the same skill both prefixed and unprefixed. Pass the active plugin's direct
`skills` folder to `inventory_fabric_skills.py --additional-skills-root`, and
pass every relevant agent/Claude discovery root with `--junction-root`. Select
one versioned source per run and record its Git commit/dirty state; duplicate
discovery names are not additional capability.
