---
name: ssot-release
description: Manage release entities with full CLI coverage, including claim/evidence membership and certify/promote/publish/revoke progression.
---

# SSOT Release

Use this skill for release-only operations.

## Command surface

- `release create|get|list|update|delete`
- `release add-claim|remove-claim|add-evidence|remove-evidence`
- `release certify|promote|publish|revoke`

## Workflow

1. Inspect release/boundary linkage and current status.
2. Maintain claim/evidence membership completeness.
3. Progress gates in strict order: certify -> promote -> publish.

## Operating rules

- Fail closed: never promote or publish when prerequisite gates fail.
- Keep release claim/evidence sets aligned with frozen boundary scope.
- For full decision-to-release orchestration, escalate to `$ssot-e2e-change-orchestrator`.

## Example

```powershell
ssot release get . --id rel:demo.v1
ssot release add-claim . --id rel:demo.v1 --claim-ids clm:demo.login.t1
ssot release certify . --release-id rel:demo.v1 --write-report
ssot release promote . --release-id rel:demo.v1
ssot release publish . --release-id rel:demo.v1
```

