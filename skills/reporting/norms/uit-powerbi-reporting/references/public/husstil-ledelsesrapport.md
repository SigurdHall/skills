# Husstil for UiT-økonomirapporter: ledelsesrapporten er fasit

Ledelsesrapport økonomidata er resultatet av mange redigerte runder med brukeren og er stilfasit for nye økonomirapporter. Reglene og brukerens begrunnelser står i `uit-powerbi-okonomi/docs/rapporter/tertialrapport/designprofil-og-samarbeid.md` (VP1–VP22) og `retningslinjer.md` (G-reglene). Generatorene er `uit-powerbi-okonomi/scripts/tertialrapport/tr_felles.py` og `tr_meny.py`. Den utrullede kopien ligger i `ws_okonomi_ppu_dev/Ledelsesrapport_okonomidata.Report`. Rapport- og arbeidsområde-ID-ene for rendering står i `../private/husstil-ledelsesrapport-id.md`.

Prosa som «følg VP12» er ikke nok. Agenter som tegner komponentene på nytt etter beskrivelsen, treffer ikke grunnlinjer, farger og kortanatomi. Derfor gjelder reglene under.

## R1 Klon komponentene, ikke tegn dem på nytt

Kopier `visual.json` fra ledelsesrapporten (siden `bevilgningsokonomi`) og bytt bare felt (`Entity`, `Property`, `queryRef`, `nativeQueryRef`, `displayName`), tekster, visualnavn og filternavn. Behold alle formateringsegenskaper. Hjelpere fra andre rapportgeneratorer, for eksempel `bygg-prosjektrapport.mjs`, har eldre stil og skal ikke brukes som mal for disse komponentene. Endres en verdi, skrives grunnen i generatoren.

| Komponent | Visual i ledelsesrapporten | Byttes |
|---|---|---|
| Tittel | `faa83328225448a76e0e` (tekstboks, Segoe UI 20 pt, «<Rapport> \|  » og sidenavnet fet) | rapport- og sidenavn |
| Sist oppdatert | gruppe `2ef3ca8c27a97d2cdb22`: `bev_tidsstempel_etikett` og kortet `298f74d6fac3bc3ee8d5` | målet (se R3) |
| Beta | `3c71f5ce16c91306660e` | x etter tittelbredden |
| Logo, skillestrek, ◀ Meny ▶ | `85a2dfe4afcefc7cccbd`, `02041846998e07412cbd`, `bev_pil_forrige`, gruppen `e05708c5d8a3354c3db8`, `bev_pil_neste` | bokmerker |
| Filterlinje | gruppe `c94e64245459a35c1ce8`: bakgrunn `db127bec4db6dd51a40a`, etiketter `8eef5bb27245600e0c90`, `bev_etikett_maaned`, `e4a506604530a827553e`, slicere `3ee853280a9157690652`, `bf643a9471a15defb4f5`, `170fc2210e6e79bd9d04`, skillestreker `6535a6055306e15082d6`, `adb3277112238e60703e` | felt, etikettekst, x etter målt bredde |
| Valgknapper | `bev_modus_knapper` (knappeslicer) | felt og fargemål |
| KPI-kort | `bev_kpi_inntekter`, `bev_hjelp_inntekter`, `bev_ikon_inntekter` | mål, tittel, ikon |

## R2 Målene, når en komponent ikke kan klones

Kontroller resultatet mot disse verdiene. De er lest fra ledelsesrapporten 25.11.2026.

**Topptekst.** Tittel 12–1092, y 0, høyde 69, venstremarg 12. Under tittelen står «Sist oppdatert» i Segoe UI Bold 9 pt og datoen i Segoe UI 9 pt, x 10, y 46,7. Beta-pillen står rett etter tittelen. Logoen står på x 1351, og ◀ Meny ▶ på x 1614–1908.

**Filterlinje.** x 12–1908, y 78–142. Bakgrunn #F6F6F6 med kant #E6E6E6 og radius 7. Etiketten står i en egen tekstboks (Segoe UI Semibold 10 pt, #252423, padding topp 20 og venstre 15, høyde 46) og sliceren rett etter (padding topp 10, høyde 56,5). Tekstboks og slicer har samme y innenfor ±1 px, så etiketten og boksen deler midtlinje. 24 px marg i begge ender. 10 px fra etiketten til boksen. Etikettbredden er målt (`powerbi-report-author text measure --weight semibold`) pluss 8 px luft, så teksten ikke brytes. År- og Måned-boksene er 110 px, Rapporteringsenhet 480 px. Gruppene skilles med en loddrett strek (shape `line`, vekt 0,5, temafarge 1 med 40 %) og like store mellomrom på begge sider. Valgknappene står høyrejustert 24 px fra høyre kant. Ingen tekst i en boks kuttes («Siste lukke…» er feil).

