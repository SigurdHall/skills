---
name: fabric-cicd-governance-doc
description: Document or design Fabric Git integration, CI/CD, deployment pipelines, branch policy, dev/test/prod, workspace permissions, release process, governance, ownership, auditability, operations, and risk controls. Use when the user asks for Fabric lifecycle, deployment, release, runbook, production readiness, governance model, tilgangsstyring, kontrollopplegg, public-sector control documentation, or safe deployment practices in Markdown.
---

# Fabric CI/CD Governance Doc

## Arbeidsflyt

1. Bruk `fabric-documentation` som hovedramme.
2. Les `../fabric-documentation/references/microsoft-fabric-principles.md`.
3. Kartlegg repo, branch, Fabric workspace, miljøer og deployment pipeline.
4. Dokumenter hvem som kan endre kildekode, hvem som kan deploye, og hvem som godkjenner.
5. Skill utvikling, test, produksjon og nødretting.
6. For PBIP/TMDL, bruk `powerbi-pbip` for tekniske valideringspunkter.

## Må Dekkes

- Git-provider, repo, branch og mappe.
- Workspace per miljø og kobling til deployment pipeline.
- Parametere og miljøspesifikke verdier.
- Roller: utvikler, data owner, report owner, reviewer, approver, workspace admin.
- PR-/review-regler.
- Test og rollback.
- Produksjonssetting og kommunikasjon.
- Logging, auditability og hendelseshåndtering.
- Sikkerhet, sensitivitet, tilgang og service principals.

## Kontrollpunkter

- Ingen hemmeligheter i repo.
- Ingen produksjonsdata i dev/test uten avklart behov.
- RLS/OLS og sensitivity labels kontrolleres etter deploy.
- Refresh credentials og gateways er dokumentert uten å eksponere secrets.
- Deployment-regler og parametere er dokumentert.

## Output

Bruk `CI/CD And Governance`-malen fra `../fabric-documentation/references/document-templates.md`.
