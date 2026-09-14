# Modellvalg, fan-out og målt responstid

Bruk dette når oppgavene fordeles mellom modeller eller når modellenes
hastighet/kvalitet skal prøves. En testet rolle-/promptkombinasjon er mer
informativ enn en generell rangering av modellnavn.

## Uavhengige svar før sammenstilling

Bruk stabile fagroller og deres lagrede historiske minne. For kritiske
oppgaver kan Luna og Sol løse samme oppgave uavhengig. Begge skal lagre sin
første vurdering før de får den andres svar. La deretter kontrollen se
begge faktiske utkast og de samme primærkildene.

Et review som har lest Luna, er ikke en ekstra uavhengig stemme. Kontroller
uenigheter i tolkning og forbehold også når hovedtallene er like. Nye
påstander om kildekonflikt krever kontroll av år, enhet, prisbasis og
periodisering. En timer eller enighet mellom avhengige svar avgjør ikke
faglig riktighet.

Kontroller dekning mot fagrollens historiske temaliste, også når begge
utkast er enige. To svar kan ha samme utelatelse. Reviewet skal bevare
kritiske vilkår fra begge svarene og begrunne strykninger med kildebelegg.
Skill feil i påstander fra manglende temaer eller nødvendige vilkår.
Riktige hovedbeløp er ikke alene tilstrekkelig.

Modellnavn, reasoning effort og tjenestenivå er separate innstillinger.
Ved testing av brukerens profiler, bruk eksakte identifikatorer, eksempelvis
`gpt-5.6-luna`/`max` og `gpt-5.6-sol`/`high`. Ikke erstatt en utilgjengelig
modell stille. Bruk priority/fast når det er ønsket og støttet, og registrer
både forespurt og faktisk observert tjenestenivå.

## Førsteutkast og femminutterskontroll

Skill mellom:

1. Umiddelbar mottakskvittering uten faglige påstander.
2. Første kildebaserte, foreløpige vurdering.
3. Ferdig prioritert førsteutkast.
4. Kontrollert utkast, med eventuelle uavklarte punkter.
5. Fullstendig departementsrapport, vedlegg og formidlingspakke.

Førsteutkastet skal konsentrere seg om beslutningsrelevante punkter uten
redundante talloppstillinger. Dette avgrenser arbeidsfasen; nødvendig
kontroll skal ikke kuttes for å spare tokens. Full kildegjennomgang og
produksjon av alle artefakter kan fortsette etter den første leveransen.

Reserver kapasitet til review. Ikke fyll alle plasser med nye analyser
når målet er rask kvalitetssikring. Mål ventetid på det andre uavhengige
svaret og i køen. Fem minutter fra Luna-utkastet er et annet mål enn fem
minutter fra første foreløpige melding eller fra brukerens bestilling.
Rapporter alle relevante tidspunkter; ikke flytt startpunktet for å få
målet til å se oppnådd ut.

Hvis femminuttersfristen passeres, lever status for hva som er kontrollert
og hva som står igjen. Ikke kall et ufullstendig review godkjent. Fullfør
den nødvendige kontrollen eller eskaler konkrete uenigheter til en
uavhengig kildekontroll.

## Repeterbar test

Lås oppgaver, input, minneversjon, kontrollpunkter og måledefinisjoner før
kjøring. Bruk samme input per sammenlignet konfigurasjon. Hold eksisterende
analysesvar og fasit utenfor førstegangssvarenes input. Et review får
ekte kandidatoutput, aldri en oppdiktet «Luna-besvarelse».

`benchmark_models.py` kjører CLI-jobber, logger observerens klokke,
hendelser, tokenbruk, feil og avhengigheter. `repeat` er antall kjøringer
av en jobb. Ved eksplisitte r1/r2-jobber brukes `repeat: 1` på hver.

```json
{
  "max_active_generations": 2,
  "jobs": [
    {"id":"luna", "case_id":"ramme", "inputs_dir":"case/input", "prompt_file":"case/prompt.txt", "schema_file":"schema.json", "model":"gpt-5.6-luna", "effort":"max", "service_tier":"priority", "repeat":1},
    {"id":"sol", "case_id":"ramme", "inputs_dir":"case/input", "prompt_file":"case/prompt.txt", "schema_file":"schema.json", "model":"gpt-5.6-sol", "effort":"high", "service_tier":"priority", "repeat":1},
    {"id":"review", "case_id":"ramme", "inputs_dir":"case/input", "prompt_file":"case/review.txt", "schema_file":"schema.json", "model":"gpt-5.6-sol", "effort":"high", "service_tier":"priority", "repeat":1, "review_of":"luna", "compare_with":"sol"}
  ]
}
```

