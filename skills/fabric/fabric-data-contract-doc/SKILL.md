---
name: fabric-data-contract-doc
description: Lag datakontrakter i Markdown for Fabric data products, lakehouse/warehouse-tabeller, semantic model-kilder, API/fil-leveranser, økonomidata, kontrollregler, SLA, skjemaendringer og eierskap. Use when documenting table contracts, source-to-Fabric interfaces, data quality rules, schema requirements, refresh expectations, consumer obligations, or public-sector/finance data governance.
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

