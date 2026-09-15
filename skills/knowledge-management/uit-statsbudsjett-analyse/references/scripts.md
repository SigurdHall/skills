# Skriptressurser

Bruk skriptene for deterministiske deler av analysen. Kildevalg,
dokumentstatus, mottaker, vesentlighet og sammenlignbare budsjettlinjer må
fortsatt vurderes faglig. Kjør uavhengige dokumentuttrekk parallelt når det
forkorter arbeidet; unngå at flere prosesser skriver til samme resultatfil.

Kommandoene nedenfor kjøres fra skillmappen. Python 3 brukes til skriptene.
Kildehenting trenger `curl`; PDF-uttrekk trenger `pymupdf`. Office-uttrekk
og tallavstemming bruker standardbiblioteket. Finn et eksisterende egnet
Python-miljø før du installerer noe. Ikke lagre årsspesifikke dokumenter i
skillmappen.

## Forbered oppdrag og kontroller full leveranse

```bash
python scripts/manage_workflow.py prepare /path/to/arbeidsdeling.json --project /path/to/prosjekt
python scripts/manage_workflow.py check /path/to/arbeidsdeling.json --project /path/to/prosjekt --output /path/to/kontroll.json
```

Planformatet er dokumentert i [agentarbeidsflyten](agent-workflow.md).
`prepare` lager varige oppdrag og delmapper, men fyller ikke inn fagminne.
`check` krever historisk minne, innlesingshash, årets erfaringer,
notater/rapporter/funn, samsvarende markerte utdrag og redaktørleveransene.
Returkode 2 betyr ufullstendig leveranse. Filkontrollen erstatter ikke
faglig lesing eller visuell kontroll.

## Kontroller tom tilstand før ny kjøring

```bash
python scripts/check_clean_state.py --project /path/to/prosjekt --year 2027 --run-id 2027-claude-v1
python scripts/check_clean_state.py --project /path/to/prosjekt --year 2027 --run-id 2027-claude-v1 --archive
```

Hver kjøring starter fra tom tilstand. Skriptet lister rester fra tidligere
forsøk for samme år (leveransemappen, hentede kilder, UiTs
forutsetningsnotat, rammebro-filer, årets erfaringsnotater) og gir
returkode 3. Med `--archive` flyttes de til `arkiv/avbrutt/<tidsstempel>-<kjøring>/`
med samme relative sti. `--keep-assumptions` lar forberedte UiT-forutsetninger
(notat, kilder, rammebro-input) stå. Fasitmappen `<år>/`, arbeidsdelingen og de
historiske minnene røres aldri.

## Finn årets kilder og sjekk publisering

```bash
python scripts/discover_sources.py check --year 2027 --output /path/to/kildesjekk.json
python scripts/discover_sources.py write --from /path/to/kildesjekk.json --output /path/to/kilder-input.json --uit-output /path/to/uit-kilder-input.json
```

`check` slår opp blått hefte, årets dokumentside og dokumentsøk på
regjeringen.no, hver fagproposisjons PDF, Prop. 1 LS og UiTs styresak
«Foreløpig fordeling av budsjett for Y» i Elements-portalen. Returkode 0
betyr alt funnet, 2 ikke publisert (blått hefte eller KD mangler), 3
delvis. `write` lager input til `fetch_sources.py`; UiT-dokumentene går
til en egen fil fordi de hører til `analyse/kilder/uit-forutsetninger-Y/`.
Bare standardbiblioteket brukes. Mønstrene står i [kildekartet](kildekart.md).

## Hent allerede identifiserte kilder

```bash
python scripts/fetch_sources.py /path/to/kilder-input.json /path/to/kilder
```

Input er en JSON-liste med disse fem feltene per kilde:

```json
[
  {
    "id": "kd-forslag-2024",
    "url": "https://www.regjeringen.no/contentassets/e506b368e0ff4721b7a335b35acd872b/nn-no/pdfs/prp202320240001_kddddpdfs.pdf",
    "budget_year": 2024,
    "stage": "regjeringens opprinnelige forslag",
    "title": "KD Prop. 1 S (2023–2024)"
  }
]
```

Skriptet laster ned PDF-er med kilde-ID som filnavn og lager `sources.json`
med URL, faktisk URL, hentetid i UTC, filstørrelse og SHA-256. Identisk
gjentakelse bevarer første registrering. Avvikende eksisterende innhold
eller metadata stoppes; velg en egen mappe for en annen dokumentversjon.
Bare PDF-signatur og filidentitet kontrolleres automatisk. Feltet
`classification_verified: false` betyr at oppgitt år/status fortsatt må
verifiseres mot dokumentets innhold.

## Trekk ut dokumentinnhold

```bash
python scripts/extract_documents.py /path/to/framlegg.pdf /path/to/presentasjon.pptx --output /path/to/uttrekk.txt
```

Støtter PDF, DOCX, PPTX og XLSX. Beholder PDF-side, lysark i presentasjonens
rekkefølge, lysarknotater, tabellceller og innebygde regneark med ark-/celle-
referanser, samt Word-topptekster og -bunntekster med XML-plassering.
Regnearkuttrekket viser formel og lagret verdi uten omberegning;
manglende lagret verdi må ikke behandles som null. Skjulte ark og
regnearkområder utenfor vist diagram kan inneholde arbeidsgrunnlag, ikke
vedtatte tall.

Bilder og skannede sider krever visuell kontroll/OCR. Eldre OLE-objekter
(`.bin`) og fot-/sluttnoter merkes som ulest. Kontroller også diagrammer
uten lesbar arbeidsbok manuelt; skriptet tolker ikke diagrammets tallcache.
Uttrekket erstatter
ikke originalen, og PDF-side er ikke nødvendigvis trykt sidetall. Les
kolonner og tabelloverskrifter visuelt før vesentlige beløp brukes.

