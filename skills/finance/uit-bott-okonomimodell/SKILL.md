---
name: uit-bott-okonomimodell
description: Tolk, kvalitetssjekk, normaliser og dokumenter UiT økonomidata etter BOTT økonomimodell og UiTs felles økonomistruktur. Use when working with datasets, extracts, flat files, multiple tables, Power BI/Tableau models, Excel files, API responses, saldotabell, hovedbok, faktura, reskontro, GL/voucher data, budget reports, prosjekt/BOA data, delprosjekt, koststed, konto, konteringsstreng, Unit4 ERP, SAP lønn, or questions about separating fact-table accounting dimensions from dimension/master tables, finance reporting, internal control, and dataset semantics.
---

# UiT BOTT Økonomimodell

## Formål

Bruk denne skillen til å tolke datasett fra UiT økonomi- og rapporteringsmiljø opp mot BOTT økonomimodell. Målet er å gjøre datasett forståelige, rapporterbare og kontrollerbare: hva hver kolonne betyr, hvilken dimensjon eller relasjon den tilhører, hvilke koblinger som bør finnes, og hvilke datakvalitetsrisikoer som må undersøkes.

For detaljer om dimensjoner, relasjoner og UiT-spesifikke føringer, les `references/bott-uit-reference.md` når oppgaven handler om konkrete felt, datamodellering eller avvik.

## Arbeidsflyt

1. Avklar kilden: Unit4 ERP, datavarehus, Tableau/Power BI, Excel, API, SAP-lønn, anleggsmodul eller prosjektmodul.
2. Inventer datasettet: list kolonner, datatyper, eksempelverdier, unikhet, nullverdier, dato-/periodefelt og beløpskolonner.
3. Klassifiser kolonner som:
   - konteringsdimensjon: `konto`, `koststed`, `prosjekt`, `delprosjekt`, `anlegg/ansattnummer`, `bygg/arbeidspakke`
   - relasjon/rapporteringsattributt: f.eks. kontoklasse, kontogruppe, finansieringskilde, aktivitet, aktivitetstype, protype, eiersted
   - transaksjonsattributt: bilagsnummer, periode, tekst, leverandør, kunde, beløp, valuta, dato
   - teknisk felt: id, lastetidspunkt, kilde, status, hash, radnummer
4. Kontroller kornnivå: avgjør om radene er transaksjoner, budsjettlinjer, aggregater, prosjekter, delprosjekter, masterdata eller rapporteringsuttrekk.
5. Bestem hvilke konteringsdimensjoner som må ligge som fremmednøkler i faktatabeller, og hvilke beskrivelser/relasjoner som skal flyttes til dimensjonstabeller.
6. Bygg en tolkningsmatrise med kolonnene `field`, `likely_bott_concept`, `dimension_or_relation`, `target_table`, `fact_key_or_dimension_attribute`, `grain`, `required`, `quality_checks`, `reporting_use`, `notes`.
7. Pek ut manglende nøkler og relasjoner som hindrer rapportering, drilldown, avstemming eller intern kontroll.
8. Skill tydelig mellom det datasettet faktisk inneholder og det som må hentes fra masterdata eller relasjonstabeller.
9. Foreslå praktiske modellgrep for BI/analyse: faktatabeller, dimensjonstabeller, hierarkier, join keys, datatyper, snapshots og valideringsmål.

## Tolkningsregler

Behandle konto, koststed og delprosjekt som de vanligste obligatoriske økonomiske kjernedimensjonene for transaksjonsnære datasett. Prosjekt skal normalt utledes fra delprosjekt, ikke tolkes som primær konteringsnøkkel hvis delprosjekt finnes.

Tolk relasjoner som rapporteringsattributter, ikke som bokførte verdier. Hvis et datasett bare har relasjonsverdier uten dimensjonsnøkkel, marker risiko for historikkendringer og tap av sporbarhet.

For UiT gjelder at instituttnivået er laveste resultatenhet som hovedregel. Dersom koststed bare finnes på fakultetsnivå eller aggregert nivå, marker dette som mulig rapporterings- eller avstemmingsbegrensning.

Delprosjekt er sentralt for aktivitets- og prosjektoppfølging. Forvent at delprosjektnummer har ni siffer og at de seks første kan indikere prosjektnummer, men ikke erstatt autoritativ prosjektkobling med ren strenglogikk uten kontroll mot masterdata.

Konto har fire siffer og følger standard statlig kontoplan/BOTT felles kontoplan. Bruk første, to første og tre første siffer til foreløpig klasse-, gruppe- og undergruppeanalyse når offisiell kontoplan ikke er koblet inn, men merk dette som avledet heuristikk.

Vær ekstra nøye med BOA, NFR, EU, egenfinansiering, avsetninger, øremerkinger, internregnskap og kostnadsomveltning. Disse krever ofte både konto- og delprosjektrelasjoner for korrekt rapportering.

## Faktatabell vs Dimensjonstabell

