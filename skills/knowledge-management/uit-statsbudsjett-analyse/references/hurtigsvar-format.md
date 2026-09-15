# Hurtigsvar: fast format for budsjettdagen

`leveranser/<kjøring>/hurtigsvar.md` skrives av fasen Hurtigsvar, normalt
innen ti minutter etter at blått hefte er publisert, og gjengis i chatten
før departementsgjennomgangen starter. Bruk overskriftene under i denne
rekkefølgen. Alle beløp i 1 000 kroner med kilde og PDF-side. Ukjent
skrives som ukjent, aldri som null.

## 1. Hovedtall

| | Beløp | Kilde |
|---|---:|---|
| Regjeringens forslag, KD kap. 260 post 50 til UiT | | blått hefte, UiT-raden, PDF-side |
| UiTs foreløpige fordeling (styresak, dato) | | `analyse/uit-forutsetninger-<år>.md` |
| Avvik | | `rammebro-kontroll.json`, status |
| Saldert <år−1> | | blått hefte |

Én setning om retningen: høyere eller lavere enn UiT la til grunn, og hvor
mye av avviket som er prisgrunnlag, finansieringsflytting og målrettede
tiltak (ikke fritt handlingsrom).

## 2. Komponenter

Broen fra `rammebro-kontroll.json`, én rad per sammenlignbar komponent:
tema, UiT-forutsetning, forslag, avvik, kilde på begge sider. Rest i hver
bro skal være 0; er den ikke det, står resten som egen rad med forklaring
«uforklart».

## 3. Fem punkter å følge opp i dag

Fra blått hefte og KD Prop. 1 S, i prioritert rekkefølge. Hvert punkt har
beløp, mottaker, vilkår og PDF-side. Typiske kandidater: prissats og
videreført kompensasjon, nye eller utfasede studieplasser, resultatregler
og overgangsordninger, kutt og inndekning, HK-dir- eller andre
finansieringsflyttinger, navngitte UiT-tiltak, endringer i
finansieringsmodellen som gjelder fra neste år.

## 4. Ikke kontrollert ennå

Hva som gjenstår: fagproposisjonene (HOD, KUD, NFD, KDD, JD, UD, ED, AID,
KLD, FIN), samordning på tvers av departementer, PowerPoint. Oppgi
forventet tidspunkt for den fulle leveransen.

## 5. Kilder og status

Dokumentdato og stadium for blått hefte og KD, tidspunkt for
publiseringssjekken, UiTs styresak med saksnummer, og hvilke forbudte
mapper som ikke er åpnet. Modell og effort for hurtigsvaret.
