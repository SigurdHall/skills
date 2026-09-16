# Kildekart for blått hefte

Kartlagt 2026-09-16. Gjelder Kunnskapsdepartementets orientering om statsbudsjettet for
universitet og høgskular, i UiT kalt «blått hefte». Filen er en referanse for kode og
mennesker; `finn_blaatt_hefte.py` leser ikke denne filen, men følger den.

## Dokumentnavn

| Målform | Forslag | Etter vedtak |
|---|---|---|
| Nynorsk (brukt fra og med 2016) | Orientering om forslag til statsbudsjettet `Y` for universitet og høgskular | Orientering om statsbudsjettet `Y` for universitet og høgskular etter vedtak i Stortinget `dato` |
| Bokmål (2014–2015) | Orientering om forslag til statsbudsjettet `Y` for universiteter og høyskoler | Orientering om statsbudsjettet `Y` for universiteter og høyskoler |

Heftets egen undertittel er «Førebels tildelingsbrev». Både `hogskular`, `hogskolar` og
`hoyskoler` forekommer i filnavn. Kode skal derfor aldri kreve én bestemt skrivemåte.

## Faste adresser

- **Base:** `https://www.regjeringen.no/contentassets/31af8e2c3a224ac2829e48cc91d89083/`
  Alle utgaver 2015–2026 ligger under denne ene GUID-en. Den brukes som hint i
  filnavnproben (A2), men er **ikke** låst i koden: A1 tar URL-en fra lenken, uansett GUID.
- **Temaside (eneste komplette vei):**
  `https://www.regjeringen.no/no/tema/utdanning/hoyere-utdanning/orientering-om-forslag-til-statsbudsjett-for-universiteter-og-hoyskoler/id619675/`
  Lister 25 PDF-lenker for budsjettårene 2014–2026, nyeste først.

## `--year` er alltid budsjettår

`--year 2026` betyr heftet for budsjettåret 2026, uansett at forslaget ble publisert i
oktober 2025 og vedtaksutgaven i desember 2025. Årsutledningen tar derfor det **høyeste**
årstallet i lenketeksten, fordi vedtakstekstene nevner både budsjettåret og vedtaksdatoen
(«… 2026 … etter vedtak i Stortinget 18. desember 2025»).

## Publiseringskalender og sjekkfrekvens

| Utgave | Publiseres | Observert |
|---|---|---|
| Forslag for `Y` | En torsdag i første halvdel av oktober `Y−1`, samme dag som Prop. 1 S | 2023-forslaget 2022-09-28, 2024-forslaget 2023-10-06 (korrigert 2023-10-10) |
| Etter vedtak for `Y` | Etter stortingsvedtaket i desember `Y−1` | 2024: 18.12.2023, 2025: 18.12.2024, 2026: 18.12.2025, 2023: 14.12.2022, 2022: 20.12.2021 |

Sjekkfrekvens: A1 ukentlig fra 1. oktober; A1 + A2 daglig 10.–20. oktober og
15. desember–20. januar.

## Veiene inn

### A1 — temasiden (primær, avgjør alene)

GET på temasiden, to forsøk (timeout 8 s, deretter 12 s). HTML-en tolkes med
`html.parser`, ikke regex: alle `<a href=…pdf>` samles, og lenketeksten er **all** tekst i
elementet, inkludert nøstede tagger. For hver lenke utledes år (lenketekst først, høyeste
tall; deretter filnavn; ellers «år ukjent») og utgave («vedtak» i teksten og ikke «forslag»
→ vedtak; «forslag» → forslag; ellers «utgave ukjent»).

### A2 — filnavnprobe (bekrefter, avgjør aldri)

To HEAD-prober parallelt mot basen, timeout 5 s:

- forslag: `orientering-om-forslag-til-statsbudsjettet-<Y>-universitet-og-hogskular.pdf`
  og `orientering-om-forslag-til-statsbudsjettet-<Y>-for-universitet-og-hogskular.pdf`
- vedtak: `orientering-om-statsbudsjettet-<Y>-for-universitet-og-hogskular.pdf`
  og `orientering-om-statsbudsjettet-<Y>-universitet-og-hogskular.pdf`

Regnes som publisert bare ved status 200 **og** `Content-Type: application/pdf`. Proben
treffer bare 2024–2026 forslag og 2025 vedtak; alle andre utgaver har filnavn proben ikke
kan gjette. A2 alene gir aldri returkode 0, men gir 7.

