# Promptform for `/uit-statsbudsjett-proeve`

Skriv skillnavnet på første linje og feltene under som `felt: verdi`, ett per
linje. Bare `år` er obligatorisk. Uoppgitte felt får standardverdien i
tabellen. Claude viser den tolkede formen som tabell før kjøringen starter og
stopper hvis et obligatorisk felt mangler eller en verdi er ugyldig.

Slå på `/fast` i sesjonen før du starter hvis du vil ha rask Opus-utdata;
skillen kan ikke gjøre det for deg.

## To workflows

| Workflow | Hva den leverer | Når |
|---|---|---|
| `uit-ramme` | Grunnlag: fjorårets vedtatte budsjett fra blått hefte etter vedtak og UiTs foreløpige fordeling. Budsjettdagen: `uit-ramme-<år>.xlsx` med UiTs rad fra blått hefte (vedtatt året før, prisjustering, hver justering, forslag) og `hurtigsvar.md`; deretter avviket mot foreløpig fordeling | September og budsjettdagen |
| `uit-departementer` | Fagproposisjonene: programmatisk søk med treff ± ett avsnitt per del, fem fagroller med minne som tolker treffene, redaktør som oppsummerer alt, kontroll | Etter rammearket, samme kjøring |

## Budsjettdagen: to kommandoer

I september, når blått hefte for året før etter vedtak og universitetsstyrets
junisak begge er publisert:

```text
/uit-statsbudsjett-proeve
år: 2027
modus: skarp
omfang: grunnlag
```

Den dagen statsbudsjettet legges fram:

```text
/uit-statsbudsjett-proeve
år: 2027
modus: skarp
omfang: ramme
grunnlag: behold
```

Excel-arbeidsboken og `hurtigsvar.md` kommer i chatten innen minutter. Når
den er lest, kjør departementsgjennomgangen i samme kjøring:

```text
/uit-statsbudsjett-proeve
år: 2027
modus: skarp
omfang: departementer
grunnlag: behold
```

Er budsjettet ikke lagt ut, stopper skillen etter publiseringssjekken og
sier når du bør prøve igjen. `omfang: alt` kjører alt i ett.

## Test på et historisk år

```text
/uit-statsbudsjett-proeve
år: 2025
modus: prøve
forbudt: 2024/, 2025/
dupliser: ramme
```

Standard `omfang: alt` og `grunnlag: nye` gir en ren test av hele løpet.

## Full prompt med alle felt

