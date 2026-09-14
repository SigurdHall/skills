---
name: uit-statsbudsjett-analyse
description: Gjennomfør UiTs statsbudsjettanalyse fra arbeidsdeling og søkeord til fagagenter med varig erfaringsminne, markerte kildeutdrag, delrapporter, avstemming mot foreløpig budsjett, PowerPoint og melding for videreformidling. Bruk for blått hefte, KD kap. 260 post 50, departementsgjennomgang og historisk prøving mot fasit. Ikke generell strategivurdering eller redigering av budsjettmodeller.
---

# UiT og statsbudsjettet

Finn hva budsjettforslaget betyr for UiT, hvilke forhåndsforutsetninger som
holder, og hva som må oppdateres i budsjettfordelingen. Lever en etterprøvbar
rammeavstemming, fagrapporter, markerte kilder og ferdig formidlingspakke.
Hent offentlige kilder selv. En samlet analyse alene fullfører ikke dette
arbeidsløpet når brukeren ber om å gjenskape hele prosessen.

Prioritet 1 er korrekt informasjon; prioritet 2 er en ferdig fremstilt
analyse raskest mulig. Bruk og vedlikehold skriptressursene for repeterbar
innhenting, uttrekk og regnekontroll. Bruk faglig skjønn til kildevalg,
relevans og harmonisering av beløp; ikke overlat dette til nøkkelord alene.

## Arbeidsdeling og varig læring

Les [agentarbeidsflyten](references/agent-workflow.md) før delegering.

1. Finn årets eller nærmeste historiske dokument «Arbeidsdeling og søkeord».
   Bevar fagområdene og prioriteringene. Bruk stabile fagroller som kan eie
   flere departementer; dokumenter endret gruppering og nye områder. Hold
   personnavn og interne lenker i prosjektet, ikke i åpne skillressurser.
2. **Hver fagagent skal ha sitt eget lagrede erfaringsminne fra tidligere
   år, med faktiske kilder, før årets analyse.** Les originalnotater,
   presentasjoner, PDF-er og innfelte skjermbilder for eget fagområde.
   Generell felles historikk eller agentens muntlige sluttmelding er ikke
   erstatning. Rekonstruert historikk skal merkes som rekonstruert nå.
3. Lagre årsvise erfaringer og et kort faglig indeksnotat: viktige tema,
   kildesteder, tidligere feil/utelatelser, gode søkeord, falske treff,
   mottaker-/periodefeller og neste års kontroller. Dokumenter manglende
   historikk uttrykkelig. Ikke fyll et kildehull med antatt erfaring.
4. Lag et varig oppdrag per fagrolle med minnestier, år/stadium, søkeord,
   kildeansvar, avgrenset skriveområde og leveransekrav. Agenten registrerer
   hash og tidspunkt for minnet den har lest før årets kilder. Ved bytte av
   modell, sesjon eller agent skal den nye agenten lese samme fagminne.
5. Kjør uavhengige roller parallelt innen tilgjengelig kapasitet. Hver rolle
   leverer **notater, ferdig rapport og maskinlesbare funn per departement**.
   Årets erfaringer lagres separat etterpå og merkes prøve eller fasitkontrollert.
   En rolle er ikke ferdig før erfaringene og delleveransene finnes på disk.

Bruk `manage_workflow.py prepare` for oppdragsfiler. Skriptet lager ikke
fagminne eller vurderinger automatisk. Redaktøren har også eget minne fra
tidligere presentasjoner, sammenstillinger og videreformidling.

## Modellvalg, responstid og ferdigstilling

Bruk [modelltestingen](references/model-testing.md) ved valg av modell og
reasoning effort. Gjenbruk lagrede målinger og faglige erfaringer; start nye
tester bare ved konkret behov eller bestilling. En raskere profil må fortsatt
oppfylle samme krav til tall, kilder, perioder, vilkår og kritisk temadekning.

Foreløpig utgangspunkt fra piloten: Sol-high til raske førsteutkast og
sammenlignende kontroll; Luna-xhigh som uavhengig analyse av ramme/KD og
KUD; Luna-max ved HODs sammensatte tilskudd og overgangsvilkår. Luna-high
er ikke validert som erstatning for ferdig faganalyse. Bruk rolleminnets
konkrete erfaringer og kontrolliste; dette er oppgavespesifikke utgangspunkt,
ikke garantier. Revider profilene når nye målinger tilsier det.

For vesentlige oppgaver: la to modeller lese samme fagminne og analysere
uavhengig før de ser hverandres svar. La kontrollen deretter få begge svar
og originalkildene. Kontroller også historiske temaer som begge har utelatt,
og at kritiske vilkår fra utkastene overlever sammenstillingen. Krev kilde-
belegg for rettelser; enighet eller et teknisk fullført kall er ikke faglig
godkjenning. Lagre både feil, dekningshull og fungerende profiler i fagminnet.

