# UiT forretningslogikk for økonomi, styring og OKR/KPI

Status: arbeidsdokument
Sist oppdatert: 2026-06-19
Omfang: UiT Norges arktiske universitet, økonomistyring, virksomhetsstyring, BOA/BEV, budsjett, rapportering og forslag til OKR/KPI.

## Formål

Dette dokumentet beskriver kjernen i UiTs økonomiske forretningslogikk fra statlig bevilgning til intern fordeling, bevilgningsøkonomi (BEV), bidrags- og oppdragsaktivitet (BOA), nettobidrag, budsjettoppfølging og strategisk styring.

Dokumentet skal brukes som felles begrepsgrunnlag for:

- økonomimodell og semantisk modell i Power BI/BI-løsninger
- økonomirapportering og tertialrapportering
- definisjon av økonomi-OKR/KPI
- kobling mellom økonomistyring, UiTs strategi, utviklingsavtale og langtidsplaner
- forklaring av styringsrelasjonen mellom KD, UiT og fakulteter/enheter

Dokumentet er ikke en formell økonomiinstruks. Der dokumentet beskriver intern logikk, må begrepene kvalitetssikres mot gjeldende UiT-rutiner, kontoplan, økonomiinstruks, tildelingsbrev, budsjettvedtak og disponeringsskriv.

## Kort kjernefortelling

UiTs økonomi kan forstås som en styringskjede:

1. Stortinget vedtar statsbudsjettet.
2. Kunnskapsdepartementet (KD) stiller bevilgning og føringer til disposisjon for UiT gjennom tildelingsbrev og supplerende tildelingsbrev.
3. KD og UiT har utviklingsavtale som konkretiserer institusjonens strategiske bidrag til nasjonale sektormål.
4. Universitetsstyret vedtar intern budsjettfordeling, overordnede prioriteringer, langtidsplaner og virksomhetsplan.
5. Rektor/disponeringsskriv fordeler rammer og forventninger til fakulteter, UMAK, UB, fellesadministrasjon og andre enheter.
6. Fakulteter og enheter omsetter rammer og føringer til årsplaner, budsjett, bemanning, porteføljevalg, BOA-ambisjoner og tiltak.
7. Regnskap, budsjett, prognose og nøkkelindikatorer følges opp i økonomirapporter, virksomhetsrapporter/tertialrapporter, dialogmøter og årsrapport.

For økonomistyring er hovedspenningen å balansere:

- stabil basisdrift finansiert av KD-bevilgningen
- strategisk omstilling og prioriteringer innenfor begrenset handlingsrom
- eksternfinansiert aktivitet som bygger faglig kapasitet uten å svekke basisøkonomien
- god utnyttelse av personell, areal, infrastruktur og data
- etterprøvbarhet, internkontroll, personvern og rapportering til KD/Riksrevisjonen

## Styringskjede og dokumenthierarki

### KD til UiT

KD styrer UiT gjennom flere mekanismer:

| Mekanisme | Rolle i økonomistyringen |
| --- | --- |
| Statsbudsjett | Stortingets vedtak om økonomiske rammer og politiske prioriteringer. |
| Tildelingsbrev | KDs årlige styringsdokument. Inneholder bevilgning, føringer, forventninger, fullmakter og rapporteringskrav. |
| Supplerende tildelingsbrev | Endringer, presiseringer eller nye tildelinger gjennom året. |
| Utviklingsavtale | Differensierte mål og styringsparametere mellom KD og UiT. Kobler UiTs profil til nasjonale sektormål. |
| Etatsstyring | Dialog om måloppnåelse, risiko, økonomi, prioriteringer og oppfølging. |
| Årsrapport og regnskap | UiTs formelle rapportering til KD, DBH og Riksrevisjonen om resultater, ressursbruk og økonomi. |

I KD tildelingsbrev 2026 er rammen tydelig: UH-sektoren skal levere høy kvalitet og relevant kompetanse i en situasjon med strammere økonomisk handlingsrom, kompetanseknapphet, teknologiutvikling, demografiske endringer og behov for effektiv ressursutnyttelse.

### UiT internt

UiTs virksomhetsstyring binder strategi, plan, økonomi og rapportering sammen:

| Internt styringselement | Rolle |
| --- | --- |
| `Eallju - Drivkraft i nord` | Overordnet strategi mot 2030. Rammesetter faglige og organisatoriske prioriteringer. |
| Overordnet langtidsplan | Rammer for felles investeringer og programmer med utgangspunkt i strategien. |
| Fakultetenes strategiske langtidsplaner | Fakultetenes realisering av strategien, inkludert faglige prioriteringer, kapasitet og økonomi. |
| Budsjettvedtak | Styrets fordeling av budsjettrammer til hovedenheter og overordnet virksomhetsplan for kommende år. |
| Disponeringsskriv | Rektors årlige styringsdokument til enhetene. Formaliserer rammer, forventninger og prioriteringer. |
| Årsplan/budsjett | Enhetenes operative prioriteringer, ressursbruk og mål for året. |
| Virksomhetsrapport/tertialrapport | Status på økonomiske resultater, styringsparametere, risiko og måloppnåelse. |
| Dialogmøter | Arena for oppfølging mellom universitetsledelse og fakulteter/enheter. |

En viktig implikasjon er at økonomimodellen ikke bare skal svare på "hva kostet det?", men også:

- hvilken strategisk prioritering aktiviteten støtter
- hvilken styringsramme som gjelder
- hvilken enhet som har resultatansvar
- om aktiviteten finansieres av bevilgning, ekstern finansiering eller en kombinasjon
- om ressursbruken gir ønsket faglig, økonomisk og samfunnsmessig effekt

## Økonomimodellen

### Hva økonomimodellen skal gjøre

Økonomimodellen er strukturen som fanger økonomisk informasjon slik at UiT kan produsere styringsinformasjon på dimensjoner som gjenspeiler aktiviteten i virksomheten.

I praksis må modellen støtte:

- regnskap, budsjett, prognose og avvik
- periodisering og tertialoppfølging
- BEV/BOA-skille
- organisasjon, fakultet, institutt, seksjon og koststed
- prosjekt, delprosjekt, arbeidspakke og finansieringskilde
- konto, kontoklasse, regnskapsgruppe og BOA-kontogrupper
- budsjettversjon og transaksjonstype
- rolle- og ansvarsdimensjoner, for eksempel prosjektleder, prosjektøkonom og delprosjektansvarlig
- sporbarhet til bilag, kilde, budsjettversjon og rapporteringsperiode

### Semantisk kjerne i lokal modell

Den lokale Power BI-modellen for økonomi har en faktatabell `fak_okonomi` med beløp, timer, periode, kilde og dimensjonsnøkler. Sentrale dimensjoner er:

| Dimensjon | Styringsrolle |
| --- | --- |
| `dim_konto` | Kontoplan, kontoklasse, resultat/balanse, regnskapsgrupper, BOA-egenfinansiering og indirekte kostnader. |
| `dim_koststed` | Organisatorisk ansvar og intern rapporteringsstruktur. |
| `dim_prosjekt` | Prosjektstruktur, prosjekttype, prosjektleder, eiersted, strategisk satsing og prosjektstatus. |
| `dim_delprosjekt` | Delprosjekt, finansieringskilde, aktivitetstype, kontrakt, egenfinansiering og periode. |
| `dim_hovedfinansiering` | Overordnet finansieringskategori. |
| `dim_budsjettversjon` | Budsjettversjon og status/tidsramme. |
| `dim_budsjettprofil` | Profilering/periodisering av budsjett. |
| `dim_periode`/`dim_dato` | Tid, rapporteringsperiode, måned og år. |
| `dim_orgreg`/organisasjon | Organisasjonsstruktur og rapporteringslinje. |

Grunnmål i modellen:

