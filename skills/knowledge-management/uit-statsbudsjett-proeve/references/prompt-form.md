# Promptform for `/uit-statsbudsjett-proeve`

Skriv skillnavnet på første linje og feltene under som `felt: verdi`, ett per
linje. Bare `år` er obligatorisk. Uoppgitte felt får standardverdien i
tabellen. Claude viser den tolkede formen som tabell før kjøringen starter og
stopper hvis et obligatorisk felt mangler eller en verdi er ugyldig.

Slå på `/fast` i sesjonen før du starter hvis du vil ha rask Opus-utdata;
skillen kan ikke gjøre det for deg.

## Minste prompt

```text
/uit-statsbudsjett-proeve
år: 2025
```

## Full prompt med alle felt

```text
/uit-statsbudsjett-proeve
år: 2025
stadium: forslag
modus: prøve
kjøring: 2025-claude-v1
prosjekt: /home/sihal7953/repos/uit-statsbudsjett
forbudt: 2024/, 2025/
dupliser: ramme
rydd: ja
profil: rask
modeller: (ingen)
mal: (ingen)
renderer: (ingen)
kun-sjekk: nei
fortsett-ved-mangler: ja
```

## Felt

| Felt | Standard | Gyldige verdier og betydning |
|---|---|---|
| `år` | ingen, må oppgis | Budsjettåret Y. Forslaget for Y publiseres normalt i oktober Y−1. |
| `stadium` | `forslag` | `forslag` (regjeringens opprinnelige Prop. 1 S), `tillegg` (tilleggsproposisjon), `saldert` (etter Stortingets vedtak), `rnb`. Bare `forslag` har automatisk kildeoppdagelse i dag; de andre krever manuelle kilde-URL-er. |
| `modus` | `prøve` | `prøve`: historisk år der UiTs egen analyse finnes som fasit; prøveårets UiT-mappe og alt senere UiT-materiale er forbudt. `skarp`: årets budsjett, ingen fasit finnes ennå. |
| `kjøring` | `<år>-claude-v1` | Navn på leveransemappen `leveranser/<kjøring>/`. Hver kjøring starter fra tom tilstand; se `rydd`. |
| `rydd` | `ja` | `ja`: rester fra tidligere forsøk for samme år (leveransemappe, hentede kilder, forutsetningsnotat, årets erfaringsnotater) flyttes til `arkiv/avbrutt/<tidsstempel>-<kjøring>/` før start. `nei`: stopp hvis rester finnes. Fasitmappen `<år>/`, arbeidsdelingen og historiske minner røres aldri. |
| `prosjekt` | `/home/sihal7953/repos/uit-statsbudsjett` | POSIX-sti til analyseprosjektet i WSL. Fra Windows leses filene via `\\wsl.localhost\Ubuntu-24.04` + samme sti. |
| `forbudt` | `<år>/` | Mapper under prosjektet som ikke skal åpnes eller listes: UiTs eget materiale for prøveåret og alt senere som er fasit. I `prøve`-modus legges alltid `<år>/` til. |
| `dupliser` | `ramme` | Deler som får uavhengig andreutkast og sammenlignende review: `ramme`, `kd`, `fin`, `hod`, `kld`, `nfd`, `aid`, `kud`, `kdd`, `jd`, `ud`, `oed`. Hver del koster to ekstra agentkall. `ingen` slår av. |
| `profil` | `rask` | `rask`: modellplanen under. `sesjon`: alle agenter arver sesjonens modell og effort. |
| `modeller` | `(ingen)` | Overstyring per fase som JSON, for eksempel `{"role_other": {"model": "opus"}}`. Faser: `prep`, `assumptions`, `role_critical`, `role_other`, `duplicate`, `review`, `editor`, `check`. |
| `mal` | `(ingen)` | Sti til UiT PowerPoint-mal. Uten mal lages bare `presentasjon.json`. |
| `renderer` | `(ingen)` | Sti til LibreOffice `soffice`. Uten renderer lages ingen PDF/PNG-forhåndsvisning. |
| `kun-sjekk` | `nei` | `ja`: kjør bare publiserings- og kildesjekken og rapporter. Ingen analyse startes. |
| `fortsett-ved-mangler` | `ja` | `ja`: start analysen når blått hefte og KD Prop. 1 S finnes, selv om noen fagproposisjoner eller UiTs forutsetninger mangler; manglene dokumenteres. `nei`: stopp ved enhver mangel. |

## Modellplanen `rask`

Riktige tall på de avgjørende punktene og kort kjøretid er prioritert.
Rollene som eier de avgjørende punktene og alle dømmende trinn kjører på
Opus med medium effort; mekaniske trinn og de øvrige rollene på Sonnet.

| Fase | Modell | Effort | Hvorfor |
|---|---|---|---|
| Forbered | sonnet | low | Henting, uttrekk og oppdragsfiler er skriptstyrt |
| Forutsetninger | opus | medium | UiTs KD-ramme og bro må være eksakt |
| kd_ramme, helse_miljo, naring_arbeid_kultur | opus | medium | Rammebro, HOD-vilkår og KUD-tilskudd var der ett utkast oftest feilet i 2024-prøvene |
| bygg_samisk_justis, nordomraader_energi | sonnet | medium | Færre navngitte UiT-beløp; review fanger avvik hvis delen dupliseres |
| Andreutkast (`dupliser`) | sonnet | medium | Uavhengig andre modell gir mangfold, ikke gjentakelse |
| Sammenlignende review | opus | medium | Dømmer mellom utkast og gjenoppretter vilkår |
| Redaktør | opus | medium | Samordner beløp på tvers av departementer |
| Kontroll | sonnet | low | Skriptkjøring, lenker og hasher |

Ingen Claude-profil er målt i dette prosjektet. Planen er en arbeidsregel
som skal justeres etter første fasitkontroll, ikke en målt anbefaling.

## Hva skjer etter prompten

1. Formen tolkes og vises. Mangler `år`, stopper Claude og ber om det.
   Ryddesjekken arkiverer rester fra tidligere forsøk (`rydd: ja`) eller
   stopper (`rydd: nei`).
2. Publiseringssjekk mot regjeringen.no og UiTs styreportal skriver
   `leveranser/<kjøring>/kildesjekk.json`. Resultatet vises som tabell:
   funnet, ikke publisert, ikke identifisert.
3. Ved `kun-sjekk: ja` eller manglende blått hefte/KD stopper kjøringen her.
4. Kildelisten skrives til `analyse/kilder/<år>/kilder-input.json`, og
   `arbeidsflyt/arbeidsdeling-<år>.json` lages fra forrige år hvis den mangler.
5. Workflowen `uit-statsbudsjett-analyse` startes med argumentene fra formen
   og modellplanen.
6. Sluttrapport med status per fase, leveransestier og hva som må gjøres før
   fasit legges inn.

## Slik hjelper Claude med å fylle formen

Spør med `/uit-statsbudsjett-proeve hjelp` eller be om «vis promptformen».
Claude svarer med denne tabellen, forrige kjørings verdier fra
`leveranser/` og forslag til `kjøring`-navn som ikke er brukt.
