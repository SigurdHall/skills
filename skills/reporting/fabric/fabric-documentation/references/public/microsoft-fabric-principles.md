# Microsoft Fabric Documentation Principles

Kildene under ble kontrollert 2026-05-26. Bruk dem som normgivende retning, men sjekk Microsoft Learn på nytt ved produksjonsnære beslutninger.

## Git Og Item Definitions

- Fabric Git integration er workspace-basert og bevarer workspace-struktur i Git.
- Git integration støtter blant annet notebooks, lakehouse, dataflows, pipelines, reports og semantic models, men støttegrad og preview-status kan endres.
- Hver Fabric item-mappe inneholder item definition files og automatisk genererte systemfiler. Frie dokumentasjonsfiler bør normalt ligge i `docs/` eller tilsvarende, ikke blandes inn i item definition-mapper uten eksplisitt grunn.
- Fabric Git integration brukes for backup, versjonering, samarbeid via branches og source-control arbeidsflyt.
- Lifecycle-dokumentasjon bør beskrive dev/test/prod, permissions, branch-policy, deployment pipeline, parametere og hvem som godkjenner produksjonssetting.

Kilder:

- Microsoft Learn: Git source code format, https://learn.microsoft.com/en-us/fabric/cicd/git-integration/source-code-format
- Microsoft Learn: Get started with Git integration, https://learn.microsoft.com/en-us/fabric/cicd/git-integration/git-get-started
- Microsoft Learn: What is Microsoft Fabric Git integration, https://learn.microsoft.com/en-us/fabric/cicd/git-integration/intro-to-git-integration
- Microsoft Learn: Best practices for lifecycle management in Fabric, https://learn.microsoft.com/en-us/fabric/cicd/best-practices-cicd

## Star Schema Og Semantic Models

- Star schema er anbefalt analytisk modellmønster for Fabric Warehouse og enterprise Power BI semantic models.
- Faktatabeller lagrer hendelser, observasjoner, målinger og dimensjonsnøkler.
- Dimensjonstabeller beskriver analyseentiteter og brukes til filtrering, gruppering og hierarkier.
- Dokumentasjon skal eksplisitt angi radkorn for fakta, naturlige nøkler eller surrogate keys, relasjoner, SCD/historikkvalg og aggregeringsregler.
- Power BI-modeller bør beskrive role-playing dimensions, degenerate dimensions, factless facts og bridge-tabeller når de brukes.

Kilder:

- Microsoft Learn: Understand star schema and the importance for Power BI, https://learn.microsoft.com/en-us/power-bi/guidance/star-schema
- Microsoft Learn: Dimensional modeling in Microsoft Fabric Warehouse, https://learn.microsoft.com/en-us/fabric/data-warehouse/dimensional-modeling-overview

## BI Strategy Og Governance

- Dokumenter BI-løsninger med tydelig skille mellom data product, semantisk modell, rapport og driftsprosess.
- Beskriv eierskap, målgruppe, godkjenningsflyt, support, endringshåndtering og risiko.
- For offentlig sektor, økonomi og persondata må dokumentasjonen dekke tilgang, dataminimering, sporbarhet, behandlingsgrunnlag og internkontroll.

Kilder:

- Microsoft Learn: Power BI implementation planning, https://learn.microsoft.com/en-us/power-bi/guidance/powerbi-implementation-planning-bi-strategy-overview

## Skills Best Practice Fra GitHub-Eksempler

- Skill-mapper bør være selvstendige og ha `SKILL.md` med YAML-frontmatter.
- `description` må være trigger-orientert og nevne konkrete oppgaver der skillen skal brukes.
- Hold hovedinstruksene korte; flytt detaljer, maler og kilder til `references/`.
- Bruk scripts bare der deterministisk eller repetitiv behandling trengs.
- Ikke stol blindt på eksempelskills; test dem i eget miljø før kritisk bruk.

Kilder:

- Anthropic skills repository, https://github.com/anthropics/skills
- Anthropic skill-creator example, https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md

