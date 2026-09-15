---
name: uit-statsbudsjett-proeve
description: Brukerstartet kjøring av UiTs statsbudsjettanalyse for ett budsjettår i Claude Code. Sjekker publisering på regjeringen.no og UiTs styreportal, skriver kildelister og starter to workflows: uit-ramme (grunnlag i september; på budsjettdagen UiTs ramme fra blått hefte som Excel-ark med fjorårets vedtatte budsjett, prisjustering og bro, deretter avvik mot UiTs foreløpige fordeling) og uit-departementer (fagroller, redaktør, kontroll). Modellplan med opus medium på avgjørende trinn, sonnet på resten. Startes bare med /uit-statsbudsjett-proeve og en promptform med år.
disable-model-invocation: true
argument-hint: "år: 2027 [omfang: grunnlag|ramme|departementer|alt] [kun-sjekk: ja]"
---

# Kjør UiTs statsbudsjettanalyse for ett år

Du starter en publiseringssjekk, grunnlaget før budsjettdagen, rammearket
på budsjettdagen, departementsgjennomgangen eller alt. Faglig arbeidsmåte,
filformater og kontrollkrav står i
[uit-statsbudsjett-analyse](../uit-statsbudsjett-analyse/SKILL.md); les den
og [kjøringsbeskrivelsen](../uit-statsbudsjett-analyse/references/claude-orchestration.md)
før fase 5. Denne skillen eier bare oppstarten: form, ryddesjekk,
publiseringssjekk, kildelister, start av workflows og sluttrapport.

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
gjenbrukes. Unntaket er grunnlaget som er forberedt med vilje
(`grunnlag: behold`): fjorårets vedtatte budsjett fra blått hefte etter
vedtak og UiTs forutsetninger, som begge finnes før budsjettet legges fram.

```text
check_clean_state.py --project <prosjekt> --year <år> --run-id <kjøring> --output <prosjekt>/reviews/rydd-<kjøring>.json [--keep-prepared]
```

Legg til `--keep-prepared` når `grunnlag: behold`. Returkode 3 betyr
rester: leveransemappen, hentede kilder for året, grunnlagsfiler,
forutsetningsnotat, rammebro-filer eller årets erfaringsnotater. Med
`rydd: ja` kjør samme kommando med `--archive`; restene flyttes til
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

## 4. Publiseringssjekk og kildelister

Grunnlaget (`omfang: grunnlag` eller `alt`): sjekk året før etter vedtak.

```text
discover_sources.py check --year <år−1> --stage saldert --output <prosjekt>/leveranser/<kjøring>/kildesjekk-grunnlag.json
discover_sources.py write --from <kildesjekk-grunnlag.json> --output <prosjekt>/analyse/kilder/saldert-<år−1>/kilder-input.json --uit-output <prosjekt>/analyse/kilder/uit-forutsetninger-<år>/kilder-input.json
```

Returkode 0 betyr at blått hefte for `<år−1>` etter vedtak og UiTs styresak
«Foreløpig fordeling av budsjett for <år>» begge er funnet; 3 betyr bare
blått hefte; 2 betyr ingen av dem.

Budsjettdagen (`omfang: ramme`, `departementer` eller `alt`): sjekk året.

```text
discover_sources.py check --year <år> --stage <stadium> --output <prosjekt>/leveranser/<kjøring>/kildesjekk.json
discover_sources.py write --from <kildesjekk.json> --output <prosjekt>/analyse/kilder/<år>/kilder-input.json --uit-output <prosjekt>/analyse/kilder/uit-forutsetninger-<år>/kilder-input.json
```

Skriptet slår opp blått hefte for året, årets dokumentside på
regjeringen.no, hver fagproposisjons dokumentside og PDF, Prop. 1 LS, og
UiTs foreløpige fordeling i styreportalen. Returkode 0 betyr komplett,
2 betyr ikke publisert (blått hefte eller KD mangler), 3 betyr delvis.
Vis resultatet som tabell: kilde, status (`funnet`, `ikke publisert`,
`ikke identifisert`), URL. Skriv i `eksponeringslogg.md` at UiT-portalen
er søkt, og at ingen dokumenter datert etter framleggelsen er åpnet.

Stopp-regler: `kun-sjekk: ja` stopper alltid etter sjekkene. Ellers stopp
ved returkode 2 for det omfanget som er valgt, og ved returkode 3 når
`fortsett-ved-mangler: nei`. Si når neste sjekk bør gjøres:
statsbudsjettet legges fram i oktober, blått hefte samme dag.

Mangler `arbeidsflyt/arbeidsdeling-<år>.json`, kopier forrige års fil,
sett `budget_year`, `run_id` og `basis`, og behold rollene. Skriv aldri om
en eksisterende arbeidsdeling for et år som allerede er kjørt.

## 5. Start workflowene

Denne skillen er brukerens bestilling av flertrinns agentkjøring. Minn
brukeren om at `/fast` må være slått på i sesjonen på forhånd hvis rask
Opus-utdata er ønsket; skriptene kan ikke slå det på. To workflows ligger i
skills-repoets `.claude/workflows/` (fra Windows:
`C:\repos\skills\.claude\workflows\`, fra WSL:
`/home/sihal7953/repos/skills/.claude/workflows/`):

| Workflow | Leverer | Kall etter `omfang` |
|---|---|---|
| `uit-ramme.js` | Grunnlag (vedtatt budsjett året før, UiTs forutsetninger); på budsjettdagen `uit-ramme-<år>.xlsx` og `hurtigsvar.md`, deretter avviket mot foreløpig fordeling | `grunnlag` → `phase_set: "grunnlag"`; `ramme` → `"budsjettdag"`; `alt` → `"alt"` |
| `uit-departementer.js` | Fagroller, redaktør, kontroll i samme kjøring | `departementer` og `alt` |

Argumenter fra formen, felles for begge:

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
  "phase_set": "<se tabellen>",
  "template": null,
  "libreoffice": null,
  "run_started_utc": "<nå, ISO 8601>"
}
```

Etter `uit-ramme` med `budsjettdag` eller `alt`: gjengi hele
`leveranser/<kjøring>/hurtigsvar.md` i chatten og oppgi stien til
`leveranser/<kjøring>/uit-ramme-<år>.xlsx` (Windows: samme sti under
`\\wsl.localhost\Ubuntu-24.04`), før du starter `uit-departementer`. Det
er informasjonen brukeren trenger først: hvor mye penger UiT har fått i
blått hefte, forklart i arkene `Sektor`, `UiT-bro`, `Mot foreløpig` og
`Kilder`, med fjorårets vedtatte budsjett, prissats og bro.

`profil: rask` gir modellplanen i promptformen; `profil: sesjon` arver
sesjonens modell. Enkeltfaser overstyres med `"models": {...}` når formen
oppgir `modeller:`. Sett `template` og `libreoffice` bare når formen oppgir
stier som finnes. Ikke start samme workflow to ganger for samme `kjøring`.

## 6. Sluttrapport

Bruk `present-complex-results`. Oppgi status per fase i begge workflows,
modellplanen som ble brukt, hurtigsvarets hovedtall, leveransemappen,
roller uten leveranse, og at fasit først legges inn etter at
`manifest.json` og `eksponeringslogg.md` er fryst. Ingen melding sendes til
mottakere.
