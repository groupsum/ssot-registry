---
name: ssot-boundary
description: Manage boundary entities with full CLI coverage, including scoped feature/profile membership and freeze operations.
---

# SSOT Boundary

Use this skill for boundary-only operations.

## Command surface

- `boundary create|get|list|update|delete|add-feature|remove-feature|add-profile|remove-profile|freeze`

## Workflow

1. Inspect current scoped features/profiles.
2. Add or remove scope members explicitly.
3. Freeze boundary when scope is final for release evaluation.

## Operating rules

- Freeze is a hard scope gate; avoid post-freeze scope churn.
- Confirm in-scope features are targeted appropriately before freezing.
- If the request includes release certify/promote/publish, escalate to `$ssot-e2e-change-orchestrator`.

## Example

```powershell
ssot boundary get . --id bnd:demo.v1
ssot boundary add-feature . --id bnd:demo.v1 --feature-ids feat:demo.login feat:demo.audit
ssot boundary freeze . --boundary-id bnd:demo.v1
```

