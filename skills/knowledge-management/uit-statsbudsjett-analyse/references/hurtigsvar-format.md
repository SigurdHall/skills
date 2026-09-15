# Hurtigsvar: fast format for budsjettdagen

Det første som skal svares på når statsbudsjettet legges fram, er hvor mye
penger UiT har fått i blått hefte. Leveransen er Excel-arbeidsboken
`leveranser/<kjøring>/uit-ramme-<år>.xlsx`, bygd av
`scripts/build_frame_workbook.py` fra tallene `scripts/parse_blaatt_hefte_table.py`
leser ut av hovedtabellen, med kolonnene tolket og kontrollert visuelt mot
PDF-siden. `hurtigsvar.md` ved siden av forklarer arket i chatten. Begge
skal finnes innen få minutter etter at blått hefte er publisert; avviket mot
UiTs foreløpige fordeling legges til i neste fase.

## Arbeidsboken

Samme ark hvert år, etter UiTs arbeidsbøker fra 2018 og 2019:

| Ark | Innhold | Formler |
|---|---|---|
| `Sektor` | Alle institusjoner i hovedtabellen: saldert året før, forslag, nominell endring i prosent; sumrad. UiT-raden er uthevet. | `(forslag−saldert)/saldert`, `SUM` |
| `UiT-bro` | «Budsjettforslag <år> for UiT inkl. justeringer»: saldert året før, én rad per kolonne i blått heftes UiT-rad (pris med sats i merknaden, studieplasser, resultat, kutt, flyttinger, andre endringer), forslag som sum, kontroll mot tabellens forslag (skal være 0), og kontroll mot vedtatt budsjett året før fra blått hefte etter vedtak i Stortinget (skal være 0). | `SUM`, to kontrollceller |
| `Mot foreløpig` | UiTs foreløpige fordeling mot forslaget per harmonisert komponent, avvik, kilde på begge sider, avvik på totalrammen. Lages i fasen Avvik. | `forslag−UiT`, `SUM` |
| `Kilder` | Dokument, stadium, URL, SHA-256, PDF-side, hentetid, kolonnetolkning med overskriftstekst, kontroller. | |

Beløp i 1 000 kroner. Kolonnetolkningen er en faglig beslutning: skriptet
gir tallene i rekkefølge, agenten gir hver kolonne etikett fra overskriften
på PDF-siden og bekrefter UiT-raden siffer for siffer mot bildet av siden.

## `hurtigsvar.md`

Bruk overskriftene under i denne rekkefølge. Ukjent skrives som ukjent,
aldri som null.

### 1. Hovedtall

| | Beløp | Kilde |
|---|---:|---|
| Regjeringens forslag, KD kap. 260 post 50 til UiT | | blått hefte, UiT-raden, PDF-side |
| Saldert <år−1> | | samme rad |
| Vedtatt <år−1> ifølge blått hefte etter vedtak i Stortinget, og differanse mot saldert i tabellen | | `analyse/saldert-<år−1>.json` |
| Prisjustering: sats og beløp, hva kolonnen inneholder | | blått hefte, PDF-side |
| Endring i kroner og prosent | | `Sektor`-arket |
| Sektorens nominelle endring | | `Sektor`-arket, sumraden |
| UiTs foreløpige fordeling (styresak, dato) | | fylles i fasen Avvik |
| Avvik mot foreløpig | | `Mot foreløpig`, fylles i fasen Avvik |

Én setning om retningen, og hvor mye av økningen som er prisgrunnlag,
finansieringsflytting og målrettede tiltak, ikke fritt handlingsrom.

### 2. UiT-broen

Én rad per kolonne i UiT-raden: etikett fra overskriften, beløp, kort
forklaring fra blått heftes tekst der den finnes, PDF-side. Kontrollcellen
fra arket gjengis: sum av justeringer minus tabellens forslag = 0.

### 3. Fem punkter å følge opp i dag

Fra blått hefte og KD Prop. 1 S, i prioritert rekkefølge, hvert med beløp,
mottaker, vilkår og PDF-side. Typiske kandidater: prissats og videreført
kompensasjon, nye eller utfasede studieplasser, resultatregler og
overgangsordninger, kutt og inndekning, HK-dir- eller andre
finansieringsflyttinger, navngitte UiT-tiltak, endringer i
finansieringsmodellen fra neste år.

### 4. Komponenter mot foreløpig fordeling

Fylles i fasen Avvik fra `rammebro-kontroll.json`: tema,
UiT-forutsetning, forslag, avvik, kilde på begge sider. Rest i hver bro skal
være 0; ellers står resten som egen rad merket «uforklart».

### 5. Ikke kontrollert ennå

Fagproposisjonene (HOD, KUD, NFD, KDD, JD, UD, ED, AID, KLD, FIN),
samordning på tvers av departementer, PowerPoint. Forventet tidspunkt for
den fulle leveransen.

### 6. Kilder og status

Dokumentdato og stadium for blått hefte og KD, tidspunkt for
publiseringssjekken, UiTs styresak med saksnummer, forbudte mapper som ikke
er åpnet, modell og effort for hurtigsvaret og avviket.
