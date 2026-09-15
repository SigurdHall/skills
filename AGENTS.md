# Repository Instructions

## Purpose

This repository stores reusable skills and related prompt workflows.

## Superpowers Policy

Superpowers are a risk-control toolkit, not the default workflow for this repository. Use repo instructions and local skill rules before broader Superpowers process rules when they conflict.

Always use `verification-before-completion` before claiming skill changes are complete, and use `systematic-debugging` for failing tests, unexpected hook behavior, routing errors, or broken skill discovery.

Use `test-driven-development` for behavior in scripts, hooks, validators, catalog discovery, and other executable logic. For markdown-only skill cleanup, reference moves, path updates, or documentation restructuring, use focused inspection plus relevant smoke checks instead of strict TDD unless the change affects behavior.

Use `writing-skills` / `skill-creator` when creating or substantially revising skills. Do not let `brainstorming` block small fixes, documentation edits, skill cleanup, or concrete implementation requests unless the user explicitly asks for design exploration.

## Codex Skills

Codex skills live under grouped folders:

`skills/<group>/<skill-name>/SKILL.md`

Use lowercase hyphen-case for skill names. Each skill folder must contain exactly one required `SKILL.md`; add `scripts/`, `references/`, or `assets/` only when they directly support the skill.

Skills should be reusable workflows, not project notes. Keep project-specific instructions in that project's own `AGENTS.md`, README, or docs.

## Skill Routing Map

Use this map when a task could trigger more than one skill:

- Thinking/planning: [interview-me](skills/thinking-planning/interview-me/SKILL.md) to draw a rough idea into a concrete brief, [grill-me](skills/thinking-planning/grill-me/SKILL.md) to pressure-test a plan that already exists, [narrative-design](skills/thinking-planning/narrative-design/SKILL.md), [skill-design](skills/thinking-planning/skill-design/SKILL.md), [small-council](skills/thinking-planning/small-council/SKILL.md), [planf3](skills/thinking-planning/planf3/SKILL.md) for `/planf3` HTML-first implementation plans in `specs/` with built-in Codex adversarial review, [bro](skills/thinking-planning/bro/SKILL.md) for `/bro` (user-invoked only, restates the last message in plain language)
- Coding/prompts: [explicit-data-flow](skills/coding/explicit-data-flow/SKILL.md) for table-transformation notebooks and ETL rebuilt as one straight-line section per output table (default when the user asks for readable transformations or less indirection), [readable-python-code](skills/coding/readable-python-code/SKILL.md) for style and naming in the same code, [prompt-engineering](skills/coding/prompt-engineering/SKILL.md), [agent-work-order-handoff](skills/coding/agent-work-order-handoff/SKILL.md) for delegating tasks to a cheaper model/subagent/future session, [present-complex-results](skills/coding/present-complex-results/SKILL.md) before the final response for a complex process or delivery, [mcp-context-hygiene](skills/coding/mcp-context-hygiene/SKILL.md) for narrow/filtered MCP tool-call discipline (any MCP server) in long sessions, [git-push-daily-log](skills/coding/git-push-daily-log/SKILL.md) for logging a git push into today's Vault daily note
- Data integration: [delta-sharing-powerbi-ppu](skills/data-integration/delta-sharing-powerbi-ppu/SKILL.md) for direct Power BI Desktop/PPU consumption, [tableau-rest-api](skills/data-integration/tableau-rest-api/SKILL.md) for Tableau REST API and extract workflows
- Fabric docs (under reporting): [fabric-documentation](skills/reporting/fabric/fabric-documentation/SKILL.md) is the hub. Narrower doc types: [fabric-architecture-doc](skills/reporting/fabric/fabric-architecture-doc/SKILL.md), [fabric-semantic-model-doc](skills/reporting/fabric/fabric-semantic-model-doc/SKILL.md), [fabric-powerbi-report-doc](skills/reporting/fabric/fabric-powerbi-report-doc/SKILL.md), [fabric-lakehouse-doc](skills/reporting/fabric/fabric-lakehouse-doc/SKILL.md), [fabric-data-contract-doc](skills/reporting/fabric/fabric-data-contract-doc/SKILL.md), [fabric-cicd-governance-doc](skills/reporting/fabric/fabric-cicd-governance-doc/SKILL.md), [fabric-delta-sharing-ingestion](skills/reporting/fabric/fabric-delta-sharing-ingestion/SKILL.md). See [fabric](skills/reporting/fabric/AGENTS.md) for the group routing.
- Fabric item operations: [fabric-item-authoring](skills/fabric/fabric-item-authoring/SKILL.md) routes create/update/deploy/delete requests through current `skills-for-fabric` mechanics and lifecycle gates.
- Finance/BOTT (under reporting norms): [uit-bott-okonomimodell](skills/reporting/norms/uit-bott-okonomimodell/SKILL.md) for field/column semantics, [bott-semantic-model](skills/reporting/norms/bott-semantic-model/SKILL.md) for star-schema modeling, [finance-bi-dax-patterns](skills/reporting/norms/finance-bi-dax-patterns/SKILL.md) for DAX measures
- Knowledge management: [vault-forvalter](skills/knowledge-management/vault-forvalter/SKILL.md) for general vault maintenance, [accomplishment-log](skills/knowledge-management/accomplishment-log/SKILL.md) for capturing/summarizing accomplishments (medarbeidersamtale, CV, jobbskifte), [weekly-production-review](skills/knowledge-management/weekly-production-review/SKILL.md) for the on-demand weekly rollup, [strategic-plan-analysis](skills/knowledge-management/strategic-plan-analysis/SKILL.md), [uit-statsbudsjett-analyse](skills/knowledge-management/uit-statsbudsjett-analyse/SKILL.md) for UiTs årlige statsbudsjettanalyse mot foreløpig budsjettfordeling (blått hefte, Prop. 1 S, fagroller med varig minne), [uit-statsbudsjett-proeve](skills/knowledge-management/uit-statsbudsjett-proeve/SKILL.md) as the user-invoked launcher with publication check
- Reporting (top group): prefer `skills-for-fabric` for live mechanics (MCP model edits, PBIR/report-author CLI, Desktop reload, workspace REST); use this group for UiT domain, offline fallback, and orchestration. See [reporting](skills/reporting/AGENTS.md) for the boundary and routing. powerbi: [powerbi-pbip](skills/reporting/powerbi/powerbi-pbip/SKILL.md) for offline PBIP/PBIR/TMDL edits, [semantic-model-metadata](skills/reporting/powerbi/semantic-model-metadata/SKILL.md) for measure/column documentation, lineage, annotations; presentation: [html-report-builder](skills/reporting/presentation/html-report-builder/SKILL.md) for static HTML reports from YAML/SQL/Parquet; orchestration: [design-bi-report-wireframes](skills/reporting/orchestration/design-bi-report-wireframes/SKILL.md) for shared StoryFrame plus target-specific Power BI/React/HTML wireframes, [pbip-full-report](skills/reporting/orchestration/pbip-full-report/SKILL.md) for complete reports, [powerbi-report-production-loop](skills/reporting/orchestration/powerbi-report-production-loop/SKILL.md) for Tableau→Power BI report/visual migration, [semantic-model-migration](skills/reporting/orchestration/semantic-model-migration/SKILL.md) for legacy/Tableau-era semantic model cleanup and AI/Copilot readiness; norms: [uit-powerbi-reporting](skills/reporting/norms/uit-powerbi-reporting/SKILL.md) for UiT finance/reporting specifics
- Presentations (under reporting): [uit-deck-generator](skills/reporting/presentation/uit-deck-generator/SKILL.md) for UiT-branded PowerPoint template/layout compliance and `.pptx` validation, [presentation-factory](skills/reporting/presentation/presentation-factory/SKILL.md) for premium HTML-first decks and hybrid PPTX export

