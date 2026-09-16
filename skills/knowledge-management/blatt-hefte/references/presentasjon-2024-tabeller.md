# Presentasjonen 2024 → arkene i rammearket

Kilde: `uit-statsbudsjett/2024/Presentasjon av statsbudsjett 2024 v.0.99.pptx` og de fem
innebygde arbeidsbøkene i `2024/_uttrekk/` (`slide3-5-ole.xlsx`, `slide6-5-ole.xlsx`,
`slide6-9-ole.xlsx`, `slide7-8-ole.xlsx`, `slide8-6-ole.xlsx`). Alle fem er utsnitt av
samme arbeidsbok med arkene `Bud.ramme`, `Hovedpost.`, `Resultatkomp.`, `Sammenligning`
og `NyeSatser`.

Denne filen er for kode og mennesker ved bygging. Den leses ikke ved kjøring.

## Lysark → ark

| Lysark | Innhold i presentasjonen | Ark i rammearket | Kilde i arbeidsboken | Avledbart fra blått hefte |
|---|---|---|---|---|
| 2 | Budsjettramme og nominell endring | `Hovedtall` | `Bud.ramme!C6:C9` | Ja. Første og siste kolonne i hovedtabellen. |
| 3 | Broen fra vedtatt ramme til forslag, to blokker (uten og med RNB) | `Hovedposter` | `Hovedpost.!B3:I20` | Delvis. Postene er heftets kolonner, ikke presentasjonens egne poster. RNB er ikke i heftet. |
| 4–5 | Tekst fra Prop. 1 S | — | — | Nei. Utenfor skopet. |
| 6 | Resultatbasert uttelling per indikator | `Resultat` | `Resultatkomp.!B4:C17` | Ja for 2025–. For 2024 har heftet åtte indikatorer og to summer. |
| 7 | Sammenligning med de andre universitetene | `Sektor` | `Sammenligning!B3:E12` | Ja, og mer fullstendig enn presentasjonen (som mangler USN). |
| 8 | Rammer og satser | `Satser` | `NyeSatser!B3:H9` | Delvis. Rammene og heftets egne satser er med; satskolonnene er ikke. |

## Hva som er avledbart

Fra blått hefte alene:

- Utgangspunkt (`Saldert budsjett Y−1`) og forslag (`Forslag rammeløyving Y`) per institusjon.
- Alle justeringskolonnene mellom dem, med heftets egne overskrifter.
- Nominell endring, prisjusteringssats og -beløp, og realvekst etter begge metoder.
- Resultatbasert uttelling per indikator og institusjon.
- Satsene heftet oppgir: studieplasskategorier, studiepoengkategorier, doktorgrader,
  fullføring, og rammene for lukket ramme til og med 2024.
- Forkortelser og institusjonsliste.

## Hva som ikke er avledbart

| Element | Hvorfor | Hva rammearket gjør |
|---|---|---|
| RNB-tillegget (86 200 for 2023) | Står i revidert nasjonalbudsjett, ikke i blått hefte. | Én inndatacelle i `Hovedtall` med kildeetikett. Tom celle gir «ikke oppgitt». |
| Presentasjonens egne poster i lysark 3 (`Inndekning satsinger`, `Rammeøkning – avvikling av ordningar i HK-dir`, `Omfordeling Ukraina`) | Aggregater og omskrivninger av heftets kolonner, laget for hånd. | `Hovedposter` bruker heftets kolonner. Kolonnen `Egen etikett` er tom for omskriving. |
| Satskolonnene i `NyeSatser` (`D`, `F`, `H`) | Regnet som ramme delt på produksjonstall fra DBH. | `Satser` viser rammene og merker satskolonnen «ikke i heftet, krever produksjonstall fra DBH». |
| Bokmålsetikettene | Heftet er på nynorsk. | Heftets etiketter brukes uendret; `Egen etikett` er tom. |

## Kjente feil i presentasjonen

1. `Hovedpost.!G5` er merket «Lønns og prisjustering 3,0 %», men `I5` er 250 434, altså
   4,4 %-tallet (samme verdi som `D5`). Etiketten er feil, ikke tallet.
2. `Sammenligning` mangler USN blant universitetene. Ni rader der det skulle vært ti.
3. `Hovedpost.!B20` sier «Realvekst justert for RNB 2023 er −0,3 %», men `I19` regner
   metode b (−0,29 %), ikke metode a. Lysark 2 viste 1,9 %, som er metode a uten RNB.
   Tallene er riktige; det er ikke samme definisjon som lysark 2.

## De fire realveksttallene

| Metode | Verdi | Kildecelle | Utregning |
|---|---|---|---|
| a, uten RNB | 1,89 % | `Hovedpost.!D19` | `D18 − 4,4 %` = 6,29 % − 4,4 % |
| b, uten RNB | −0,29 % | ingen | (239 289 − 250 434) / 3 806 533 |
| a, med RNB | 1,75 % | `Hovedpost.!I18` | `I18 − 4,4 %` = 6,15 % − 4,4 % |
| b, med RNB | −0,29 % | `Hovedpost.!I19` | (239 289 − 250 434) / 3 892 733 |

Presentasjonen kommuniserte 1,9 % (metode a uten RNB) og «−0,3 % justert for RNB»
(metode b med RNB). Rammearket viser metode b uten RNB som hovedtall og de tre andre i
kontrollblokken, med etikett på hver.

## Den lukkede avvikslisten

Fase 5 sammenligner hver celle i `assets/fasit-2024.json` mot rammearket. Bare avvikene
under er tillatt. Alt annet feller testen.

| Id | Gjelder | Avvik |
|---|---|---|
| A1 | `Hovedpost.!D12`, `I12` | `Omfordeling Ukraina` −734 er en egen post i forslagsheftets tekst, men ikke en egen kolonne i hovedtabellen. |
| A2 | `Sammenligning!B4:E12` | USN mangler i presentasjonens sektortabell. |
| A3 | `NyeSatser!D5:D8`, `F5:F8`, `H5:H8` | Satskolonnen er DBH-produksjonsbasert og ikke avledbar. Bare rammekolonnene `C`, `E`, `G` er kontrollgrunnlag. |
| A4 | `Hovedpost.!G5` | Kjent feil: blokk 2 er merket «3,0 %», men bruker 4,4 %-tallet 250 434. |

Listen står også maskinlesbar i `assets/fasit-2024.json` under `tillatte_avvik`.

## Endringslogg for malspesifikasjonen

Endres `assets/mal-rammeark.json` i fase 4 eller senere, føres endringen her med dato og
årsak, og malen regenereres med `mal.py`.

| Dato | Endring | Årsak |
|---|---|---|
| 2026-09-16 | Første versjon av spesifikasjonen. | Fase 1. |
