---
name: ssot-risk
description: Manage risk entities with full CLI coverage, including linkage and mitigation/acceptance/retirement lifecycle operations.
---

# SSOT Risk

Use this skill for risk-only operations.

## Command surface

- `risk create|get|list|update|delete|link|unlink|mitigate|accept|retire`

## Workflow

1. Inspect risk severity, status, and release-blocking flags.
2. Update linked impact context (features/claims/tests/evidence/issues).
3. Transition risk lifecycle with mitigate/accept/retire as policy decisions are made.

## Operating rules

- Treat active release-blocking risks as certification blockers.
- Keep link context current before mitigation or acceptance decisions.
- If the request includes certify/promote/publish progression, escalate to `$ssot-e2e-change-orchestrator`.

## Example

```powershell
ssot risk get . --id rsk:demo.login.availability
ssot risk mitigate . --id rsk:demo.login.availability --note "Mitigated by failover patch"
ssot risk retire . --id rsk:demo.login.availability --note "No remaining exposure in release scope"
```

