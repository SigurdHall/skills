# Promptform for `/uit-statsbudsjett-proeve`

Skriv skillnavnet på første linje og feltene under som `felt: verdi`, ett per
linje. Bare `år` er obligatorisk. Uoppgitte felt får standardverdien i
tabellen. Claude viser den tolkede formen som tabell før kjøringen starter og
stopper hvis et obligatorisk felt mangler eller en verdi er ugyldig.

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
| `kjøring` | `<år>-claude-v1` | Navn på leveransemappen `leveranser/<kjøring>/`. Må være ubrukt; velg `-v2` osv. ved ny kjøring. |
| `prosjekt` | `/home/sihal7953/repos/uit-statsbudsjett` | POSIX-sti til analyseprosjektet i WSL. Fra Windows leses filene via `\\wsl.localhost\Ubuntu-24.04` + samme sti. |
| `forbudt` | `<år>/` | Mapper under prosjektet som ikke skal åpnes eller listes. I `prøve`-modus legges alltid `<år>/` til. |
| `dupliser` | `ramme` | Deler som får uavhengig andreutkast og sammenlignende review: `ramme`, `kd`, `fin`, `hod`, `kld`, `nfd`, `aid`, `kud`, `kdd`, `jd`, `ud`, `oed`. Hver del koster to ekstra agentkall. `ingen` slår av. |
| `mal` | `(ingen)` | Sti til UiT PowerPoint-mal. Uten mal lages bare `presentasjon.json`. |
| `renderer` | `(ingen)` | Sti til LibreOffice `soffice`. Uten renderer lages ingen PDF/PNG-forhåndsvisning. |
| `kun-sjekk` | `nei` | `ja`: kjør bare publiserings- og kildesjekken og rapporter. Ingen analyse startes. |
| `fortsett-ved-mangler` | `ja` | `ja`: start analysen når blått hefte og KD Prop. 1 S finnes, selv om noen fagproposisjoner eller UiTs forutsetninger mangler; manglene dokumenteres. `nei`: stopp ved enhver mangel. |

## Hva skjer etter prompten

1. Formen tolkes og vises. Mangler `år`, stopper Claude og ber om det.
2. Publiseringssjekk mot regjeringen.no og UiTs styreportal skriver
   `leveranser/<kjøring>/kildesjekk.json`. Resultatet vises som tabell:
   funnet, ikke publisert, ikke identifisert.
3. Ved `kun-sjekk: ja` eller manglende blått hefte/KD stopper kjøringen her.
4. Kildelisten skrives til `analyse/kilder/<år>/kilder-input.json`, og
   `arbeidsflyt/arbeidsdeling-<år>.json` lages fra forrige år hvis den mangler.
5. Workflowen `uit-statsbudsjett-analyse` startes med argumentene fra formen.
6. Sluttrapport med status per fase, leveransestier og hva som må gjøres før
   fasit legges inn.

## Slik hjelper Claude med å fylle formen

Spør med `/uit-statsbudsjett-proeve hjelp` eller be om «vis promptformen».
Claude svarer med denne tabellen, forrige kjørings verdier fra
`leveranser/` og forslag til `kjøring`-navn som ikke er brukt.