| Mål | Modellogikk |
| --- | --- |
| `Regnskap` | Summerer `fak_okonomi[belop_regnskap]`, men ekskluderer definerte balanse-, oppgjørs- og mellomværendekonti fra basisoppfølging. |
| `Budsjett rå` | Teknisk/skjult råsum av `fak_okonomi[belop_budsjett]`. Skal ikke brukes direkte i rapportvisualer. |
| `Budsjett grunnlag` | Teknisk/skjult budsjettgrunnlag der samme kontoekskludering som for `Regnskap` er brukt før budsjettversjon legges på. Alle rapportbudsjett skal bygge på dette målet, ikke på `Budsjett rå`. |
| `Budsjett` | Budsjett filtrert til gjeldende BEVAAR-budsjett for valgt år, med `transaksjon_dato` til og med den 20. i påfølgende måned. |
| `Budsjett - Godkjent` | BEV-helpermål filtrert til rektorgodkjent BEVAAR-basis, `BEVAAR<år>_M1`. Rektorgodkjent totalbudsjett summerer dette med godkjent BOAVUR-basis. |
| `Budsjett BOA - Godkjent` | BOA-helpermål filtrert til rektorgodkjent BOAVUR-basis, `BOAVUR<år>_M1`, og prosjekttyper som starter med `Z`. |
| `Budsjett total - Godkjent` | Rektorgodkjent totalbudsjett som summerer `Budsjett - Godkjent` og `Budsjett BOA - Godkjent`. |
| `Budsjett godkjent hittil valgt måned` | Rektorgodkjent totalbudsjett januar til valgt måned, basert på `BEVAAR<år>_M1 + BOAVUR<år>_M1`. |
| `Årsbudsjett - Godkjent` | Fullårs rektorgodkjent totalbudsjett, basert på `BEVAAR<år>_M1 + BOAVUR<år>_M1`. |
| `Regnskap hittil valgt måned` | Regnskap filtrert til valgt år og måned. Perioden vises først når publiseringsdatoen `DATE(valgt år, valgt måned + 1, 10)` er passert, og regnskapslinjer avgrenses med `sist_oppdatert` til samme dato. |
| `Budsjett hittil valgt måned` | Budsjett filtrert til valgt år og måned, gjeldende BEVAAR-budsjett og `transaksjon_dato` til og med den 20. i påfølgende måned. |
| `Avvik mot budsjett hittil valgt måned` | Regnskap hittil minus budsjett hittil. |
| `Regnskap / budsjett hittil valgt måned` | Regnskap hittil dividert på budsjett hittil. |
| `Prosentavvik mot budsjett hittil valgt måned` | Avvik hittil dividert på budsjett hittil. |
| `Regnskap / budsjett hittil valgt måned i fjor` | Samme forholdstall, men for valgt måned i foregående år. |
| `Prosentavvik mot budsjett hittil valgt måned, år i visual` | Grafmål som beregner prosentavvik for hvert år på aksen, begrenset til siste fem år fra valgt år. |
| `Prosentavvik mot budsjett hittil måned i visual` | Grafmål som beregner prosentavvik hittil for hver måned i valgt år, begrenset til måneder til og med valgt måned. |
| `Budsjett resterende år` | Gjeldende BEVAAR-budsjett fra måneden etter valgt måned til desember, med samme 20-dagers as-of-regel og samme kontoekskludering som øvrige budsjettmål. |
| `Årsprognose` | Regnskap hittil valgt måned pluss gjeldende budsjett for resterende år. |
| `Avvik årsprognose mot gjeldende årsbudsjett` | Årsprognose minus gjeldende årsbudsjett. |
| `Årsprognose / gjeldende årsbudsjett` | Årsprognose dividert på gjeldende årsbudsjett. |
| `Prosentavvik årsprognose mot gjeldende årsbudsjett` | Prognoseavvik dividert på gjeldende årsbudsjett. |

### Measure-lag i økonomirapporten

Økonomirapporten bruker flere DAX-lag for å holde forretningslogikken eksplisitt og gjenbrukbar:

| Lag | Rolle |
| --- | --- |
| `01 Basis` | Rå og renset regnskaps-/budsjettgrunnlag. Kontoekskludering ligger her. |
| `02 Budsjettversjon` | Tekstnøkler for budsjettversjoner, for eksempel `BEVAAR<år>`, `BEVAAR<år>_M1`, `BOAVUR<år>` og `BOAVUR<år>_M1`. |
| `03 Budsjettkategori` | BEV, BOA og totalbudsjettområde. Prosjekttypeavgrensning ligger her, ikke i visualfilter. |
| `04 Hittil og helår` | Valgt periode, hittil, helår og resterende år. |
| `05 Resultatområde` | Inntekter, kostnader og nettobidrag basert på `dim_konto[kontorelasjon4]` eller `kontorelasjon4_kode`. |
| `06 KPI` | Avvik, regnskap/budsjett-forhold og prosentavvik for kort og standardgrafer. |
| `07 Prognose` | Årsprognose basert på regnskap hittil pluss totalbudsjett for resterende år. |
| `08` og `09` | Side-spesifikke measures for økonomiutvikling og prognoseutvikling. |

Standardkort og standardgrafer skal bruke eksplisitte measures for inntekter, kostnader og nettobidrag. De skal ikke være avhengige av at samme `kontorelasjon4`- eller `prosjekttype_kode`-filter er lagt riktig på hvert visual. Visualfiltre kan fortsatt brukes i ad hoc-tabeller og frie analyser.

Totalbudsjettet i økonomirapporten defineres som:

```text
Totalbudsjett = BEV + BOA
BEV = BEVAAR<år> for prosjekttype A1, A2, I1, I2, I3
BOA = BOAVUR<år> for prosjekttyper som starter med Z
```

For rektorgodkjent totalbudsjett brukes tilsvarende godkjente M1-versjoner:

```text
Rektorgodkjent totalbudsjett = BEV godkjent + BOA godkjent
BEV godkjent = BEVAAR<år>_M1 for prosjekttype A1, A2, I1, I2, I3
BOA godkjent = BOAVUR<år>_M1 for prosjekttyper som starter med Z
```

Relasjonen mellom `fak_okonomi` og `dim_prosjekt` skal være aktiv i økonomimodellen. BEV/BOA-mål kan derfor filtrere direkte på `dim_prosjekt[prosjekttype_kode]` uten å gjenta relasjonsaktivering i hvert mål.

Relasjonen mellom `dim_prosjekt[koststed_kode]` og `dim_koststed[koststed_kode]` skal være inaktiv når både `fak_okonomi -> dim_prosjekt` og `fak_okonomi -> dim_koststed` er aktive. Ellers får modellen to aktive filterveier mellom faktatabellen, prosjekt og koststed. Koststedfiltrering skal gå direkte fra `dim_koststed` til `fak_okonomi`; prosjektfiltrering skal gå direkte fra `dim_prosjekt` til `fak_okonomi`.

As-of-regler i lokal modell:

| Datatype | Dato-/snapshotregel |
| --- | --- |
| Regnskap | Perioden vises først når `DATE(valgt år, valgt måned + 1, 10) <= TODAY()`. Når perioden vises, filtreres regnskapslinjer med `fak_okonomi[sist_oppdatert] <= DATE(valgt år, valgt måned + 1, 10)`. For mai 2026 betyr det at regnskap for mai vises fra 10.06.2026, med linjer oppdatert til og med 10.06.2026. |
| Budsjett | `fak_okonomi[transaksjon_dato] <= DATE(valgt år, valgt måned + 1, 20)`. For mai 2026 betyr det budsjettlinjer med transaksjonsdato til og med 20.06.2026. |
| Graf over år | Samme regler brukes per år i visualet: regnskap styres av publisering den 10. i påfølgende måned og `sist_oppdatert`, mens gjeldende budsjett styres av `transaksjon_dato` til 20. i påfølgende måned. |

Avvik, prosentavvik og prognosemål som bygger på regnskap skal returnere blank når regnskapsgrunnlaget for perioden ikke er publisert, slik at blankt regnskap ikke behandles som 0 mot budsjett.

### Konto- og resultatlogikk

Basis-målene i økonomirapporten skal vise driftsoppfølging mot budsjett. Følgende konti ekskluderes derfor direkte i DAX for `Regnskap` og `Budsjett grunnlag`: `1030`, `1039`, `1040`, `1048`, `1049`, `1060`, `1069`, `1070`, `1101`-`1109`, `1130`-`1139`, `1150`, `1160`, `1161`, `1169`, `1170`, `1179`, `1200`-`1211`, `1220`, `1229`, `1230`, `1231`, `1239`, `1240`, `1249`, `1250`, `1251`, `1258`, `1259`, `1260`, `1261`, `1262`, `1269`, `1270`, `1278`, `1279`, `1280`-`1290`, `1297`-`1300`, `1330`, `1340`, `1350`-`1352`, `1361`, `1441`, `1460`-`1463`, `1500`, `1501`, `1530`, `1532`, `1540`-`1545`, `1570`-`1580`, `1700`, `1701`, `1760`, `1790`, `1791`, `1900`, `1901`, `1920`, `1950`, `1960`-`1964`, `1967`-`1969`, `2000`, `2001`, `2050`, `2051`, `2150`-`2192`, `2400`-`2403`, `2500`, `2550`, `2600`-`2602`, `2611`, `2615`, `2620`, `2630`-`2640`, `2650`, `2690`, `2695`, `2700`-`2720`, `2740`, `2770`-`2790`, `2800`, `2801`, `2807`-`2809`, `2900`-`2916`, `2931`-`2944`, `2960`-`2963`, `2980`-`2983`, `2990`, `2992`, `2993`, `2996`, `2999` og `8901`.

Begrunnelsen er at disse kontoene i hovedsak er balanse-, anleggs-, fordrings-, bank-, egenkapital-, gjelds-, avgifts-, oppgjørs- og mellomværendekonti. De beskriver finansiering, oppgjør, periodiseringer, interne mellomværender eller balanseposisjoner, ikke ordinær drift i resultatoppfølgingen. Hvis de tas med i basis-mål for regnskap/budsjett, kan de gi kunstige avvik, dobbelttelling eller blande balansebevegelser inn i inntekts-, kostnads- og nettobidragskortene. Konto `2160`, `2161`, `2170` og `2171` er balansekontoer for avsetninger. De hører hjemme i avsetningsanalyse, ikke i nettobidragsberegning eller generelle basis-mål.

Standard-KPI-er skal ha resultatområde og budsjettområde definert i DAX. Visualfiltre på `kontorelasjon4` og `prosjekttype_kode` skal bare brukes når visualet er eksplisitt laget som en fleksibel analyseflate.

Anbefalt DAX-filter for eksplisitte resultatområde-mål:

| Begrep | DAX-filter | Kommentar |
| --- | --- | --- |
| Inntekter | `dim_konto[kontorelasjon4] = "Inntekter"` eller tilsvarende kode i `kontorelasjon4_kode`. | Brukes i egne inntektsmål, for eksempel `Regnskap / budsjett hittil total - Inntekter`. |
| Kostnader | `dim_konto[kontorelasjon4] = "Kostnader"` eller tilsvarende kode. | Fortegnslogikken følger kildemodellen; ikke bruk `ABS` i målet. |
| Nettobidrag | `dim_konto[kontorelasjon4] = "Nettobidrag"` eller tilsvarende kode. | Viser nettobidrag slik kontorelasjonen er modellert i `dim_konto`. |
| Total | Ingen resultatområdefilter. | Brukes for samlet status på valgt enhet, campus, prosjekt eller annen rapportkontekst. |

