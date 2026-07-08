---
name: accomplishment-log
description: Capture and summarize what the user has produced at work, for medarbeidersamtale, CV, or jobbskifte. Two capture entry points — user dictates ("jeg har noe å tilføre, kan du skrive noe om dette?") or assisted discovery ("finn ut hva jeg har gjort og lag nytt notat om dette") — plus an on-demand full-period summarize. Not general vault maintenance (see vault-forvalter) and not the weekly rollup (see weekly-production-review). Triggers: medarbeidersamtale, CV-oppdatering, jobbskifte, hva har jeg levert, oppsummer prestasjonene mine, karrierelogg, brag document, work log.
---

# Accomplishment Log

## Scope

Owns capture and summarize of what the user has *produced* at work — not
general note maintenance (vault-forvalter's job) and not the weekly
technical rollup (weekly-production-review's job, which this skill's Mode 2
can also draw on for a longer period).

## First Reads

Before writing to the Vault, read:

1. `private/Vault/_principal.md`
2. `private/Vault/_forvalter.md`
3. `private/Vault/_kontekst.md`

Use these as the operating contract for the Vault, per `vault-forvalter`.

## Ledger location and shape

`private/Vault/Notes/Career/career-log-YYYY.md` — one file per year (not
one file per entry), to keep capture low-friction. This is a stable-
content-type subfolder of the existing `Notes/` top-level folder, the same
pattern as `Resources/RSS` — no change to `_forvalter.md`'s folder
enumeration needed.

Create the current year's file from
`private/Vault/Templates/career-log-template.md` if it doesn't exist yet.
Frontmatter:

```yaml
---
created: YYYY-MM-DD
status: kontekstuell
vekt: 1.0
tags: [career, accomplishments]
kilder: []
---
```

`status: kontekstuell` — matches `_forvalter.md`'s own definition ("bundet
til pågående arbeid"), no temporal decay, which is the right semantics for
a career ledger.

Per-entry shape, **appended at the end of the file**:

```markdown
## YYYY-MM-DD — <short title>
- **Prosjekt:** 
- **Hva:** 
- **Hvorfor / effekt:** 
- **Referanse:** <!-- commit hash, PR, handovers/... path, or blank -->
```

Date is user-supplied-or-today — don't assume "today"; the user will
sometimes want to log something from weeks ago (backfill).

## Mode 1 — Capture

Two entry points, both low-friction:

**1a. User dictates** ("jeg har noe å tilføre, kan du skrive noe om
dette?") — the user describes what happened; structure it into the entry
shape above. Don't demand every field be filled.

**1b. Assisted discovery** ("finn ut hva jeg har gjort og lag nytt notat om
dette") — investigate before writing:
- `git log` (recent activity across the known repos under `C:\repos`)
- Recent `private/Vault/Journal/Entries/*.md` "📦 Leveranser" sections
  (written by `coding/git-push-daily-log`)
- Recent files under `C:\repos\handovers\`

Draft a candidate entry from what this turns up, then **present it to the
user for confirmation/editing before writing it to the ledger** — never
write silently. This avoids inventing impact/significance the user hasn't
actually confirmed; the investigation finds raw material, the user still
owns what it means.

## Mode 2 — Summarize

Triggered on request (e.g. before a medarbeidersamtale or job change), not
on a schedule.

1. Ask the target audience/purpose first — internal review vs. external CV
   changes grouping and tone. Don't guess.
2. Read the relevant `career-log-YYYY.md` file(s) for the requested period.
   A job-change summary plausibly spans multiple years — don't assume
   "current year" is enough.
3. May cross-reference `git log` or `handovers/` as supporting detail, but
   **only when the user has framed the request that way** — never pull
   these in automatically to pad the summary.
4. Write/update a themed note under `private/Vault/Summaries/` (reusing the
   existing, currently-empty folder — this is exactly what it's for),
   grouped by theme/impact, not just chronology:

```yaml
---
created: YYYY-MM-DD
status: kontekstuell
vekt: 1.0
tags: [career, accomplishments, summary]
kilder: []          # e.g. [[Notes/Career/career-log-2026]]
periode: YYYY-MM-DD–YYYY-MM-DD
formål: medarbeidersamtale | cv | jobbskifte
---

## {{title}}

## Sammendrag
## Hovedtemaer
### <tema>
## Kvantifiserbar effekt (der mulig)
## Ikke inkludert / usikkert
## Lenker
```

Stay within what the ledger actually says — no invented impact claims not
already in a captured entry.

## Privacy note

Career/performance content is more sensitive than average Vault notes — it
may reference colleagues, compensation, or internal specifics. It's subject
to the same git exposure as the rest of the Vault (per `vault-forvalter`'s
Git Workflow); this is a deliberate accepted tradeoff, not a silent
assumption — flag it if entries start accumulating real names/numbers and
the Vault's git remote status changes.

## Pairs with

- `coding/git-push-daily-log` — the per-push technical log this skill's
  Mode 1b reads from. Doesn't duplicate its frontmatter/entry conventions.
- `knowledge-management/weekly-production-review` — the weekly rollup;
  Mode 2 here is the longer-period, curated counterpart, not a replacement.

## Git Workflow

For Vault changes, per `vault-forvalter`'s convention:

- Show changed files and summarize intent before commit.
- Commit only after user confirmation.
- Push only after user confirmation.
