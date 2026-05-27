# UiT Visual Profile For Deck Generation

Use this as the practical deck-generation subset of UiT's official visual
profile. Prefer official UiT PowerPoint templates over hand-built styling.

## Official Sources

- UiT logo page:
  https://uit.no/ansatte/kommunikasjonstips/grafisk/profilmanual/sub?p_document_id=861333
- UiT colors:
  https://uit.no/ansatte/kommunikasjonstips/grafisk/profilmanual/sub?p_document_id=861335
- UiT profile and diagonal elements:
  https://uit.no/ansatte/kommunikasjonstips/grafisk/profilmanual/sub?p_document_id=861336
- UiT PowerPoint and Word templates:
  https://uit.no/ansatte/kommunikasjonstips/grafisk/maler/sub?p_document_id=861316
- Downloaded assets in this skill:
  `assets/UiT_logo_Bokmaal.zip`, `assets/UiT_fargekart_CMYK.pdf`,
  `assets/uit-logo-bokmal/`.

## Template Rule

UiT states that standardized templates should be used for documents where UiT
is the sender, and that separate templates for sections, faculties, or centers
should not be used. For generated decks:

- Start from an official UiT PowerPoint template or an existing deck built on
  that template.
- Preserve slide size, master/layouts, background graphics, fonts, and built-in
  placeholders unless they are empty artifacts after generation.
- Do not recreate the logo, seal, or profile graphics manually when the
  template already provides them.

## Colors

Official palette:

| Name | RGB | Hex | Use |
| --- | --- | --- | --- |
| Main dark blue | 0, 51, 73 | `#003349` | primary brand color, headings, dark backgrounds |
| Blue | 0, 115, 150 | `#007396` | secondary accents, charts, diagrams |
| Light blue | 89, 190, 201 | `#59BEC9` | light accents, fills, information surfaces |
| Red | 203, 51, 59 | `#CB333B` | warning/decision emphasis, sparse accents |
| Yellow | 242, 169, 0 | `#F2A900` | highlight/accent, sparse use |
| Black/white | standard | `#000000` / `#FFFFFF` | text and surfaces |

The local generator may use pale tints for readability, but should not drift
into a new palette.

## Background And Text Combinations

Use these default combinations:

| Background | Primary text | Accent | Notes |
| --- | --- | --- | --- |
| White | dark blue or near-black | red/yellow/blue | safest for dense executive content |
| Dark blue | white | yellow or light blue | use for cover, divider, closing, strong message |
| Light blue tint | dark blue or near-black | dark blue/red | good for explainers and cards |
| Red | white | dark blue only if contrast holds | use rarely for risk/decision emphasis |
| Yellow | dark blue or black | dark blue | use sparingly; avoid large dense text blocks |

Do not use color as the only carrier of meaning. Use labels, ordering, or icons
as well.

## Logo Rules

Practical rules from the official profile:

- Use UiT logo with seal and name mark in official templates.
- Do not alter the logo, colors, proportions, typography, or composition.
- Use the dark blue logo as default; use positive/negative variants only where
  contrast requires it.
- Do not place the logo on noisy or low-contrast backgrounds.
- If using the seal alone, ensure it is large enough to be readable.

## Graphics

UiT's profile uses a diagonal element and profile/ray element. For generated
PowerPoints:

- Prefer the template's existing diagonal/profile graphics.
- If a slide needs a simple manual accent, use restrained diagonal/vertical
  blocks in official colors.
- Do not overuse decorative rays or rebuild the profile element unless a real
  official asset is available.
- For charts, use dark blue as the base series, blue/light blue for secondary
  series, red for negative/risk, and yellow for highlight. Keep labels visible.

## Presentation Accessibility

Official UiT presentation guidance emphasizes:

- short, descriptive titles
- limited information per slide
- using images, charts, and illustrations where they aid understanding
- not using text smaller than 24 pt as a general rule
- good contrast between background and text

For dense internal executive decks, smaller supporting text may be necessary,
but the generator should keep headings large and body text concise.
