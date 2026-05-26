# BOTT/UiT økonomimodell reference

Kondensert referanse for å tolke UiT økonomidata etter BOTT økonomimodell. Bruk denne når du skal forstå datasettfelt, lage datamodell, validere rapporter eller forklare avvik.

## Primærkilder

- UiT: Retningslinje for felles økonomistruktur, `UIT.ORGØK.øko.ret.01`, fastsatt 2022-01-01, sist endret 2024-04-08: https://uit.no/Content/847306/cache%3D1715689849000/Retningslinje%20for%20felles%20%C3%B8konomistruktur%20%28%C3%B8konomimodell%29.pdf
- BOTT: Beskrivelse av BOTT økonomimodell v1.3, versjon 2022-07-01: https://i.ntnu.no/documents/portlet_file_entry/1305837853/BOTT%2B%C3%B8konomimodell%2Bv%2B1.3.pdf/43002243-2516-f1ed-a8e9-d1003365bb4a?download=true&status=0
- UiT: Kontoplan, arbeidsstøtte økonomi og innkjøp: https://uit.no/ansatte/arbeidsstotte-okonomi-innkjop/regnskap/sub?p_document_id=831022
- UiT: Budsjett og økonomistyring, omtaler at UiTs økonomimodell er basert på BOTT v1.3 og danner struktur for økonomirapportering: https://uit.no/ansatte/arbeidsstotte-okonomi-innkjop/budsjettstyring

## Modellkjerne

BOTT økonomimodell er et rammeverk for økonomisk styring og rapportering. Den bygger på konteringsdimensjoner og relasjoner:

- Dimensjon: verdi som registreres eller konteres i regnskapet.
- Relasjon: rapporteringsattributt knyttet til en dimensjonsverdi.
- Relasjoner er obligatoriske, men relasjonsverdier er ikke synlige som egne konteringsverdier.
- Relasjoner kan endres og kan påvirke historikk dersom rapporteringsuttrekk ikke snapshotter historiske relasjonsverdier.

BOTT tar utgangspunkt i DFØs standard konteringsstreng med dim 0 til dim 7. Dim 3 og dim 4 brukes ikke av BOTT. De seks relevante dimensjonene er:

| Dim | Navn | Typisk felt | Lengde | Tolkning |
| --- | --- | --- | --- | --- |
| 0 | Konto | `konto`, `account` | 4 siffer | Art: inntekt, kostnad, eiendel, gjeld, kapital |
| 1 | Koststed | `koststed`, `cost_center` | 8 siffer | Organisatorisk tilordning |
| 2 | Prosjekt | `prosjekt`, `project` | 6 siffer | Prosjekt over delprosjekt; utledes normalt fra delprosjekt |
| 5 | Delprosjekt | `delprosjekt`, `arbeidsordre`, `dim5`, `work_order` | 9 siffer | Detaljert aktivitets-/prosjektoppfølging og vanlig konteringsnivå |
| 6 | Anlegg/ansattnummer | `anlegg`, `ansattnr`, `employee_id`, `asset_id` | varierer | Anlegg, lønn, reise, avskrivninger |
| 7 | Bygg/arbeidspakke | `bygg`, `arbeidspakke`, `building`, `work_package` | varierer | Eiendom eller kontraktsfestet arbeidspakke |

## UiT hovedføringer

- UiTs økonomimodell er basert på BOTT økonomimodell v1.3.
- UiTs formelle organisasjonsstruktur har tre nivåer, og instituttnivået er normalt laveste resultatenhet.
- Inntekter og kostnader skal som hovedregel minimum føres på instituttnivå.
- I hovedsak konteres det på konto, koststed og delprosjekt.
- Prosjekt utledes av delprosjekt og konteres ikke direkte når delprosjekt brukes.
- Delprosjekt er obligatorisk for alle transaksjoner i UiTs retningslinje, med ni siffer: seks siffer prosjekt + tre siffer løpenummer.
- Delprosjekt tilsvarer arbeidsordre/dim 5 i Unit4 ERP og k-element 7 i SAP.
- Navn på delprosjekt skal starte med fakultetskode (2 siffer) eller instituttkode (4 siffer) der det er hensiktsmessig.
- Alle øremerkede delprosjekter skal ha inntekter/saldooverføring og kostnader per delprosjekt, samt eget budsjett.

## Konto

Konto er obligatorisk for alle transaksjoner. Konto har fire siffer, er standard i BOTT og følger standard statlig kontoplan.

Viktige relasjoner:

- Klasse: første siffer i kontoen.
- Gruppe: to første siffer.
- Undergruppe: tre første siffer.
- Kategorisering av konto: inntekter, kostnader, eiendeler, gjeld, virksomhetskapital.
- BOA prosjektregnskapsrapport.
- Rapportering NFR.
- Rapportering EU.
- Gruppering kostnadsomveltning.
- Universitetsspesifikke kontogrupperinger, der UiT bruker en relasjon til internregnskapsrapportering.

UiT opplyser at de bruker standard kontoplan for statlige virksomheter, BOTT felles kontoplan på firesiffernivå og en egen UiT-kontoplan med beskrivelser.

