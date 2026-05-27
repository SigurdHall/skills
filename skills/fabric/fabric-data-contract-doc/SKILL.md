---
name: fabric-data-contract-doc
description: Create or review data contracts in Markdown for Fabric data products, lakehouse/warehouse tables, semantic model sources, APIs, files, finance data, schema changes, quality rules, SLA, ownership, and consumer obligations. Use when the user asks for datakontrakt, tabellkontrakt, interface contract, source-to-Fabric agreement, field definitions, data quality checks, refresh expectations, breaking changes, or public-sector/finance data governance.
---

# Fabric Data Contract Doc

## Arbeidsflyt

1. Bruk `fabric-documentation` som hovedramme.
2. Finn produsent, konsumenter, leveranseform, refresh og eier før du skriver.
3. Dokumenter skjema med feltnavn, datatype, obligatoriskhet, definisjon, eksempel og kvalitetssjekk.
4. For økonomidata, bruk `uit-bott-okonomimodell` til å klassifisere felt og `bott-semantic-model` til å vurdere fakta/dimensjon.
5. Skill kontraktskrav fra observerte datafeil.

## Skjematabell

Bruk denne tabellen for viktige felt:

| Felt | Type | Påkrevd | Definisjon | Nøkkel/rolle | Kvalitetsregel | Merknad |
| --- | --- | --- | --- | --- | --- | --- |
| `<field>` | `<type>` | Ja/Nei | `<meaning>` | `<key/measure/attribute>` | `<rule>` | `<note>` |

## Må Dekkes

- Eier og kontaktpunkt.
- Konsumenter og bruksområde.
- Kilde, leveranseform og refresh/SLA.
- Radkorn og nøkler.
- Datatyper, null-regler og gyldige verdier.
- Endringsprosess og bakoverkompatibilitet.
- Feilhåndtering og eskalering.
- Sikkerhet, sensitivitet, personvern og lagring.

## Output

Bruk `Data Contract`-malen fra `../fabric-documentation/references/document-templates.md`.