## Skill Format

Each `SKILL.md` must start with YAML frontmatter containing at least:

```yaml
---
name: skill-name
description: Short trigger-oriented description of when to use the skill.
---
```

The `description` should mention the main trigger words, use cases, and boundaries. It should be specific enough that Codex can decide when the skill applies without reading the whole file.

After the frontmatter, keep the skill procedural and concise. Prefer clear steps, decision rules, file locations, commands, and validation checks over long background explanation.

## Creating Or Updating Skills

Use the `skill-creator` workflow when creating or substantially revising a skill.

Keep skills compact:

- Put trigger words and use cases in the `description` frontmatter.
- Keep `SKILL.md` procedural and concise.
- Move long examples, schemas, or policy detail into `references/`.
- Do not add README, changelog, quick-reference, or install-guide files inside skill folders.

Use optional subfolders only when they have a concrete purpose:

- `scripts/` for reusable helper scripts that the skill instructs Codex to run or modify.
- `references/` for longer examples, schemas, policies, or domain material.
- `assets/` for templates, images, snippets, or other reusable inputs.

Do not duplicate large examples in both `SKILL.md` and `references/`.

## Validation

Before committing skill changes, check that:

- The skill directory name is lowercase hyphen-case.
- The skill has exactly one `SKILL.md`.
- The frontmatter has `name` and `description`.
- The description is trigger-oriented and not just a generic summary.
- Relative paths referenced by the skill exist.
- Scripts referenced by the skill are runnable or clearly documented.
- The skill does not contain secrets, personal data, or project-specific confidential details.

## Existing Claude Commands

Legacy Claude command files live under `.claude/commands/`. When a command becomes useful for Codex, convert it into a proper Codex skill under `skills/` instead of editing it in place.

## Git Discipline

Use English imperative commit messages. Keep commits focused: one logical skill/setup change per commit.

Do not rewrite unrelated skills while changing one skill. Do not remove legacy Claude commands unless the user explicitly asks for cleanup.
