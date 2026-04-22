---
name: ssot-claim
description: Manage claim entities with full CLI coverage, including link management, evaluation, status progression, and tier controls.
---

# SSOT Claim

Use this skill for claim-only operations.

## Command surface

- `claim create|get|list|update|delete|link|unlink|evaluate|set-status|set-tier`

## Workflow

1. Inspect current claim support graph.
2. Update claim metadata and links to features/tests/evidence.
3. Evaluate claim support and adjust tier/status when policy requires explicit updates.

## Operating rules

- Keep claim status and tier separate: lifecycle maturity vs assurance strength.
- Prefer evidence/test linkage plus evaluation before manual status escalation.
- If the request includes certify/promote/publish progression, escalate to `$ssot-e2e-change-orchestrator`.

## Example

```powershell
ssot claim get . --id clm:demo.login.t1
ssot claim link . --id clm:demo.login.t1 --feature-ids feat:demo.login --test-ids tst:demo.login.integration
ssot claim evaluate . --claim-id clm:demo.login.t1
```

