---
name: powerbi-report-production-loop
description: Use when migrating Tableau workbooks, dashboards, extracts, calculated fields, parameters, or report production patterns into Power BI/PBIP reports, especially when coordinating subagents, parity checks, table migration, semantic model design, DAX translation, visual rebuilds, and release-ready output artifacts.
---

# Power BI Report Production Loop

Use this skill to run a concise Tableau-to-Power-BI migration loop from workbook inventory to release-ready PBIP artifacts. Keep the main thread as the production owner; use subagents to inspect, translate, build, and verify slices independently.

**REQUIRED SUB-SKILLS:** Use `powerbi-pbip` before reading or editing PBIP/PBIR/TMDL/report JSON. Use `pbip-full-report` when creating or substantially adapting a complete report.

**MECHANICS:** Delegate generic Power BI process to `skills-for-fabric`: `powerbi-report-planning` for page plan/spec, `powerbi-report-design` for chart/layout choices, and `powerbi-report-authoring`/`semantic-model-authoring` for live builds. This skill owns the migration loop and parity, not generic tooling.

## Loop

1. Establish the parity contract: source workbook, target audience, required pages, certified totals, filters, refresh assumptions, and non-goals.
2. Run the four migration waves from [subagents.md](references/public/subagents.md):
   - Wave 1: inventory and parity contract.
   - Wave 2: table and semantic migration.
   - Wave 3: report production.
   - Wave 4: validation, governance, and release.
3. Track deliverables with [output-artifacts.md](references/public/output-artifacts.md).
4. Apply [table-migration.md](references/public/table-migration.md) for Tableau extract/logical table to Power BI table decisions.
5. Stop the loop only when parity evidence, known gaps, and release blockers are explicit.

## Operating Rules

- Treat Tableau as source behavior, not source architecture. Rebuild in Power BI around a clear semantic model.
- Separate data model work, DAX translation, visual rebuild, and validation.
- Prefer auditable parity checks over visual similarity alone.
- Keep assumptions, unresolved gaps, and manual review items in the output artifacts.
- Do not publish or automate decisions involving sensitive finance, HR, personal, or internal-control data without explicit privacy and governance review.

## References

- [subagents.md](references/public/subagents.md): subagent definitions and four-wave migration loop.
- [output-artifacts.md](references/public/output-artifacts.md): expected deliverables and completion gates.
- [table-migration.md](references/public/table-migration.md): table, field, calculation, and relationship migration rules.
