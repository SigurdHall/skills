---
name: uit-statsbudsjett-proeve
description: Brukerstartet kjøring av UiTs statsbudsjettanalyse for ett budsjettår i Claude Code. Sjekker først om blått hefte, KD Prop. 1 S og fagproposisjonene er publisert på regjeringen.no og om UiTs foreløpige fordeling finnes, skriver kildelisten, og starter workflowen uit-statsbudsjett-analyse i fasesett: forutsetninger (september), hurtigsvar (budsjettdagen, minutter) og full departementsgjennomgang. Modellplan med opus medium på avgjørende roller, sonnet på resten. Startes bare med /uit-statsbudsjett-proeve og en promptform med år.
disable-model-invocation: true
argument-hint: "år: 2027 [omfang: hurtig|full|alt|forutsetninger] [kun-sjekk: ja]"
---

# Kjør UiTs statsbudsjettanalyse for ett år

Du starter en publiseringssjekk, UiTs forutsetninger, hurtigsvaret på
budsjettdagen eller hele årsanalysen. Faglig arbeidsmåte, filformater og
kontrollkrav står i [uit-statsbudsjett-analyse](../uit-statsbudsjett-analyse/SKILL.md);
les den og [kjøringsbeskrivelsen](../uit-statsbudsjett-analyse/references/claude-orchestration.md)
før fase 5. Denne skillen eier bare oppstarten: form, ryddesjekk,
publiseringssjekk, kildeliste, start av workflow og sluttrapport.

Argumentene er `$ARGUMENTS`. Formen er dokumentert i
[promptformen](references/prompt-form.md). Hvis argumentet er `hjelp` eller
tomt, vis promptformens tabell, forrige kjørings verdier fra
`leveranser/` og et ubrukt `kjøring`-navn, og stopp.

## 1. Tolk formen

Les hvert `felt: verdi`. Fyll standardverdier fra promptformen. Krev `år`.
Avvis ugyldige verdier med én setning og stopp. Vis den tolkede formen som
tabell i chatten før neste steg. I `prøve`-modus skal `<år>/` alltid være i
`forbudt`.

## 2. Ryddesjekk

Hver kjøring starter fra tom tilstand; ingenting fra et tidligere forsøk
gjenbrukes. Unntaket er UiTs forutsetninger som er forberedt med vilje
(`forutsetninger: behold`), fordi de finnes før budsjettet legges fram.

```text
check_clean_state.py --project <prosjekt> --year <år> --run-id <kjøring> --output <prosjekt>/reviews/rydd-<kjøring>.json [--keep-assumptions]
```

Legg til `--keep-assumptions` når `forutsetninger: behold`. Returkode 3
betyr rester: leveransemappen, hentede kilder for året, forutsetningsnotat,
rammebro-filer eller årets erfaringsnotater. Med `rydd: ja` kjør samme
kommando med `--archive`; restene flyttes til
`arkiv/avbrutt/<tidsstempel>-<kjøring>/` med samme relative sti, og du
oppgir stien i chatten. Med `rydd: nei` stopp og be om nytt `kjøring`-navn
eller opprydding. Skriptet rører aldri `<år>/`, arbeidsdelingen eller de
historiske minnene.

## 3. Miljø

Prosjektet ligger i WSL. Kjør skript med WSL-Python uten shell, slik at
stier ikke siteres om:

- PowerShell-verktøyet: `wsl.exe -e /home/sihal7953/.venvs/statsbudsjett/bin/python <skript> <argumenter>`
- Bash-verktøyet: samme kommando med `MSYS_NO_PATHCONV=1` foran.

Les og skriv prosjektfiler med Read/Write/Glob på
`\\wsl.localhost\Ubuntu-24.04` + POSIX-stien. Skriptene ligger i
`/home/sihal7953/repos/skills/skills/knowledge-management/uit-statsbudsjett-analyse/scripts/`.
Hvis venv-et mangler, følg runbooken `docs/agent-continuation.md` i prosjektet.

## 4. Publiseringssjekk og kildeliste

```text
discover_sources.py check --year <år> --stage <stadium> --output <prosjekt>/leveranser/<kjøring>/kildesjekk.json
```

Skriptet slår opp blått hefte for året, årets dokumentside på
regjeringen.no, hver fagproposisjons dokumentside og PDF, Prop. 1 LS, og
UiTs foreløpige fordeling i styreportalen. Returkode 0 betyr komplett,
2 betyr ikke publisert (blått hefte eller KD mangler), 3 betyr delvis.
Vis resultatet som tabell: kilde, status (`funnet`, `ikke publisert`,
`ikke identifisert`), URL. Skriv i `eksponeringslogg.md` at UiT-portalen
er søkt, og at ingen dokumenter datert etter framleggelsen er åpnet.

