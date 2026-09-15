---
name: codex-uit-statsbudsjett-proeve
description: Kjør Codex-versjonen av UiTs statsbudsjettprøve med Node og Codex CLI, skriptstyrt kildehenting, rammeark, Luna-fagroller og samlet kontroll. Bruk når brukeren ber om codex-uit-statsbudsjett-proeve eller en Codex-kjøring av uit-ramme og uit-departementer. Claude-starten finnes i uit-statsbudsjett-proeve.
---

# UiTs statsbudsjettprøve med Codex

Les [analyseskillen](../uit-statsbudsjett-analyse/SKILL.md) for fagkrav og
[Codex-kjøringen](../uit-statsbudsjett-analyse/references/codex-orchestration.md)
for argumenter, tester og videreføring. Bruk samme skript, kildeformater,
fagminner, rammeark og leveransekontrakt som Claude-versjonen.

1. Finn prosjekt, budsjettår, omfang og Python fra brukerens bestilling og
   eksisterende miljø. Budsjettår må være kjent før en virkelig kjøring.
   Lag en JSON-argumentfil i prosjektet med ubrukt `run_id`, normalt
   `codex-<år>-v1`. Årets arbeidsdeling kopieres til kjøringens mappe;
   originalen bevares. Fasitmappen for prøveåret er alltid forbudt.
2. Kjør `--dry-run` først. Den viser argumenter og modellplan uten nettverk,
   modellkall eller filskriving. Kontroller Node, Codex-innlogging, Python
   og modulene i prosjektets runtime-krav. Fra Windows kjører du Node inne
   i WSL; `python` skal være én kjørbar POSIX-sti.
3. Start `codex-uit-ramme.js` fra skills-repoets `.claude/workflows/` med
   `--args <fil>`. `phase_set` er `grunnlag`, `budsjettdag` eller `alt`.
   `check_only: true` gjør bare publiseringssjekken. Manglende blått hefte/KD
   stopper en analysekjøring. `archive: true` arkiverer eksisterende
   årsgrunnlag ved en ny kjøring; oppgi hva som flyttes. Ikke slå det på
   når bestillingen bare gjelder bygging eller testing av kode.
4. Gjengi `hurtigsvar.md` og lenk Excel-arket straks hurtigsvaret er
   kontrollert. Start `codex-uit-departementer.js` med samme argumentfil
   når omfanget omfatter departementene. Samme kjøring fortsetter uten ny
   opprydding. Sluttkontrollen fryser leveransen og hindrer overskriving.
5. Oppgi faktisk status, manglende kilder/deler/PPTX, filstier og målte
   modellkall. Skill maskinell fil- og regnekontroll fra faglig og visuell
   kontroll. Ikke kall en ufullstendig analyse ferdig. Meldingsutkastet
   lagres; ingen melding sendes.

Luna er arbeidshest på fagroller: `high` på kritiske deler, `medium` på
øvrige. Astra brukes på rammetall, uavhengig rammeutkast, review og redaktør.
`models` overstyrer modell og effort per fase. Innstillingene er en
arbeidshypotese, ikke et målt kvalitets- eller hastighetsløfte. Prøv endret
effort på avgrensede, identiske input i separate kjøringer; behold beløp,
enhet, mottaker og vilkår som vurderingskriterier.