Nettobidrag er derfor ikke bare et BOA-begrep. Det er et styringsmål for økonomisk bidrag i resultatregnskapet. For BOA må nettobidrag vurderes sammen med finansieringskilde, prosjekt/delprosjekt, egenfinansiering, indirekte kostnader, frikjøp/lønn og intern kostnadsfordeling.

Fortegn må standardiseres i rapportering. I lokal økonomirapport er valgt hovedlogikk `regnskap / budsjett`, uten `ABS`. Det betyr at 100 % betyr at regnskap er lik budsjett, under 100 % betyr lavere regnskap enn budsjett, og over 100 % betyr høyere regnskap enn budsjett. For inntekter og kostnader må tolkningen av "bra/dårlig" forklares i rapporttekst eller terskler, fordi fortegn og styringsønske kan være ulikt.

Anbefalt bruk i standardkort:

| Kort | Hovedverdi | Referansefelt | Fast resultatområde |
| --- | --- | --- | --- |
| Inntekter mot budsjett | `Regnskap / budsjett hittil total - Inntekter` | `Prosentavvik hittil total - Inntekter`, `Regnskap / budsjett hittil total i fjor - Inntekter` | Ligger i DAX-målet. |
| Kostnader mot budsjett | `Regnskap / budsjett hittil total - Kostnader` | `Prosentavvik hittil total - Kostnader`, `Regnskap / budsjett hittil total i fjor - Kostnader` | Ligger i DAX-målet. |
| Nettobidrag mot budsjett | `Regnskap / budsjett hittil total - Nettobidrag` | `Prosentavvik hittil total - Nettobidrag`, `Regnskap / budsjett hittil total i fjor - Nettobidrag` | Ligger i DAX-målet. |
| Total mot budsjett | `Regnskap / budsjett hittil total` | `Prosentavvik hittil total`, `Regnskap / budsjett hittil total i fjor` | Ingen fast resultatområdefilter. |

Visualfiltre på `kontorelasjon4` kan fortsatt brukes i frie analysevisualiseringer, men standardkort, standardgrafer og gjenbrukbare KPI-er skal ha fast område- og prosjektlogikk i DAX når definisjonen er en del av forretningslogikken.

### Trendgraf for budsjettavvik

Grafen for utvikling over tid skal vise hvor mye valgt område avviker fra budsjettet i samme måned de siste årene. Formålet er ikke å vise akkumulert utvikling måned for måned, men å sammenligne samme rapporteringssnitt på tvers av år.

Anbefalt oppsett:

| Rolle i visual | Felt |
| --- | --- |
| X-akse | `graf_aar[aar]`, frikoblet aksetabell. Ikke bruk `dim_dato[aar]` her, fordi år-sliceren da filtrerer grafen ned til ett år. |
| Verdi | `Prosentavvik mot budsjett hittil valgt måned, år i visual` |
| Filter | Siste fem år håndteres i målet: år i visual fra valgt år minus fire til valgt år. |
| Resultatområde | Eksplisitt resultatområde-measure, eller `kontorelasjon4` som forklaring dersom grafen skal vise flere linjer samtidig. |

Målet bruker valgt måned fra slicer/rapportkontekst, men året fra visualets akse. For hvert år beregnes:

```text
prosentavvik = (regnskap hittil valgt måned - budsjett hittil valgt måned) / budsjett hittil valgt måned
```

Regnskap hentes fra `fak_okonomi[periode]` januar til valgt måned for året på aksen, men vises først når publiseringsdatoen den 10. i påfølgende måned er passert. Regnskapslinjene filtreres med `fak_okonomi[sist_oppdatert]` til samme publiseringsdato. Budsjett hentes fra gjeldende BEVAAR-budsjett med `transaksjon_dato` til og med den 20. i påfølgende måned for året på aksen.

### Trendgraf for månedlig hittil-avvik

Økonomistatus kan også vise hvordan prosentavviket mot budsjett utvikler seg måned for måned i valgt år. Dette er et annet spørsmål enn grafen over år: her er året fast fra år-sliceren, mens måneden kommer fra grafens akse.

Anbefalt oppsett:

| Rolle i visual | Felt |
| --- | --- |
| X-akse | `graf_maaned[maaned_nummer]`, frikoblet månedstabell. |
| Verdi | `Prosentavvik mot budsjett hittil måned i visual` |
| Filter | Bruk `Vis måned i graf = 1` som visualfilter dersom grafen skal vise to måneder ekstra med luft etter valgt måned. |
| Resultatområde | Eksplisitt resultatområde-measure for inntekter, kostnader eller nettobidrag. |

For hver måned på aksen beregnes:

```text
prosentavvik = (regnskap hittil måned i visual - budsjett hittil måned i visual) / budsjett hittil måned i visual
```

Regnskap bruker publiseringsregelen den 10. i påfølgende måned. For mars i valgt år betyr det at regnskap først vises fra 10. april, og regnskapslinjer avgrenses med `fak_okonomi[sist_oppdatert]` til samme publiseringsdato. Budsjett bruker fortsatt `fak_okonomi[transaksjon_dato]` til og med den 20. i påfølgende måned. Periodene januar til valgt måned inngår i hittil-beløpet, og verdimålet returnerer blank for måneder etter valgt måned.

`Valgt Mnd + 2` og `Vis måned i graf` brukes for å styre hvor langt X-aksen vises:

```text
Valgt Mnd + 2 = MIN(12, valgt måned + 2)
```

Dette gir to måneder ekstra etter valgt måned for å skape luft i grafen. Hvis valgt måned er november, stopper aksen på desember og viser dermed én ekstra måned. Hvis valgt måned er desember, vises ikke ekstra måneder. De ekstra månedene har ingen verdi i `Prosentavvik mot budsjett hittil måned i visual`; de brukes bare som tom akseplass.

### Økonomiutvikling as-of

Siden `Økonomiutvikling as-of` viser hvordan regnskap og budsjettgrunnlag utvikler seg gjennom året når hvert månedssnitt leses med en fast as-of-regel. Formålet er å se hele utviklingsbildet for ett eller flere valgte år, ikke bare valgt måned.

Alle mål for siden ligger i `Measures\08 Økonomiutvikling`. Regnskapslinjen følger felles `Regnskap publiseringsdag = 10`, mens budsjettlinjene bruker den lokale parameteren `Økonomiutvikling as-of dager = 20`.

Årfilteret på siden bruker `slicer_aar[aar]`. Denne tabellen henter år direkte fra `fak_okonomi[periode]`, slik at årflisen bare viser år som faktisk finnes i økonomifakta. `fak_okonomi` er i Power Query filtrert til perioder fra `CurrentYear - 6` til `CurrentYear + 6`, uttrykt som `YYYYMM`, der måned må ligge mellom `01` og `12`.

Frikoblede tabeller:

| Tabell | Bruk |
| --- | --- |
| `okonomiutvikling_maaned` | X-akse med måned 1-12, kortnavn og sortering. |
| `okonomiutvikling_linje` | Linjevalg: `Regnskap`, `Rektorgodkjent` og 12 gjeldende budsjett-snapshots (`Jan`-`Des`). Sorteringen skal vise `Regnskap` og `Rektorgodkjent` først i legend. |

Hovedgrafen bruker:

| Rolle i visual | Felt |
| --- | --- |
| X-akse | `okonomiutvikling_maaned[maaned_kortnavn]` |
| Legend | `okonomiutvikling_linje[linje_navn]` |
| Verdi | `Økonomiutvikling verdi` |
| Small multiples | `slicer_aar[aar]` |
| Årvalg | Flervalgs-slicer/flis på `slicer_aar[aar]`. |

Linjelogikken er:

| Linje | Regel |
| --- | --- |
| `Regnskap` | Kumulert regnskap januar til måned på X-aksen. Måneden vises først fra `DATE(år, måned + 1, [Regnskap publiseringsdag])`, og regnskapslinjer filtreres med `sist_oppdatert` til samme dato. |
| `Rektorgodkjent` | Kumulert `BEVAAR<år>_M1 + BOAVUR<år>_M1` januar til måned på X-aksen, med BEV avgrenset til prosjekttype A1/A2/I1/I2/I3 og BOA til prosjekttyper som starter med Z. |
| `Jan`-`Des` | Kumulert gjeldende `BEVAAR<år>` januar til måned på X-aksen, men budsjett-snapshot leses med cutoff fra linjens snapshotmåned. |

Kortene på siden bruker område-spesifikke avviksmål:

| Kort | Mål | Fast resultatområde |
| --- | --- | --- |
| Inntekter | `Økonomiutvikling prosentavvik snitt - Inntekter`, `min`, `maks` | Ligger i DAX-målene. |
| Kostnader | `Økonomiutvikling prosentavvik snitt - Kostnader`, `min`, `maks` | Ligger i DAX-målene. |
| Nettobidrag | `Økonomiutvikling prosentavvik snitt - Nettobidrag`, `min`, `maks` | Ligger i DAX-målene, inkludert BEV-prosjekttyper der det er en del av definisjonen. |
| Total | `Økonomiutvikling prosentavvik snitt`, `min`, `maks` | Ingen fast resultatområde- eller nettobidragfilter. |

Hovedgrafen skal ikke ha `kontorelasjon4`-filter. Den skal vise totalbildet for valgt rapportkontekst, mens kortene gir egne deskriptive avviksstatistikker per resultatområde.

