# Tabellkart for blått hefte

Hva `les_blaatt_hefte.py` faktisk finner i hvert hefte, og hvor. Alle sidetall er **PDF-sider**
(1-basert); trykt side er PDF-side − 1 i alle 19 kontrollerte heftene. Kilden er kjøringen
2026-09-16 over `uit-statsbudsjett/analyse/kilder/blaatt-hefte/*/*.pdf` og de sju eldre stiene
under `analyse/kilder/<år>/`. Leseren finner alle tabellene på innhold, ikke på sidetall, så
tabellen under er dokumentasjon og ikke inndata til koden.

## Sider per hefte

| Hefte | Forkortingsliste | Hovedtabell (post 50) | Kolonneforklaring (prissats) | Resultat | Satser (åpen) | Lukket ramme |
|---|---|---|---|---|---|---|
| 2021 forslag | 4 | 19 | 38 | 30 | 36 | 37 |
| 2021 vedtak | 4 | 19 | 38 | 30 | 36 | 37 |
| 2022 forslag (korrigert 2021-10-13) | 4 | 19 | 17 | 30 | 36 | 37 |
| 2022 vedtak (2021-12-20) | 4 | 17 | 16 | 27 | 34 | 34 |
| 2023 forslag | 4 | 17 | 15 | 26 | 32 | 33 |
| 2023 vedtak | 4 | 17 | 15 | 27 | 33 | 34 |
| 2024 forslag (begge filene) | 4 | 16 | 14 | 26 | 32 | 32 |
| 2024 vedtak | 4 | 16 | 14 | 27 | 33 | 33 |
| 2025 forslag | 4 | 13 | 11 | 24 | 21 | finnes ikke |
| 2025 vedtak | 4 | 13 | 11 | 25 | 22 | finnes ikke |
| 2026 forslag | 4 | 12 | 11 | 23 | 20 | finnes ikke |
| 2026 vedtak | 4 | 12 | 11 | 23 | 20 | finnes ikke |

Kapitler: hovedtabellen står alltid i `3.3.1 Universitet og statlege høgskular (kap. 260, post 50)`,
privattabellen i `3.3.2 … (kap. 260, post 70)` 2–4 sider senere. Resultattabellen står i
`4.2 Endring i regelstyrt resultatutteljing` (2021–2023), `4.2.1 Budsjettendring gjennom den
resultatbaserte utteljinga` (2024) og `4.3 Budsjettendring gjennom den resultatbaserte utteljinga`
(2025–2026). Satsene står i finansieringskapittelet: `4.4.x` til og med 2023, `4.2.2` i 2024,
`4.2 Satsar og indikatorar` fra 2025.

## Hovedtabellens kolonner

Første kolonne er alltid utgangspunktet og siste alltid ramme/forslag; alt imellom skifter.

- **2021** (11): Saldert budsjett 2020 · ABE-reform · Prisjustering · St.plassar 2016-2020 ·
  5. året lærarutd. · Rekr.-stillingar · Resultatbasert utteljing · Statens innkjøpssenter ·
  Midlar til Udir · Andre endringar · **Budsjettforslag 2021** (vedtak: **Budsjett 2021**)
- **2022 forslag** (12): Rammeløyving 2021 · ABE-reform · Prisjustering · Studieplassar 2016-2020 ·
  Studieplassar barnevern · 5. året lærarutd. · Resultatbasert utteljing · Inndekning satsingar ·
  Endra reisevanar i staten · Ny premiemodell pensjon · Andre endringar · Forslag rammeløyving 2022
- **2022 vedtak** (13): som forslaget, men «Endra reisevanar» og én kolonne til, `Grøn forsking`,
  før `Rammeløyving 2022`
- **2023** (10): Saldert budsjett 2022 · Prisjustering · Studieplassar 2019–2022 ·
  Resultatbasert utteljing · Inndekning satsingar · Endra reisevanar · Premiemodell pensjon ·
  Studieavgift utanfrå EØS · Andre endringar · Forslag rammeløyving 2023
- **2024** (12): Saldert budsjett 2023 · Prisjustering · Studieplassar 2019–2023 ·
  Utfasing rekr.-stillingar · Resultatbasert utteljing · Inndekning satsingar ·
  Omfordeling Ukraina · Rammeauke (jf. kap. 3.3.3) · Studieavgift · Nye studieplassar ·
  Andre endringar · Forslag rammeløyving 2024
- **2025** (13): Saldert budsjett 2024 · Prisjustering · Studieplassar 2020–2024 ·
  Utfasing rekr.-stillingar · Resultatbasert utteljing · Overgangsordning nytt fin.sys. ·
  Reduksjon · Studieavgift · Eigenbetaling for gjentak · Desentralisert og fleksibel utdanning ·
  Nye studieplassar · Andre endringar · Forslag rammeløyving 2025
- **2026** (9): Saldert budsjett 2025 · Prisjustering · Resultatbasert utteljing ·
  Studieplassar 2020–2025 · Nye studieplassar · Bu- og reisestønad · Reduksjon ·
  Andre endringar · Forslag rammeløyving 2026

