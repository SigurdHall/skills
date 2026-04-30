---
name: vault-forvalter
description: Maintain the user's Obsidian Vault as a knowledge system. Use when the task involves private/Vault, _principal, _forvalter, _kontekst, note cleanup, links/backlinks, topic pages, note classification, RSS note processing, Vault structure, or syncing Vault changes to GitHub.
---

# Vault Forvalter

## First Reads

Before making Vault changes, read:

1. `private/Vault/_principal.md`
2. `private/Vault/_forvalter.md`
3. `private/Vault/_kontekst.md`

Use these as the operating contract for the Vault.

## Core Rules

- Preserve the user's meaning. Do not rewrite opinions into safer or more generic claims.
- Add structure only when it reduces future retrieval cost.
- Prefer meaningful wikilinks over dense linking.
- Use topic pages as navigation and synthesis nodes, not as decorative indexes.
- Do not delete notes.
- Distinguish facts, assessments, assumptions, and recommendations when adding analysis.

## Linking Workflow

1. List Markdown files and existing wikilinks.
2. Read the relevant notes before editing links.
3. Add `Relaterte notater` sections where useful.
4. Add or update topic pages under `private/Vault/Topics/` when multiple notes share a stable theme.
5. Validate wikilinks against actual file basenames.
6. Present changes and ask for confirmation before commit or push unless the user has already explicitly approved.

## Git Workflow

For Vault changes:

- Show changed files and summarize intent before commit.
- Commit only after user confirmation.
- Push only after user confirmation.
- Main branch is acceptable for the private Vault when explicitly approved by the user.
