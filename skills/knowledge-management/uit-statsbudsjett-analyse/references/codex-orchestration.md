# Codex: skript, Luna-fagroller og kontroll

Codex-variantene ligger ved siden av Claude-workflowene i
`.claude/workflows/codex-uit-ramme.js` og `codex-uit-departementer.js`.
Kjør dem med **Node i WSL/Linux**. De bruker `codex exec`; Claude-verktøyet
`Workflow` er ikke nødvendig. Gjenbrukbare kjørekomponenter ligger åpent i
analyseskillens `scripts/codex_*.mjs`.

## Oppstart

Opprett en JSON-fil i analyseprosjektet. Eksempel for en ny historisk prøve:

```json
{
  "budget_year": 2025,
  "run_id": "codex-2025-v1",
  "project": "/home/sihal7953/repos/uit-statsbudsjett",
  "python": "/home/sihal7953/.venvs/statsbudsjett/bin/python",
  "config": "arbeidsflyt/arbeidsdeling-2025.json",
  "phase_set": "alt",
  "mode": "prøve",
  "forbidden_dirs": ["2024/", "2025/"],
  "duplicate_parts": ["ramme"],
  "concurrency": 3,
  "archive": false,
  "keep_prepared": false,
  "continue_missing": true
}
```

Python-stien må finnes i miljøet som faktisk kjører. `python3` er standard.
Node 22 eller nyere og innlogget Codex CLI kreves. CLI-flaggene er kontrollert
mot lokalt installert Codex CLI 0.154.0 (`codex exec --help`).

Fra skills-repoet:

```bash
node .claude/workflows/codex-uit-ramme.js --args ../uit-statsbudsjett/codex-workflow-2025.json --dry-run
node .claude/workflows/codex-uit-ramme.js --args ../uit-statsbudsjett/codex-workflow-2025.json
node .claude/workflows/codex-uit-departementer.js --args ../uit-statsbudsjett/codex-workflow-2025.json
```

`--dry-run` oppretter ingen filer og starter ingen prosesser eller modellkall.
`check_only: true` skriver publiseringssjekker i en ubrukt leveransemappe,
uten å starte analyseagenter. Støttet automatisk stadium er `forslag`.

| Valg | Virkning |
|---|---|
| `phase_set: grunnlag` | Fjorårets vedtatte blå hefte og UiTs foreløpige forutsetninger |
| `phase_set: budsjettdag` | Rammeark og hurtigsvar, deretter avvik |
| `phase_set: alt` | Begge delene av rammeworkflowen; departementene startes med neste kommando |
| `keep_prepared: true` | Behold forberedt grunnlag ved en ny kjøring |
| `archive: true` | Flytt rester som ryddeskriptet identifiserer, før en ny kjøring |
| `template`, `libreoffice` | Eksisterende UiT-mal og LibreOffice til PPTX og rendering |
| `timeout_ms` | Maksimal tid per modellprosess, standard 900000 ms |
| `models` | Overstyr enkelte modellfaser, eksempel under |

En videreføring med samme `run_id` bruker kjøringens egen arbeidsdeling.
Den kjører ikke oppryddingen på nytt. En fase kan ikke startes to ganger,
og en fryst eller feilet kjøring krever et nytt `run_id` og håndtering av
eventuelle rester. Låsen `.codex-statsbudsjett.lock` hindrer to Codex-kjøringer
i prosjektet samtidig. Ved maskinbrudd: kontroller at PID-en i låsefilen er
avsluttet før låsen fjernes. Låsen koordinerer ikke en samtidig Claude-kjøring.

## Arbeidsfordeling og fart

| Trinn | Utførelse |
|---|---|
| Oppdagelse, henting, uttrekk, tabellparser, treff, sluttkontroll | Direkte skript, ingen modell |
| Forutsetninger, første rammeark, avvik | `gpt-6-astra`, high |
| kd_ramme, helse_miljo, naring_arbeid_kultur | `gpt-5.6-luna`, high |
| bygg_samisk_justis, nordomraader_energi | `gpt-5.6-luna`, medium |
| Uavhengig rammeutkast, sammenlignende review, redaktør | `gpt-6-astra`, high |

Henting gjenbruker PDF-er bare når kildeidentitet og SHA-256 stemmer.
Kildemanifestet har én skriver. Fagroller kan kjøre parallelt med et tak på
`concurrency` faktiske modellprosesser. Primær- og andreutkast bruker samme
historiske minnegrunnlag, egne mapper og hver sin eksponeringslogg; review
venter på begge svarene. Isolasjonen mellom utkast er en promptregel,
ikke et filsystem som teknisk skjuler den andre agentens filer.

Eksempel på avgrenset effort-prøve:

```json
{"models": {"role_other": {"effort": "high"}}}
```

Dette beholder Luna og endrer bare effort. Faser som kan overstyres:
`assumptions`, `quick`, `deviation`, `role_critical`, `role_other`,
`duplicate`, `review`, `editor`. Ukjent modell gir feil fra Codex og byttes
ikke ut automatisk. Kjøretid, forespurt modell/effort og mottatt bruksdata
lagres per kall under `leveranser/<run_id>/runtime/`. Faktisk modell og
tjenestenivå oppgis bare når klienten rapporterer dem.

## Kontroll og begrensninger

Hurtigsvaret vises før avviksfasen, etter bekreftet visuell kolonnekontroll
og bro uten rest. Ukjent er `null`, aldri null kroner. Årsspesifikke
eksempelleveranser brukes ikke som mal for prøvebesvarelsen.

Sluttkontrollen samler loggfragmenter, kjører leveranse- og regnekontroll,
skriver verifikasjon og hasher sluttfilene til sist. Manglende PPTX eller
visuell kontroll gir ufullstendig leveranse. Manifestet fryser det som ble
levert, også når status er ufullstendig; det er ikke en faglig godkjenning.
Ikke åpne fasit før leveransen og eksponeringsloggen er fryst.

## Lokal verifikasjon

```bash
node --test --test-isolation=none tests/test_codex_*.mjs
python -m pytest tests/test_statsbudsjett_*.py
```

Node-testene bruker kontrollerte prosesser og syntetiske data. De beviser
kjørelogikk, feilhåndtering og filkontroll, ikke analysepresisjon eller
live tilgang til modellene. En full historisk prøve må vurderes separat.