### A3 — diff mot kjente utgaver

Alle PDF-lenker på temasiden sammenlignes med `references/kjente-utgaver.json`. Lenker som
ikke står der, og som har år ≥ det etterspurte året eller ukjent år, gir returkode 3 når
ingen kandidat ble funnet. Er ingen av de kjente lenkede utgavene gjenfunnet, er siden
bygget om: returkode 5.

### A4 — manuelt websøk (fallback, ikke i kjeden)

Ingen websøk kjøres i kjeden. Ved returkode 2, 4 eller 5 legger rapporten ved en ferdig
søkestreng som et menneske kan lime inn i en ekstern søkemotor (de indekserer PDF-ene, i
motsetning til regjeringen.nos eget søk):

```
site:regjeringen.no/contentassets orientering statsbudsjettet <Y> universitet hogskular
```

## Returkoder fra `finn_blaatt_hefte.py`

| Kode | Betydning |
|---|---|
| 0 | Funnet entydig (eller flertydig, løst i kode, med `merknad` satt) |
| 2 | Temasiden lest, ingen kandidat for året, og A2 svarte 404 → ikke publisert |
| 3 | Ukjent lenke med år ≥ `Y` eller ukjent år må vurderes |
| 4 | Nettfeil etter begge forsøk → si aldri «ikke publisert» |
| 5 | Strukturbrudd: temasiden svarte, men ingen kjent utgave ble gjenfunnet |
| 7 | A2 fant PDF (200 + `application/pdf`) uten lenke på temasiden |

Flertydighet er ikke en egen kode. Finnes to kandidater for samme år og utgave, velger
koden den med nyeste dato i lenketekst eller filnavn, ellers den som står sist på den
kronologiske siden. Begge rapporteres, og `merknad` settes, slik at orkestratoren gir 10.

## Forkastede veier (kontrollert 2026-09-16)

| Vei | Hvorfor forkastet |
|---|---|
| Statsbudsjettportalen `id1437` og årssidene under den | Lenker ikke til blått hefte |
| Dokumentsøket `id2000006` | Lenker ikke til blått hefte |
| Nettstedssøket `id86008` | Regjeringen.nos eget søk indekserer ikke PDF-innhold |
| KDs pressemeldinger på budsjettdagen | Lenker til Prop. 1 S, ikke til heftet |
| RSS `/no/rss/Rss/2581966/` | Finnes, men bare `documentType` respekteres; heftet dukker ikke opp, og siden har ingen RSS-autodiscovery |
| DBH / HK-dir | Speiler ikke PDF-en |

## Avvik som styrer designet

- **D1 — filnavn følger ikke noe mønster.** 2023-forslaget heter
  `2022.09.28-forslag-til-orientering-2023-samlefil.pdf`, 2024-vedtaket
  `v3.-orientering-om-statsbudsjettet-2024-…`. Derfor er A1 primær og A2 bare bekreftende.
- **D2 — to filer for 2024-forslaget.** Avklart 2026-09-16, se eget avsnitt under.
- **D3 — portal og pressemelding lenker ikke** til heftet, bare til proposisjonene.
- **D4 — regjeringen.nos eget søk indekserer ikke PDF-ene.** Eksterne søkemotorer gjør det;
  derfor er A4 manuell.
- **D5 — ingen RSS-autodiscovery** på temasiden, og feeden som finnes filtrerer bort heftet.
- **D6 — én GUID siden 2015.** Praktisk, men behandlet som hint: en ny GUID skal ikke
  gjøre skillen blind, og A1 leser URL-en fra lenken.

## D2 avklart: hvilken 2024-forslagsfil gjelder?

| | A (gjeldende) | B (dublett) |
|---|---|---|
| Filnavn | `orientering-om-forslag-til-statsbudsjettet-2024-universitet-og-hogskular.pdf` | `orientering-om-forslag-til-statsbudsjettet-2024-for-universitet-og-hogskular.pdf` |
| Lenket fra temasiden | ja | nei |
| Byte | 1 350 258 | 1 157 108 |
| SHA-256 | `7394abe6ef36dc21…` | `0301c7eacf28e684…` |
| Sider | 44 | 44 |
| PDF-metadata | opprettet 2023-09-29, endret 2023-10-09 | opprettet 2023-09-29, endret 2023-10-02 |

