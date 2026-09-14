# Kjøring i Claude Code: oppstart, agenter, arbeidsflyt og kvitteringer

Les dette når analysen skal kjøres i Claude Code. Filformater, minne og
leveransekrav står i [agentarbeidsflyten](agent-workflow.md); dette
dokumentet beskriver hvordan kjøringen startes og kontrolleres.
[Modelltestingen](model-testing.md) gjelder Codex CLI og OpenAI-profiler og
er historisk observasjon, ikke en regel for Claude.

## Oppstart

Brukeren starter kjøringen med skillen
[uit-statsbudsjett-proeve](../../uit-statsbudsjett-proeve/SKILL.md) og en
promptform med minst `år`. Den skillen tolker formen, kjører
`scripts/discover_sources.py check` (publiseringssjekk og kildeoppdagelse
mot regjeringen.no og UiTs styreportal), skriver `kilder-input.json`, og
starter workflow-skriptet. Uten publisert blått hefte og KD Prop. 1 S
stopper den. Se [kildekartet](kildekart.md) for mønstrene skriptet bruker.

## Verktøyvalg

| Behov | Bruk |
|---|---|
| Hele årsanalysen | Workflow-skriptet `.claude/workflows/uit-statsbudsjett-analyse.js` i skills-repoet, startet av `/uit-statsbudsjett-proeve`. Direkte: `Workflow({scriptPath, args})`. |
| Én rolle på nytt, én del rettet, eller fasitsammenligning | Agent-verktøyet direkte, med oppdragsfilen fra `leveranser/<kjøring>/oppdrag/<rolle>.md` som prompt-grunnlag. |
| Deterministiske trinn: kildeoppdagelse, henting, uttrekk, avstemming, markering, filkontroll | Python-skriptene i `scripts/`. Ikke la en modell regne det et skript kan regne. |

## Miljø

Prosjektet ligger i WSL (`/home/sihal7953/repos/uit-statsbudsjett`).
Python er `~/.venvs/statsbudsjett/bin/python` i WSL, opprettet fra
`docs/runtime-reference/requirements-observed.txt`.

Fra en Claude Code-sesjon på Windows:

- Les og skriv filer med Read/Write/Glob på UNC-stien
  `\\wsl.localhost\Ubuntu-24.04` + POSIX-stien.
- Kjør skript uten shell, slik at stier ikke siteres om: PowerShell-verktøyet
  `wsl.exe -e /home/sihal7953/.venvs/statsbudsjett/bin/python <skript> <argumenter>`,
  eller Bash-verktøyet med `MSYS_NO_PATHCONV=1` foran samme kommando.
- Ikke bruk heredoc gjennom `wsl.exe -e bash -lc`; Windows avkorter lange
  kommandoer og apostrofer bryter siteringen. Skriv filer og kjør dem.

Workflow-skriptet får dette som `unc_project` og `python_cmd`; da får hver
agent samme instruks. Fra en WSL-sesjon utelates begge.

## Faser i workflow-skriptet

1. **Forbered** (én agent, lav effort). Henter kilder med `fetch_sources.py`
   fra `analyse/kilder/<år>/kilder-input.json`, lager tekstuttrekk med
   sidemarkører, kjører `manage_workflow.py prepare`, oppretter eller
   utvider `leveranser/<kjøring>/eksponeringslogg.md` og dokumenterer hva
   som mangler.
2. **Forutsetninger** (én agent). Bruker treffet fra `kildesjekk.json`
   (UiTs styresak) eller slår opp styreportalen selv, henter dokumentene og
   skriver `analyse/uit-forutsetninger-<år>.md` etter 2024-filens struktur.
   Ukjent forblir ukjent.
3. **Fagroller** (parallelt, én agent per rolle). Hver agent leser sitt
   historiske minne, forrige års prøveerfaring og reviewerfaringer, skriver
   `minne-lest.json` med SHA-256 før kildene åpnes, leverer `notater.md`,
   `rapport.md` og `funn.json` per del, kjører `build_evidence.py` og lagrer
   årets erfaring separat. Deler i `duplicate_parts` får et uavhengig
   andreutkast i `kontroll/<del>/` som ikke leser `deler/`, og et
   sammenlignende review som bare retter med kildebelegg.
4. **Redaktør** (én agent, etter alle roller). Kvittering, samlet rapport,
   presentasjonsspesifikasjon, meldingsutkast, `assemble_evidence.py`, og
   `build_presentation.py` når mal og renderer er oppgitt.
5. **Kontroll** (én agent, lav effort). `manage_workflow.py check`,
   `reconcile_budget.py`, lenkekontroll, hashmanifest, fullført
   eksponeringslogg og `verifikasjon.md`.

Skriptet venter på alle roller før redaktøren starter. Alt annet kjører som
pipeline. Standardvalg gir 10 agentkall pluss to per duplisert del.

## Modell og effort

Alle agenter arver sesjonens modell. Sett ikke lavere effort for deler med
sammensatte vilkår (HOD, KUD, ramme); de Codex-baserte prøvene viste at
laveste effort ga utelatte vilkår og en enhetsfeil (millioner oppgitt som
kroner). Lav effort er bare for Forbered og Kontroll. Ingen Claude-profil er
målt i dette prosjektet; skriv observasjoner fra kjøringen inn i fagrollens
erfaringsnotat med dato, modell og effort, uten å generalisere fra én
kjøring.

## Kvitteringer og eksponering

- `minne-lest.json` skrives før første kildelesing og kontrolleres av
  `manage_workflow.py check`.
- `eksponeringslogg.md` per kjøring lister forbudte mapper, hva som faktisk
  ble lest, og utilsiktede treff. Publiseringssjekken noterer hvilke
  styremøter og sakstitler den så. Loggen fullføres før fasit åpnes og
  fryses sammen med leveransen.
- Første besvarelse fryses med hash i `manifest.json` før fasit. Rettelser
  etter fasit går i ny versjon.

## Kjente begrensninger

- PowerPoint-rendering krever LibreOffice eller PowerPoint på maskinen og en
  lokal UiT-mal (`template`, `libreoffice`). Uten disse leveres
  `presentasjon.json`, og PowerPoint merkes som ikke produsert.
- `benchmark_models.py` starter Codex-klienten og brukes ikke fra Claude.
- Workflow-skriptet kan ikke lese klokken; tidsstempler gis i
  `run_started_utc`.
- Kildeoppdagelsen dekker stadiet `forslag`. Tilleggsproposisjon, saldert
  budsjett og RNB krever manuelle URL-er i `kilder-input.json`.