```bash
python scripts/benchmark_models.py suite.json --output resultater --parallel 3
python scripts/analyze_model_timings.py resultater --output tidsanalyse.json
python scripts/score_model_answers.py resultater/jobs/luna/answer.txt --gold gold.json --case ramme --output tallkontroll.json
```

Utdata ligger under `resultater/jobs/<id>/`: kopiert input, prompt,
råhendelser, tidsstemplede hendelser, stderr, svar og metrics.
`compare_with` gjør at review venter på og får begge uavhengige svar.
Uten feltet testes sekvensiell kontroll av ett utkast.

Bruk `build_search_index.py` til en mekanisk sideindeks fra avtalte
søkeord når dette forbedrer tiden til relevante kilder. Fullstendige
originaler skal fortsatt være tilgjengelige. Indeksen er ikke en fasit,
relevansvurdering eller bevis på at et søk er uttømmende.

## Måle- og evalueringsgrenser

- CLI kan pakke også commentary inn i JSON-summary. Timing må lese dette
  formatet og vanlig tekst. Rålogger skal bevares ved parserkorreksjoner.
- Meldingshendelser er ikke nødvendigvis første token. Ikke rapporter
  TTFT eller ren inferenshastighet uten faktisk grunnlag.
- Prosessnedstenging er ikke det samme som tidspunktet da svaret var klart.
- Priority/fast i kommandoen beviser ikke backendens nivå. Bruk bare en
  faktisk providerkvittering, aldri en verdi fra modelltekst eller tool-data.
- Kontroller tall maskinelt, men vurder kildebelegg, vilkår, mottaker og
  misvisende forbehold faglig. Lik sum kan skjule feil forståelse.
- Rapporter cachebruk, oppgavestørrelse, kø, feil, stoppede jobber og antall
  repetisjoner. En adaptiv endring er en ny kohort; ikke bland resultatene.
- Godkjenningsavvisninger må følges. Offentlig avgrensede eller syntetiske
  testdata kan være et tryggere alternativ, men må ikke fremstilles som
  testing av hele det interne fagminnet.

Lagre observerte modellstyrker og feil i fagrollens erfaringer med dato,
modell/effort/tier, oppgavetype og kilde til testresultatet. Ikke gjør én
pilot til en universell sannhet om modellen eller et garantert tidsløfte.

## Gjenbruk, effort og ferdigstilling

Gjenbruk lagrede målinger før nye tester startes. Ved sammenligning av
high, xhigh og max skal input, prompt, arbeidsfase og kvalitetskrav holdes
like. Velg lavere effort bare for oppgaver der kravene fortsatt er oppfylt.
Raske hovedtall kan skjule mangelfulle periodeforklaringer eller temadekning.

`analyze_model_timings.py --table tider.md` lager lesbare tabeller med
tidspunkt, ventetid og rapportert tokenbruk. Ta med tiden fra første utkast
i paret selv om dette kom fra Sol. `prepare_blind_review.py` lager anonyme,
uendrede kandidatsvar med samme godkjente kilder og kontrollsett. Lagre
koblingsnøkkelen utenfor vurdererens mappe; hold modellnavn og tider skjult
til vurderingen er lagret. Gjenbruk ferdige vurderinger ved identisk svarhash.

Suite-input må ligge innenfor suite-mappen; kopier identiske kilder dit
før kjøring, og registrer hash. Lokal svarvalidering kontrollerer JSON-
objekt og teknisk fullføring, ikke full skjemavalidering eller faglig kvalitet.
Timeout etterfølges av avgrenset opprydding av jobbens egen POSIX-prosessgruppe.

Når brukeren ber om ferdigstilling eller oppgir knapp usage, avslutt
testutvidelser. Fullfør nødvendige pågående kontroller, merk antakelser og
lever observerte resultater og en foreløpig anbefaling der grunnlaget er
begrenset. Ikke bruk flere modellrunder for å bekrefte uendrede resultater.
