---
name: ssot-entity-analyze
description: Analyze SSOT entities and their relationships across families using CLI exports and graph-aware views. Use when Codex must explain cross-entity coverage, gaps, dependency chains, or risk/release impact.
---

# SSOT Entity Analyze

Use this skill when the user asks for cross-entity analysis rather than single-row inspection.

## Command surface

- Family snapshots: `<entity> list`
- Registry-wide views: `registry export`
- Relationship views: `graph export`
- Quality baseline: `validate`

## Workflow

1. Pull focused lists for in-scope families.
2. Export graph/registry views for cross-entity joins.
3. Compute the requested analysis shape: coverage, missing links, dependency chains, bottlenecks, or release blockers.
4. Validate registry health when analysis leads to corrective recommendations.

## Operating rules

- Use graph exports for relationship claims; do not infer edges from naming conventions.
- Keep analysis reproducible by citing exact CLI commands used.
- If the request turns into lifecycle execution, hand off to `$ssot-e2e-change-orchestrator`.

## Examples

```powershell
ssot-registry graph export . --format json --output .tmp/graph.json
ssot-registry registry export . --format json --output .tmp/registry.json
ssot-registry feature list .
ssot-registry validate . --write-report
```

