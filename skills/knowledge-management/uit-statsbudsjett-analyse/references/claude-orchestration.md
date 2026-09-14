# Kjøring i Claude Code: agenter, arbeidsflyt og kvitteringer

Les dette når analysen skal kjøres i Claude Code. Filformater, minne og
leveransekrav står i [agentarbeidsflyten](agent-workflow.md); dette
dokumentet beskriver hvordan rollene faktisk startes og kontrolleres.
[Modelltestingen](model-testing.md) gjelder Codex CLI og OpenAI-profiler og
er historisk observasjon, ikke en regel for Claude.

## Verktøyvalg

| Behov | Bruk |
|---|---|
| Hele årsanalysen med fem fagroller, redaktør og kontroll | Workflow-skriptet `.claude/workflows/uit-statsbudsjett-analyse.js` i skills-repoet. Tilgjengelig som `/uit-statsbudsjett-analyse` når Claude kjører i repoet, ellers `Workflow({scriptPath: "<repo>/.claude/workflows/uit-statsbudsjett-analyse.js", args: {...}})`. |
| Én rolle på nytt, én del rettet, eller fasitsammenligning | Agent-verktøyet direkte, med oppdragsfilen fra `leveranser/<kjøring>/oppdrag/<rolle>.md` som prompt-grunnlag. |
| Deterministiske trinn: kildehenting, uttrekk, avstemming, markering, filkontroll | Python-skriptene i `scripts/` fra venv-et. Ikke la en modell regne det et skript kan regne. |

Kjør fra en sesjon som ser prosjektmappen direkte. Prosjektet ligger i WSL;
fra en Windows-sesjon må hver kommando gå gjennom `wsl.exe -e bash -lc`,
og `args.shell_prefix` settes til det. Python er
`~/.venvs/statsbudsjett/bin/python` i WSL, opprettet fra
`docs/runtime-reference/requirements-observed.txt`.

## Faser i workflow-skriptet

1. **Forbered** (én agent, lav effort). Henter kilder med `fetch_sources.py`
   fra `analyse/kilder/<år>/kilder-input.json`, lager tekstuttrekk med
   sidemarkører, kjører `manage_workflow.py prepare`, oppretter
   `leveranser/<kjøring>/eksponeringslogg.md` med forbudte mapper og
   dokumenterer hva som mangler.
2. **Forutsetninger** (én agent). Finner UiTs foreløpige fordeling for året
   i møteportalen, henter dokumentene med `fetch_sources.py` og skriver
   `analyse/uit-forutsetninger-<år>.md` etter 2024-filens struktur. Ukjent
   forblir ukjent.
3. **Fagroller** (parallelt, én agent per rolle). Hver agent leser sitt
   historiske minne og forrige års prøveerfaring, skriver `minne-lest.json`
   med SHA-256 før kildene åpnes, leverer `notater.md`, `rapport.md` og
   `funn.json` per del, kjører `build_evidence.py` per del og lagrer årets
   erfaring separat. Deler i `args.duplicate_parts` får i tillegg et
   uavhengig andreutkast i `kontroll/<del>/` som ikke leser `deler/`, og et
   sammenlignende review som skriver `kontroll.md` og bare retter rapporten
   med kildebelegg.
4. **Redaktør** (én agent, etter alle roller). Leser eget minne, skriver
   kvittering, samlet rapport, presentasjonsspesifikasjon, meldingsutkast,
   kjører `assemble_evidence.py` og `build_presentation.py` når mal og
   renderer er oppgitt, og lagrer egne erfaringer.
5. **Kontroll** (én agent, lav effort). Kjører `manage_workflow.py check`,
   `reconcile_budget.py` på årets rammebro, lenkekontroll, hashmanifest og
   fullfører eksponeringsloggen. Rapporterer manglende deler som manglende.

Skriptet venter på alle roller før redaktøren starter, fordi redaktøren
trenger alle delrapportene. Alt annet kjører som pipeline.

## Modell og effort

Alle agenter arver sesjonens modell. Sett ikke lavere effort for deler med
sammensatte vilkår (HOD, KUD, ramme); de Codex-baserte prøvene viste at
laveste effort ga utelatte vilkår og en enhetsfeil (millioner oppgitt som
kroner). Lav effort er bare for Forbered og Kontroll. Ingen Claude-profil er
målt i dette prosjektet; skriv observasjoner fra kjøringen inn i
fagrollens erfaringsnotat med dato, modell og effort, uten å generalisere
fra én kjøring.

## Kvitteringer og eksponering

- `minne-lest.json` skrives før første kildelesing og kontrolleres av
  `manage_workflow.py check`.
- `eksponeringslogg.md` per kjøring lister forbudte mapper (prøveårets
  UiT-mappe og senere fasit), hva som faktisk ble lest, og utilsiktede
  treff. Loggen fullføres før fasit åpnes og fryses sammen med leveransen.
- Første besvarelse fryses med hash i `manifest.json` før fasit. Rettelser
  etter fasit går i ny versjon.

## Kjente begrensninger

- PowerPoint-rendering krever LibreOffice eller PowerPoint på maskinen og en
  lokal UiT-mal (`args.template`, `args.libreoffice`). Uten disse leveres
  `presentasjon.json`, og PowerPoint merkes som ikke produsert.
- `benchmark_models.py` starter Codex-klienten og brukes ikke i Claude-kjøring.
- Workflow-skriptet kan ikke lese klokken; tidsstempler gis i
  `args.run_started_utc`.
