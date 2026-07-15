# Fabric Platform Skills

This top-level group owns reusable Microsoft Fabric platform operations and
routing. It does not replace `skills-for-fabric` item mechanics or the
documentation skills under `reporting/fabric/`.

Current skill:

- `fabric-item-authoring` — route Fabric item creation, update, deployment, and
  deletion through current item-specific skills and lifecycle gates.

Rules:

- Verify current Microsoft capability and the installed `skills-for-fabric`
  version on every live authoring run.
- Keep endpoint payload mechanics in `skills-for-fabric`; keep this group thin.
- Separate planning, mutation acceptance, read-back, and runtime verification.
- Require snapshots and explicit scope for destructive or overwrite operations.