Bare tre sider skiller filene (pdf-side 2, 13 og 14). A har et tillegg på forsiden:
«Tabellen i kap. 3.2 Universitets- og høgskulebygg … er korrigert (10. oktober)
samanlikna med versjonen publisert 6. oktober», og tallet for bygg der
Nærings- og fiskeridepartementet er oppdragsgivar er rettet fra 893 900 til 906 600.
De øvrige forskjellene er mellomrom og linjeskift.

**Konklusjon:** A er den korrigerte og gjeldende utgaven; B er førsteversjonen fra
6. oktober 2023. Korreksjonen gjelder KDDs byggtabell, ikke kap. 260 post 50, så
hovedtabellen og UiT-raden er identiske i de to filene (pdf-side 16 er byte-lik i
tekstuttrekket). Prosjektets tidligere lokale kopi
(`analyse/kilder/2024/blaatt-hefte-forslag-2024.pdf`) har hash `0301c7ea…` og er altså B,
den ulenkede førsteversjonen. Begge er lagret; A er merket `gjeldende: true` i
`kjente-utgaver.json`, B `gjeldende: false` med filnavnet
`blaatt-hefte-2024-forslag-ulenket.pdf`.

## Lokale kopier

Nedlastet 2026-09-16 til `uit-statsbudsjett/analyse/kilder/blaatt-hefte/<budsjettår>/`:
13 filer, alle utgaver 2021–2026 (forslag og vedtak) pluss 2024-dubletten. Hash, størrelse
og sidetall står i `kjente-utgaver.json`; per mappe ligger `kilder.json` med URL og
hentetidspunkt. De sju eldre kopiene i `analyse/kilder/{2021,2022,2023,2024,saldert-2024,2025}/`
er hashet i `analyse/kilder/blaatt-hefte/inventar-lokalt.json` og er byte-like med de
nedlastede, med det ene unntaket at 2024-forslaget der er B (se D2).

## Live-kontroller

| Dato | Kommando | Resultat | Tid |
|---|---|---|---|
| 2026-09-16 | `finn_blaatt_hefte.py --year 2027 --stage forslag` | returkode 2 (ikke publisert): A1 200 med 25 PDF-lenker, 12 av 12 lenkede kjente utgaver gjenfunnet, begge A2-prober 404, ingen ukjent lenke å vurdere | 0,57 s |
| 2026-09-16 | `finn_blaatt_hefte.py --year 2026 --stage alle` | returkode 0, begge utgaver funnet entydig | 0,28 s |

Begge ligger langt under finn-budsjettet på 25 sekunder.

## Tidsmåling av hele kjeden, 2026-09-16

`kjor_blaatt_hefte.py --year 2026 --stage forslag` med tom lokal cache, tre kjøringer fra WSL: vegg-til-vegg 0,94 / 0,85 / 0,85 s (finn 0,27–0,29 s, hent 0,25–0,34 s, les 0,11 s, bygg 0,03 s). Budsjettet er 120 s. `--year 2027` gir returkode 2 på 0,5 s.


## Revidert nasjonalbudsjett (RNB) og budsjettløpet, kartlagt 2026-09-16

Statsbudsjettet har tre tidspunkter for UiT på kap. 260 post 50: forslag (blått hefte, oktober året før), vedtatt (blått hefte etter vedtak i Stortinget, desember; tildelingsbrevet gjentar rammen som ett tall) og revidert (RNB, mai i budsjettåret). **UiTs RNB-tall står ikke i RNB-proposisjonen**, som bare har sektortall for post 50. De står i KDs **supplerende tildelingsbrev nr. 1 til statlige universiteter og høyskoler**, publisert på regjeringen.no ca. fem uker etter proposisjonen. Det finnes ingen RNB-utgave av blått hefte. Tallene vedlikeholdes i `rnb-tillegg.json` og bygges inn i `budsjettbase.json` med `bygg_base.py`.

