# Repository Instructions

## Purpose

This repository stores reusable skills and related prompt workflows.

## Codex Skills

Codex skills live under:

`skills/<skill-name>/SKILL.md`

Use lowercase hyphen-case for skill names. Each skill folder must contain exactly one required `SKILL.md`; add `scripts/`, `references/`, or `assets/` only when they directly support the skill.

Skills should be reusable workflows, not project notes. Keep project-specific instructions in that project's own `AGENTS.md`, README, or docs.

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
