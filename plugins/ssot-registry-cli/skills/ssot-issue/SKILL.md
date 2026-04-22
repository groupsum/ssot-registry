---
name: ssot-issue
description: Manage issue entities with full CLI coverage, including planning, release-blocking semantics, and close/reopen lifecycle transitions.
---

# SSOT Issue

Use this skill for issue-only operations.

## Command surface

- `issue create|get|list|update|delete|link|unlink|plan|close|reopen`

## Workflow

1. Inspect issue state and linked impact surfaces.
2. Update issue metadata, severity, and release-blocking flags.
3. Plan or close/reopen according to current delivery state.

## Operating rules

- Treat release-blocking issues as gating artifacts for certification.
- Keep linked feature/claim/test/evidence/risk context accurate.
- If the request spans boundary/release progression, escalate to `$ssot-e2e-change-orchestrator`.

## Example

```powershell
ssot issue get . --id iss:demo.login.blocker
ssot issue plan . --ids iss:demo.login.blocker --horizon current
ssot issue close . --id iss:demo.login.blocker
```

