---
name: ssot-scope-to-frozen-boundary
description: Drive SSOT target-setting from planned features to a frozen delivery boundary, including profile inclusion, boundary creation, pre-freeze validation, and freeze. Use when Codex needs to take already-defined scope and turn it into an immutable delivery boundary.
---

# SSOT Scope To Frozen Boundary

Use this skill after ADRs, SPECs, and features already exist and the task is to turn scope into a frozen boundary.

## Workflow

1. Inspect the target features and any profiles that should expand boundary scope.
2. Ensure planned features are current or explicitly allowed.
3. Create or update the boundary with feature IDs and optional profile IDs.
4. Validate repo state if scope coherence is uncertain.
5. Freeze the boundary and confirm the snapshot-producing step succeeded.

## Operating rules

- Treat freeze as the point where scope stops changing.
- Treat freeze as a scope lock only; implementation, migration, and verification usually still need to happen after this skill finishes.
- Require all in-scope features to be current or explicit before freeze.
- Prefer a single authoritative boundary row over ad hoc feature lists in later commands.
- If the request still needs ADR, SPEC, or feature creation, hand off to `$ssot-decision-to-scope`.
- If the request includes implementation, migration, or release work, escalate to `$ssot-e2e-change-orchestrator`.

## Common commands

```powershell
ssot feature get . --id feat:demo.change
ssot boundary list .
ssot boundary create . --id bnd:demo.change --title "Demo change boundary" --feature-ids feat:demo.change
ssot boundary add-profile . --boundary-id bnd:demo.change --profile-ids prf:demo.bundle
ssot validate .
ssot boundary freeze . --boundary-id bnd:demo.change
```

## References

- `references/freeze-readiness.md`
- `references/profile-boundary-notes.md`
