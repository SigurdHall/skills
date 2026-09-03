---
name: fabric-item-authoring
description: Use whenever creating, updating, renaming, deploying, or deleting a Microsoft Fabric item. Routes work to the narrow item-specific skills-for-fabric workflow and enforces capability, snapshot, dependency, drift, long-running-operation, verification, and recovery gates.
---

# Fabric Item Authoring

Route Fabric item changes through the narrowest supported authoring skill. This
skill owns lifecycle safety and orchestration; it does not duplicate item
payloads, REST endpoints, or specialist mechanics from `skills-for-fabric`.

## Workflow

1. Identify the exact item type, operation, workspace, environment, target
   identity, dependencies, and success check. Treat "object" as ambiguous until
   the Fabric item type is known.
2. Read [item-routing-matrix.md](references/item-routing-matrix.md) and confirm
   which `skills-for-fabric` source is active in this session:

   - Claude Code (local or cloud): the `fabric-collection` plugins declared in
     this repo's `.claude/settings.json`, pinned to one upstream tag. Confirm
     with `claude plugin list`; skills appear as `fabric-skills:<skill>` and
     `powerbi-authoring:<skill>`.
   - Codex on Windows: the `C:\repos\skills-for-fabric` checkout and its
     junctions. When availability is uncertain, run:

   ```powershell
   $env:UV_CACHE_DIR = 'C:\repos\skills\.uv-cache'
   uv run C:\repos\skills\skills\fabric\fabric-item-authoring\scripts\inventory_fabric_skills.py `
     C:\repos\skills-for-fabric `
     --junction-root C:\repos\.agents\skills `
     --junction-root C:\repos\.claude\skills
   ```

   For the plugin route, point the same script at the marketplace clone and
   the installed bundle's `skills` folder:

   ```bash
   python skills/fabric/fabric-item-authoring/scripts/inventory_fabric_skills.py \
     ~/.claude/plugins/marketplaces/fabric-collection \
     --additional-skills-root ~/.claude/plugins/cache/fabric-collection/fabric-skills/<version>/skills
   ```

   Record the selected Git commit, dirty state, package version, and duplicate
   names.

3. Check the current Microsoft item-management matrix and the item-specific
   definition documentation. A definition-format reference is not proof that
   create, update, delete, service-principal access, or Git integration is
   supported.
4. Route to the dedicated `*-authoring-*` skill. Pair it with the matching
   consumption or operations skill for read-back and runtime verification.
5. Apply every applicable gate in
   [lifecycle-gates.md](references/lifecycle-gates.md): capability, authority,
   snapshot, dependencies, validation, apply, long-running-operation polling,
   read-back, and recovery evidence.
6. For repeated multi-item deployment, prefer `fabric-cicd` and an ordered
   dependency manifest. Use direct REST for a bounded item operation where the
   official contract is explicit.
7. Report separately what was planned, changed, API-accepted, read back, and
   runtime-verified. Never equate HTTP acceptance with a working item.

Use this status block in the handoff:

```text
Planned:
Mutated:
API accepted / LRO terminal:
Read back:
Runtime verified:
Recovery evidence:
Open gaps:
```

## Stop Conditions

- Do not invent a generic item definition when no current official definition
  contract exists.
- Do not mutate before workspace and item identity are unambiguous.
- Do not send secrets or connection credentials in chat, source files, or logs.
- Do not delete, overwrite a complete definition, or detach dependencies
  without an explicit snapshot and user-confirmed scope.
- If no dedicated skill exists, produce a capability-gated implementation plan
  and propose the narrow missing skill. The only exception is an explicitly
  bounded partial route in the routing matrix: stay inside its documented item
  shape and verification rules. Do not silently expand a partial route or turn
  this router into a second source of endpoint truth.
- When an item-specific skill has a stricter or more precise verification rule,
  follow it and record the exception; this router must not create conflicting
  API guidance.

## Resources

- [item-routing-matrix.md](references/item-routing-matrix.md): current local
  coverage, ownership, and gaps.
- [lifecycle-gates.md](references/lifecycle-gates.md): official-source gates for
  item definitions, authentication, connections, Git, CI/CD, polling, and
  recovery.
- [deployment-promotion.md](references/deployment-promotion.md): environment
  mapping, dependency, evidence, and rollback contract for test-to-production.
- `scripts/inventory_fabric_skills.py`: metadata-only inventory of an installed
  `skills-for-fabric` tree and its discovery junctions.
