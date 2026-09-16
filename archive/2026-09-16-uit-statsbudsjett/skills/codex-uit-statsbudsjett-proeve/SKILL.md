---
name: codex-uit-statsbudsjett-proeve
description: Hent årets blå hefte og lever UiTs nye budsjettramme som tabell straks. Trekk deretter ut søkeordtreff med omkringliggende avsnitt fra departementenes Prop. 1 S. Bruk når brukeren ber om codex-uit-statsbudsjett-proeve eller en Codex-prøve av statsbudsjettet for UiT.
---

# UiTs statsbudsjett: rammetabell først, departementstreff deretter

Kjør de to trinnene nedenfor i rekkefølge. Prioritet 1 er å vise UiTs nye
ramme fra årets blå hefte så raskt som mulig. Bruk fastmode der kjøremiljøet
støtter det; ikke bruk tid på modellvalg eller modelltester. Ikke påstå at
fastmode er aktivert uten bekreftelse. Bruk skript til henting, uttrekk,
søk og summering. Vurder bare det som trengs for å lese kilden korrekt.

## Klargjør

1. Bruk prosjektet og budsjettåret fra bestillingen. Spør bare hvis året
   mangler og ikke kan utledes. Forslaget for år Y publiseres høsten Y−1.
2. Lag en ubrukt mappe `leveranser/codex-<år>-v<N>/` i prosjektet. Når brukeren
   ber om arkivering, flytt rester fra tidligere forsøk for året til en
   datert mappe under `arkiv/`; bevar relative stier og skriv hva som flyttes.
   Bevar originaldokumenter og arbeidsdeling. Ikke les prøveårets fasitmappe.
3. Bruk tilgjengelige verktøy direkte. Kontroller bare avhengigheter som
   neste operasjon trenger. Start kildehentingen uten å vente på oppsett av
   andre leveranser.

## Trinn 1 — ny ramme fra blått hefte, straks

1. Finn og last ned blått hefte for **det bestilte budsjettåret** fra
   regjeringen.no. Kontroller år og at dokumentet gjelder regjeringens
   opprinnelige forslag. Lagre PDF og kilde-URL. Hvis heftet ikke er
   publisert, oppgi det; ikke erstatt det med et annet år eller et vedtak.
2. Trekk ut UiT-raden i rammetabellen, kolonneoverskriftene, fotnotene og
   forklaringene til UiTs endringer. Les også tilhørende detaljtabeller når
   hovedtabellen viser til dem. Behold beløp, fortegn og enhet fra kilden.
3. Sett beregningen inn i denne tabellen. Bruk én rad per endringskomponent
   i årets hefte, med kildens egne betegnelser:

   | Komponent | Beløp i 1 000 kr | Forklaring / kilde og side |
   |---|---:|---|
   | Saldert budsjett Y−1, slik det står i årets hefte | | |
   | Endringskomponent fra heftet — én rad per komponent | | |
   | Forslag til ny ramme Y | | |
   | Kontroll: saldert + endringer − forslag | | |

4. Kontroller UiT-raden og kolonneoverskriftene mot PDF-bildet. Summer
   saldert og endringene; kontrollraden skal være 0. Vis eventuell rest
   uttrykkelig og merk tall som ikke er avklart. Ikke lag en endringspost
   for å få summen til å stemme. Detaljer som inngår i en hovedpost skal
   ikke telles en gang til.
5. **Vis tabellen i chatten med en gang**, med lenke til blått hefte og
   sidetall. Oppgi ny ramme og nominell endring i kroner og prosent fra
   saldert. Lagre samme svar som `hurtigsvar.md` og tabellen som CSV i
   kjøringsmappen. Excel kan lages med eksisterende rammeark-skript når
   inputformatet passer; det skal ikke forsinke tabellen.
6. Fortsett direkte til trinn 2. UiTs foreløpige fordeling, historikk,
   fagminner og departementsanalyse er ikke forutsetninger for rammetabellen.

## Trinn 2 — søkeordtreff fra departementenes Prop. 1 S

1. Les `arbeidsflyt/arbeidsdeling-<år>.json`, ellers nærmeste eksisterende
   arbeidsdeling. Bruk departementene og søkeordene der, inkludert UiTs
   navnevarianter. Bevar originalfilen.
2. Hent departementenes Prop. 1 S for Y−1–Y fra regjeringen.no og lag
   tekstuttrekk med PDF-sidetall. Hent og behandle uavhengige dokumenter
   parallelt når verktøyene tillater det. Registrer manglende dokumenter og
   fortsett med de tilgjengelige.
3. Søk mekanisk etter søkeordene. Trekk ut hele treffavsnittet med avsnittet
   før og etter. Ta med overskrift, kapittel/post og tabell eller fotnote
   når treffet trenger det. Behold beløp, mottaker og vilkår i utdraget.
4. Samle overlappende treff og merk hvilke søkeord som traff. Fjern bare
   åpenbare feiltreff. Merk omtale av tidligere år som historisk omtale;
   ikke presenter den som en ny bevilgning. Ikke skriv en selvstendig
   fagrapport for hvert treff.
5. Lagre `<departement>-treff.md` og maskinlesbare treff i kjøringsmappen.
   Hvert utdrag skal ha dokumenttittel, URL, PDF-side, søkeord og kildetekst.
   Avslutt med en oversikt over departement, dokument, antall treff og
   lenke til utdraget. Skill «ingen søkeordtreff» fra «dokument mangler».

## Verktøy og avgrensning

Bruk enkeltskriptene i [analyseskillens scripts](../uit-statsbudsjett-analyse/scripts/):
`fetch_sources.py`, `extract_documents.py`, `parse_blaatt_hefte_table.py`
og `extract_hits.py`. Les bare den relevante delen av
[skriptbeskrivelsen](../uit-statsbudsjett-analyse/references/scripts.md)
ved behov for argumenter og filformat. Hvis tabellparseren ikke støtter
årets oppsett, les UiT-tabellen direkte fra PDF-en og regn summen med kode.

Denne prosedyren er standard også ved «full prøve»: begge trinn skal
utføres. De eldre `codex-uit-ramme.js` og `codex-uit-departementer.js`
orkestrerer en større analyse og skal ikke startes som standard her.
Fagminnearbeid, avstemming mot foreløpig fordeling, uavhengige modellutkast,
redaktør, PowerPoint og meldingsutkast utføres bare når brukeren ber om det.
