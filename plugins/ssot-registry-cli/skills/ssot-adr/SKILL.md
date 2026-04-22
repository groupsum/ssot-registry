---
name: ssot-adr
description: Manage ADR entities with full CLI coverage, including create/update/status/supersede/sync and reservation flows. Use for ADR-focused operations that should stay within the ADR surface.
---

# SSOT ADR

Use this skill for ADR-only work.

## Command surface

- `adr create|get|list|update|set-status|supersede|delete|sync`
- `adr reserve create|list`

## Workflow

1. Inspect with `adr get` or `adr list`.
2. Mutate content/status with `adr update` or `adr set-status`.
3. Use `adr supersede` for lineage instead of deleting historical ADRs.
4. Run `adr sync` after document edits that should refresh registry metadata.

## Operating rules

- Preserve ADR lineage and status history.
- Prefer reserve flows before creating numbered ADRs when ranges are constrained.
- If the request includes SPEC + feature + boundary + release lifecycle steps, escalate to `$ssot-e2e-change-orchestrator`.

## Example

```powershell
ssot adr get . --id adr:1001
ssot adr update . --id adr:1001 --title "Updated ADR title"
ssot adr set-status . --id adr:1001 --status approved --note "Approved for current release scope"
ssot adr sync .
```