Stopp-regler: `kun-sjekk: ja` stopper alltid her. `omfang: forutsetninger`
trenger bare UiT-saken (`uit_forelopig_fordeling.status = funnet`) og
ignorerer returkode 2. Ellers stopp ved returkode 2, og ved returkode 3
når `fortsett-ved-mangler: nei`. Si når neste sjekk bør gjøres:
statsbudsjettet legges fram i oktober, blått hefte samme dag.

Skriv kildelistene:

```text
discover_sources.py write --from <kildesjekk.json> --output <prosjekt>/analyse/kilder/<år>/kilder-input.json --uit-output <prosjekt>/analyse/kilder/uit-forutsetninger-<år>/kilder-input.json
```

Mangler `arbeidsflyt/arbeidsdeling-<år>.json`, kopier forrige års fil,
sett `budget_year`, `run_id` og `basis`, og behold rollene. Skriv aldri om
en eksisterende arbeidsdeling for et år som allerede er kjørt.

## 5. Start workflowen

Denne skillen er brukerens bestilling av flertrinns agentkjøring. Minn
brukeren om at `/fast` må være slått på i sesjonen på forhånd hvis rask
Opus-utdata er ønsket; skriptet kan ikke slå det på. Kall Workflow-verktøyet
med `scriptPath: /home/sihal7953/repos/skills/.claude/workflows/uit-statsbudsjett-analyse.js`
(fra Windows: `C:\repos\skills\.claude\workflows\uit-statsbudsjett-analyse.js`)
og disse argumentene fra formen:

```json
{
  "project": "<prosjekt>",
  "unc_project": "\\\\wsl.localhost\\Ubuntu-24.04<prosjekt>",
  "skill": "/home/sihal7953/repos/skills/skills/knowledge-management/uit-statsbudsjett-analyse",
  "python_cmd": "wsl.exe -e /home/sihal7953/.venvs/statsbudsjett/bin/python",
  "config": "arbeidsflyt/arbeidsdeling-<år>.json",
  "budget_year": <år>,
  "run_id": "<kjøring>",
  "stage": "<stadium som tekst>",
  "sources_input": "analyse/kilder/<år>/kilder-input.json",
  "duplicate_parts": ["<dupliser>"],
  "forbidden_dirs": ["<forbudt>"],
  "profile": "<profil>",
  "phase_set": "<fasesett>",
  "template": null,
  "libreoffice": null,
  "run_started_utc": "<nå, ISO 8601>"
}
```

Fasesett etter `omfang`:

| `omfang` | Workflow-kall | Når |
|---|---|---|
| `forutsetninger` | ett kall, `phase_set: "forutsetninger"` | September: UiTs junisak er publisert, budsjettet ikke |
| `hurtig` | ett kall, `phase_set: "hurtig"` | Budsjettdagen, første minutter |
| `full` | ett kall, `phase_set: "full"` | Samme dag, etter hurtigsvaret, samme `kjøring` |
| `alt` (standard) | to kall: først `"hurtig"`, så `"full"` | Test eller når alt skal gå i ett |

Etter et kall med `hurtig` eller `alt`: gjengi hele
`leveranser/<kjøring>/hurtigsvar.md` i chatten og oppgi stien til
Excel-arbeidsboken `leveranser/<kjøring>/uit-ramme-<år>.xlsx` (Windows:
samme sti under `\\wsl.localhost\Ubuntu-24.04`), før du starter `full`. Det
er informasjonen brukeren trenger først: hvor mye penger UiT har fått i
blått hefte, forklart i arkene `Sektor`, `UiT-bro`, `Mot foreløpig` og
`Kilder`.

`profil: rask` gir modellplanen i promptformen; `profil: sesjon` arver
sesjonens modell. Enkeltfaser overstyres med `"models": {...}` når formen
oppgir `modeller:`. Sett `template` og `libreoffice` bare når formen oppgir
stier som finnes. Ikke start samme fasesett to ganger for samme `kjøring`.

## 6. Sluttrapport

Bruk `present-complex-results`. Oppgi status per fase, modellplanen som
ble brukt, hurtigsvarets hovedtall, leveransemappen, roller uten
leveranse, og at fasit først legges inn etter at `manifest.json` og
`eksponeringslogg.md` er fryst. Ingen melding sendes til mottakere.