## UiT-radene

| Hefte | Utgangspunkt | Prisjustering | Resultat (kolonne) | Ramme/forslag |
|---|---|---|---|---|
| 2021 forslag | 3 405 234 | 108 420 | 13 865 | 3 607 742 |
| 2021 vedtak | 3 405 234 | 108 420 | 13 865 | 3 604 321 |
| 2022 forslag | 3 604 321 | 93 255 | 18 877 | 3 648 676 |
| 2022 vedtak | 3 604 321 | 93 255 | 18 877 | 3 647 822 |
| 2023 forslag | 3 647 822 | 109 435 | 50 932 | 3 806 489 |
| 2023 vedtak | 3 647 822 | 109 435 | 50 976 | 3 806 533 |
| 2024 forslag | 3 806 533 | 250 434 | −5 085 | 4 045 822 |
| 2024 vedtak | 3 806 533 | 245 987 | −5 085 | 4 061 059 |
| 2025 forslag | 4 061 059 | 157 470 | −25 307 | 4 155 453 |
| 2025 vedtak | 4 061 059 | 157 470 | −25 311 | 4 175 449 |
| 2026 forslag | 4 175 449 | 150 316 | −27 919 | 4 276 564 |
| 2026 vedtak | 4 175 449 | 150 316 | −27 919 | 4 281 564 |

## Prissats og sitat

| Budsjettår | Sats | `ren_sats` | Avvik for UiT | Sitat (forkortet) |
|---|---|---|---|---|
| 2021 | 3,2 % | ja | −547 | «…har departementet nytta ein prisjusteringsfaktor på 3,2 pst.» |
| 2022 | 2,6 % | ja | −457 | «Kolonnen Prisjustering viser prisjusteringa av Rammeløyving 2021 minus ABE-reduksjonen. Satsen for prisjustering er 2,6 pst.» |
| 2023 | 3,0 % | ja | 0 | «Kolonnen Prisjustering viser prisjusteringa av Saldert budsjett 2022. Satsen for prisjustering er 3,0 pst.» |
| 2024 | 4,4 % | **nei** | +82 947 (forslag) / +78 500 (vedtak) | «…og vidareføring av den ekstraordinære prisjusteringa som blei løyvd i samband med revidert nasjonalbudsjett for 2023. Satsen for prisjustering for 2024 er 4,4 pst.…» |
| 2025 | 3,8 % | **nei** | +3 150 | «…og tilbakeføring av prisjusteringa som blei redusert i budsjettforliket i 2024. Satsen for prisjustering for 2025 er 3,8 pst.» |
| 2026 | 3,6 % | ja | 0 | «Kolonnen Prisjustering viser prisjusteringa av Saldert budsjett 2025. Satsen for prisjustering for 2026 er 3,6 pst.» |

Toleransen er 0,0005 × utgangspunkt. 2021 og 2022 avviker med under 600 kroner (avrunding);
2024 og 2025 avviker fordi kolonnen inneholder mer enn satsen. 2021 har ingen setning om
kolonnen, bare prisjusteringsfaktoren i finansieringskapittelet.

## Resultattabellen

- **2021–2024**: ti kolonner, åtte indikatorer og to sumkolonner (`Sum endring open ramme` =
  indeks 4, `Sum endring lukka ramme` = indeks 9). Tabellen går over to sider, statlige
  institusjoner først; leseren leser fortsettelsessiden når den har samme antall kolonnebånd.
- **2025–2026**: fire kolonner, `Studiepoeng · Doktorgradar · Fullføring · Sum` (sum = indeks 3),
  alt på én side, statlige og private i samme tabell med en `Sum`-rad til slutt (som ikke er en
  kortkode og derfor ikke blir en datarad).
- UiT 2025 forslag: −21 307 / −2 996 / −1 881 / −25 307. UiT 2026 forslag: −12 395 / −2 904 /
  −12 620 / −27 919.

## Satser

- **2021–2024**: kategoritabell A–F (fire satskolonner i 2024: studieplasstildeling, studiepoeng,
  kandidat enkel, kandidat dobbel), indikatortabell (doktorgrad, utveksling, Erasmus+) og
  `Indikator / Rammer` for lukket ramme. 2024 har i tillegg en forhåndstabell for 2025-kategoriene.
- **2025–2026**: overgangstabell A–F (sats for opptrapping av gamle studieplasstildelinger),
  kategoritabell 1–3 med to kolonner (sats per 60-studiepoengeining, studieplasstildeling) og
  `Indikator / Sats` for doktorgrader og fullføring. Lukket ramme finnes ikke; feltet er `null`.

## Avvik og funn

- **F1 Kolonnene skifter hvert år.** 9–13 kolonner, nye navn, ny rekkefølge. Bare første og siste
  er stabile i betydning. Ingen årsspesifikk kode; kolonnenavnene tas som de står.