Når du får flere tabeller eller en stor flat fil, normaliser etter dette prinsippet:

- Faktatabeller skal beholde konteringsdimensjoner som nøkler: konto, koststed, delprosjekt, eventuelt prosjekt, anlegg/ansattnummer og bygg/arbeidspakke, samt dato/periode, bilag/faktura/reskontro-id og beløpsfelt.
- Dimensjonstabeller skal inneholde beskrivelser, hierarkier og relasjoner: kontonavn, kontoklasse, kontogruppe, internregnskapsgruppering, koststedsnavn, nivå 2/3/4, prosjekt-/delprosjektnavn, finansieringskilde, aktivitet, aktivitetstype, protype, eiersted, sentertype mv.
- Ikke flytt konteringsnøklene ut av faktatabellene. De trengs for avstemming, drilldown, filtrering og sporbarhet.
- Ikke dupliser lange beskrivelser og relasjonsattributter i hver rad i store faktatabeller hvis de kan modelleres som dimensjoner.
- Hvis relasjoner endres over tid, vurder snapshot-dimensjon eller gyldighetsperiode før du bygger historiske rapporter.

Anbefalte minimumsnøkler:

| Faktatabell | Korn | Konteringsdimensjoner i faktatabell | Typiske dimensjonstabeller |
| --- | --- | --- | --- |
| `fact_balance` / saldotabell | saldo per periode og konteringskombinasjon | periode, konto, koststed, delprosjekt, ev. prosjekt, ev. anlegg/ansattnummer, ev. bygg/arbeidspakke | konto, koststed, prosjekt, delprosjekt, periode |
| `fact_general_ledger` / hovedbok | bokføringslinje/bilagslinje | bilag/linje, periode/dato, konto, koststed, delprosjekt, ev. prosjekt, ev. anlegg/ansattnummer, ev. bygg/arbeidspakke | konto, koststed, prosjekt, delprosjekt, leverandør/kunde ved behov, periode |
| `fact_invoice` / faktura | fakturalinje eller fakturahode, avklar korn | faktura-id, fakturalinje, konto, koststed, delprosjekt, ev. prosjekt, leverandør/kunde, dato/periode | konto, koststed, delprosjekt, leverandør/kunde, periode |
| `fact_subledger` / reskontro | åpen post, reskontropost eller transaksjon | reskontro-id, post-id, konto, koststed, delprosjekt, ev. prosjekt, leverandør/kunde, dato/periode | konto, koststed, delprosjekt, leverandør/kunde, periode, reskontrostatus |

Hvis `prosjekt` finnes både som egen kolonne og kan utledes fra `delprosjekt`, behold gjerne prosjekt som teknisk/fysisk kolonne i faktatabellen bare når den trengs for ytelse, avstemming eller kildekompatibilitet. Merk den da som avledet/denormalisert og valider mot delprosjekt-master.

## Kvalitetssjekker

Utfør relevante sjekker og rapporter funn presist:

- Konto: fire siffer, gyldig kontoklasse, riktig kategori for beløpets art, kobling til kontoplan.
- Koststed: åtte siffer på laveste nivå, hierarki mot nivå 2/3/4, minimum instituttnivå der det er relevant.
- Prosjekt: seks siffer, men ikke direkte konteringsnivå når delprosjekt finnes.
- Delprosjekt: ni siffer, kobling til prosjekt, finansieringskilde, aktivitet og aktivitetstype.
- Beløp: fortegn, valuta, periode, budsjett/regnskap-skille, aggregeringslogikk.
- Relasjoner: obligatoriske verdier, `Ikke aktuell` der det faktisk er korrekt, konsistens mellom protype, finansieringskilde og rapporteringsbehov.
- Historikk: merk at endrede relasjoner kan påvirke historiske rapporter hvis relasjonsverdier ikke er snapshotet.
- Personvern: ansattnummer, fritekst, leverandør/kunde og reisekostnader kan inneholde personopplysninger eller sensitiv informasjon.

## Outputformat

Når du tolker et datasett, lever et kort, praktisk svar med:

1. Datakorn og antatt kilde.
2. Kolonne-til-BOTT/UiT-tolkningsmatrise.
3. Foreslått faktatabell/dimensjonstabell-separasjon.
4. Nødvendige fremmednøkler i saldotabell, hovedbok, faktura og/eller reskontro.
5. Viktigste rapporteringsmuligheter.
6. Datakvalitets- og kontrollfunn.
7. Manglende masterdata eller relasjonstabeller.
8. Anbefalt neste steg for modellering, rapportering eller opprydding.

Bruk tabeller når datasettet har mange felt. Vær tydelig på usikkerhet, og skill mellom dokumentert regel, sterk indikasjon og antakelse.

## Kilder

Bruk `references/bott-uit-reference.md` for kondensert fagreferanse og kilde-URL-er. Ved presise regelspørsmål eller produksjonsnær dokumentasjon bør primærkildene kontrolleres på nytt, fordi UiT-relasjoner og rapporteringsbehov kan endres.
