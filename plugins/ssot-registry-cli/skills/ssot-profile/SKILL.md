---
name: ssot-profile
description: Manage profile entities with full CLI coverage, including composition links and profile evaluation/verification.
---

# SSOT Profile

Use this skill for profile-only operations.

## Command surface

- `profile create|get|list|update|delete|link|unlink|evaluate|verify`

## Workflow

1. Inspect profile configuration and composed feature/profile links.
2. Update profile metadata and composition links.
3. Evaluate or verify profile guard behavior.

## Operating rules

- Keep profile composition explicit through link/unlink operations.
- Use evaluate/verify before release gating decisions.
- If the request extends into release lifecycle progression, escalate to `$ssot-e2e-change-orchestrator`.

## Example

```powershell
ssot profile get . --id prf:demo.core
ssot profile link . --id prf:demo.core --feature-ids feat:demo.login
ssot profile evaluate . --profile-id prf:demo.core
```

