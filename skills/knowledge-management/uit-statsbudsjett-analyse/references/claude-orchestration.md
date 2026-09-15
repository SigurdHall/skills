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

## Fasesett og faser i workflow-skriptet

`phase_set` velger hva som kjøres, slik at budsjettdagen ikke venter på
hele departementsgjennomgangen:

| Fasesett | Faser | Når |
|---|---|---|
| `forutsetninger` | Forbered (bare UiT-dokumenter), Forutsetninger | September, når universitetsstyrets junisak er publisert |
| `hurtig` | Forbered, Forutsetninger (hopper over når notatet er forberedt), Hurtigsvar | Budsjettdagen, første minutter |
| `full` | Fagroller, Redaktør, Kontroll | Samme kjøring, etter hurtigsvaret |
| `alt` | alle seks | Test |

1. **Forbered** (sonnet, lav effort). Henter kilder med `fetch_sources.py`
   fra `analyse/kilder/<år>/kilder-input.json` og UiT-dokumentene fra
   `analyse/kilder/uit-forutsetninger-<år>/kilder-input.json`, lager
   tekstuttrekk med sidemarkører (blått hefte og KD først), kjører
   `manage_workflow.py prepare`, oppretter `eksponeringslogg.md`.
2. **Forutsetninger** (opus, medium). Skriver
   `analyse/uit-forutsetninger-<år>.md` og `<år>-rammebro-input.json`
   (UiT-siden) fra styresaken; gjenbruker et forberedt notat når det
   finnes. Ukjent forblir ukjent.
3. **Hurtigsvar** (opus, medium). UiT-raden i blått hefte kontrollert
   visuelt, forslagssiden i rammebroen, `reconcile_budget.py`, og
   `leveranser/<kjøring>/hurtigsvar.md` i det faste formatet fra
   [hurtigsvar-format.md](hurtigsvar-format.md). Hovedtallene logges i
   framdriftsvisningen; launcheren gjengir filen i chatten.
4. **Fagroller** (parallelt). Kritiske roller på opus, øvrige på sonnet;
   `minne-lest.json` før kildene, `notater.md`, `rapport.md`, `funn.json`,
   `build_evidence.py`, årets erfaring. kd_ramme kontrollerer hurtigsvarets
   bro på nytt mot kildene i stedet for å kopiere den. Deler i
   `duplicate_parts` får uavhengig andreutkast og review.
5. **Redaktør** (opus). Samlet rapport, presentasjonsspesifikasjon,
   meldingsutkast, kildepakke; avvik mot hurtigsvaret nevnes.
6. **Kontroll** (sonnet, lav). `manage_workflow.py check`, begge
   rammebro-kontroller, lenker, manifest med modellplan, eksponeringslogg
   fryst, `verifikasjon.md`.

Redaktøren venter på alle roller; alt annet kjører som pipeline.
Standardvalg gir 3 + 7 agentkall pluss to per duplisert del.

## Modell og effort

Workflow-skriptet har en modellplan per fase. Standardprofilen `rask`
prioriterer riktige tall på de avgjørende punktene og kort kjøretid: Opus
med medium effort på forutsetningene, rollene kd_ramme, helse_miljo og
naring_arbeid_kultur, sammenlignende review og redaktør; Sonnet på
forbered, de to øvrige rollene, andreutkast og kontroll. Tabellen med
begrunnelse står i launcherens
[promptform](../../uit-statsbudsjett-proeve/references/prompt-form.md).
`profile: sesjon` arver sesjonens modell for alle agenter; `models`
overstyrer enkeltfaser. Slå på `/fast` i sesjonen før start hvis rask
Opus-utdata er ønsket; skriptet kan ikke gjøre det.

Sett ikke lavere effort enn medium for deler med sammensatte vilkår (HOD,
KUD, ramme); de Codex-baserte prøvene viste at laveste effort ga utelatte
vilkår og en enhetsfeil (millioner oppgitt som kroner). Ingen Claude-profil
er målt i dette prosjektet. Hver agent får sin modell og effort i prompten
og skriver dem i fagrollens erfaringsnotat; juster planen etter første
fasitkontroll, ikke etter én kjøring.

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