Siden har også en egen graf for utvikling i årsresultatet. Grafen bruker samme månedlige as-of-regel, men viser fullårsresultatet slik det ser ut i budsjettet ved hvert månedssnitt. Gjeldende budsjett (`BEVAAR<år>` + `BOAVUR<år>`) vises som utviklingslinje gjennom året. Rektorgodkjent budsjett (`BEVAAR<år>_M1` + `BOAVUR<år>_M1`) vises som rett referanselinje. Fullårsregnskap vises også som rett referanselinje, men bare for historiske år; inneværende år har ikke fullårsregnskap som fasit.

Hovedgrafen bruker rapportside-tooltipen `Tooltip - budsjettperiode`. Når brukeren peker på en periode, holdes perioden fast, mens tooltip-grafen itererer `tooltip_snapshot_maaned` fra januar til desember og viser budsjettet for den valgte perioden slik det var ved hvert månedssnitt. For historiske år viser tooltipen også endelig avvik mot regnskap som `Regnskap - Budsjett` for perioden.

Tooltip-bindingen er teknisk avhengig av at kildegrafen har `Tooltips`-rolle med `okonomiutvikling_maaned[maaned_nummer]` og `slicer_aar[aar]`, og at tooltip-siden har `pageBinding.parameters` for de samme feltene. Uten denne bindingen kan tooltip-siden være definert i PBIR uten at den vises når brukeren holder musepekeren over grafen.

### Prognoseutvikling as-of

Siden `Prognoseutvikling` viser hvordan årsprognosen endres gjennom året når hvert månedssnitt leses med en fast as-of-regel. Siden er ett-årsbasert og årflisen skal være single-select. Prognosemålene bruker `[Valgt År]` som fallback dersom visualet mangler eksplisitt årkontekst, slik at grafene ikke blanker ved lasting. Alle mål for siden ligger i `Measures\09 Prognoseutvikling`. Regnskapsdelen følger felles `Regnskap publiseringsdag = 10`, mens budsjettdelen bruker den lokale parameteren `Prognoseutvikling as-of dager = 20`.

Prognosebanene bygger på samme styringsregel som årsprognosen ellers i modellen:

```text
prognose per as-of måned = regnskap hittil as-of måned + gjeldende BEVAAR-budsjett for resterende perioder
```

Dette beskriver dagens BEVAAR-baserte prognoseregel. Hvis prognoseutvikling skal følge totalbudsjettdefinisjonen fullt ut, må det avklares om BOAVUR også skal inngå i resterende budsjett og i tooltipenes endelige avvik.

Hovedgrafen bruker `okonomiutvikling_maaned` som x-akse og `prognoseutvikling_linje` som legend. `Regnskap` vises med UiT-gul og er en hard faktisk linje for perioder der publiseringsdatoen den 10. i påfølgende måned er passert. Linjene `Jan`-`Des` er prognosebaner der hver linje starter i regnskapsverdien for sin publiserte as-of-måned og fortsetter med gjeldende budsjett for resten av året. Fargene blir gradvis lysere for senere snapshot-måneder for å gjøre tidsrekkefølgen lesbar uten et eget gradientvisual.

Hovedgrafen bruker rapportside-tooltipen `Tooltip - prognoseperiode`. Når brukeren peker på en periode, holdes perioden fast, mens tooltip-grafen itererer `tooltip_snapshot_maaned` fra januar til desember og viser prognoseverdien for den valgte perioden ved hvert månedssnitt. Før perioden er publisert brukes budsjett as-of snapshot; etter publisering brukes regnskap for perioden. For historiske år viser tooltipen også endelig avvik mot regnskap som `Regnskap - Budsjett` for perioden. Den nederste grafen viser utviklingen i årsresultatet for as-of-prognosene, altså total årsprognose beregnet på nytt for hvert månedssnitt.

Tooltip-bindingen er teknisk avhengig av at kildegrafen har `Tooltips`-rolle med `okonomiutvikling_maaned[maaned_nummer]` og `slicer_aar[aar]`, og at tooltip-siden har `pageBinding.parameters` for de samme feltene. Mini-linjen i tooltipen bruker `tooltip_snapshot_maaned[snapshot_kortnavn]` på aksen.

Synlige beløps- og avviksmål i rapporten skal formateres med tusenskille og uten desimaler. Prosentmål skal vises uten desimaler.

I TMDL skal synlige beløpsmål bruke `formatString: #,0`. Prosentmål skal bruke `formatString: 0\ %;-0\ %;0\ %`. I norsk Power BI-locale vises tusenskille som mellomrom.

### Prognoselag

Årsprognosen i lokal økonomirapport bygger på en enkel styringsregel:

```text
årsprognose = regnskap hittil valgt måned + gjeldende budsjett for resterende år
```

Prognoselaget skal derfor ikke bruke et eget prognosefelt i kilden. Det bruker samme grunnmål og samme ekskluderte konti som øvrig driftsoppfølging:

| Mål | Regel |
| --- | --- |
| `Budsjett resterende år` | `Budsjett grunnlag` filtrert til gjeldende BEVAAR-budsjett, periodene etter valgt måned til desember og `transaksjon_dato <= DATE(valgt år, valgt måned + 1, 20)`. |
| `Årsprognose` | `Regnskap hittil valgt måned + Budsjett resterende år`. |
| `Avvik årsprognose mot gjeldende årsbudsjett` | `Årsprognose - Årsbudsjett - Gjeldende`. |
| `Årsprognose / gjeldende årsbudsjett` | `Årsprognose / Årsbudsjett - Gjeldende`. |
| `Prosentavvik årsprognose mot gjeldende årsbudsjett` | Prognoseavvik dividert på gjeldende årsbudsjett. |

Når valgt måned er desember, er resterende budsjett `0`, og årsprognosen blir lik regnskap hittil desember med 10. januar som publiseringscutoff.

Denne delen beskriver dagens BEVAAR-prognose. Utvidelse til BOAVUR/totalbudsjett må avklares før prognosemålene kan dokumenteres som full rektorgodkjent eller gjeldende totalbudsjett.

## Budsjettversjon og transaksjonstype

Budsjettanalyse skal alltid angi hvilken budsjettbasis som brukes. UiT-modellen må skille mellom budsjettversjon, beløpsfelt og transaksjonstype.

`transaksjonstype` kan brukes til å lese budsjettet slik det er tilgjengelig i saldotabeller i Unit4 nå. `dim_budsjettversjon` gir i tillegg et nomenklatur som kan brukes til å tolke budsjettversjoner, skille årlig budsjett fra langtidsbudsjett/prosjektbudsjett og forstå milepæler, kopier og rulleringer.

### Budsjettfelt i `fak_okonomi`

| Felt | Bruk |
| --- | --- |
| `belop_budsjett` | Generelt budsjettbeløp. Brukes av teknisk råmål `Budsjett rå`; styringsmål skal alltid legge på eksplisitt budsjettversjon. |
| `belop_budsjett_opprinnelig` | Opprinnelig/godkjent budsjettfelt i kilden. Skal ikke blandes inn i generiske budsjettmål uten avklart formål. |
| `belop_budsjett_revidert` | Revidert/gjeldende budsjettfelt i kilden. Skal ikke erstatte eksplisitt versjonsfilter uten avklart formål. |
| `transaksjonstype_budsjett` | Kode for budsjettbasis/prognosemilepæl. Skal brukes eksplisitt i tertial- og prognoselogikk. |
| `zk_dim_budsjettversjon` | Kobling til `dim_budsjettversjon`. |
| `zk_dim_budsjettprofil` | Kobling til budsjettprofil/periodiseringslogikk. |

I lokal `Økonomi_rapport.pbip` er praktisk DAX-regel at budsjettbeløp hentes fra `belop_budsjett`, men bare etter at målet har valgt budsjettversjon. En ren `SUM(fak_okonomi[belop_budsjett])` gir ikke styringsmessig mening fordi flere budsjettversjoner kan ligge i samme faktagrunnlag.

Implementerte budsjettversjonsregler i lokal rapport:

| Målgruppe | Versjonsregel |
| --- | --- |
| Gjeldende årsbudsjett | `dim_budsjettversjon[versjon_kode] = "BEVAAR" & valgt år`, for eksempel `BEVAAR2026`. |
| Rektorgodkjent totalbudsjett | `BEVAAR<år>_M1` for BEV og `BOAVUR<år>_M1` for BOA, for eksempel `BEVAAR2026_M1 + BOAVUR2026_M1`. |
| Hittil valgt måned | Gjeldende BEVAAR-budsjett kombinert med `fak_okonomi[periode]` fra januar til valgt måned. |
| Budsjett as-of | Gjeldende BEVAAR-budsjett filtreres med `fak_okonomi[transaksjon_dato] <= DATE(valgt år, valgt måned + 1, 20)`. |
| År i visual/graf | Versjonskode bygges fra året på aksen, for eksempel `BEVAAR2024`. |

### Budsjettversjonsdimensjonen

`dim_budsjettversjon` bør tolkes som en styringsdimensjon, ikke bare som teknisk metadata.

| Felt | Bruk |
| --- | --- |
| `versjon_kode` | Stabil kode for budsjettversjonen, for eksempel `BEVAAR2026`, `BEVAAR2026_M1`, `BOAPRO` eller `BOAVUR2026_M1`. |
| `versjon_navn` | Lesbart navn som forklarer om versjonen er gjeldende budsjett, milepæl, kopi, rullering eller budsjettarbeid. |
| `status` | Status i Unit4. I observerte data er mange relevante versjoner satt til `N`; status må derfor ikke alene brukes som styringsfilter. |
| `tidsramme` | Budsjettområde/periode, for eksempel årstall, `LTB`, `BOAPRO`, `BOAVURLT`, `EVUPRO` eller `BOAKOP`. |
| `transaksjonstype` | Primær klassifisering for saldotabell-/styringsbasis: `DA`, `DB`, `DC` eller blank/ukjent. |

