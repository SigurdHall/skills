# Repository Instructions

## Purpose

This repository stores reusable skills and related prompt workflows.

## Codex Skills

Codex skills live under grouped folders:

`skills/<group>/<skill-name>/SKILL.md`

Use lowercase hyphen-case for skill names. Each skill folder must contain exactly one required `SKILL.md`; add `scripts/`, `references/`, or `assets/` only when they directly support the skill.

Skills should be reusable workflows, not project notes. Keep project-specific instructions in that project's own `AGENTS.md`, README, or docs.

## Skill Routing Map

Use this map when a task could trigger more than one skill:

- Thinking/planning: [grill-me](skills/thinking-planning/grill-me/SKILL.md), [narrative-design](skills/thinking-planning/narrative-design/SKILL.md), [skill-design](skills/thinking-planning/skill-design/SKILL.md), [small-council](skills/thinking-planning/small-council/SKILL.md)
- Coding/prompts: [readable-python-code](skills/coding/readable-python-code/SKILL.md), [prompt-engineering](skills/coding/prompt-engineering/SKILL.md)
- Data integration: [delta-sharing-powerbi-ppu](skills/data-integration/delta-sharing-powerbi-ppu/SKILL.md) for direct Power BI Desktop/PPU consumption, [tableau-rest-api](skills/data-integration/tableau-rest-api/SKILL.md) for Tableau REST API and extract workflows
- Fabric docs: [fabric-documentation](skills/fabric/fabric-documentation/SKILL.md) is the hub. Narrower doc types: [fabric-architecture-doc](skills/fabric/fabric-architecture-doc/SKILL.md), [fabric-semantic-model-doc](skills/fabric/fabric-semantic-model-doc/SKILL.md), [fabric-powerbi-report-doc](skills/fabric/fabric-powerbi-report-doc/SKILL.md), [fabric-lakehouse-doc](skills/fabric/fabric-lakehouse-doc/SKILL.md), [fabric-data-contract-doc](skills/fabric/fabric-data-contract-doc/SKILL.md), [fabric-cicd-governance-doc](skills/fabric/fabric-cicd-governance-doc/SKILL.md), [fabric-delta-sharing-ingestion](skills/fabric/fabric-delta-sharing-ingestion/SKILL.md). See [fabric](skills/fabric/AGENTS.md) for the group routing.
- Finance/BOTT: [uit-bott-okonomimodell](skills/finance/uit-bott-okonomimodell/SKILL.md) for field/column semantics, [bott-semantic-model](skills/finance/bott-semantic-model/SKILL.md) for star-schema modeling, [finance-bi-dax-patterns](skills/finance/finance-bi-dax-patterns/SKILL.md) for DAX measures
- Knowledge management: [vault-forvalter](skills/knowledge-management/vault-forvalter/SKILL.md), [strategic-plan-analysis](skills/knowledge-management/strategic-plan-analysis/SKILL.md)
- Local Power BI files: prefer `skills-for-fabric` for live mechanics (MCP model edits, PBIR/report-author CLI, Desktop reload, workspace REST); use this group for UiT domain + offline fallback. See [powerbi-local](skills/powerbi-local/AGENTS.md) for the boundary and routing. [powerbi-pbip](skills/powerbi-local/powerbi-pbip/SKILL.md) for offline PBIP/PBIR/TMDL edits, [pbip-full-report](skills/powerbi-local/pbip-full-report/SKILL.md) for building complete reports, [powerbi-report-production-loop](skills/powerbi-local/powerbi-report-production-loop/SKILL.md) for Tableau-to-Power BI migration, [uit-powerbi-reporting](skills/powerbi-local/uit-powerbi-reporting/SKILL.md) for UiT finance/reporting specifics
- Reporting: [html-report-builder](skills/reporting/html-report-builder/SKILL.md) for static HTML reports from YAML specs, SQL, and local Parquet/CSV via the html-report-toolkit CLI
- Presentations: [uit-deck-generator](skills/presentations/uit-deck-generator/SKILL.md) for UiT-branded PowerPoint template/layout compliance and `.pptx` validation, [presentation-factory](skills/presentations/presentation-factory/SKILL.md) for premium HTML-first decks and hybrid PPTX export

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