Gi mottakskvittering raskt og skill den fra første kildebaserte vurdering.
Mål ferdig utkast og review med kø og venting på det andre svaret inkludert.
Fem minutter er et mål som må prøves, ikke et kvalitetsstempel. Registrer
forespurt priority/fast separat fra faktisk bekreftet tjenestenivå.

Ved «ferdigstill», «ferdigstill+rapport» eller knapp gjenværende usage:
stopp nye utvidelser, bruk eksisterende belegg og gjør nødvendige, tydelig
merkede antakelser om arbeidsopplegget. Fullfør nødvendig kontroll og lever
rapporten med dokumenterte begrensninger. Ikke gjett manglende kildetall
eller utsett ferdigstillingen for valg agenten kan ta selv.

## Avgrens år og dokumentstatus

- Skill budsjettåret fra publiseringsåret: forslag for år Y kommer normalt
  høsten Y−1. Prop. 1 S (Y−1–Y) gjelder Y.
- Avklar gjennom konteksten om oppgaven gjelder regjeringens opprinnelige
  forslag, tilleggsproposisjon, saldert budsjett eller RNB. Når brukeren vil
  prøve analysen før fasit, bruk opprinnelig forslag og dokumenterte
  forutsetninger fra før framleggelsen.
- Ved historisk prøving: hold treningsår, prøveår og fasit atskilt. Ikke åpne
  prøveårets UiT-presentasjon, endelige budsjettfordeling eller senere
  tildelingsbrev før prøvebesvarelsen er lagret. Før logg over kilder brukt,
  utilsiktet eksponering og avgrensninger. Frys besvarelsen med dato og
  filhash før sammenligning; senere rettelser skal være synlige.

## Finn UiTs forutsetninger først

1. Finn styrets foreløpige fordeling for Y, normalt junimøtet Y−1, med
   saksframlegg, vedlegg og vedtaksprotokoll. Søk i UiTs møteportal etter
   «Foreløpig fordeling av budsjett», «Foreløpig budsjettfordeling» og året.
   Registrer saksnummer, dato og om innstillingen ble endret ved vedtak.
2. Trekk ut KD-ramme, pris-/lønnsanslag og grunnlag, kjente kutt,
   sikkerhetsmargin, studieplassopptrapping/-utfasing, resultatanslag,
   pensjon/arbeidsgiveravgift, engangsmidler og særskilte satsinger.
   Skill KD-bevilgning fra intern viderefordeling og planleggingsrammer.
3. Bruk historiske UiT-presentasjoner og arbeidsnotater til å lære
   prioriteringer og tidligere feil. PPTX kan ha avgjørende regneark under
   `ppt/embeddings/`, inkludert prognoser utenfor synlig diagramområde.
   Knytt arbeidsarket til lysark via relasjoner; merk skjulte tall som
   arbeidsgrunnlag og sjekk dem mot vedtatt foreløpig fordeling når mulig.
4. Behold ukjent som ukjent. Et tall fra statsbudsjettet, et tidligere år
   eller en intern fakultetstabell dokumenterer ikke UiTs forhåndsanslag.
   Fortsett med tilgjengelige kilder og pek presist på manglende grunnlag.

## Hent og undersøk statsbudsjettet

Bruk [kildekartet](references/kildekart.md) for innganger og søkeområder.
Last ned riktig utgave av blått hefte og relevante fagproposisjoner.
Registrer URL, dokumenttittel, år, status og hentetidspunkt; behold PDF
og lesbart uttrekk i oppdragets mappe.

- Start med UiT-raden og forklaringene i blått hefte, deretter detaljer om
  resultatfinansiering og studieplasser. Kontroller mot KD Prop. 1 S.
- Søk både UiTs navn, enheter, prosjekter og faglige interesseområder på
  tvers av departementer. Les avsnitt og kapittel/post rundt treffet:
  rapportering for tidligere år er ikke et nytt budsjettforslag.
- Hent skatte-/avgiftsforslag når arbeidsgiverkostnader berøres. Registrer
  kostnadsvirkning separat fra bevilgningsendring og eventuell kompensasjon.
- Kontroller vesentlige tabeller visuelt. Bevar minusfortegn, kolonneår,
  fotnoter og enhet. Oppgi både trykt side og PDF-side når de er forskjellige.
- Be hver fagagent velge **presis side og markering for hvert vesentlig
  funn**, inklusive beløp, mottaker og nødvendige vilkår. Lag markert PDF,
  sidebilde og lesbart tekstuttrekk med `build_evidence.py`. Hele original-
  siden beholdes. Kontroller at markeringen treffer riktig forekomst;
  «ordet finnes et sted» er ikke tilstrekkelig. Bruk et ekstra funn/kilde-
  utdrag når vilkår eller tabelloverskrift står på en annen side.
- Søk spesielt etter endringer uten UiT-navn: finansieringsmodell,
  resultatindikatorer, forskningsprogrammer, studentvilkår og generelle kutt.
  «Ikke funnet» skal angi hvilke dokumenter/områder som er undersøkt.

## Avstem og forklar

Lag to broer i hele tusen kroner:

