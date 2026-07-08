---
name: repo-governance
description: Use when creating, splitting, publishing, or linking repositories, especially private UiT work repos, GitHub visibility decisions, repository topics, naming, or backlinks.
---

# Repo Governance

Use this before creating, splitting, publishing, or linking repositories.

## Rules

- Default visibility is `private`.
- Do not create a public repository without explicit user confirmation in the current turn.
- For UiT repositories, require topics `uit` and `uit-private`.
- Add at least one domain topic such as `powerbi`, `tableau`, `okonomi`, `hr`, `dataforum`, `llm`, `budget`, `migration`, `governance`, or `semantic-model`.
- Add backlinks in both directions:
  - child README links to parent/hub repo and original source path.
  - parent/hub README or manifest links to child repo.
- Check `git status --short --branch` before moving, committing, or pushing.
- Do not move `.env`, `.env.*`, local caches, generated outputs, private data dumps, or credentials.

## Required Checklist

1. Confirm source path and target repo name.
2. Confirm visibility. If public, stop and ask for explicit confirmation.
3. Confirm required topics.
4. Confirm backlink text for child README.
5. Confirm hub entry.
6. Create repo.
7. Add files.
8. Run relevant tests or smoke checks.
9. Commit and push.
10. Update hub manifest and migration log.

## Safe GitHub CLI Defaults

Private repo creation:

```powershell
gh repo create SigurdHall/<repo-name> --private --description "<description>"
gh repo edit SigurdHall/<repo-name> --add-topic uit --add-topic uit-private
```

Public repo creation is blocked until the user explicitly confirms:

```text
BLOCKED: public repository requires explicit user confirmation.
```