## Kontroller rammebroen

```bash
python scripts/reconcile_budget.py /path/to/rammebro-input.json --output /path/to/rammebro-kontroll.json
```

Input er en manuelt kildeverifisert og faglig harmonisert bro:

```json
{
  "unit": "NOK_thousand",
  "opening": "1000.5",
  "expected_total": "1010.5",
  "proposed_total": "1015.5",
  "expected_source": "UiT: dokument og side",
  "proposed_source": "Statsbudsjett: dokument og side",
  "rows": [
    {"id": "pris", "expected": "30", "proposed": "40"},
    {"id": "kutt", "expected": "-20", "proposed": "-25"}
  ]
}
```

Beløp er heltall eller tekst med punktum som desimaltegn, uten
tusenskilletegn. `unit` er `NOK` eller `NOK_thousand`. `null` betyr ukjent.
Legg gjerne forklaring, label og kilde per rad; ekstra felt beholdes i
kontrollresultatet. Ikke legg inn en beregnet rest som om den var et
kildebelagt tiltak.

Skriptet gir avvik per komponent, forskjell mellom totalene, rest i hver
rammebro og rest i avviksbroen. Returkode 0 betyr eksakt avstemt;
returkode 2 betyr avvik eller ufullstendige beløp. Det godtar ikke dupliserte
komponent-ID-er, flyttall eller uendelige beløp. Avstemming beviser
aritmetikk, ikke at to linjer betyr det samme eller er disponibel økonomi.

## Lag markerte PDF-sider og samlet kildepakke

```bash
python scripts/build_evidence.py /path/to/del/funn.json --project /path/to/prosjekt --output /path/to/del/belegg
python scripts/assemble_evidence.py /path/to/arbeidsdeling.json --project /path/to/prosjekt --output /path/to/kildepakke.pdf
```

Funnformatet står i [agentarbeidsflyten](agent-workflow.md). Kildestier er
relative til prosjektet. Sidevalg og tekstankre er faglige beslutninger;
skriptet søker ikke selv etter mulige tema.

`build_evidence` bevarer hele kildesiden og markerer valgte tekstankre.
Det lager PDF, PNG, tekstuttrekk og JSON med kildehash og sidehenvisning.
Manglende eller tvetydige ankere stopper publiseringen. Flere tettliggende
tekstspenn på samme linje kan være én forekomst; andre flertreff krever et
mer presist anker. Ikke velg tilfeldig første treff. Eksisterende ferdige
kildepakker overskrives ikke; bruk ny mappe ved revisjon.

`assemble_evidence` samler delene i arbeidsdelingens rekkefølge, bevarer
markeringene og lager bokmerker og sideindeks. Samlingen summerer ikke
beløp eller fjerner ulike belegg for samme finansieringsflytting.

## Bygg og kontroller PowerPoint

Les UiT-deck-generatorens profil- og spec-veiledning først.

```bash
python scripts/build_presentation.py /path/to/presentasjon.json --template /path/to/uit-mal.pptx --output /path/to/statsbudsjettet.pptx --libreoffice /path/to/soffice
```

Krever `python-pptx`; rendering trenger LibreOffice, `pymupdf`, Pillow og
de faktiske temafontene, blant annet Open Sans. Wrapperen gjenbruker
UiT-deck-generatoren i samme skill-repo, tømmer gamle lysark med relasjoner,
bevarer mastere og legger `notes` og `sources` fra hvert spec-lysark i
PowerPoint-notatene.

Bullets får separate tittel-/undertittel-/tekstområder og 24-punkts
brødtekst. Lange lysark må likevel redigeres og rendres på nytt.
`--libreoffice` eksporterer den faktiske PPTX-filen til `preview/` med
PDF, sidebilder og oversiktsbilde. Skriptet kontrollerer sideantallet;
tekst, fontmapping, overlapp og kilder kontrolleres visuelt.

Manglende fonter kan gi feil tegnavstand selv når filen åpner. Ved
IPC-/prosessfeil i en kommandosandkasse, skill denne begrensningen fra
brukerens container og følg miljøets godkjenningsmekanisme for lokal rendering.
Ikke lever en ukontrollert forhåndsvisning som visuelt kontrollert.

## Modelltesting og blind kvalitetskontroll

Les [modelltestingen](model-testing.md) for oppgaver, profiler, avhengigheter
og målegrenser. Disse ressursene bruker standardbiblioteket; sideindeksen
trenger `pymupdf`. Kjøreren bruker den installerte `codex`-klienten.

```bash
python scripts/build_search_index.py --help
python scripts/benchmark_models.py suite.json --output resultater --parallel 3
python scripts/analyze_model_timings.py resultater --output tider.json --table tider.md
python scripts/score_model_answers.py resultater/jobs/kandidat/answer.txt --gold gold.json --case ramme --output tallkontroll.json
python scripts/prepare_blind_review.py resultater --case ramme --inputs case/input --gold gold.json --output blind/ramme --mapping kontroll/ramme-kobling.json
```

Sideindeksen finner mekaniske treff, ikke faglig relevans. Tallkontrollen
gir eksakte treff og kandidater til faglig vurdering. Blindpakken bevarer
svarbytes, kopierer kildene og holder modellmetadata utenfor vurderingsmappen.
Lag en ny mappe ved revisjon. Rålogger og tidligere dommer skal bevares.

## Verifiser etter endring

Kjør fra `skills`-repoet:

```bash
python -m pytest tests/test_statsbudsjett_*.py -q
```

Kontroller deretter endret skript på ett aktuelt dokument eller en faktisk
rammebro. Bruk syntetiske dokumenter i tester; ikke kopier interne
arbeidsdokumenter inn i det åpne skill-repoet.