Anbefalt tolkningsrekkefølge:

1. Bruk eksplisitt `transaksjonstype` når den finnes.
2. Bruk `versjon_kode` som fallback når `transaksjonstype` er blank, særlig for eldre milepæler, kopier og rulleringsversjoner.
3. Bruk `tidsramme` til å skille årlig BEV-budsjett, langtidsbudsjett, BOA-prosjektbudsjett, BOA-vurdering, EVU og rammebudsjett.
4. Ikke bland budsjettversjoner med ulik `tidsramme` i samme KPI uten eksplisitt filter.

### Transaksjonstyper

| Transaksjonstype | Betydning | Styringsbruk |
| --- | --- | --- |
| `DA` | Gjeldende budsjett | Skal brukes når rapporten skal vise budsjettet slik det ligger som gjeldende operativt budsjett i saldotabellene. Typiske versjoner er `BEVAAR2026`, `BEVLTB`, `BOAPRO` og `BOAVUR`. |
| `DB` | Godkjent budsjett | Skal brukes når rapporten skal sammenligne mot godkjent budsjett/milepæl. Typiske 2026-eksempler er `BEVAAR2026_M1`, `BEVLTB2026_M1`, `BOAPRO2026_M1` og `BOAVUR2026_M1`. |
| `DC` | Siste milepæl | Skal brukes som tertial/prognose-basis: godkjent budsjett frem til tertial 1, tertial 1 frem til tertial 2, og deretter siste godkjente milepæl. Eksempel i observerte data er `BEVLTB2025_M2`. |

### Nomenklatur for budsjettversjoner

Observerte budsjettversjoner følger mønstre som kan brukes i datamodellering og kontrollregler:

| Mønster | Betydning | Eksempler |
| --- | --- | --- |
| `BEVAAR<år>` | Gjeldende årlig bevilgningsbudsjett. | `BEVAAR2026` med `transaksjonstype = DA`. |
| `BEVAAR<år>_M<n>` | Milepælversjon for årlig bevilgningsbudsjett. | `BEVAAR2026_M1` med `transaksjonstype = DB`. |
| `BEVAAR<år>_BA*` | Budsjettarbeid eller milepæl knyttet til årsbudsjett. | `BEVAAR2024_BA1`, `BEVAAR2023_BA`. |
| `BEVLTB` | Gjeldende langtidsbudsjett. | `BEVLTB` med `transaksjonstype = DA`. |
| `BEVLTB<år>_M<n>` | Milepælversjon for langtidsbudsjett. | `BEVLTB2026_M1` med `transaksjonstype = DB`; `BEVLTB2025_M2` med `transaksjonstype = DC`. |
| `*_RULL` | Kopi/førbilde før rullering. | `BEVLTB2025_RULL`, `BOAVUR2026_RULL`. |
| `*_SK*`, `*_BACKUP`, `*KOP` | Sikkerhetskopi eller snapshot. | `BEVLTB2022_SK`, `BEVAAR2023BACKUP`, `BOAKOP`, `EVUKOP`. |
| `BOAPRO` | Prosjektbudsjett for sikre/etablerte BOA-prosjekter. | `BOAPRO` med `transaksjonstype = DA`. |
| `BOAPRO<år>_M<n>` | Milepælversjon for sikre/etablerte BOA-prosjekter. | `BOAPRO2026_M1` med `transaksjonstype = DB`. |
| `BOAVUR` | BOA-vurdering med manuelle endringer basert på forventninger til fremtidig utvikling. | `BOAVUR` med `transaksjonstype = DA`. |
| `BOAVUR<år>_M<n>` | Milepælversjon for BOA-vurdering med manuelle forventningsjusteringer. | `BOAVUR2026_M1` med `transaksjonstype = DB`. |
| `EVUPRO`, `EVUVUR` | EVU-budsjett og EVU-vurdering. | `EVUPRO`, `EVUVUR`. |
| `RAMME<år>` | Rammebudsjett. | `RAMME2022`, `RAMME2022_M1`. |
| `Ukjent` | Manglende eller ukjent klassifisering. | Skal håndteres eksplisitt som datakvalitets-/mappingavvik. |

Dette gir en praktisk regel: `transaksjonstype` er beste styringsfilter når den er satt, mens `versjon_kode` og `tidsramme` forklarer hva budsjettversjonen faktisk representerer og kan brukes som fallback/mappinggrunnlag.

### Dynamisk bruk av nomenklaturet

Nomenklaturet bør modelleres som avledede attributter i budsjettversjonsdimensjonen eller i en egen mappingtabell. Da kan rapportene velge riktig budsjettversjon dynamisk basert på år, rapporteringsperiode, budsjettområde og ønsket sammenligningsgrunnlag.

Anbefalte avledede felt:

| Avledet felt | Regel | Eksempel |
| --- | --- | --- |
| `budsjettomrade` | Avledes fra prefiks i `versjon_kode` og/eller `tidsramme`. | `BEVAAR`, `BEVLTB`, `BOAPRO`, `BOAVUR`, `EVU`, `RAMME`. |
| `budsjettar` | Første fire-sifrede år i `versjon_kode`, eventuelt `tidsramme` når den er numerisk. | `BEVAAR2026_M1` gir `2026`; `BEVLTB` har ikke år i kode og må tolkes som gjeldende LTB. |
| `milepaelnummer` | Tallet etter `_M` når koden følger `*_M<n>`. | `BOAPRO2026_M1` gir `1`; `BEVAAR2024_M4` gir `4`. |
| `versjonsrolle` | Avledes først fra `transaksjonstype`, deretter fra mønster i `versjon_kode`. | `DA = gjeldende`, `DB = godkjent`, `DC = siste_milepael`, `_RULL = for_rullering`, `*KOP = kopi`. |
| `er_kopi` | Sann hvis koden/navnet indikerer kopi, snapshot, sikkerhetskopi eller backup. | `BOAKOP`, `EVUKOP`, `BEVAAR2023BACKUP`, `*_SK*`. |
| `er_rullering` | Sann hvis koden ender på eller inneholder `_RULL`. | `BEVLTB2025_RULL`, `BOAVUR2026_RULL`. |
| `er_budsjettarbeid` | Sann hvis koden inneholder `_BA` eller navn beskriver budsjettarbeid. | `BEVAAR2024_BA1`, `BEVLTB2025_BA1`. |
| `er_test` | Sann hvis koden/navnet indikerer test. | `BOAVUR-TEST`. |
| `kan_brukes_i_styring` | Sann for operative styringsversjoner; usann for kopi/test/rullering med mindre rapporten eksplisitt er revisjonsspor/historikk. | `BEVAAR2026`, `BEVAAR2026_M1`, `BOAPRO2026_M1` er styringsrelevante; `BOAPRO_R26` er normalt historikk. |

Anbefalt dynamisk prioritering:

1. Filtrer først på `budsjettomrade`, for eksempel `BEVAAR` for årlig bevilgningsbudsjett, `BEVLTB` for langtidsbudsjett, `BOAPRO` for BOA-prosjektbudsjett eller `BOAVUR` for BOA-vurdering.
2. Filtrer på `budsjettar` når området er årsbundet. For gjeldende langtidsbudsjett uten år i koden brukes `tidsramme = "LTB"` og `transaksjonstype = "DA"`.
3. Filtrer på ønsket budsjettbasis:
   - `DA` for gjeldende budsjett.
   - `DB` for godkjent budsjett.
   - `DC` for siste milepæl.
4. Ekskluder kopier, testversjoner, rulleringsførbilder og sikkerhetskopier fra ordinære styringsrapporter.
5. Dersom `transaksjonstype` mangler, bruk eksplisitt mapping fra `versjon_kode`; ikke la blank automatisk bety "ikke relevant".
6. Dersom flere versjoner fortsatt matcher, velg høyest `milepaelnummer` for siste milepæl, eller den versjonen økonomifunksjonen har markert som styringsversjon.

Praktiske rapportvalg:

| Rapportvalg | Dynamisk filter |
| --- | --- |
| Gjeldende årsbudsjett BEV for valgt år | `budsjettomrade = "BEVAAR"`, `budsjettar = valgt år`, `transaksjonstype = "DA"`. |
| Godkjent årsbudsjett BEV for valgt år | `budsjettomrade = "BEVAAR"`, `budsjettar = valgt år`, `transaksjonstype = "DB"`; fallback til godkjent `_M1` dersom eldre år mangler transaksjonstype. |
| Siste milepæl BEV for valgt tertial | Bruk `transaksjonstype = "DC"` der den finnes; ellers velg milepæl etter tertialregel og eksplisitt mapping. |
| Gjeldende langtidsbudsjett | `budsjettomrade = "BEVLTB"`, `tidsramme = "LTB"`, `transaksjonstype = "DA"`. |
| Godkjent langtidsbudsjett | `budsjettomrade = "BEVLTB"`, `transaksjonstype = "DB"` eller godkjent LTB-milepæl for valgt planår. |
| BOA prosjektbudsjett gjeldende | `budsjettomrade = "BOAPRO"`, `transaksjonstype = "DA"`. Brukes for sikre/etablerte BOA-prosjekter. |
| BOA prosjektbudsjett godkjent | `budsjettomrade = "BOAPRO"`, `transaksjonstype = "DB"` eller riktig `BOAPRO<år>_M<n>` etter mapping. Brukes som godkjent basis for sikre/etablerte prosjekter. |
| BOA-vurdering gjeldende | `budsjettomrade = "BOAVUR"`, `transaksjonstype = "DA"`. Brukes når porteføljen skal justeres manuelt etter forventet fremtidig utvikling. |
| BOA-vurdering godkjent | `budsjettomrade = "BOAVUR"`, `transaksjonstype = "DB"` eller riktig `BOAVUR<år>_M<n>` etter mapping. Brukes som godkjent milepæl for vurdert BOA-portefølje. |

