# Kildekart for UiTs statsbudsjettanalyse

Les ved kildeinnhenting. Dette er en søkehjelp; departementsansvar,
kapittelnumre, ordninger og UiTs prioriteringer må kontrolleres for året.
Listen er ikke bevis for at et tiltak finnes eller får nye midler.

## Automatisk oppdagelse

`scripts/discover_sources.py check --year Y` finner kildene under uten
manuell leting og sier om årets forslag er publisert. Mønstrene det bruker,
kontrollert 14.09.2026:

| Kilde | Hvor skriptet ser | Mønster |
|---|---|---|
| Blått hefte, forslag | Fast mappe på regjeringen.no, deretter [KDs kronologiske side](https://www.regjeringen.no/no/tema/utdanning/hoyere-utdanning/orientering-om-forslag-til-statsbudsjett-for-universiteter-og-hoyskoler/id619675/) | `/contentassets/31af8e2c3a224ac2829e48cc91d89083/orientering-om-forslag-til-statsbudsjettet-Y-for-universitet-og-hogskular.pdf`; 2022–2024 avvek i filnavnet og fanges av sidesøket |
| Årets budsjettside | [Statsbudsjett-indeksen](https://www.regjeringen.no/no/statsbudsjett/id1437/) viser gjeldende år; eldre år via Stortingets side `statsbudsjettet-Y` | `/no/statsbudsjett/Y/id…/` og undersiden `dokumenter-og-pressemeldinger`, som lister hvert departements Prop. 1 S og Prop. 1 LS |
| Fagproposisjoner | Dokumentsidene `/no/dokumenter/prop.-1-s-(Y−1)Y/id…/`, også fra dokumentsøket med `term="Prop. 1 S (Y−1–Y)"` | `DC.Creator` gir departementet; PDF-lenken heter `prp(Y−1)Y0001<kode>dddpdfs.pdf` (`_kd`, `hod`, `kld`, `nfd`, `aid`, `kud`, `kdd`, `_jd`, `_ud`, `_ed`/`oed`, `ls0`) |
| UiTs foreløpige fordeling | Elements Cloud publikumsportal, universitetsstyret (utvalg 3), fra mai 2024. Eldre møter ligger i [UiTs gamle møteportal](https://uit.no/moteportalen/um/utvalg?utvalg=2) | API `publikum/api/PredefinedQuery/DmbMeetings?year=Y−1&dmbName=3`, `DmbHandlings/GetByMeetingId/{møte}`, `DmbHandlings/{sak}`; API-kall trenger headeren `Tenant: 970422528_PROD-970422528`. Dokumenter: `publikum/Documents/ShowDocument/{Database}/{RegistryEntryId}/{DocumentId}`, protokoll `Documents/ShowDmbHandlingDocument/{Database}/{sak}/Protokoll` |

Departementsnavn endres ved omorganisering (Energidepartementet fra 2024,
Digitaliserings- og forvaltningsdepartementet fra 2025). Skriptet melder
departementer det ikke kan plassere; legg dem til i `DEPARTMENT_PARTS`.
Publisering skjer normalt en torsdag i første halvdel av oktober; blått hefte
legges ut samme dag.

## Primærkilder

| Behov | Inngang og kontroll |
|---|---|
| UiTs forhåndsanslag | Universitetsstyrets junimøte året før budsjettåret: «Foreløpig fordeling av budsjett for Y» med saksframlegg, vedlegg og protokoll. Registrer saksnummer (S nn/åå), arkivsak, dato og om innstillingen ble endret ved vedtak. |
| Forslagets institusjonstall | Blått hefte, utgave «forslag» eller «etter vedtak» etter oppdraget; begge kan ligge i samme mappe. |
| KD og øvrige departementer | [Statsbudsjettet](https://www.regjeringen.no/no/statsbudsjett/): velg år, fagproposisjoner, dokumentets første side og PDF. |
| Rammetildeling | KD kap. 260 post 50 og vedlegg med institusjonsfordeling; blått hefte viser endringer og detaljer. Ikke forveksle kapittelets sektortotal med UiT-raden. |
| Kostnader og makro | Prop. 1 LS for skatter/avgifter; Nasjonalbudsjettet for makro. En KPI-prognose er ikke automatisk KDs lønns-/priskompensasjon. |
| Vedtak og oppdateringer | Stortingets budsjettinnstillinger/vedtak, tilleggsproposisjoner, tildelingsbrev og RNB. Bruk bare statusen som oppdraget omfatter. |

## Søk i departementene

| Område | Vanlige søkeord og saker |
|---|---|
| KD | UiT, Universitetet i Tromsø, Norges/Noregs arktiske universitet; deflator/prisjustering, resultatbasert uttelling, åpen/open og lukket/lukka ramme, ABE/avbyråkratisering, inndekning/omprioritering, studieavgift, studieplasser/studieplassar, rekrutteringsstillinger, utfasing, HK-dir, desentralisert/fleksibel utdanning, samisk/nordsamisk, leksikografi, NKFS, medisin, luftfart/Bardufoss, ny finansieringsmodell, studiepoengkategorier. |
| KDD/KMD og Statsbygg | Divvun, samisk språkteknologi, universitetsmuseum/Tromsø Museum, universitetsbygg og husleie, nordområder/distrikt. Sjekk forskjellen mellom byggebevilgning til Statsbygg og ramme til UiT. |
| HOD | Tromsøundersøkelsen, Senter for samisk helseforskning, Saminor, Nasjonalt senter for distriktsmedisin, allmennmedisinsk forskning, PraksisNett, RKBU Nord, RVTS Nord, dobbelkompetanse odontologi, helseprofesjoner og Helse Nord. |
| NFD | Senter for hav og Arktis, jordobservasjon/rombasert virksomhet, FF Helmer Hanssen, FF Kronprins Haakon, Havforskningsinstituttet, Nofima, marin/maritim forskning, FORNY/TTO, Grønn plattform. |
| KLD | COAT (og historisk KOAT), Framsenteret, Norsk Polarinstitutt, polarforskning/Svalbard, Arven etter Nansen, forskningsfartøy. |
| JD | Rettsgenetisk senter, rettsmedisin, beredskap, sikkerhet, nordområder. |
| AID/ASD | Trygderett, EØS, arbeidsliv, NAV, velferdsforskning; fleruniversitetstiltak kan ha felles ramme. |
| UD | Nordområder, Arktis, Barentssamarbeid, Russland, Ukraina, polar-/forskningssamarbeid. |
| ED/OED | Energiforskning, FME, PETROSENTER, petroleum, hydrogen, havvind. Ofte eksterne søknadsmuligheter fremfor navngitt UiT-tildeling. |
| KUD | Kunstutdanning, museum, kulturforskning, likestilling, rekrutteringspiloter og andre navngitte fagmiljøer. Skillet mellom universitetsmuseum og øvrige museer er avgjørende. |
| FIN | Ekstra arbeidsgiveravgift, innslagspunkt, sats, kompensasjon, andre dokumenterte arbeidsgiverkostnader. |

Utvid søket fra årets foreløpige fordeling og satsingsinnspill. Historiske
skrivefeil og navnevarianter kan være nyttige søkealiaser, men skal ikke
videreføres som offisielle navn i leveransen.

## Funnregistrering

For hvert vesentlig funn, behold:

- budsjettår, dokumentdato og status; kilde-URL og lokal fil;
- departement, kapittel/post, trykt side og PDF-side;
- mottaker, ordning/prosjekt, beløp og enhet;
- nivå eller endring, sammenligningsgrunnlag og eventuell prisbasis;
- varighet og vilkår, UiTs relevans og konkret oppfølging;
- kilde til UiTs forhåndsanslag og status for sammenlignbarhet.

Dokumenter også forventede satsinger som ikke er funnet i de undersøkte
kildene. Et fravær i navnesøk alene beviser ikke avslag eller nullbevilgning.