## Koststed

Koststed definerer hvilken enhet transaksjonen tilordnes. Koststed består av åtte siffer og er hierarkisk:

- Nivå 2: to siffer, fakultet/enhet eller tilsvarende.
- Nivå 3: fire siffer, institutt eller tilsvarende.
- Nivå 4: seks siffer, forskningsgrupper, seksjoner, senter mv.
- Laveste koststed: åtte siffer.

UiT bruker ikke campus-relasjonen operativt i modellen; forvent `Ikke aktuell` dersom feltet finnes. Koststedstype kan blant annet være leiested, kjernefasilitet eller ikke aktuell.

## Prosjekt

Prosjekt er seks siffer og inngår i hierarki med hovedprosjekt og delprosjekt. Prosjekt kan knytte sammen flere delprosjekter. I BOA tilsvarer prosjekt ofte kontraktsprosjektet.

Viktige relasjoner:

- Hovedprosjekt: overordnet nivå for rapportering av flere prosjekter.
- Overordnet prosjektkategorisering: brukes ved behov for ekstra rapporteringsnivå.
- Strategisk satsing: benyttes ikke ved UiT, normalt `Ikke aktuell`.
- Sentertype: SFI, SFF, SFU, FME, nasjonalt senter, annet senter, ikke aktuell.

## Delprosjekt

Delprosjekt er detaljert aktivitets- og styringsnivå. Det er alltid knyttet til prosjekt og er sentralt ved BOA, bevilgning, interne prosjekter og øremerkinger.

Viktige relasjoner:

- Finansieringskilde: hvem som finansierer delprosjektet.
- Spesifisering av finansieringskilde: mer detaljert kilde/program.
- Aktivitetstype: øverste aktivitetsnivå.
- Aktivitet: undergruppe under aktivitetstype.
- Avsetninger og overføringer: brukes for bundne/øremerkede midler og oppfølging.
- Protype: Bidrag, Bidrag EVU, Oppdrag, Oppdrag EVU, Intern, Intern EVU, Intern eiendom.
- Kunde: fra kunderegister.
- Eiersted: koststedkode for eier av prosjekt/delprosjekt.
- Prosjektleder: ansattnummer.

Bruk protype og finansieringskilde sammen ved tolkning av bidrag, oppdrag, intern aktivitet, EVU, TDI, frikjøp, egenfinansiering og fakturering.

## Anlegg/ansattnummer

Dimensjonen brukes for informasjon fra anleggsmodul og lønnssystem. Den gir grunnlag for detaljert oppfølging av lønns- og reisekostnader og anlegg.

Mulige relasjoner:

- For anlegg: eiersted, utstyrsgruppe, overordnet anlegg.
- For ansattnummer: stillingskategori og stillingskode.

Personvern: ansattnummer og reisekostnader kan være personopplysninger. Behandle bare aggregerte eller pseudonymiserte data når det er mulig.

## Bygg/arbeidspakke

Dimensjonen brukes for eiendom eller kontraktsfestede arbeidspakker. Byggnummer og arbeidspakke er gjensidig utelukkende verdier.

Bygg kan ha relasjoner for:

- Bygggruppe.
- Eierskap: egne lokaler, leide lokaler Statsbygg, leide lokaler andre, ikke aktuell.

Det er normalt ingen relasjoner knyttet til arbeidspakke.

## Datasetttolkning: anbefalt matrise

Bruk denne kolonnemalen i analyser:

| field | likely_bott_concept | dimension_or_relation | target_table | fact_key_or_dimension_attribute | expected_format | grain | required | checks | reporting_use | confidence | notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |

Eksempel:

| field | likely_bott_concept | dimension_or_relation | target_table | fact_key_or_dimension_attribute | expected_format | grain | required | checks | reporting_use | confidence | notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| konto | Konto | Dim 0 | fact + dim_account | fact foreign key | 4 digits | transaction/balance | yes | numeric, valid in account master | result/balance/accounting category | high | Join to UiT kontoplan |
| kontonavn | Konto description | Dim 0 attribute | dim_account | dimension attribute | text | account | no | one active name per account or historized | labels | high | Avoid duplicating in facts |
| koststed | Koststed | Dim 1 | fact + dim_cost_center | fact foreign key | 8 digits | transaction/balance | usually yes | hierarchy levels 2/3/4 | organization reporting | high | Check institute-level reporting |
| delprosjekt | Delprosjekt | Dim 5 | fact + dim_subproject | fact foreign key | 9 digits | transaction/balance | yes | join to project master | project/activity/financing | high | Derive project only after validation |
| prosjekt | Prosjekt | Dim 2 | dim_subproject or fact when needed | derived/optional fact key | 6 digits | transaction/master | derived | equals delprosjekt project relation | project hierarchy | medium | Do not assume direct posting |
| finansieringskilde | Financing source | Relation on delprosjekt | dim_subproject | dimension attribute | controlled value | subproject | yes for reporting | valid relation value | BOA/BEV funding reporting | high | Snapshot if historical reporting requires it |

## Faktatabeller og dimensjoner

