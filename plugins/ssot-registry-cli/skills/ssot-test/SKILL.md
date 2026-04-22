---
name: ssot-test
description: Manage test entities with full CLI coverage, including feature/claim/evidence linkage and path-focused verification setup.
---

# SSOT Test

Use this skill for test-only operations.

## Command surface

- `test create|get|list|update|delete|link|unlink`

## Workflow

1. Inspect current test coverage and links.
2. Create/update test rows with stable `test.path` values.
3. Link tests to features, claims, and evidence rows.

## Operating rules

- Treat test rows as registry truth for verification scope, independent of test framework.
- Keep claim/evidence links complete so status synchronization can derive accurate states.
- If the request includes full release closure, escalate to `$ssot-e2e-change-orchestrator`.

## Example

```powershell
ssot test get . --id tst:demo.login.integration
ssot test update . --id tst:demo.login.integration --test-path tests/test_login.py
ssot test link . --id tst:demo.login.integration --feature-ids feat:demo.login --claim-ids clm:demo.login.t1
```