Tertialregelen for siste milepæl bør defineres eksplisitt:

| Rapporteringsfase | Anbefalt basis for `DC`/siste milepæl |
| --- | --- |
| Før tertial 1 er godkjent | Godkjent budsjett (`DB`). |
| Etter tertial 1 og før tertial 2 | Tertial 1-milepæl, typisk `_M1`. |
| Etter tertial 2 og før tertial 3/årsavslutning | Tertial 2-milepæl, typisk `_M2`. |
| Etter tertial 3/årsavslutning | Siste godkjente milepæl for året, typisk `_M3` eller høyeste godkjente milepæl i området. |

For at dette skal være robust bør mappingen ikke hardkodes direkte i mange DAX-mål. Lag heller en felles budsjettversjonsmapping med feltene over, og la DAX/SQL filtrere på `budsjettomrade`, `budsjettar`, `versjonsrolle`, `milepaelnummer` og `kan_brukes_i_styring`.

Eksempel på konseptuell filterlogikk:

```text
VelgBudsjettversjon(
  omrade = "BEVAAR",
  ar = valgt_ar,
  basis = "gjeldende" | "godkjent" | "siste_milepael",
  rapporteringsperiode = valgt_periode
)

1. finn versjoner i valgt omrade og ar/tidsramme
2. fjern kopi/test/rullering hvis rapporttypen er styring
3. velg transaksjonstype DA, DB eller DC når den finnes
4. hvis DC mangler, velg milepael etter tertialregel
5. hvis transaksjonstype mangler historisk, bruk godkjent mapping fra versjon_kode
6. returner én versjon eller marker avvik dersom flere/ingen matcher
```

Konsekvens for KPI:

- `Avvik mot budsjett` er ufullstendig uten budsjettbasis (`DA`, `DB` eller `DC`).
- `Prognoseavvik` bør normalt sammenligne prognose/siste estimat mot `DC` eller gjeldende budsjett, avhengig av styringsspørsmålet.
- `Budsjettlojalitet` bør måles mot `DB` dersom spørsmålet er om enheten holder styregodkjent ramme.
- `Driftsstyring hittil` bør måles mot `DA` dersom spørsmålet er om enheten styrer etter gjeldende revidert ramme.
- `Tertialoppfølging` bør vise både `DB`, `DA` og `DC` når målgruppen trenger å skille opprinnelig plan, revidert plan og siste milepæl.
- Versjoner med blank `transaksjonstype` skal ikke automatisk utelates. De bør klassifiseres med eksplisitt mapping dersom de er relevante for historiske sammenligninger eller revisjonsspor.

Anbefalt navnestandard:

| KPI-navn | Definisjon |
| --- | --- |
| `Avvik mot godkjent budsjett` | Regnskap minus budsjett med `transaksjonstype_budsjett = "DB"` eller `belop_budsjett_opprinnelig`. |
| `Avvik mot gjeldende budsjett` | Regnskap minus budsjett med `transaksjonstype_budsjett = "DA"` eller `belop_budsjett_revidert`. |
| `Avvik mot siste milepæl` | Regnskap/prognose minus budsjettbasis med `transaksjonstype_budsjett = "DC"`. |
| `Prognose mot godkjent budsjett` | Prognose minus `DB`. |
| `Prognose mot gjeldende budsjett` | Prognose minus `DA`. |
| `Prognose mot siste milepæl` | Prognose minus `DC`. |

## Bevilgningsprosessen (BEV)

### Fra KD-bevilgning til internfordeling

Bevilgningsøkonomien er UiTs basisfinansierte virksomhet. Prosessen kan beskrives slik:

1. KD tildeler årlig ramme og føringer til UiT.
2. UiT vurderer konsekvensene for basisdrift, strategiske satsinger, avsetninger, lønns- og prisvekst, studieplasser, særskilte tildelinger, investeringer og risiko.
3. Universitetsstyret vedtar budsjett og intern fordeling.
4. Rektor konkretiserer rammene i disponeringsskriv til enhetene.
5. Fakulteter/enheter lager årsplan og budsjett innenfor tildelt ramme.
6. Regnskap, budsjett og prognose følges opp tertialvis og i årsrapport.

BEV-logikken skal svare på:

- Holder enheten rammen?
- Hvilke deler av basisdriften har varig strukturell ubalanse?
- Hvilke avvik skyldes timing/periodisering, og hvilke skyldes reell over- eller underaktivitet?
- Brukes avsetninger i tråd med plan?
- Er ressursbruken koblet til strategi, kvalitet, studieportefølje, forskning og samfunnsoppdrag?

### BEV i tertialmodell

Den lokale tertialmodellen skiller BEV og BOA gjennom feltet `Prosjekt[BEV/BOA]`. BEV-målene filtrerer på `BEV`, for eksempel:

- `BEV_årsbudsjett`
- `BEV_budsjett_hittil`
- `BEV_regnskap_hittil`
- `BEV_prognose`

Denne logikken bør være konsistent med økonomimodellen i Power BI og med definisjonene i styringsdokumentet.

## BOA-prosessen

BOA er eksternfinansiert aktivitet der UiT mottar bidrag eller oppdrag fra eksterne finansieringskilder. BOA skal bidra til faglig utvikling, ekstern relevans, forsknings- og utdanningskvalitet og strategiske mål. Samtidig må BOA styres slik at den ikke skaper skjulte kostnader eller svekker basisøkonomien.

I budsjett- og prognoselogikken må BOA deles i minst to budsjettområder:

| Budsjettområde | Betydning | Bruk |
| --- | --- | --- |
| `BOAPRO` | Sikre/etablerte BOA-prosjekter med prosjektbudsjett. | Brukes som prosjektbudsjettgrunnlag for aktivitet som er etablert og skal styres som del av BOA-porteføljen. |
| `BOAVUR` | BOA-vurdering med manuelle endringer ut fra forventninger til fremtidig utvikling. | Brukes til porteføljevurdering/prognose der forventede nye, endrede eller bortfallende aktiviteter må justeres manuelt utover sikre prosjekter. |

Konsekvensen er at `BOAPRO` og `BOAVUR` ikke bør blandes uten tydelig formål. `BOAPRO` beskriver det sikre prosjektgrunnlaget, mens `BOAVUR` beskriver en vurdert fremtidig portefølje. Avvik, prognose og nettobidrag må derfor merkes med om de er basert på etablert prosjektbudsjett eller vurdert BOA-portefølje.

### Hovedprosess

| Fase | Økonomisk styringspunkt |
| --- | --- |
| Ide og utlysning | Strategisk relevans, kapasitet, finansieringskilde, krav til egenandel og indirekte kostnader. |
| Søknad og budsjett | Fullkost, lønn, overhead/indirekte kostnader, egenfinansiering, investeringer, risiko og kontantstrøm. |
| Kontrakt | Avtalevilkår, rapporteringskrav, betalingsplan, revisjonskrav, resultatansvar og prosjektstruktur. |
| Prosjektopprettelse | Prosjekt/delprosjekt, finansieringskilde, aktivitetstype, budsjettprofil, ansvar, datoer og roller. |
| Gjennomføring | Timer, lønn, innkjøp, inntektsføring, indirekte kostnader, egenfinansiering og fremdrift. |
| Tertial/prognose | Avvik mot budsjett, forventet sluttresultat, risiko, kostnadsdekning og leveranser. |
| Avslutning | Sluttrapport, sluttregnskap, restmidler, avsetninger, inntektsføring og læring. |

### BOA som økonomisk logikk

BOA bør analyseres på minst fire nivåer:

| Nivå | Spørsmål |
| --- | --- |
| Portefølje | Øker UiT eksternfinansiert aktivitet på strategisk riktige områder? |
| Fakultet/enhet | Har enheten kapasitet, kompetanse og økonomisk bærekraft i BOA-porteføljen? |
| Prosjekt | Har prosjektet finansiering, fremdrift og kostnadskontroll? |
| Delprosjekt/arbeidspakke | Er kostnader, inntekter, egenfinansiering og indirekte kostnader riktig ført? |

### Egenfinansiering og indirekte kostnader

BOA krever særlig kontroll på:

- `egenfinansiering_prosent` og faktiske egenandeler
- konti merket for `boa_egenfinansiering`
- konti merket for `boa_indirekte_kostnader`
- om lønn, frikjøp og indirekte kostnader dekkes av ekstern finansiering eller basis
- om egenfinansiering er planlagt, godkjent og synlig i enhetens ramme
- om prosjektet gir positivt, nøytralt eller negativt nettobidrag

Egenfinansiering er ikke nødvendigvis negativt. Den kan være strategisk riktig hvis den bygger kapasitet, kvalitet, nettverk, rekruttering eller samfunnsoppdrag. Den må likevel være eksplisitt besluttet og synlig i styringsinformasjonen.

## Nettobidrag

Nettobidrag er et sentralt brobegrep mellom regnskap, BOA og strategisk ressursstyring.

I økonomimodellen bør nettobidrag defineres som:

```text
Nettobidrag = relevante inntekter + relevante kostnader innen resultatkonti 3-7
```

Konto `2160`, `2161`, `2170` og `2171` skal ikke brukes som nettobidragskonti. De er balansekontoer for avsetninger og skal behandles i avsetningsanalyse eller balanseoppfølging. Nettobidrag skal derfor beregnes fra relevante resultatkonti, ikke fra disse avsetningskontoene.