Målet med modellering er at faktatabeller inneholder målbare hendelser eller saldoer, mens dimensjonstabeller forklarer, grupperer og hierarkiserer nøklene.

### Faktatabeller

Behold disse feltene som nøkler i faktatabeller når de finnes i kilden:

- `konto` / Dim 0.
- `koststed` / Dim 1.
- `delprosjekt` / Dim 5.
- `prosjekt` / Dim 2 når kilden har den, eller når den trengs for avstemming/ytelse; merk som avledet hvis den kommer fra delprosjekt.
- `anlegg` eller `ansattnummer` / Dim 6 når relevant.
- `bygg` eller `arbeidspakke` / Dim 7 når relevant.
- `periode`, `regnskapsdato`, `bilagsdato`, `forfallsdato` etter faktatype.
- Faktaspesifikke id-er: bilag, bilagslinje, faktura, fakturalinje, reskontropost, leverandør/kunde, transaksjons-id.
- Mål: beløp, mengde, budsjett, regnskap, restbeløp, valuta, mva-beløp, debet/kredit eller fortegn.

### Dimensjonstabeller

Flytt beskrivelser, hierarkier og relasjoner til dimensjoner:

- `dim_account`: konto, kontonavn, klasse, gruppe, undergruppe, kategori, BOA/NFR/EU-rapportering, internregnskapsgruppering.
- `dim_cost_center`: koststed, navn, nivå 2, nivå 3, nivå 4, koststedstype, eventuell campusverdi.
- `dim_project`: prosjekt, navn, hovedprosjekt, overordnet prosjektkategorisering, sentertype, strategisk satsing der brukt.
- `dim_subproject`: delprosjekt, navn, prosjekt, finansieringskilde, spesifisering, aktivitetstype, aktivitet, avsetning/overføring, protype, kunde, eiersted, prosjektleder.
- `dim_asset_employee`: anlegg/ansattnummer, eiersted, utstyrsgruppe, stillingskategori, stillingskode. Vurder tilgangsstyring.
- `dim_building_work_package`: bygg/arbeidspakke, bygggruppe, eierskap.
- `dim_date` / `dim_period`: kalender, regnskapsperiode, tertial, år.
- `dim_vendor_customer`: leverandør/kunde dersom faktura/reskontro skal analyseres på motpart.

### Faktatype-spesifikke anbefalinger

| Faktatype | Korn | Må ha som faktanøkler | Bør ikke ligge repetert i fakta |
| --- | --- | --- | --- |
| Saldotabell | saldo per periode og konteringskombinasjon | periode, konto, koststed, delprosjekt, ev. prosjekt, beløpstype | konto-/koststed-/prosjektnavn, relasjonsbeskrivelser |
| Hovedbok | bilagslinje | bilag, linje, dato/periode, konto, koststed, delprosjekt, beløp, tekst | kontohierarki, koststedshierarki, finansieringskilde, aktivitet |
| Faktura | fakturahode eller fakturalinje | faktura-id, fakturalinje hvis linjekorn, datoer, konto/koststed/delprosjekt hvis kontert, leverandør/kunde | leverandørnavn, kontonavn, prosjektbeskrivelser |
| Reskontro | reskontropost/transaksjon/apen post | reskontro-id, post-id, leverandør/kunde, datoer, konto/koststed/delprosjekt hvis tilgjengelig, restbeløp/status | lange motpartstekster, relasjonsnavn, hierarkier |

Når en stor flat fil inneholder både koder og beskrivelser, foreslå å splitte den i fakta + dimensjoner. Behold originalfilens rad-id eller en beregnet hash for sporbarhet tilbake til kilden.

## BI/datamodellering

For Power BI, Tableau eller semantisk modell:

- Bruk transaksjoner eller budsjettlinjer som faktatabell.
- Lag dimensjonstabeller for konto, koststed, prosjekt, delprosjekt, periode og eventuelt ansatt/anlegg.
- Hold relasjonstabeller i dimensjonene eller i egne masterdata-tabeller, avhengig av historikkbehov.
- For historiske rapporter: vurder snapshots av relasjoner per rapporteringsperiode.
- Definer DAX/SQL-mål eksplisitt for regnskap, budsjett, avvik, avviksprosent, BOA, bevilgning, interne prosjekter og øremerkinger.
- Dokumenter fortegnslogikk og kontoklassefilter slik at resultat og balanse ikke blandes utilsiktet.

## Vanlige avvik å flagge

- Prosjekt finnes, men delprosjekt mangler.
- Delprosjekt finnes uten gyldig prosjektkobling.
- Konto er tekstblandet, feil lengde eller mangler kontoplanrelasjon.
- Koststed er aggregert når rapporteringen krever lavere nivå.
- Relasjoner inneholder gamle eller nye verdier uten gyldighetsdato.
- `Ikke aktuell` er brukt som standardverdi uten faglig vurdering.
- BOA/NFR/EU-rapportering forsøkes uten relevante konto- og delprosjektrelasjoner.
- Ansattnummer eller fritekst inngår i åpne rapporter uten vurdering av personvern.
