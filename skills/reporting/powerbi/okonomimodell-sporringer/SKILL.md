---
name: okonomimodell-sporringer
description: SKAL brukes før alle DAX-spørringer mot Okonomimodell, enten formålet er kontroll, verifisering, test av mål, røyktest etter deploy eller utforsking av sammenhenger i dataene. Ruter all DAX til PPU-kopien (okonomimodell_ppu), deler opp eller flytter til SQL-endepunktet når spørringen sprenger minnetaket, og slipper bare 5 små røyktestkall per dag mot den levende modellen på F8. Triggere er kontroller mot økonomimodellen, sjekk tallene, test målet, utforsk dataene, finn sammenheng, røyktest, deploy-sjekk, executeQueries, DAX mot Okonomimodell og okonomimodell_ppu. Ikke for modellendringer (semantic-model-authoring) eller rapportlayout.
---

# Spørringer mot Okonomimodell

Den levende Okonomimodell ligger på en liten F-kapasitet (F8). All DAX mot en publisert modell regnes som interaktiv CU. Det gjelder executeQueries, XMLA, MCP og `sempy.evaluate_dax` fra notebook, og det finnes ingen innstilling som gjør det om til bakgrunn. Interaktiv CU glattes bare over 5 minutter, så noen få tunge spørringer gir overage og throttling for alle. Derfor går alt arbeid mot en kopi på PPU, og den levende modellen får bare små røyktester.

ID-er, vertsnavn og de målte spørringene står i `references/private/okonomimodell.md` og `references/private/okonomimodell.json`. Mappen er gitignorert. Mangler filene, spør brukeren før du kaller noe.

## Ruting

1. **PPU er standard.** Alle kontroller, mål-tester og utforsking går mot `okonomimodell_ppu`. Den er en importkopi som genereres fra Okonomimodell sin TMDL og oppdateres daglig fra samme gold-data. PPU belaster ikke F8.
2. **Mål som ikke er deployet til PPU ennå**, testes med `DEFINE MEASURE` foran `EVALUATE` mot PPU. Definer hele kjeden, fordi modellmål ikke ser skyggede definisjoner.
3. **Minnefeil på PPU** («Resource Governance … memory limit»): del spørringen opp etter år, `dim_periode[periode_aar]`, og kjør år for år. Feiler ett år også, skriv spørringen som aggregert T-SQL mot SQL-endepunktet til gold-lakehouset. Den regnes som bakgrunns-CU.
4. **F8 bare for røyktest og deploy.** Høyst 5 kall per dag. Hvert kall skal være av klasse S (se under) og må først være kjørt på PPU. Skriptet håndhever begge deler.

## Størrelsesklasser

Klassen settes etter svartid på PPU. Målingene ble gjort med ca. 14 mill. rader i regnskapsfakta.

| Klasse | PPU-tid | Typisk form | Hvor |
|---|---|---|---|
| S | under 1 s, høyst 500 rader i svaret | Skalarer, per år eller periode, per enhet, enhet × kontogruppe, kjedede prognosemål per enhet, telling av tusenvis av grupper | PPU, og F8 som røyktest |
| M | 1–10 s | SWITCH-mål over modus × kolonne, materialisering av ca. 2 mill. kombinasjoner, ett mål per bilagslinje for ett år | Bare PPU |
| L | 10–150 s | Mål evaluert millioner av ganger: per bilagslinje over alle år, hittil-mål per delprosjekt × konto × periode, tekstnøkler per rad, RANKX over alle linjer | Bare PPU, én om gangen, helst delt opp etter år |
| X | feiler | Over 10 240 MB per spørring, for eksempel hittil-mål per bilagslinje × periode over alle år, eller tekst over maksimal lengde | Del opp etter år, ellers SQL-endepunktet |

På F8 er minnetaket 1 GB per spørring. En spørring som går fint på PPU, kan derfor feile på F8. Det er en grunn til at bare klasse S sendes dit.

Budsjettet på F8 er regnet ut slik: F8 har 2 400 CU-s per glattevindu på 5 minutter. Anslaget er at et kall i klasse S koster høyst ca. 32 CU-s, så fem kall bruker under 7 % av vinduet. Anslaget er ikke målt ennå. Etter første røyktest kontrollerer du forbruket i Capacity Metrics og justerer grensen.

## Skriv spørringene slik

- Én `EVALUATE` per kall. executeQueries godtar bare én spørring, og svaret er begrenset til 100 000 rader og 1 mill. verdier.
- Store grupperinger pakkes inn i `ROW ( "rader", COUNTROWS ( SUMMARIZECOLUMNS ( … ) ) )` eller aggregeres til få rader. Da måler du beregningen, ikke overføringen.
- Hva en spørring koster, avhenger av hvor mange ganger målene evalueres, ikke av antall rader i faktatabellen. Bare å gruppere millioner av rader er billig. Å evaluere et hittil-mål per rad er dyrt.
- Gjenbruk lagrede svar før du spør igjen. Hver spørring skal ha én setning om hvilken feil eller sammenheng den kan avsløre.

## Kjøring

Spørringene legges i en `.dax`-fil som blokker. Hver blokk starter med `-- <KODE> <hva den avslører>`.

```bash
python -I scripts/okonomimodell_dax.py --fil sporringer.dax                 # PPU, alle blokker
python -I scripts/okonomimodell_dax.py --fil sporringer.dax K03 K07         # PPU, utvalgte blokker
python -I scripts/okonomimodell_dax.py --fil roykttest.dax --mal f8         # F8, bare klasse S som er kjørt på PPU
```

Skriptet kjører blokkene én og én og skriver en JSON-linje per blokk med sekunder, antall rader, de tre første radene, eventuell feil og klassen. Svarene lagres under `--ut`, som standard `./ut/okonomimodell`. Kjøringer mot PPU logges i `~/.fabric_ko/okonomimodell_ppu_logg.jsonl`. Mot F8 gjør skriptet dette:

- avviser spørringer som ikke er kjørt på PPU de siste 7 dagene med klasse S
- teller kall per dag i `~/.fabric_ko/` og stopper etter 5
- bruker den samme låsen og 20 s-pausen som `fabric-cu-glatting`

## Rapportering

Etter en runde oppgir du hvor mange kall som gikk til PPU og hvor mange til F8. Oppgi også klassen til den tyngste spørringen og om noe falt tilbake til oppdeling per år eller til SQL-endepunktet.