- **F2 «Inst.» bare noen år.** Institusjonskolonnen har overskrift `Inst.` i 2022 og i
  resultattabellen 2021–2024, og ingen overskrift i 2023–2026. Den er ikke et kolonnebånd
  (båndene bygges bare fra tallcellene), så den påvirker ikke kontroll B.
- **F3 Radrekkefølgen skifter.** 2021–2024 lister universitetene først, deretter høgskolene;
  2025–2026 er alfabetisk på kortkode. Ingen kode er avhengig av rekkefølgen.
- **F4 Kortkodene skifter.** `SH`→`SA`, `HiNN`→`HINN`, `HiVo`→`HVO`, `HiM`/`HIM`. Alt slås opp på
  `kortkode_norm` (store bokstaver); `kortkode` beholder heftets skrivemåte.
- **F5 Tomme celler har to former.** Ingen tekst i 2021–2023, synlig `-` fra 2024. Båndmetoden
  behandler begge som `null`; rekkefølgelesing ville gitt feil kolonne.
- **F6 Forslag og vedtak har ulik struktur.** Vedtaksheftene har egne kolonner for det som kom i
  budsjettforliket (`Grøn forsking` i 2022) og ligger 2 sider tidligere i 2022.
- **F7 Sluttkolonnens navn.** `Forslag rammeløyving ÅÅÅÅ` i forslag, `Rammeløyving ÅÅÅÅ` i vedtak,
  men `Budsjettforslag 2021`/`Budsjett 2021` i 2021. Kontroll B godtar begge ordene sammen med
  budsjettåret, og utgaven utledes av om ordet «forslag» står i overskriften.
- **F8 Resultatstrukturen brøt i 2025.** Åtte indikatorer og to summer ble tre indikatorer og én sum.
- **F9 Satsstrukturen brøt i 2025.** Kategoriene A–F ble 1–3 med overgangstabell, og lukket ramme
  ble avviklet.
- **F10 Sektorsammenligningen er hovedtabellen.** Ingen egen tabell; universitetene plukkes ut av
  institusjonslisten.
- **F11 Kjedebrudd.** Forslag 2023 → saldert 2024 avviker med 44 for UiT (budsjettforliket).
  Kjeden *vedtak Y−1 → Y* er derimot hel for alle institusjoner i alle kontrollerte par
  (2022V→2023F, 2023V→2024F, 2024V→2025F, 2025V→2026F): kontroll C gir `ok` uten avvik.
  Kontroll C skal derfor kjøres mot vedtaksheftet, ikke mot forslaget.
- **F12 2025 etter vedtak summerer ikke for UiT.** Radens tolv endringskolonner gir 4 176 209,
  mens heftet trykker 4 175 449 (760 mindre). Det er heftets tall som føres videre som saldert
  budsjett 2025 i 2026-heftet. Alle 20 andre rader summerer. Leseren advarer og setter
  `alle_rader_summerer = false`; den stopper først når to eller flere rader ikke summerer.
- **F13 Et ellevte universitet fra 2025 etter vedtak.** Høgskolen i Innlandet ble Universitetet i
  Innlandet (`INN`), så navneregelen gir elleve universiteter i 2025V og 2026 mot ti før.

## Lesbarhet (det maskinen må tåle)

- Overskriftene er vannrette, men stablet over 2–6 linjer med bindestrekdeling: `Pris-` +
  `justering` → `Prisjustering`, mens `rekr.-` + `stillingar` → `rekr.-stillingar` og `BOA-` +
  `inntekter` → `BOA-inntekter`. Regelen er: fjern bindestreken bare når tegnet foran er en liten
  bokstav.
- Tall splittes i flere ord ved tusenskille. Naboord med luke under 4 pt limes til én celle.
- Minus er ASCII `-` klistret til første fragment. Tankestrek i årstallsintervaller
  (`2019–2023`) blir stående uendret.
- Kolonnene er høyrestilte med stabile høyrekanter (±1 pt). Klustring på `x1` med luke 6 pt gir
  riktig antall bånd i alle 19 hefter, og ingen rad får to celler i samme bånd.
- «Oversikt over budsjettendringar» treffer to sider per hefte (post 50 og post 70). Sidevalget
  krever både teksten `post 50` og minst 15 kortkoderader.
- Antall statlige institusjoner = kortkodene i forkortingslisten minus kortkodene i post 70-tabellen
  = 21 i alle årene 2021–2026.
- Kjøretiden er 0,2–0,3 sekunder per hefte (budsjettet i planen er 15 s).

## Kjente svakheter i satslesingen

Satstabellene er brødtekst med kolonner, ikke tallrader, og leses derfor løsere enn hovedtabellen:

- Tallene er riktige i alle tabellene, men flerlinjers etiketter kan havne på naboraden eller
  bli slått sammen med nabokolonnen (for eksempel `Kategori Utdanning` som én kolonne i 2025).
- Tabelltittelen er blokken som ender på `(tal i kroner)`. I 2021 og 2022 henger et avsnitt med
  i tittelen fordi PDF-en legger avsnitt og bildetekst i samme blokk.
- Ingen test hviler på satsinnholdet; kontrakten tar det «som det står».
