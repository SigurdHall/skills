# Skills for Fabric i Claude Code-skysesjoner

Dato: 2026-09-03

## Kortversjon

Microsoft `skills-for-fabric` er nå deklarert som Claude Code-plugins i
`.claude/settings.json` i dette repoet. Alle skysesjoner som har `skills`-repoet
med, installerer pluginene automatisk ved oppstart. Mekanismen er verifisert
fra en skycontainer 2026-09-03: markedsplassen ble klonet, begge bundles ble
installert på versjon `0.3.14`, og den lokale Power BI-modelleringsserveren
startet via `npx`.

Du fant ikke skillene i repo-velgeren fordi `microsoft/skills-for-fabric` ikke
ligger i din GitHub-konto. Skysesjoner kan bare hente repoer du har tilgang til.
Løsningen er derfor ikke å legge til repoet i sesjonen, men å la et repo du
allerede har med deklarere markedsplassen.

## Hva som er deklarert

```json
"extraKnownMarketplaces": {
  "fabric-collection": {
    "source": { "source": "github", "repo": "microsoft/skills-for-fabric", "ref": "v0.3.14" }
  }
},
"enabledPlugins": {
  "fabric-skills@fabric-collection": true,
  "powerbi-authoring@fabric-collection": true
}
```

| Bundle | Skills | Alltid-på-kostnad | MCP-servere |
| --- | --- | --- | --- |
| `fabric-skills` | 22 skills, alle Fabric-workloads | ca. 3 200 tokens per sesjon | 3 HTTP-servere mot `api.fabric.microsoft.com` (krever innlogging) |
| `powerbi-authoring` | `semantic-model-authoring` og fire `powerbi-report-*` | ca. 1 200 tokens per sesjon | lokal `powerbi-modeling-mcp` via `npx` |

Skillene får plugin-prefiks: `fabric-skills:spark-cli`,
`powerbi-authoring:semantic-model-authoring`. `semantic-model-authoring` ligger i
begge bundles, så oppgi hvilken bundle som ble brukt i en handoff.

Versjonen er pinnet til tag `v0.3.14` (commit `714ea2f`). Det følger regelen i
`fabric-item-authoring` om én versjonert kilde per kjøring. Oppdater ved å endre
`ref`, lese `CHANGELOG.md` oppstrøms og oppdatere
`skills/fabric/fabric-item-authoring/references/item-routing-matrix.md`.

## Begrensninger i skyen

- `az`, `powerbi-report-author`, `powerbi-desktop` og `sqlcmd` finnes ikke i
  containeren. Skills som forutsetter disse fungerer som referanse og
  planleggingsgrunnlag, ikke som live mutasjon, inntil et setup-script
  installerer verktøyene og miljøet har API-legitimasjon.
- De tre HTTP MCP-serverne i `fabric-skills` krever interaktiv innlogging.
  Skysesjoner støtter ikke nettleserbasert innlogging.
- Repoets egne 44 skills under `skills/<gruppe>/<navn>/` er fortsatt ikke
  synlige for Claude Code i skyen. Claude Code leser bare `.claude/skills/`,
  `.claude/commands/` og plugins. Det er neste steg, ikke dekket her.
- `reporting/AGENTS.md` og `reporting/CLAUDE.md` viser fortsatt til
  `semantic-model-consumption`, som ble fjernet oppstrøms. Read-only DAX ligger
  nå i `fabriciq`.

## Bivirkning lokalt

Claude Code på Windows leser samme prosjektinnstilling når du åpner
`C:\repos\skills`. Etter at mappen er markert som trusted, registreres
markedsplassen og begge bundles installeres på `v0.3.14` på prosjektnivå. Det
berører ikke Codex-junctions under `.agents/skills`, som fortsatt peker på
`0.3.5`-sjekkuten. Har du allerede en `fabric-collection`-markedsplass på
brukernivå med en annen kilde, bør den fjernes med
`claude plugin marketplace remove fabric-collection` for å unngå to versjoner.

## Slik trimmer du

Sett `"fabric-skills@fabric-collection": false` for å beholde bare Power
BI-bundlen. Det fjerner 22 skills og de tre HTTP MCP-serverne fra oppstart.
