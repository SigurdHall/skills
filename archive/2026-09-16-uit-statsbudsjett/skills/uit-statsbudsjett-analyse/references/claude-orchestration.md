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
| Hele årsanalysen | De to workflow-skriptene `.claude/workflows/uit-ramme.js` og `.claude/workflows/uit-departementer.js` i skills-repoet, startet av `/uit-statsbudsjett-proeve`. Direkte: `Workflow({scriptPath, args})`. |
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

## To workflows

| Workflow | Fasesett | Faser | Når |
|---|---|---|---|
| `uit-ramme.js` | `grunnlag` | Grunnlag, Forutsetninger | September: blått hefte for året før etter vedtak og universitetsstyrets junisak er publisert |
| `uit-ramme.js` | `budsjettdag` | Hurtigsvar, Avvik | Budsjettdagen, første minutter |
| `uit-ramme.js` | `alt` | alle fire | Test |
| `uit-departementer.js` | | Forbered, Fagroller, Redaktør, Kontroll | Samme kjøring, etter rammearket |

**uit-ramme**

1. **Grunnlag** (sonnet, lav). Henter blått hefte for året før etter vedtak i
   Stortinget, parser hovedtabellen med `parse_blaatt_hefte_table.py` og
   skriver `analyse/saldert-<år−1>.json`; UiT-radens siste tall er vedtatt
   budsjett året før. Henter UiTs styresaksdokumenter.
2. **Forutsetninger** (opus, medium). Skriver
   `analyse/uit-forutsetninger-<år>.md` og `<år>-rammebro-input.json`
   (UiT-siden) fra styresaken; UiTs bro skal starte på vedtatt året før.
   Gjenbruker et forberedt notat.
3. **Hurtigsvar** (henting på sonnet lav, Excel-ark på opus medium). Henter
   bare blått hefte og KD, parser tabellen, tolker kolonnene visuelt mot
   PDF-siden, finner prissatsen, kontrollerer saldert i tabellen mot vedtatt
   året før, bygger `leveranser/<kjøring>/uit-ramme-<år>.xlsx` med
   `build_frame_workbook.py` og skriver `hurtigsvar.md` i formatet fra
   [hurtigsvar-format.md](hurtigsvar-format.md). Dette er det første svaret.
4. **Avvik** (opus, medium). Harmoniserer forslagssiden mot UiTs bro,
   kjører `reconcile_budget.py`, legger arket `Mot foreløpig` inn i
   arbeidsboken og oppdaterer hurtigsvaret.

**uit-departementer**

1. **Forbered** (sonnet, lav). Henter de øvrige fagproposisjonene, lager
   uttrekk, kjører `manage_workflow.py prepare`, og kjører det
   programmatiske søket `extract_hits.py`: per del ett dokument med hvert
   treffavsnitt pluss avsnittet før og etter, PDF-side og søkeord.
2. **Fagroller** (parallelt, opus medium). Hver rolle tolker treffene for
   sine deler mot PDF-siden, leter i tillegg etter tiltak uten UiT-navn,
   og leverer `minne-lest.json`, `notater.md`, `rapport.md`, `funn.json`,
   `build_evidence.py` og årets erfaring. kd_ramme kontrollerer rammearkets
   bro på nytt mot kildene. Deler i `duplicate_parts` får uavhengig
   andreutkast (sonnet) og review (opus).
3. **Redaktør** (fable, high). Oppsummerer rammeark, hurtigsvar, treff og
   delrapporter til samlet rapport, presentasjonsspesifikasjon,
   meldingsutkast med Excel-arket som første vedlegg, kildepakke.
4. **Kontroll** (sonnet, lav). `manage_workflow.py check`, begge
   rammebro-kontroller, ny bygging av arbeidsboken som kontroll, lenker,
   manifest med modellplan, eksponeringslogg fryst, `verifikasjon.md`.

Redaktøren venter på alle roller; alt annet kjører som pipeline eller
parallelt. `budsjettdag` bruker tre agentkall, `grunnlag` to,
`uit-departementer` sju pluss to per duplisert del.

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
