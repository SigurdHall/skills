# Skills for Fabric i Claude Code-skysesjoner

Dato: 2026-09-03

## Kortversjon

Microsoft `skills-for-fabric` `v0.3.14` ligger nå som en pinnet, vendored kopi
under `.claude/skills/` i dette repoet, med de delte referansene under
`.claude/common/` og `.claude/mcp-setup/`. Claude Code leser `.claude/skills/`
fra klonede repoer, både når `skills` er hovedrepo og når det er ett av flere
repoer i sesjonen. Verifisert i en skycontainer 2026-09-03: 26 skills lastet i
begge oppsett.

Du fant ikke skillene i repo-velgeren fordi `microsoft/skills-for-fabric` ikke
ligger i din GitHub-konto. Skysesjoner kan bare hente repoer du har tilgang til,
så innholdet må ligge i et repo du allerede har med.

Plugin-ruten ble testet først og forkastet. Dokumentasjonen sier at plugins
deklarert i repoets `.claude/settings.json` installeres ved sesjonsstart, men en
ekte skysesjon på `master` med deklarasjonen inne fikk verken plugins eller
registrert markedsplass. I tillegg laster Claude Code plugin-skills og
prosjekt-skills med samme navn dobbelt, så plugin pluss vendored kopi lokalt
gir 26 uprefiksede og 27 prefiksede skills samtidig.

## Oppsett

| Sti | Innhold |
| --- | --- |
| `.claude/skills/<navn>/` | 26 skill-mapper, uendret fra oppstrøms `skills/` |
| `.claude/common/` | delte referanser som skillene lenker til via `../../common/` |
| `.claude/mcp-setup/` | MCP-registreringsnotater som `sqldw-cli` lenker til |
| `.claude/LICENSE-skills-for-fabric` | MIT-lisensen fra oppstrøms |
| `.claude/skills-for-fabric.vendor.json` | tag, commit, pakkeversjon, dato og skill-liste |

Skillene har uprefiksede navn i Claude Code, for eksempel `spark-cli` og
`semantic-model-authoring`. Ingen av dem kolliderer med repoets egne 44 skills.
Alltid-på-kostnaden er om lag 4 400 tokens per sesjon for de 26 beskrivelsene.

`extraKnownMarketplaces` i `.claude/settings.json` peker fortsatt på
`fabric-collection` pinnet til samme tag, slik at `/plugin` kan installere
bundlene lokalt ved behov. `enabledPlugins` er bevisst ikke satt.

## Oppdatering

```bash
python scripts/vendor_skills_for_fabric.py --tag v0.3.15
python scripts/vendor_skills_for_fabric.py --tag v0.3.15 --source C:\repos\skills-for-fabric
```

Skriptet kloner taggen fra GitHub, eller bruker en lokal sjekkut som må stå på
samme tag. Det fjerner bare skill-mapper som manifestet lister som vendored,
kopierer alt på nytt og skriver nytt manifest. En fremmed mappe med samme navn
som en oppstrøms skill stopper kjøringen uten `--force`. Les `CHANGELOG.md`
oppstrøms og oppdater `ref` i `.claude/settings.json` og
`skills/fabric/fabric-item-authoring/references/item-routing-matrix.md` i samme
endring.

## Hva som ble testet

| Test | Resultat |
| --- | --- |
| `claude plugin marketplace add` og `plugin install` fra skycontaineren | fungerer, begge bundles på 0.3.14, `npx`-modelleringsserver starter |
| `enabledPlugins` i prosjektinnstilling, ekte skysesjon på `master` | ingen plugins, markedsplass ikke registrert |
| `enabledPlugins`, hodeløs CLI i repo-katalogen | markedsplass registrert på riktig tag, plugins ikke aktivert |
| vendored `.claude/skills/`, hodeløs økt i repo-katalogen | 26 prosjekt-skills lastet |
| vendored `.claude/skills/`, økt fra `/home/user` med repoet som tilleggskatalog | 26 skills lastet fra tilleggskatalog |
| plugin og vendored kopi samtidig | 26 pluss 22 lastet, ingen duplikater hoppet over |

## Begrensninger i skyen

- `az`, `powerbi-report-author`, `powerbi-desktop` og `sqlcmd` finnes ikke i
  containeren. Skills som forutsetter disse fungerer som referanse og
  planleggingsgrunnlag, ikke som live mutasjon, inntil et setup-script
  installerer verktøyene og miljøet har API-legitimasjon.
- Plugin-bundlenes MCP-servere følger ikke med den vendored kopien. Registrer
  `powerbi-modeling-mcp` selv der den skal brukes.
- Repoets egne 44 skills under `skills/<gruppe>/<navn>/` er fortsatt ikke
  synlige for Claude Code i skyen. Claude Code leser bare `.claude/skills/`,
  `.claude/commands/` og plugins. Det er neste steg, ikke dekket her.
- `reporting/AGENTS.md` og `reporting/CLAUDE.md` viser fortsatt til
  `semantic-model-consumption`, som ble fjernet oppstrøms. Read-only DAX ligger
  nå i `fabriciq`.

## Bivirkning lokalt

Claude Code på Windows laster de 26 vendored skillene uprefikset når du åpner
`C:\repos\skills`. Har du `powerbi-authoring`-pluginen installert der, kommer de
fem Power BI-skillene i tillegg med prefiks. Codex-junctions under
`.agents/skills` berøres ikke, men peker fortsatt på `0.3.5`-sjekkuten, så det
er to versjoner mellom verktøyene inntil junctions oppdateres til samme tag.

## Slik trimmer du

Slett mapper under `.claude/skills/` du ikke vil ha. Neste vendoring-kjøring
legger dem tilbake, så legg til en ekskluderingsliste i skriptet hvis
trimmingen skal være varig.
