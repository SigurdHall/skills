# Promptform for `/uit-statsbudsjett-proeve`

Skriv skillnavnet på første linje og feltene under som `felt: verdi`, ett per
linje. Bare `år` er obligatorisk. Uoppgitte felt får standardverdien i
tabellen. Claude viser den tolkede formen som tabell før kjøringen starter og
stopper hvis et obligatorisk felt mangler eller en verdi er ugyldig.

Slå på `/fast` i sesjonen før du starter hvis du vil ha rask Opus-utdata;
skillen kan ikke gjøre det for deg.

## Budsjettdagen: to kommandoer

I september, når universitetsstyrets junisak er publisert:

```text
/uit-statsbudsjett-proeve
år: 2027
modus: skarp
omfang: forutsetninger
```

Den dagen statsbudsjettet legges fram:

```text
/uit-statsbudsjett-proeve
år: 2027
modus: skarp
omfang: alt
forutsetninger: behold
```

Først kommer Excel-arbeidsboken `uit-ramme-2027.xlsx` med UiTs rad fra
blått hefte forklart (arkene `Sektor`, `UiT-bro`, `Kilder`) og
`hurtigsvar.md` i chatten, innen minutter. Så legges avviket mot UiTs
foreløpige fordeling inn (`Mot foreløpig`), og deretter fortsetter
departementsgjennomgangen i samme kjøring. Er budsjettet ikke lagt ut,
stopper skillen etter publiseringssjekken og sier når du bør prøve igjen.

## Test på et historisk år

```text
/uit-statsbudsjett-proeve
år: 2025
modus: prøve
forbudt: 2024/, 2025/
dupliser: ramme
```

## Full prompt med alle felt