Den praktiske fortolkningen avhenger av fortegn:

- Dersom inntekter er negative og kostnader positive, må nettobidrag eventuelt normaliseres for ledelsesrapportering.
- Dersom rapporten viser regnskap/budsjett-forhold, må "bra/dårlig" vurderes ulikt for inntekter og kostnader.
- For BOA må nettobidrag alltid sees sammen med ekstern finansieringsandel, egenfinansiering, indirekte kostnader og prosjektets livsløp.

Anbefalte styringsspørsmål:

- Hva er nettobidrag per fakultet/enhet?
- Hva er nettobidrag per finansieringskilde og prosjekttype?
- Hvor mye basisfinansiering bindes opp i BOA?
- Dekker prosjektene sine indirekte kostnader?
- Er negativt nettobidrag strategisk besluttet eller utilsiktet?
- Hvilke prosjekter har høy risiko for sluttavvik?

## UiTs avtaler med KD

Begrepet "avtaler med KD" bør forstås som en kombinasjon av formelle styringsdokumenter og styringsdialog:

| Dokument/prosess | Økonomisk betydning |
| --- | --- |
| Tildelingsbrev | Tildelt ramme, føringer, rapporteringskrav, særskilte midler og fullmakter. |
| Utviklingsavtale | UiTs strategiske mål og styringsparametere i dialogen med KD. |
| Etatsstyring | Oppfølging av mål, økonomi, risiko og tiltak. |
| Årsrapport | UiTs rapportering på resultater, ressursbruk, måloppnåelse og regnskap. |
| Satsingsforslag | UiTs innspill om nye tiltak utenfor eksisterende rammer. |

For 2023-2026 er utviklingsavtalen bygget rundt tre mål:

1. Internasjonalt fremragende på kunnskap og kompetanse om og for Arktis og nordområdene.
2. Nyskapende, demokratiske og bærekraftige løsninger på store samfunnsutfordringer.
3. Utvikle studenter og ansattes kompetanse og talent, med mangfold som drivkraft og ressurs.

Økonomimodellen bør derfor kunne koble økonomisk ressursbruk og resultater til disse målene, ikke bare til konti og koststeder.

## UiTs avtaler med fakultetene og enhetene

Internt er "avtalen" mellom UiT sentralt og fakultetene/enhetene først og fremst en styringsrelasjon:

| Styringsledd | Innhold |
| --- | --- |
| Budsjettvedtak | Styrets fordeling av økonomiske rammer og overordnede prioriteringer. |
| Disponeringsskriv | Rektors formalisering av rammer, forventninger og oppgaver til enhetene. |
| Strategiske langtidsplaner | Enhetenes flerårige plan for å realisere strategien. |
| Årsplan og budsjett | Enhetenes operative prioriteringer og ressursdisponering. |
| Dialogmøter | Oppfølging av måloppnåelse, kvalitet, økonomi, risiko og tiltak. |
| Virksomhetsrapport/tertialrapport | Status på økonomi og sentrale styringsparametere. |

Fakultetene har resultatansvar i linjen. Det betyr at økonomirapporteringen bør gjøre det lett å skille:

- ramme gitt fra UiT sentralt
- lokal disponering
- varige bindinger, særlig lønn og areal
- midlertidige midler og prosjektmidler
- BOA-aktivitet og tilhørende egenfinansiering
- avsetninger og planlagt bruk av avsetninger
- risiko og tiltak

## Økonomi-OKR/KPI

OKR-er bør være få, styrbare og knyttet til reelle beslutninger. KPI-er bør ha definert eier, datakilde, frekvens, terskel og budsjettbasis.

### Objective 1: Styrke økonomisk bærekraft og handlingsrom

| Key result/KPI | Definisjon | Datagrunnlag |
| --- | --- | --- |
| Strukturell balanse per enhet | Varige inntekter minus varige kostnader, justert for midlertidige tiltak. | Regnskap, budsjett, prognose, årsplan. |
| Avvik mot gjeldende budsjett | Regnskap hittil minus `DA`. | `fak_okonomi`, `transaksjonstype_budsjett = "DA"`. |
| Avvik mot godkjent budsjett | Regnskap hittil minus `DB`. | `fak_okonomi`, `transaksjonstype_budsjett = "DB"`. |
| Prognose mot siste milepæl | Prognose minus `DC`. | Tertial/prognosemodell. |
| Andel frie midler | Midler uten varig binding delt på total bevilgningsramme. | Budsjett, lønn, avsetninger. |
| Planlagt bruk av avsetninger | Faktisk og prognostisert bruk mot vedtatt investerings-/avsetningsplan. | Avsetningsplan, regnskap, prognose. |

### Objective 2: Gjøre BOA-porteføljen faglig sterk og økonomisk bærekraftig

| Key result/KPI | Definisjon | Datagrunnlag |
| --- | --- | --- |
| BOA-volum | Regnskapsført BOA-inntekt/kostnad per periode, enhet og finansieringskilde. | Prosjekt, delprosjekt, hovedfinansiering. |
| Nettobidrag BOA | Nettobidrag på BOA-prosjekter, normalisert for fortegn. | Konto 3-7 for bredt nettobidrag, prosjekt/delprosjekt, BEV/BOA. Konto `2160`, `2161`, `2170` og `2171` er avsetningskonti og skal ikke brukes i nettobidragsberegningen. |
| Egenfinansieringsandel | Faktisk egenfinansiering delt på total prosjektkostnad. | `egenfinansiering_prosent`, konti for egenfinansiering. |
| Dekning indirekte kostnader | Faktisk dekkede indirekte kostnader mot budsjettert/forventet dekning. | BOA-konti, prosjektbudsjett. |
| Prosjekter med sluttavviksrisiko | Prosjekter der prognose avviker vesentlig fra budsjett/kontrakt. | Prognose, budsjett, regnskap. |
| Tilslags- og søknadsaktivitet | Antall søknader, tilslag og finansieringsvolum. | Forsknings-/prosjektadministrative data. |

### Objective 3: Øke kvaliteten på økonomistyring og datagrunnlag

| Key result/KPI | Definisjon | Datagrunnlag |
| --- | --- | --- |
| Andel prosjekter med komplett dimensjonering | Prosjekter/delprosjekter med gyldig koststed, finansieringskilde, ansvarlig, periode og status. | Dimensjonstabeller. |
| Budsjettlinjer med eksplisitt transaksjonstype | Andel budsjettlinjer med `DA`, `DB` eller `DC`. | `fak_okonomi`. |
| Avvik mellom prosjekt og delprosjekt | Rader der prosjektkobling ikke samsvarer med delprosjektets prosjektnummer. | `fak_okonomi`, `dim_delprosjekt`, `dim_prosjekt`. |
| Kildeoppdatering | Tid siden siste oppdatering av økonomidata. | Modellmetadata/kildetidspunkt. |
| Rapporterte kontrollavvik | Antall og alvorlighet på datakvalitets- og kontrollavvik. | Manifest, valideringsregler, internkontroll. |

## Strategi-OKR/KPI

Strategi-OKR bør koble UiTs strategi, utviklingsavtale og langtidsplaner til ressursbruk og resultater. Under er forslag til målstruktur.

### Objective A: Være en drivkraft for kunnskap og kompetanse i, om og for Arktis og nordområdene

| KPI | Økonomikobling |
| --- | --- |
| Ressursbruk på prioriterte arktiske/nordområder | Kostnader, investeringer og BOA-volum merket med strategisk satsing/fagområde. |
| Ekstern finansiering innen arktiske/nordområder | BOA-inntekter og tilslag på relevante prosjekter. |
| Fleksible utdanningstilbud i nord | Budsjett og kostnader knyttet til fleksible/desentraliserte tilbud. |
| Samisk og kvensk kompetanse | Ressursbruk, BOA, studieplasser og tiltak knyttet til samisk/kvensk språk, kultur og samfunn. |

### Objective B: Bidra til nyskapende, demokratiske og bærekraftige løsninger

| KPI | Økonomikobling |
| --- | --- |
| Ressursbruk på store samfunnsutfordringer | Kostnader/BOA knyttet til klima, helse, teknologi, samfunnssikkerhet, tillit og fellesskap. |
| Tverrfaglige satsinger | Budsjett, regnskap og BOA på tverrfaglige programmer/prosjekter. |
| Digital omstilling | Investeringer, driftskostnader og gevinster knyttet til digitalisering, data og AI. |
| Åpen vitenskap og forskningsinfrastruktur | Kostnader og investeringer på infrastruktur, data, publisering og tilgjengeliggjøring. |

### Objective C: Utvikle studenter og ansattes kompetanse og talent

| KPI | Økonomikobling |
| --- | --- |
| Kompetanse- og talentutvikling | Ressursbruk på karriereutvikling, lederutvikling, merittering og kompetansetiltak. |
| Rekruttering og gjennomføring | Kostnader og resultater knyttet til studentrekruttering, gjennomføring og livslang læring. |
| Arbeids-, lærings- og studiemiljø | Investeringer og driftskostnader på campus, areal, digitalt læringsmiljø og HMS. |
| Areal- og campusutnyttelse | Kostnad per areal, leiekostnader, utnyttelse og tiltak for bedre bruk av eksisterende areal. |

## Datakrav og internkontroll

For at økonomi- og strategi-KPI skal være styrbare, må hvert mål ha:

- definert eier
- datakilde
- oppdateringsfrekvens
- filterlogikk
- fortegnslogikk
- budsjettbasis (`DA`, `DB`, `DC`, opprinnelig eller revidert)
- organisasjonsnivå
- toleransegrenser
- forklaring på forventet handling ved avvik

