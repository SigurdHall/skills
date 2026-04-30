# Repository Instructions

## Purpose

This repository stores reusable skills and related prompt workflows.

## Codex Skills

Codex skills live under:

`skills/<skill-name>/SKILL.md`

Use lowercase hyphen-case for skill names. Each skill folder must contain exactly one required `SKILL.md`; add `scripts/`, `references/`, or `assets/` only when they directly support the skill.

## Creating Or Updating Skills

Use the `skill-creator` workflow when creating or substantially revising a skill.

Keep skills compact:

- Put trigger words and use cases in the `description` frontmatter.
- Keep `SKILL.md` procedural and concise.
- Move long examples, schemas, or policy detail into `references/`.
- Do not add README, changelog, quick-reference, or install-guide files inside skill folders.

## Existing Claude Commands

Legacy Claude command files live under `.claude/commands/`. When a command becomes useful for Codex, convert it into a proper Codex skill under `skills/` instead of editing it in place.

## Git Discipline

Use English imperative commit messages. Keep commits focused: one logical skill/setup change per commit.
