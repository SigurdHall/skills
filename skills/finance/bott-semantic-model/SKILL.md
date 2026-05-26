---
name: bott-semantic-model
description: Lag, vurder og dokumenter semantiske modeller og Power BI/Tableau-stjerneskjema for BOTT-baserte økonomidata. Use when working with UiT/BOTT finance datasets, Unit4/ERP extracts, saldotabell, hovedbok, budsjett, faktura, reskontro, konto, koststed, prosjekt, delprosjekt, anlegg/ansatt, bygg/arbeidspakke, konteringsstreng, semantic models, Power BI, TMDL, PBIP, star schemas, fact/dimension separation, and model quality checks.
---

# BOTT Semantic Model

## Formål

Bruk denne skillen til å lage semantiske modeller for økonomidata som følger BOTT økonomimodell. Modellen skal være enkel å avstemme, lett å forstå for økonomibrukere og trygg å bruke i Power BI eller Tableau.

## Grunnregel

Ikke lag kunstige koblingsnøkler for BOTT-konteringsdimensjonene når kildedata allerede har autoritative koder.

Faktatabeller skal beholde disse feltene som faktiske koblingsnøkler:

- `Kontonr.`
- `Koststedsnr.`
- `Delprosjektnr.`
- `Prosjektnr.` når kilden har den, men valider mot delprosjekt
- `Anlegg-/ansattnr.`
- `Bygg-/arbeidspakkenr.` og/eller `Arbeidspakke`

Dimensjonstabellene skal ha samme naturlige kodefelt som nøkkelkolonner. Ikke erstatt dem med `konto_nokkel`, `koststed_nokkel`, hash-nøkler eller surrogatnøkler med mindre brukeren eksplisitt ber om en fysisk lagerdesign som krever det.

## Arbeidsflyt

1. Inventer kildedata: tabeller, kolonner, datatyper, radkorn, beløpsfelt og kodefelt.
2. Finn faktatabeller: saldo, hovedbok, budsjett, faktura, reskontro eller brede økonomistyringsfakta.
3. Finn BOTT-konteringsdimensjoner i fakta:
   - Dim 0: konto
   - Dim 1: koststed
   - Dim 2: prosjekt
   - Dim 5: delprosjekt
   - Dim 6: anlegg/ansatt
   - Dim 7: bygg/arbeidspakke
4. Behold konteringsdimensjonenes kodefelt i faktatabellene.
5. Flytt navn, hierarkier og relasjoner til dimensjonstabeller.
6. Dedupliser dimensjonstabeller på naturlig nøkkel, ikke på generert nøkkel.
7. Dokumenter relasjoner som én-til-mange fra dimensjon til fakta.
8. Legg inn kontrollregler for nøkkeldekning, historikk og ikke-additive felt.

## Faktatabeller

Faktatabeller skal inneholde:

- konteringskoder som koblingsfelt
- periode/dato
- bilag, linje, faktura, reskontro-id eller annen drilldown-identifikator
- beløpsfelt og mengdefelt
- kilde/status der det trengs for å skille regnskap, budsjett og prognose

Eksempel for økonomistyring:

| Felt i fakta | Bruk |
| --- | --- |
| `Firmakode` | kobling til firma |
| `Periode` | kobling til periode |
| `Kontonr.` | kobling til konto |
| `Koststedsnr.` | kobling til koststed |
| `Delprosjektnr.` | kobling til delprosjekt |
| `Prosjektnr.` | kobling til prosjekt, valideres mot delprosjekt |
| `Anlegg-/ansattnr.` | kobling til anlegg/ansatt der relevant |
| `Bygg-/arbeidspakkenr.` | kobling til bygg/arbeidspakke der relevant |
| `Regnskapsbeløp` | additivt regnskapsmål |
| `Budsjettbeløp` | additivt budsjettmål |

## Dimensjonstabeller

Dimensjoner skal beholde kodefeltet som nøkkel og inneholde beskrivelser, hierarkier og relasjoner.

Typiske dimensjoner:

| Dimensjon | Nøkkel | Typiske attributter |
| --- | --- | --- |
| `dim_konto` | `Firmakode`, `Kontonr.` | kontonavn, klasse, gruppe, undergruppe, kategori, BOA/NFR/EU-gruppering |
| `dim_koststed` | `Firmakode`, `Koststedsnr.` | koststedsnavn, fakultet, institutt, seksjon, koststedstype |
| `dim_delprosjekt` | `Firmakode`, `Delprosjektnr.` | navn, prosjekt, finansieringskilde, aktivitet, aktivitetstype, eiersted |
| `dim_prosjekt` | `Firmakode`, `Prosjektnr.` | navn, hovedprosjekt, type, sentertype, status, roller |
| `dim_anlegg_ansatt` | `Firmakode`, `Anlegg-/ansattnr.` | navn/type/stillingskode der tilgang er vurdert |
| `dim_bygg_arbeidspakke` | `Firmakode`, bygg-/arbeidspakke-kode | navn, type, bygggruppe, eierskap |
| `dim_periode` | `Periode` | år, måned, periodedato, status |

Hvis en dimensjon har historiske attributter, vurder gyldighetsperioder eller snapshot. Ikke bland historikk inn i fakta uten en bevisst regel.

## Power BI

For CSV-output som skal lastes i Power BI:

- Skriv UTF-8 med BOM (`utf-8-sig`) for norske tegn.
- Bruk semikolon som separator når kilden og norsk Excel/Power BI-miljø allerede bruker semikolon.
- Bruk samme separator i alle tabeller.
- La første rad være rene kolonnenavn.
- Ikke legg inn kommentarer eller metadata øverst i CSV-filene.
- Bruk faktiske konteringskoder som relasjonskolonner.

Anbefalte relasjoner:

- `dim_konto[Kontonr.]` -> `fakta[Kontonr.]`, eventuelt sammen med `Firmakode`
- `dim_koststed[Koststedsnr.]` -> `fakta[Koststedsnr.]`, eventuelt sammen med `Firmakode`
- `dim_delprosjekt[Delprosjektnr.]` -> `fakta[Delprosjektnr.]`, eventuelt sammen med `Firmakode`
- `dim_prosjekt[Prosjektnr.]` -> `fakta[Prosjektnr.]`, eventuelt sammen med `Firmakode`
- `dim_periode[Periode]` -> `fakta[Periode]`

Power BI støtter ikke sammensatte relasjoner direkte i modellvisningen. Hvis `Firmakode` faktisk trengs for unikhet, lag en lesbar komposittkolonne basert på autoritative koder, for eksempel `Firmakode|Kontonr.`. Ikke bruk hash som forretningsnøkkel.

## Kontroller

Rapporter disse funnene når modellen foreslås eller bygges:

- manglende nøkkelverdier i fakta
- faktanøkler uten treff i dimensjon
- dimensjonsnøkler med flere ulike attributtverdier
- ikke-additive felt som kontraktsbeløp, prosentsatser og statusfelt
- personvernrisiko i ansattnummer, navn, fritekst og motpartsinformasjon
- relasjoner som kan ha endret historikk uten gyldighetsdato

## Output

Når du leverer en modell, inkluder:

1. Faktatabeller og radkorn.
2. Dimensjoner og naturlige nøkler.
3. Relasjoner med faktiske kolonnenavn.
4. Felt som skal holdes i fakta.
5. Felt som skal flyttes til dimensjoner.
6. Dedupliseringsregel per dimensjon.
7. Power BI-importnotater og kontrollregler.