Kontrollregler som bør ligge i modellen:

1. Regnskap og budsjett skal ikke blandes i samme mål uten eksplisitt kilde- eller beløpstypefilter.
2. Budsjett-KPI skal angi transaksjonstype/budsjettbasis.
3. `DB`, `DA` og `DC` skal ikke brukes om hverandre i trend uten tydelig merking.
4. Prosjekt og delprosjekt skal ha gyldig kobling.
5. Konto skal finnes i `dim_konto` og ha gyldig kontoklasse/resultat-balanse-flagg.
6. BOA-prosjekter skal ha finansieringskilde, ansvarlig, periode og status.
7. Egenfinansiering og indirekte kostnader skal være synlige i BOA-rapportering.
8. Person-/ressursfelt og fritekstfelt skal vurderes for personvern og tilgangsstyring.
9. Historisering/snapshot bør vurderes for finansieringskilde, aktivitetstype, konto- og organisasjonsrelasjoner når rapporter skal være reproduserbare.

## Dokumentasjonsgap avdekket

| Område | Hva mangler | Hvorfor det betyr noe | Foreslått avklaring |
| --- | --- | --- | --- |
| Budsjettversjonsmapping | Det finnes anbefalt nomenklatur for `DA`, `DB` og `DC`, men flere lokale DAX-mål bygger fortsatt versjonskoder direkte, for eksempel `BEVAAR<år>` og `BOAVUR<år>_M1`. | Hardkodede versjoner gjør det vanskeligere å endre styringsbasis når Unit4 eller budsjettprosessen endres. | Etabler en liten mappingtabell eller dokumentert regel for budsjettområde, år, transaksjonstype, milepæl og fallback. |
| BOA i prognose og minigrafer | Rektorgodkjent totalbudsjett er definert som `BEVAAR<år>_M1 + BOAVUR<år>_M1`, men enkelte utviklings- og prognosemål må verifiseres før dokumentasjonen kan si at alle viser totalbudsjett. | Brukeren kan ellers sammenligne regnskap mot BEV-only budsjett uten at det er synlig. | Avklar om `BOAVUR`/`BOAVUR_M1` skal inngå i alle as-of-, prognose- og tooltipmål, eller bare i rektorgodkjente referanser. |
| Tooltipenes endelige avvik | Tooltipene viser historisk `Regnskap - Budsjett`, men budsjettgrunnlaget bør navngis mer presist. | Fortegn og budsjettbasis må være entydig når tallet brukes til forklaring av historisk avvik. | Bestem om avviket skal måles mot gjeldende BEVAAR, rektorgodkjent totalbudsjett eller en annen totalbudsjettbasis. |
| Kontoekskludering | Ekskluderte konti er implementert i DAX, men eierskap, endringsprosess og kontroll mot kontoplan er ikke dokumentert detaljert. | Kontoendringer kan gi skjulte brudd i alle styringsmål. | Legg inn eier, endringslogg og test for konti som skal ekskluderes fra basisoppfølging. |
| Resultatområder og fortegn | Inntekter, kostnader, nettobidrag og total har mål, men terskler for bra/dårlig avvik er ikke ferdig forvaltningsdefinert. | Avviksfarger og KPI-vurderinger kan bli misvisende uten felles fortegnsregel. | Dokumenter standard fortegnslogikk og terskler per resultatområde. |
| Sikkerhet og personvern | Person-/ressursfelt, prosjektleder, eiersted og fritekstfelter er nevnt, men RLS/tilgangsmodell og personvernvurdering er ikke spesifisert. | Økonomirapporter kan inneholde person- eller prosjektinformasjon som ikke skal være bredt tilgjengelig. | Dokumenter rapportroller, tilgangsnivåer og hvilke felter som skal skjules eller aggregeres. |
| Datakvalitetskontroller | Kontrollregler er listet, men konkrete tester for manglende dimensjonskoblinger, duplikate budsjettversjoner og prosjekt-/delprosjektavvik mangler. | Feil i nøkler og mapping kan gi riktige summer på feil styringsdimensjon. | Lag konkrete DAX-, Power Query- eller kildebaserte tester med terskel og eier. |
| Power BI Desktop-validering | PBIP-/JSON-kontroller kan bekrefte definisjoner, men ikke at tooltip faktisk rendres riktig på hover. | Tooltip-feil oppdages ofte først visuelt i Desktop eller Service. | Lag en kort manuell sjekkliste for hover, filtrering, tallformat og historiske år. |
| Historisering og reproduserbarhet | Behovet for snapshot er nevnt, men ikke omsatt til modellregel. | Historiske rapporter kan endre seg hvis dimensjoner, finansieringskilde eller organisasjonsrelasjon endres. | Definer hvilke dimensjoner som må historiseres og hvilken rapportdato som skal brukes i analyser. |

## Anbefalt videre arbeid

1. Lage en begrepskatalog for økonomimodellen med eier og definisjon per begrep.
2. Etablere en KPI-katalog med DAX-/SQL-definisjon, filterlogikk og budsjettbasis.
3. Validere transaksjonstype-logikken (`DA`, `DB`, `DC`) mot økonomifunksjonen og tertialprosessen.
4. Definere standard fortegnslogikk for inntekter, kostnader, nettobidrag og avvik.
5. Avklare om prognose- og as-of-grafer skal bruke totalbudsjett med BOAVUR eller bare BEVAAR der de i dag er BEV-baserte.
6. Lage en Power BI Desktop-sjekkliste for tooltip-sider, minigrafer, tallformat og historiske avvik.
7. Koble strategiske satsinger og utviklingsavtalens styringsparametere til økonomidimensjoner.
8. Lage datakvalitetstester for prosjekt/delprosjekt, konto, budsjettversjon og finansieringskilde.
9. Skille tydelig mellom styrings-KPI for ledelse og kontroll-KPI for økonomiforvaltning.

## Lokale modellreferanser

Dette dokumentet bygger blant annet på disse lokale filene:

- `PowerBI/Okonomi/Økonomi_rapport.SemanticModel/definition/tables/fak_okonomi.tmdl`
- `PowerBI/Okonomi/Økonomi_rapport.SemanticModel/definition/tables/_Measures.tmdl`
- `PowerBI/Okonomi/Økonomi_rapport.SemanticModel/definition/tables/okonomiutvikling_maaned.tmdl`
- `PowerBI/Okonomi/Økonomi_rapport.SemanticModel/definition/tables/okonomiutvikling_linje.tmdl`
- `PowerBI/Okonomi/Økonomi_rapport.SemanticModel/definition/tables/prognoseutvikling_linje.tmdl`
- `PowerBI/Okonomi/Økonomi_rapport.SemanticModel/definition/tables/tooltip_snapshot_maaned.tmdl`
- `PowerBI/Okonomi/Økonomi_rapport.SemanticModel/definition/tables/dim_konto.tmdl`
- `PowerBI/Okonomi/Økonomi_rapport.SemanticModel/definition/tables/dim_prosjekt.tmdl`
- `PowerBI/Okonomi/Økonomi_rapport.SemanticModel/definition/tables/dim_delprosjekt.tmdl`
- `PowerBI/Okonomi/Økonomi_rapport.SemanticModel/definition/tables/dim_hovedfinansiering.tmdl`
- `PowerBI/Tertialrapport/uit_tertialrapport.SemanticModel/definition/tables/_Measures.tmdl`
- `Tableau API/docs/okonomistyring-star-schema.md`

## Offentlige kilder

- UiT virksomhetsstyring: <https://uit.no/virksomhetsstyring>
- UiT strategi mot 2030, `Eallju - Drivkraft i nord`: <https://fr.uit.no/om/strategi2030>
- KD tildelingsbrev til universiteter og høyskoler 2026: <https://www.regjeringen.no/no/dokumenter/tildelingsbrev-til-universiteter-og-hoyskoler-2026/id3141095/>
- KD tildelingsbrev 2026 for UiT, PDF: <https://www.regjeringen.no/contentassets/bd39e5357ca74704a531e63be939a233/tildelingsbrev-2026-universitetet-i-tromso-norges-arktiske-universitet.pdf>
- Langtidsplan for forskning og høyere utdanning 2023-2032: <https://www.regjeringen.no/no/dokumenter/meld.-st.-5-20222023/id2931400/>

## Åpne avklaringer

- Mappingregler for budsjettversjoner med blank `transaksjonstype` bør dokumenteres i KPI-katalogen, slik at eldre milepæler, kopier og rulleringer håndteres likt i alle rapporter.
- Det bør bekreftes om rektorgodkjent BEVAAR-/BOAVUR-basis alltid skal være `BEVAAR<år>_M1` og `BOAVUR<år>_M1`, eller om godkjent basis senere skal velges dynamisk fra `transaksjonstype = "DB"`/mappingtabell.
- Det bør avklares om `DC` skal modelleres som egen budsjettbasis, prognosegrunnlag eller tertial-milepæl i alle rapporter, og hvordan dette skal slå ut for årlig BEV, langtidsbudsjett, BOA-prosjektbudsjett og BOA-vurdering.
- Det bør avklares hvilke konti som inngår i nettobidrag for ulike rapporteringsformål, spesielt for BOA.
- Det bør bekreftes at verdiene i `dim_konto[kontorelasjon4]` er stabile styringsverdier for `Inntekter`, `Kostnader`, `Nettobidrag` og eventuelt andre kort/visualer.
- Det bør avklares hvordan strategisk satsing skal registreres på prosjekt, delprosjekt, koststed eller annen dimensjon.
- Det bør avklares hvilke BOA-prosjekter som skal klassifiseres som strategisk ønsket selv om de gir negativt kortsiktig nettobidrag.