| Budsjettår | RNB-proposisjon | Supplerende tildelingsbrev | UiT-endring (1 000 kr) |
|---|---|---|---|
| 2023 | Prop. 118 S (2022–2023), 11.05.2023 | ikke funnet på regjeringen.no; tallet 86 200 er fra UiTs egen arbeidsbok 2024 | +86 200 (ikke verifisert offentlig) |
| 2024 | [Prop. 104 S (2023–2024)](https://www.regjeringen.no/no/dokumenter/prop.-104-s-20232024/id3039096/), 14.05.2024, post 50 +29,1 mill. | [25.06.2024](https://www.regjeringen.no/contentassets/13ee8262d9d14e789db11fef841a3f29/supplerende-tildelingsbrev-revidert-nasjonalbudsjett-2024-kap.-260-post-50-statlige-universiteter-og-2383249.pdf) | +8 300 (Bardufoss 7 500, profesjonsnære 800) |
| 2025 | [Prop. 146 S (2024–2025)](https://www.regjeringen.no/no/dokumenter/prop.-146-s-20242025/id3100917/), 15.05.2025, post 50 −18,7 mill. | [02.07.2025](https://www.regjeringen.no/contentassets/13ee8262d9d14e789db11fef841a3f29/supplerende-tildelingsbrev-nr.1-til-statlige-universiteter-og-hoyskoler-tilleggsbevilgninger-og-omprioriteringer-statsbudsjettet2025.pdf) | −907 (egenbetalingskuttet omfordelt: −1 091 → −1 998) |
| 2026 | [Prop. 96 S (2025–2026)](https://www.regjeringen.no/no/dokumenter/prop.-96-s-20252026/id3159643/), 12.05.2026, post 50 +31,1 mill. | [25.06.2026](https://www.regjeringen.no/contentassets/35e08b38d60a46b9b1ef32ee999b853b/supplerende-tildelingsbrev-nr.-1-til-statlige-universiteter-og-hoyskoler-om-tilleggsbevilgninger-og-omprioriteringer-i-statsbuds.pdf) | +364 (NBP, flatt til alle unntatt Nord) |

Brevene ligger lokalt i `uit-statsbudsjett/analyse/kilder/rnb/<år>/` med sha256 i `rnb-tillegg.json`. Brevet for 2025 inneholder også tildelinger over kap. 226 og 275 som ikke gjelder post 50.

Navigasjonsveier for RNB (kontrollert 2026-09-16):

| # | Vei | Vurdering |
|---|---|---|
| R1 | KDs samleside for tildelingsbrev `https://www.regjeringen.no/no/dokument/dep/kd/Tildelingsbrev/id753324/` med lenker til årssidene og til de supplerende sektorbrevene. Regex: `href="(/contentassets/[0-9a-f]{32}/supplerende-tildelingsbrev[^"]*statlige-universiteter[^"]*\.pdf)"` | stabil, beste inngang |
| R2 | Nettstedssøk etter proposisjoner: `/no/sok/id86008/?documenttype=dokumenter%2Fproposisjoner&term=Tilleggsbevilgninger+og+omprioriteringer`. Regex: `href="(/no/dokumenter/prop\.-\d+-s-\d{8}/id\d+/)"` | stabil, følg 301 |
| R3 | RNB-undersiden per år `/no/statsbudsjett/<år>/rnb/id<7 siffer>/` (2024 id3033175, 2025 id3095290, 2026 id3155542) | halvstabil, id-en er ny hvert år |
| R4 | Proposisjonens dokumentside → PDF `prp<sesjon 8 siffer><propnr 4 siffer>000dddpdfs.pdf` | stabil struktur |
| R5 | contentassets-mappen for brevene (2024 og 2025 samme GUID, 2026 ny) | ustabil, aldri hardkod |
| R6 | Årssidene for tildelingsbrev `/no/dokumenter/tildelingsbrev-til-universiteter-og-hoyskoler-<år>/id…/` (2025 bryter mønsteret: `tildelingsbrev-2025/id3075320/`) | halvstabil |
| R7 | Stortingets Innst. S til RNB (447 S 2023–2024, 540 S 2024–2025, 450 S 2025–2026) | kryssjekk, ikke per institusjon |

Kalender: RNB-proposisjonen midten av mai, Stortingets vedtak medio juni, supplerende tildelingsbrev 25.06–02.07. Sjekk R1 fra 10. juni. Tildelingsbrevet for året (desember) gjentar vedtatt ramme som ett tall og viser til blått hefte for spesifikasjonen (2024: 4 061 059 000; 2025: 4 175 449 000; 2026: 4 281 564 000).
