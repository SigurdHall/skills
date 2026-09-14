# Fagagenter, erfaring og delleveranser

## Minne følger fagrollen

En runtime-agent er midlertidig. En stabil fagrolle eier historikken og
kan overtas av en ny agent. Lagre minnet i analyseprosjektet:

```text
arbeidsflyt/arbeidsdeling.json
arbeidsflyt/leveransekontrakt.md
arbeidsminne/<rolle>/erfaringer-<historiske-aar>.md
arbeidsminne/<rolle>/erfaringer-<aar>-proeve.md
leveranser/<kjøring>/oppdrag/<rolle>.md
leveranser/<kjøring>/deler/<rolle>/minne-lest.json
leveranser/<kjøring>/deler/<rolle>/<departement>/
  notater.md
  rapport.md
  funn.json
  belegg/kildeutdrag.pdf
  belegg/kildeutdrag.md
  belegg/kildeutdrag.json
  belegg/bilder/<funn-id>.png
```

Bruk årsvise seksjoner eller separate årsfiler med en indeks. Historiske
erfaringer skal være egne for fagområdet og kildebelagte. Kortfattet minne
er bedre enn kopierte dokumenter; råuttrekk kan ligge ved som bevisgrunnlag.

Per år: kilder lest, vesentlige funn, riktig dokumentstadium, hva som ble
oversett/feiltolket, gode søk og falske treff, konkret regel for neste gang.
F.eks. flytting til et annet departement kan forklare hvorfor et senere
navnesøk ikke gir treff. Sektorbeløp og gamle rapporterte tall kan være
relevante uten å være nye UiT-bevilgninger.

Bevar historisk minne som det var ved kjøringsstart. Nye funn fra årets
analyse skal ikke tilbakedateres til tidligere år. Etter fasitkontroll kan
årets notat få status kontrollert og tas inn i neste års minneindeks. Noter
hva som ble rettet, med dato og fasit-/primærkilde.

## Oppdrag og planformat

Oppdraget skal forklare formål og relevans, minnestier, faktiske kilder,
år/stadium, forbudt fasitgrunnlag, egne skriveområder og konkrete filer som
skal leveres. Registrer rolle og kildeansvar i JSON:

```json
{
  "budget_year": 2024,
  "run_id": "2024-proeve",
  "stage": "regjeringens opprinnelige forslag",
  "history_years": [2018, 2019, 2020, 2021, 2022, 2023],
  "roles": [
    {
      "id": "helse",
      "parts": ["hod"],
      "keywords": ["Tromsøundersøkelsen", "samisk helseforskning"],
      "history": "arbeidsminne/helse/erfaringer-2018-2023.md"
    }
  ],
  "editor": {
    "id": "redaktor",
    "history": "arbeidsminne/redaktor/erfaringer-2018-2023.md",
    "deliverables": ["samlet-rapport.md", "statsbudsjettet-2024.pptx", "videreformidling.md"]
  }
}
```

Eksemplet viser én rolle; den virkelige planen skal dekke alle områdene i
arbeidsdelingen. Grupper departementer når de faglig henger sammen, men
behold én delrapport per proposisjon. Redaktøren samordner kryssende tiltak
som UD→KDD eller AID→OED. Tilføy FIN når arbeidsgiverkostnader må undersøkes.

`minne-lest.json` skal minst ha `role`, `sha256` for planens historiske
minnefil og `read_at_utc`. Redaktørens receipt heter
`leveranser/<kjøring>/minne-lest-redaktor.json`. Dette dokumenterer angitt
innlesing og versjon; det beviser ikke alene at agenten har forstått minnet.
Vurder det faglige innholdet og hvordan læringen faktisk brukes.

## Funnformat for markerte kilder

`funn.json` er en liste. Ett funn har minst:

```json
{
  "id": "hod-undersokelse",
  "title": "Kort tittel",
  "claim": "Presis egen formulering av dokumentert funn.",
  "classification": "direkte_tilskudd",
  "amount_nok": null,
  "amount_kind": "nivaa_2024",
  "implication": "Betydning og oppfølging for UiT.",
  "source": "kilder/hod-forslag.pdf",
  "pdf_page": 90,
  "printed_page": "88",
  "chapter": "714",
  "post": "79",
  "anchors": ["kort entydig tekst med beløp og mottaker"],
  "source_url": "https://..."
}
```

Klassifiser som `kd_ramme`, `direkte_tilskudd`, `fellespott`, `kostnad`,
`politisk_forutsetning` eller `finansieringsflytting`. Beløp kan være null;
oppgi nivå, endring eller flereårsramme eksplisitt. Bruk egne funn-ID-er og
angi i rapporten når et funn bare spesifiserer et annet, så de ikke summeres.

Arbeidsnotatet skal også dokumentere søk uten treff og avviste treff med
grunn. Et negativt resultat har ikke et oppdiktet positivt tekstanker.
Tom funnliste får et eksplisitt tomt kildeuttrekk, ikke en falsk PDF.

## Redaksjon og videreformidling

Sammenstill hovedtall, uventede endringer, navngitte UiT-tilskudd,
faglige muligheter/avviklinger og hva som må avklares internt. Oppgi åpne
spørsmål med ansvarlig fagområde og nødvendig grunnlag, uten å finne på
at en person har påtatt seg oppgaven.

PowerPoint og meldingsutkast skal vise at det gjelder forslag, vedtak
eller prøve. I historisk prøving skal en ferdig melding være et tydelig
utkast, ikke se ut som en faktisk utsendt melding fra det historiske året.
Meldingen skal kunne brukes med små redaksjonelle justeringer og angi
riktige vedlegg. Ingen faktisk sending følger av å lage utkastet.
