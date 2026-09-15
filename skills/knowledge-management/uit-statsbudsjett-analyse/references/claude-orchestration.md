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
| `hurtig` | Hurtigsvar, Forbered (parallelt), Forutsetninger (hopper over når notatet er forberedt), Avvik | Budsjettdagen, første minutter |
| `full` | Fagroller, Redaktør, Kontroll | Samme kjøring, etter hurtigsvaret |
| `alt` | alle sju | Test |

1. **Hurtigsvar** (henting på sonnet lav, Excel-ark på opus medium). Henter
   bare blått hefte og KD, trekker ut tekst, kjører
   `parse_blaatt_hefte_table.py`, tolker kolonnene visuelt mot PDF-siden,
   bygger `leveranser/<kjøring>/uit-ramme-<år>.xlsx` med
   `build_frame_workbook.py` og skriver `hurtigsvar.md` i formatet fra
   [hurtigsvar-format.md](hurtigsvar-format.md). Hovedtallene logges;
   launcheren gjengir filen i chatten. Dette er det første svaret.
2. **Forbered** (sonnet, lav), parallelt med Excel-arket. Henter de øvrige
   kildene og UiT-dokumentene, lager uttrekk, kjører
   `manage_workflow.py prepare`, utvider `eksponeringslogg.md`.
3. **Forutsetninger** (opus, medium). Skriver
   `analyse/uit-forutsetninger-<år>.md` og `<år>-rammebro-input.json`
   (UiT-siden) fra styresaken; gjenbruker et notat forberedt i september.
4. **Avvik** (opus, medium). Harmoniserer forslagssiden mot UiTs bro,
   kjører `reconcile_budget.py`, legger arket `Mot foreløpig` inn i
   arbeidsboken og oppdaterer hurtigsvaret med avviket.
5. **Fagroller** (parallelt). Kritiske roller på opus, øvrige på sonnet;
   `minne-lest.json` før kildene, `notater.md`, `rapport.md`, `funn.json`,
   `build_evidence.py`, årets erfaring. kd_ramme kontrollerer hurtigsvarets
   bro på nytt mot kildene. Deler i `duplicate_parts` får uavhengig
   andreutkast og review.
6. **Redaktør** (opus). Samlet rapport, presentasjonsspesifikasjon,
   meldingsutkast med Excel-arket som første vedlegg, kildepakke.
7. **Kontroll** (sonnet, lav). `manage_workflow.py check`, begge
   rammebro-kontroller, ny bygging av arbeidsboken som kontroll, lenker,
   manifest med modellplan, eksponeringslogg fryst, `verifikasjon.md`.

Redaktøren venter på alle roller; alt annet kjører som pipeline eller
parallelt. `hurtig` bruker fire til fem agentkall, `full` sju pluss to per
duplisert del.

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