**Valgknapper.** Pille uten kant, 105 × 28 px, 8 px mellom. Fyll #E4F0F4 og tekst #003349 fet 10 pt. Hover #CCE3EA. Valgt: fyll #003349 og tekst #FFFFFF. Førstevalget er en knappeslicer (`advancedSlicerVisual`), fordi bare den kan skjule knapper som ikke er aktuelle (V4, AV1). Må valget lages med bokmerkeknapper (`actionButton`), får de de samme fargene og ingen kant. Hvit pille med mørk blå kant er Prosjektrapportens stil, ikke husstilen.

**KPI-kort.** Ett `cardVisual`, høyde 176, padding 12, hvit bakgrunn med kant #EAEAEA og radius 7. Tittel Segoe UI 12 pt fet #252423 med «?» (`bev_hjelp_*`) rett etter teksten og ikonflis øverst til høyre. Undertittel 9 pt #666666 sier hva tallet er. Skillelinje #808080. I flisen står periodeteksten over tallet (`label` `aboveValue`, 10 pt #555555, sentrert) og hovedtallet sentrert i Segoe UI Bold 30 pt (`calloutSize` 50). Til høyre står to kontekstmål (`referenceLabel`): tittel 8 pt grå over verdien, verdi 12 pt fet, kort merke under (høyst ca. 18 tegn), `paddingAfterDivider` 20. Flere enn to kontekstmål, venstrejustert hovedtall eller lavere kort er avvik som brukeren må godkjenne. Får kortene ikke plass, endres rutenettet (færre kort per rad, en veksler, egen side), ikke kortet.

**Millioner.** `valueDisplayUnits` 1000000 gir «M» etter nettleserens språk, både i ledelsesrapporten og i nye rapporter. Skal det stå «mill.», må det løses med formatstreng i målet, likt for alle rapportene.

## R3 Toppteksten viser «Sist oppdatert», aldri perioden

Under tittelen står «Sist oppdatert» (fet) og «dd.mm.yyyy kl. hh.mm» (VP10). Perioden står i periodeteksten over innholdet og i kortenes periodelinje, ikke i toppteksten. Mangler modellen et tidsstempel, legges `gold_status` (skjemaet `gold_okonomi`) inn som skjult tabell uten relasjon med `utvalg.eksterneTabeller` i modellprofilen. Mønsteret er `ws_okonomi_ppu/verktoy/profil.fellesutgifter-dl.json` med målet «Data sist oppdatert økonomi» (E44), som regner UTC om til norsk tid. Rapportmålene «Sist oppdatert tekst» og «Sist oppdatert etikett» kopieres fra `reportExtensions.json` i ledelsesrapporten. Et manglende tidsstempel er en modellendring å foreslå, ikke en grunn til å vise noe annet.

## R4 Funksjonelle avvik beholder utseendet

Krever planen annen mekanikk enn ledelsesrapporten, for eksempel en Filtrer-knapp (`ApplyAllSlicers`) som holder igjen alle slicere og derfor tvinger fram bokmerkeknapper, skal komponenten likevel se ut som komponenten i ledelsesrapporten. Avviket skrives som funksjon i planen, med grunnen. Plasser bare knapper brukeren har bedt om, der brukeren har bedt om dem, og spør før en knapp får en ny plass.

## R5 Kontroll før levering

Statiske kontroller og klikktest sier ingenting om stil. Før en runde leveres:

1. Rendre ledelsesrapportens første side og den nye siden med `ws_okonomi_ppu_dev/verktoy/rapport/render/render.mjs` i samme oppløsning.
2. Klipp toppen av begge (lerret y 0–340, topptekst, filterlinje og første kortrad) og legg dem over hverandre i ett bilde.
3. Sjekk grunnlinjen mellom etikett og boks, knappefarger og kant, kortanatomi og toppteksten mot R2 og R3.
4. Rett avvik som ikke er godkjent, før bildet sendes til brukeren.
