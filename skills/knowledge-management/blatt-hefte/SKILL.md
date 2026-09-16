---
name: blatt-hefte
description: Bygg UiTs rammeark fra Kunnskapsdepartementets «blått hefte» (Orientering om forslag til statsbudsjettet for universitet og høgskular) på under to minutter. Bruk når brukeren ber om blått hefte, rammeark, statsbudsjettet for UiT, realvekst, kap. 260 post 50, eller vil vite om årets hefte er publisert. Leverer én Excel-arbeidsbok (Hovedtall, Hovedposter, Resultat, Sektor, Satser, Kilder) og en statusprompt. Ikke Prop. 1 S, ikke departementsgjennomgang, ikke UiTs styresak eller foreløpige fordeling.
---

# blatt-hefte

Én kommando. Alt er kode; du starter den, leser statusprompten og følger
stoppreglene. Ikke les `references/` eller `assets/` før kjøring; de er for
skriptene og for mennesker som spør om kilder.

## Kjør

Fra Windows (Bash-verktøyet):

```text
MSYS_NO_PATHCONV=1 wsl.exe -e /home/sihal7953/.venvs/statsbudsjett/bin/python /home/sihal7953/repos/skills/skills/knowledge-management/blatt-hefte/scripts/kjor_blaatt_hefte.py --year <budsjettår> --stage forslag
```

Fra WSL: samme skript med `~/.venvs/statsbudsjett/bin/python`. `--stage vedtak`
gir utgaven etter vedtak i Stortinget. `--rnb <tusen kroner>` legger inn
tillegget fra revidert nasjonalbudsjett året før, så realvekst med RNB fylles.
`--year` er alltid budsjettåret: forslaget for 2027 legges fram i oktober 2026.

Leveranse: `/home/sihal7953/repos/uit-statsbudsjett/leveranser/rammeark/`
(`uit-ramme-<år>-<utgave>.xlsx`, `blaatt-hefte-<år>-<utgave>.json`,
`status-<år>-<utgave>.md`, `tid-<år>-<utgave>.json`). Fra Windows leses de under
`\\wsl.localhost\Ubuntu-24.04` + samme sti.

## Etter kjøringen

Skriv ut innholdet i statusfilen ordrett i en kodeblokk. Ikke legg til, fjern
eller oppsummer noe. Oppgi deretter stien til arket på én linje.

| Returkode | Betyr | Gjør |
|---|---|---|
| 0 | Ark levert, alle kontroller grønne | Vis statusprompten. |
| 10 | Ark levert med merknad | Vis statusprompten; merknaden står i punkt 2 og skal nevnes først. |
| 2 | Ikke publisert (temasiden lest, ingen utgave for året) | Vis statusprompten. Si når neste sjekk bør gjøres: forslag en torsdag i første halvdel av oktober, vedtak i desember/januar. |
| 3 | Ukjent lenke på temasiden med årstall ≥ året | Vis statusprompten og finn-rapporten til brukeren. Ikke velg selv. |
| 4 | Nettfeil etter to forsøk | Vis statusprompten. Foreslå `--pdf` hvis brukeren har filen, ellers websøket i rapporten. |
| 5 | Temasiden svarte, men ingen kjente utgaver ble gjenfunnet (strukturbrudd) | Vis til brukeren. Ikke prøv igjen. Kildekartet må oppdateres av et menneske. |
| 7 | Fil funnet ved filnavnprobe uten lenke fra temasiden | Velg filen når statusprompten viser rimelig størrelse (1–2 MB) og PDF; ellers til brukeren. Kjør igjen med `--pdf` på den nedlastede filen. |
| 8 | Budsjettbrudd (120 s), ingen ark | Vis tidene i punkt 6. Kjør igjen med `--pdf` på lokal fil. |
| 9 | Kontrollfeil i lesingen, ingen ark | Vis kontrollutdraget til brukeren. Ikke prøv igjen; tabellen må ses på av et menneske. |

## Nødprosedyre

Er regjeringen.no nede eller heftet lastet ned i nettleseren, kjør med
`--pdf <sti til PDF>`. finn og hent hoppes over, kontroll C bruker forrige
års vedtaksutgave hvis den ligger i `analyse/kilder/blaatt-hefte/<år−1>/`.

Websøk som fallback når kode 2, 4 eller 5 kommer etter publiseringsdatoen:
`site:regjeringen.no/contentassets orientering statsbudsjettet <år> universitet hogskular`.

## Hva arket inneholder

Kolonner, indikatorer og kategorier er heftets egne for året, på nynorsk.
Kolonnen «Egen etikett» er tom og kan fylles for hånd. Realvekst regnes som
(endring − heftets prisjustering) / utgangspunkt, med og uten RNB; kontrollblokken
i `Hovedtall` viser også nominell endring minus prissats. Når
prisjusteringskolonnen inneholder mer enn satsen (2024, 2025), står avviket og
heftets forklaring i arket.

## Ressurser

- `assets/blaatt-hefte.schema.json`: kontrakten mellom leser og bygger.
- `assets/mal-rammeark.json` og `.xlsx`: malspesifikasjon og mal.
- `assets/fasit-2024.json`: presentasjonens 2024-tall, brukt i testene.
- `references/kildekart-blaatt-hefte.md`: hvor heftene ligger og hvordan nye oppdages.
- `references/tabellkart-blaatt-hefte.md`: tabellenes plassering og kolonner per år.
- `references/kjente-utgaver.json`: alle utgaver 2021–2026 med URL og hash.
- `references/presentasjon-2024-tabeller.md`: hvilke lysark arket speiler.

Tester: `~/.venvs/statsbudsjett/bin/python -m pytest tests/test_blaatt_hefte_*.py -q` fra skills-repoet.
