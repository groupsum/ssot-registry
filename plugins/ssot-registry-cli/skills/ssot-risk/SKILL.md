---
name: ssot-risk
description: Manage risk entities with full CLI coverage, including linkage and mitigation/acceptance/retirement lifecycle operations.
---

# SSOT Risk

Use this skill for risk-only operations.

## Command discipline

- Do not spend turns rediscovering syntax with `--help` during normal SSOT work. Use the command surface and examples in this skill directly.
- Pick one verified CLI rail for the repo (`ssot`, `ssot-registry`, `ssot-cli`, or `uv run ssot`) and reuse it consistently by substituting that rail into the examples below.
- Only inspect parser or help text when the user explicitly asks about the CLI surface or when observed runtime behavior contradicts the command patterns documented here.
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

