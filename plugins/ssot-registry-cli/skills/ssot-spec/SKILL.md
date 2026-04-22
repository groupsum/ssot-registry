---
name: ssot-spec
description: Manage SPEC entities with full CLI coverage, including ADR link management, status/supersede flows, sync, and reservation operations.
---

# SSOT SPEC

Use this skill for SPEC-only work.

## Command surface

- `spec create|get|list|update|link|unlink|set-status|supersede|delete|sync`
- `spec reserve create|list`

## Workflow

1. Inspect with `spec get` or `spec list`.
2. Update text/status with `spec update` and `spec set-status`.
3. Maintain ADR linkage with `spec link`/`spec unlink`.
4. Use `spec supersede` for continuity and `spec sync` for metadata refresh.

## Operating rules

- Keep SPECs declarative and maintain ADR linkage through CLI links.
- Prefer supersede to preserve historical traceability.
- If the request spans SPECs plus freeze/certify/promote/publish, escalate to `$ssot-e2e-change-orchestrator`.

## Example

```powershell
ssot spec get . --id spec:2001
ssot spec link . --id spec:2001 --adr-ids adr:1001
ssot spec set-status . --id spec:2001 --status approved --note "Ready for targeted implementation"
ssot spec sync .
```

