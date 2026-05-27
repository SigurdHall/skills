# Deck Spec Schema

Use this JSON shape with `scripts/generate_uit_deck.py`.

## Minimal Example

```json
{
  "deck_id": "Deck A",
  "title": "Fra rapportmigrering til styringsdata",
  "subtitle": "Hoveddeck til ledermøte",
  "outcome": "Få beslutning om pilot for styrt dataplattform.",
  "footer": "UiT virksomhetsstyring",
  "slides": [
    {
      "type": "bullets",
      "title": "Beslutningen vi må ta",
      "message": "Dette er et styringsvalg, ikke et rent verktøyvalg.",
      "bullets": [
        "A. Isolert migrering viderefører dagens fragmentering.",
        "B. Pilot for styrt dataplattform bygger varig styringsevne.",
        "Anbefaling: B, avgrenset til 90 dager."
      ]
    }
  ]
}
```

If the first slide is not `type: "cover"`, the script creates a cover from
top-level `title`, `subtitle`, and `outcome`.

Generated slides include simple click-to-appear animations for main content.

## Slide Types

### bullets

```json
{
  "type": "bullets",
  "title": "Dagens risiko",
  "message": "Fragmentert rapportering gir styringsrisiko.",
  "bullets": ["Lokale definisjoner.", "Manuelle uttrekk.", "Lav gjenbruk."]
}
```

### cards

```json
{
  "type": "cards",
  "title": "Hva Fabric kan styrke",
  "message": "Fabric samler flere deler av dataløpet.",
  "cards": [
    {"title": "Innhenting", "body": "Pipelines og kildesporing."},
    {"title": "Modell", "body": "Felles beregninger og begreper."}
  ]
}
```

### two-column

```json
{
  "type": "two-column",
  "title": "Fra dagens rigg til ønsket rigg",
  "message": "Forskjellen er forvaltning, ikke bare verktøy.",
  "left_title": "I dag",
  "left_items": ["Lokale uttrekk", "Personavhengig logikk"],
  "right_title": "Med styrt dataplattform",
  "right_items": ["Sertifiserte modeller", "Gjenbrukbare rapporter"]
}
```

### table

```json
{
  "type": "table",
  "title": "Roller og ansvar",
  "message": "Piloten må ha tydelig eierskap.",
  "headers": ["Rolle", "Ansvar"],
  "rows": [
    ["Økonomi", "Eier styringsbehov og begreper."],
    ["ITA", "Eier plattform, sikkerhet og integrasjon."]
  ]
}
```

### timeline

```json
{
  "type": "timeline",
  "title": "Neste steg",
  "message": "Kort pilot og beslutning etter demonstrert verdi.",
  "steps": [
    {"label": "30 dager", "body": "Kartlegg kilder og begreper."},
    {"label": "60 dager", "body": "Foreslå modell og kontrakt."},
    {"label": "90 dager", "body": "Vis lederpakke og beslutningsnotat."}
  ]
}
```

### process

Use for dataflows, roadmaps, governance processes, and migration paths.

```json
{
  "type": "process",
  "title": "Dataflyten",
  "message": "Fra kildesystem til lederrapport er det flere styringspunkter.",
  "steps": [
    {"label": "Kilder", "body": "Unit4/BOTT, HR og lokale filer."},
    {"label": "Plattform", "body": "Innhenting, historikk og kvalitet."},
    {"label": "Modell", "body": "Felles begreper og tilgang."},
    {"label": "Rapport", "body": "Lederflate og analyse."}
  ]
}
```

### hub

Use for operating models, role ecosystems, domains, and central-local
governance balances.

```json
{
  "type": "hub",
  "title": "Desentralisert styring krever styrt dataplattform",
  "message": "Felles spilleregler sentralt, analyse og lederstøtte lokalt.",
  "center": "Styrt dataplattform",
  "spokes": [
    {"title": "Sentralt", "body": "Definisjoner, tilgang og kvalitet."},
    {"title": "Domener", "body": "Faglig betydning og prioritering."},
    {"title": "Lokalt", "body": "Analyse og lederstøtte."},
    {"title": "ITA", "body": "Arkitektur, sikkerhet og drift."}
  ]
}
```

### decision

Use for explicit choices and trade-offs. Keep to two options.

```json
{
  "type": "decision",
  "title": "Beslutningen vi må ta",
  "message": "Dette er et styringsvalg, ikke et rent verktøyvalg.",
  "options": [
    {"title": "A. Isolert migrering", "body": "Rask flytting, men dagens fragmentering videreføres."},
    {"title": "B. Styrt pilot", "body": "Bygger varig styringsevne gjennom et data product."}
  ]
}
```

### quote

```json
{
  "type": "quote",
  "title": "Hovedbudskap",
  "quote": "Ikke bare migrer rapportene. Bruk migreringen til å bygge styringsevne.",
  "attribution": "Anbefalt lederbudskap"
}
```

## Generation Command

```powershell
python scripts/generate_uit_deck.py --spec deck.json --output deck.pptx --template C:\path\to\UiT-template.pptx
```

Optional:

```powershell
python scripts/generate_uit_deck.py --print-schema
```
