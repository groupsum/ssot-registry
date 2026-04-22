---
name: ssot-feature
description: Manage feature entities with full CLI coverage, including planning, lifecycle transitions, and dependency/claim/test link management.
---

# SSOT Feature

Use this skill for feature-only operations.

## Command surface

- `feature create|get|list|update|delete|link|unlink|plan`
- `feature lifecycle set`

## Workflow

1. Inspect feature state and links.
2. Apply roadmap targeting with `feature plan`.
3. Update support state with `feature lifecycle set`.
4. Manage claim/test/dependency links with `feature link`/`feature unlink`.

## Operating rules

- Distinguish planning (`plan`) from support policy (`lifecycle`).
- Keep target claim tier and linked claim/test support coherent.
- If the request includes freeze or release progression, escalate to `$ssot-e2e-change-orchestrator`.

## Example

```powershell
ssot feature get . --id feat:demo.login
ssot feature plan . --ids feat:demo.login --horizon current --claim-tier T1 --target-lifecycle-stage active
ssot feature link . --id feat:demo.login --claim-ids clm:demo.login.t1 --test-ids tst:demo.login.integration
```

