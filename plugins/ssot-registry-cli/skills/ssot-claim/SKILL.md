---
name: ssot-claim
description: Manage claim entities with full CLI coverage, including link management, evaluation, status progression, and tier controls.
---

# SSOT Claim

Use this skill for claim-only operations.

## Command discipline

- Do not spend turns rediscovering syntax with `--help` during normal SSOT work. Use the command surface and examples in this skill directly.
- Pick one verified CLI rail for the repo (`ssot`, `ssot-registry`, `ssot-cli`, or `uv run ssot`) and reuse it consistently by substituting that rail into the examples below.
- Only inspect parser or help text when the user explicitly asks about the CLI surface or when observed runtime behavior contradicts the command patterns documented here.
## Command surface

- `claim create|get|list|update|delete|link|unlink|evaluate|set-status|set-tier`

## Workflow

1. Inspect current claim support graph.
2. Update claim metadata and links to features/tests/evidence.
3. Evaluate claim support and adjust tier/status when policy requires explicit updates.

## Operating rules

- Keep claim status and tier separate: lifecycle maturity vs assurance strength.
- Prefer evidence/test linkage plus evaluation before manual status escalation.
- Do not repurpose a lower-tier claim row into a higher-tier claim when the lower-tier proof must remain visible. Create the new higher-tier claim row and link it alongside the existing lower-tier claims.
- Promotion across tiers is additive: linking a `T2` claim to a feature does not justify unlinking its existing `T0` or `T1` claims.
- If the request includes certify/promote/publish progression, escalate to `$ssot-e2e-change-orchestrator`.

## Example

```powershell
ssot claim get . --id clm:demo.login.t1
ssot claim link . --id clm:demo.login.t1 --feature-ids feat:demo.login --test-ids tst:demo.login.integration
ssot claim evaluate . --claim-id clm:demo.login.t1
```