```text
/uit-statsbudsjett-proeve
år: 2025
stadium: forslag
modus: prøve
omfang: alt
forutsetninger: nye
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
| `stadium` | `forslag` | `forslag` (regjeringens opprinnelige Prop. 1 S), `tillegg`, `saldert`, `rnb`. Bare `forslag` har automatisk kildeoppdagelse i dag; de andre krever manuelle kilde-URL-er. |
| `modus` | `prøve` | `prøve`: historisk år der UiTs egen analyse finnes som fasit; prøveårets UiT-mappe og alt senere UiT-materiale er forbudt. `skarp`: årets budsjett, ingen fasit finnes ennå. |
| `omfang` | `alt` | `forutsetninger`: bare UiTs foreløpige fordeling, kan kjøres før budsjettet finnes. `hurtig`: kilder, forutsetninger og hurtigsvar. `full`: departementsgjennomgang, redaktør og kontroll i en kjøring som allerede har hurtigsvar. `alt`: hurtig og deretter full. |
| `forutsetninger` | `nye` | `nye`: forutsetningsnotat og UiT-kilder lages på nytt (ren test). `behold`: et notat forberedt med `omfang: forutsetninger` beholdes og gjenbrukes; ryddesjekken lar det stå. |
| `kjøring` | `<år>-claude-v1` | Navn på leveransemappen `leveranser/<kjøring>/`. `hurtig` og `full` skal bruke samme navn. |
| `rydd` | `ja` | `ja`: rester fra tidligere forsøk for samme år flyttes til `arkiv/avbrutt/<tidsstempel>-<kjøring>/` før start. `nei`: stopp hvis rester finnes. Fasitmappen `<år>/`, arbeidsdelingen og historiske minner røres aldri. |
| `prosjekt` | `/home/sihal7953/repos/uit-statsbudsjett` | POSIX-sti til analyseprosjektet i WSL. Fra Windows leses filene via `\\wsl.localhost\Ubuntu-24.04` + samme sti. |
| `forbudt` | `<år>/` | Mapper under prosjektet som ikke skal åpnes eller listes: UiTs eget materiale for prøveåret og alt senere som er fasit. I `prøve`-modus legges alltid `<år>/` til. |
| `dupliser` | `ramme` | Deler som får uavhengig andreutkast og sammenlignende review: `ramme`, `kd`, `fin`, `hod`, `kld`, `nfd`, `aid`, `kud`, `kdd`, `jd`, `ud`, `oed`. Hver del koster to ekstra agentkall. `ingen` slår av. |
| `profil` | `rask` | `rask`: modellplanen under. `sesjon`: alle agenter arver sesjonens modell og effort. |
| `modeller` | `(ingen)` | Overstyring per fase som JSON, for eksempel `{"role_other": {"model": "opus"}}`. Faser: `prep`, `quick`, `assumptions`, `deviation`, `role_critical`, `role_other`, `duplicate`, `review`, `editor`, `check`. |
| `mal` | `(ingen)` | Sti til UiT PowerPoint-mal. Uten mal lages bare `presentasjon.json`. |
| `renderer` | `(ingen)` | Sti til LibreOffice `soffice`. Uten renderer lages ingen PDF/PNG-forhåndsvisning. |
| `kun-sjekk` | `nei` | `ja`: kjør bare publiserings- og kildesjekken og rapporter. Ingen analyse startes. |
| `fortsett-ved-mangler` | `ja` | `ja`: start analysen når blått hefte og KD Prop. 1 S finnes, selv om noen fagproposisjoner mangler; manglene dokumenteres. `nei`: stopp ved enhver mangel. |

## Hurtigsvaret

Leveransen er Excel-arbeidsboken `leveranser/<kjøring>/uit-ramme-<år>.xlsx`,
bygd deterministisk fra blått heftes hovedtabell etter mønster fra UiTs
arbeidsbøker 2018–2019: `Sektor` (alle institusjoner, saldert, forslag,
nominell endring, sum), `UiT-bro` (saldert året før, hver justering i
UiT-raden, forslag som sum, kontroll mot tabellen), `Mot foreløpig` (avvik
per komponent, fra fasen Avvik) og `Kilder`. `hurtigsvar.md` forklarer
arket i det faste formatet i `references/hurtigsvar-format.md` i
analyseskillen og gjengis i chatten.

## Modellplanen `rask`

Riktige tall på de avgjørende punktene og kort kjøretid er prioritert.
Rollene som eier de avgjørende punktene og alle dømmende trinn kjører på
Opus med medium effort; mekaniske trinn og de øvrige rollene på Sonnet.

| Fase | Modell | Effort | Hvorfor |
|---|---|---|---|
| Hurtigsvar: henting | sonnet | low | Blått hefte og KD hentes og parses skriptstyrt |
| Hurtigsvar: Excel-ark | opus | medium | Kolonnetolkning og UiT-raden er dagens viktigste tall |
| Forbered | sonnet | low | Øvrige kilder, uttrekk og oppdragsfiler, parallelt med hurtigsvaret |
| Forutsetninger | opus | medium | UiTs KD-ramme og bro må være eksakt |
| Avvik | opus | medium | Harmonisering mot UiTs foreløpige fordeling |
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
2. Ryddesjekken arkiverer rester fra tidligere forsøk (`rydd: ja`) eller
   stopper (`rydd: nei`). Forberedte forutsetninger beholdes bare med
   `forutsetninger: behold`.
3. Publiseringssjekk mot regjeringen.no og UiTs styreportal skriver
   `leveranser/<kjøring>/kildesjekk.json`. Resultatet vises som tabell.
4. Ved `kun-sjekk: ja` eller manglende blått hefte/KD stopper kjøringen her
   (unntatt `omfang: forutsetninger`, som bare trenger UiT-saken).
5. Kildelistene skrives, og `arbeidsflyt/arbeidsdeling-<år>.json` lages fra
   forrige år hvis den mangler.
6. Workflowen startes med fasesettet fra `omfang`. Hurtigsvaret gjengis i
   chatten så snart det finnes.
7. Sluttrapport med status per fase, leveransestier og hva som må gjøres før
   fasit legges inn.

## Slik hjelper Claude med å fylle formen

Spør med `/uit-statsbudsjett-proeve hjelp` eller be om «vis promptformen».
Claude svarer med denne tabellen, forrige kjørings verdier fra
`leveranser/` og forslag til `kjøring`-navn som ikke er brukt.