1. Saldert basisår + regjeringens endringer = foreslått KD-ramme.
2. UiTs foreløpige KD-ramme + avvik per sammenlignbar komponent = foreslått
   KD-ramme. Positivt avvik betyr høyere bevilgning enn UiT la til grunn.

Bruk kolonnene **tema, UiT-forutsetning, forslag, avvik, kilde på begge
sider, konsekvens/oppfølging**. Sett bare null når den komplette broen
eller teksten dokumenterer at ingen endring er innarbeidet.

- Harmoniser bruttolinjer og nettolinjer før subtraksjon. Opptrapping og
  utfasing kan ligge samlet i statsbudsjettet og separat hos UiT.
- Prisjustering kan inneholde videreført RNB-kompensasjon fra basisåret.
  Sammenlign beløp på samme grunnlag; ikke bruk samlet prisbeløp som ny
  årlig sats eller prisjuster et allerede prisjustert tillegg på nytt.
- Åpen og lukket resultatramme må skilles. Vis både årets endring og avvik
  fra UiTs anslag. Intern fordelingsandel er ikke hele KD-uttellingen.
  Registrer produksjonsår, gjennomsnittsperioder og overgangsregler per
  indikator; en generell regel om to års etterslep er ikke alltid nok.
- Behandle anslått samlet kutt og sikkerhetsmargin samlet når delbeløpene
  bare er avrundede. Ikke tell både samlet kutt og dets delkomponenter.
- Flytting fra prosjekt-/programmidler til ramme er en finansieringsendring;
  avklar tidligere UiT-inntekter og forpliktelser før den omtales som fritt
  handlingsrom. Hold pensjonsnøytrale og andre tekniske endringer synlige.
- Skill rammetildeling, annen navngitt UiT-tildeling, felles-/konkurransepott,
  kostnadsvirkning og politisk føring. Ikke summer dem som én UiT-bevilgning.
- Vis videreår som videreført effekt, opp-/nedtrapping, engangseffekt eller
  usikkert anslag. Nasjonale satser/modellendringer er ikke vedtatte
  framtidige institusjonsrammer.

## Leveranse og kontroll

Bruk [skriptressursene](references/scripts.md) til identifiserte
PDF-nedlastinger, dokumentuttrekk med kildesteder og avstemming av en faglig
harmonisert rammebro. Lagre årsspesifikke input/output i analyseprosjektet.
Når oppgaven avdekker nyttig, gjentakbar kode, vedlikehold den i `scripts/`
og test den mot både kontrollerte eksempler og aktuelle dokumenter.

Redaktøren sammenstiller først når delene og deres fagminner er levert.
Samordne kapittel-/departementsflyttinger og flere omtaler av samme tiltak
før summering. Bruk ferdige delrapporter; ikke reduser dem til navnesøk.

Den komplette leveransen inneholder:

- arbeidsdeling, varige rolleoppdrag og dokumentert innlest fagminne;
- arbeidsnotater, rapport og markerte kildeutdrag per del, også et dokumentert
  negativt resultat når ingen relevant tildeling er funnet;
- samlet rapport med avstemming, prioriterte funn, videreår og oppfølging;
- **faktisk PowerPoint-fil**, redigerbar kildespesifikasjon og visuell kontroll;
- **ferdig meldingsutkast for videreformidling**, med emne, mottakergruppe,
  hovedfunn, dokumentstatus og vedlegg; send bare etter eksplisitt autorisasjon;
- lagrede erfaringer fra årets arbeid og tydelig logg over endringer mot
  tidligere prøve. Års- og fasittall hører til prosjektet, ikke skillen.

Bruk [UiT-deck-generator](../../reporting/presentation/uit-deck-generator/SKILL.md)
og `build_presentation.py` for PowerPoint fra en egnet UiT-mal. Wrapperen
fjerner gamle lysark med relasjoner og legger kilder i lysarknotatene.
En outline eller fil som bare åpner er ikke en visuelt kontrollert presentasjon.
Render lysarkene og rett overlapp, for liten tekst, feil år og gamle plassholdere.

Kjør `manage_workflow.py check` før ferdigmelding. Den kontrollerer
fildekning, minneidentitet og samsvar mellom funn og kildeutdrag; faglig
riktighet og visuell kvalitet kontrolleres i tillegg. Rapporter en manglende
del som manglende, selv om rammeberegningen eller skripttestene er riktige.

Regn broene på nytt og vis eventuell uforklart rest. Kontroller minst
totalramme, prisbeløp, resultat og største kutt mot originalene. Skill
regnefeil, avrunding, ulik avgrensning og uverifiserte årsaksforklaringer.
Gi brukeren et tydelig svar på hva som bør oppdateres i foreløpig fordeling.

Når fasit senere gis: sammenlign tall, vesentlige tema, dokumentstatus,
avvik mot prognose og begrunnelse. Registrer oversette funn, feil tall,
falske treff og kildehull; endre skillen bare for påviste, gjenbrukbare
svakheter. Ikke skriv prøvebesvarelsen om til å se riktig ut i ettertid.
