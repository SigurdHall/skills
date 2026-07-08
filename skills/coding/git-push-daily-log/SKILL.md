---
name: git-push-daily-log
description: After a git push performed on the user's behalf, log it into today's Obsidian daily note with an expanded comment on what/why — not just the raw commit message — creating the daily note from template if it doesn't exist yet. Triggers: after pushing, log this push, daily note, journal entry for today, git push.
---

# Git Push Daily Log

## Scope

Runs after any `git push` performed on the user's behalf, in any repo under
`C:\repos`. Writes a technical, per-push entry into today's Vault daily
note — close to git history, not curated. This is distinct from
`knowledge-management/accomplishment-log`'s Notes/Career ledger, which is a
higher-level, hand-curated record of what's review-worthy.

## Procedure

1. After a successful push, determine today's date and the Journal file
   path: `private/Vault/Journal/Entries/YYYY.MM.DD.md` (dot-separated —
   matches the existing Journal convention, not RSS's dash convention).
2. **If the file exists:** open it, find the `## 📦 Leveranser` section
   (added to the Daily Note template between Tanker and Sluttevaluering),
   and append an entry there. Multiple pushes the same day append
   additional entries under the same section — don't overwrite earlier
   ones.
3. **If it does not exist:** create it from
   `private/Vault/Templates/Daily Note - {{date_YYYY-MM-DD}}.md`,
   substituting the Templater placeholders by hand — Templater doesn't run
   outside Obsidian:
   - `date:` → today's date, `YYYY-MM-DD`
   - `day:` → today's weekday name
   - `week:` → ISO week, `[W]WW`
   - The `# <dddd, D. MMMM YYYY>` heading → today's date, spelled out
   Then append the push entry to `## 📦 Leveranser` as in step 2.
4. Entry shape per push:
   - Repo/project name
   - One-line what (not just the raw commit subject)
   - **Expanded comment** (2–4 sentences): why this change, what problem it
     solves, anything a future reader wouldn't get from `git log` alone —
     draw on the session's own context, not just the commit message text
   - Optional: commit hash(es), and a link to a `handovers/...` doc if this
     push accompanied one

## Known limitation

Only fires when Claude Code performs the push. A push done manually by the
user outside a session isn't logged in this version — no daily-note
coverage for that case yet.

## Pairs with

`knowledge-management/accomplishment-log` for the underlying Vault
frontmatter/entry conventions — don't duplicate those rules here. Its Mode
1b ("assisted discovery") reads the `## 📦 Leveranser` sections this skill
writes.