```text
/uit-statsbudsjett-proeve
år: 2025
stadium: forslag
modus: prøve
omfang: alt
grunnlag: nye
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
| `omfang` | `alt` | `grunnlag`: bare `uit-ramme` fase Grunnlag og Forutsetninger, kan kjøres før budsjettet finnes. `ramme`: `uit-ramme` på budsjettdagen (Hurtigsvar og Avvik). `departementer`: bare `uit-departementer`, i en kjøring som har rammearket. `alt`: begge workflows i rekkefølge. |
| `grunnlag` | `nye` | `nye`: grunnlaget lages på nytt (ren test). `behold`: grunnlag forberedt med `omfang: grunnlag` beholdes; ryddesjekken lar det stå. |
| `kjøring` | `<år>-claude-v1` | Navn på leveransemappen `leveranser/<kjøring>/`. `ramme` og `departementer` skal bruke samme navn. |
| `rydd` | `ja` | `ja`: rester fra tidligere forsøk for samme år flyttes til `arkiv/avbrutt/<tidsstempel>-<kjøring>/` før start. `nei`: stopp hvis rester finnes. Fasitmappen `<år>/`, arbeidsdelingen og historiske minner røres aldri. |
| `prosjekt` | `/home/sihal7953/repos/uit-statsbudsjett` | POSIX-sti til analyseprosjektet i WSL. Fra Windows leses filene via `\\wsl.localhost\Ubuntu-24.04` + samme sti. |
| `forbudt` | `<år>/` | Mapper under prosjektet som ikke skal åpnes eller listes: UiTs eget materiale for prøveåret og alt senere som er fasit. I `prøve`-modus legges alltid `<år>/` til. |
| `dupliser` | `ramme` | Deler i `uit-departementer` som får uavhengig andreutkast og sammenlignende review: `ramme`, `kd`, `fin`, `hod`, `kld`, `nfd`, `aid`, `kud`, `kdd`, `jd`, `ud`, `oed`. Hver del koster to ekstra agentkall. `ingen` slår av. |
| `profil` | `rask` | `rask`: modellplanen under. `sesjon`: alle agenter arver sesjonens modell og effort. |
| `modeller` | `(ingen)` | Overstyring per fase som JSON, for eksempel `{"role_other": {"model": "opus"}}`. Faser: `prep`, `assumptions`, `quick`, `deviation`, `role_critical`, `role_other`, `duplicate`, `review`, `editor`, `check`. |
| `mal` | `(ingen)` | Sti til UiT PowerPoint-mal. Uten mal lages bare `presentasjon.json`. |
| `renderer` | `(ingen)` | Sti til LibreOffice `soffice`. Uten renderer lages ingen PDF/PNG-forhåndsvisning. |
| `kun-sjekk` | `nei` | `ja`: kjør bare publiserings- og kildesjekkene og rapporter. Ingen workflow startes. |
| `fortsett-ved-mangler` | `ja` | `ja`: start når blått hefte og KD Prop. 1 S finnes, selv om noen fagproposisjoner mangler; manglene dokumenteres. `nei`: stopp ved enhver mangel. |

## Rammearket

`leveranser/<kjøring>/uit-ramme-<år>.xlsx` bygges deterministisk fra blått
heftes hovedtabell etter mønster fra UiTs arbeidsbøker 2018–2019:

| Ark | Innhold |
|---|---|
| `Sektor` | Alle institusjoner: saldert året før, forslag, nominell endring, sum |
| `UiT-bro` | Vedtatt/saldert året før, hver justering i UiT-raden med prissats i merknaden, forslag som sum, kontroll mot tabellen, kontroll mot vedtatt budsjett fra blått hefte etter vedtak |
| `Mot foreløpig` | UiTs foreløpige fordeling mot forslaget per komponent, avvik (fasen Avvik) |
| `Kilder` | Dokument, URL, SHA-256, PDF-side, prissats, kolonnetolkning, kontroller |

`hurtigsvar.md` forklarer arket i formatet i `references/hurtigsvar-format.md`
i analyseskillen og gjengis i chatten.

## Modellplanen `rask`

Riktige tall på de avgjørende punktene og kort kjøretid er prioritert.
Trinnene som eier de avgjørende tallene og alle dømmende trinn kjører på
Opus med medium effort; mekaniske trinn og de øvrige rollene på Sonnet.

| Workflow og fase | Modell | Effort | Hvorfor |
|---|---|---|---|
| `uit-ramme` Grunnlag (henting) | sonnet | low | Blått hefte etter vedtak og UiT-dokumenter hentes og parses skriptstyrt |
| `uit-ramme` Forutsetninger | opus | medium | UiTs KD-ramme og bro må være eksakt |
| `uit-ramme` Hurtigsvar (henting) | sonnet | low | Blått hefte og KD hentes og parses skriptstyrt |
| `uit-ramme` Hurtigsvar (Excel-ark) | opus | medium | Kolonnetolkning, prissats og UiT-raden er dagens viktigste tall |
| `uit-ramme` Avvik | opus | medium | Harmonisering mot UiTs foreløpige fordeling |
| `uit-departementer` Forbered, Kontroll | sonnet | low | Skriptstyrt, inkludert programmatisk søk med treff ± ett avsnitt |
| Alle fem fagroller | opus | medium | Tolker de programmatiske treffene mot PDF-siden; rammebro, HOD-vilkår og KUD-tilskudd var der ett utkast oftest feilet i 2024-prøvene |
| Andreutkast (`dupliser`) | sonnet | medium | Uavhengig andre modell gir mangfold, ikke gjentakelse |
| Sammenlignende review | opus | medium | Dømmer mellom utkast |
| Redaktør | fable | high | Oppsummerer rammeark, treff og delrapporter til én rapport |

Ingen Claude-profil er målt i dette prosjektet. Planen er en arbeidsregel
som skal justeres etter første fasitkontroll, ikke en målt anbefaling.

## Hva skjer etter prompten

1. Formen tolkes og vises. Mangler `år`, stopper Claude og ber om det.
2. Ryddesjekken arkiverer rester fra tidligere forsøk (`rydd: ja`) eller
   stopper (`rydd: nei`). Forberedt grunnlag beholdes bare med
   `grunnlag: behold`.
3. Publiseringssjekk mot regjeringen.no og UiTs styreportal, for året før
   etter vedtak (grunnlag) og for året (budsjettdagen). Resultatet vises som
   tabell.
4. Ved `kun-sjekk: ja` eller manglende blått hefte/KD stopper kjøringen her.
5. Kildelistene skrives, og `arbeidsflyt/arbeidsdeling-<år>.json` lages fra
   forrige år hvis den mangler.
6. `uit-ramme` startes; Excel-arket og hurtigsvaret gjengis i chatten så
   snart de finnes. Så `uit-departementer` etter `omfang`.
7. Sluttrapport med status per fase, leveransestier og hva som må gjøres før
   fasit legges inn.

## Slik hjelper Claude med å fylle formen

Spør med `/uit-statsbudsjett-proeve hjelp` eller be om «vis promptformen».
Claude svarer med denne tabellen, forrige kjørings verdier fra
`leveranser/` og forslag til `kjøring`-navn som ikke er brukt.
