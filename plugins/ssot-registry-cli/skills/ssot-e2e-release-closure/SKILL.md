---
name: ssot-e2e-release-closure
description: Execute end-to-end release closure from beginning boundary setup through freeze, post-freeze implementation and verification, publication, and ending boundary verification, with fail-closed gates and mandatory status synchronization.
---

# SSOT E2E Release Closure

Use this skill when the request is boundary-to-boundary release execution, not just partial release commands.

## Command surface

- Scope and boundary: `feature plan`, `boundary create|add-feature|add-profile|freeze`
- Verification closure: `test list`, `evidence update`, `claim evaluate`, `profile evaluate`, `evidence verify`
- Status convergence: `registry sync-statuses`
- Release progression: `release create|add-claim|add-evidence|certify|promote|publish`
- Guards and evidence artifacts: `validate`, `registry export`, `graph export`

## Boundary-to-boundary flow

1. Beginning boundary preflight
- Run `ssot validate . --write-report`.
- Inspect target features/profiles and ensure boundary scope inputs are explicit.

2. Beginning boundary setup
- Create/update boundary scope from target features/profiles.
- Freeze boundary with `boundary freeze`.
- Treat freeze as the point where scope is locked; it does not mean the frozen work is already implemented or certifiable.

3. Post-freeze implementation delivery
- Implement the frozen scope in code, schema, migrations, and repo-native tests before attempting proof closure.
- Keep feature implementation state aligned with the code that actually landed.

4. Verification execution and evidence ingestion
- Treat `test list` rows as required verification set.
- Execute repo-native tests per `test.kind`/`test.path`.
- Update evidence rows with real artifact outcomes and paths.

5. Status convergence checkpoint (mandatory)
- Run `registry sync-statuses --dry-run`, review deltas, then apply `registry sync-statuses`.
- Re-run `validate --write-report`.

6. Proof closure and blockers
- Run `claim evaluate`, `profile evaluate`, and `evidence verify` for boundary scope.
- Ensure no open release-blocking issues and no active release-blocking risks in boundary scope.

7. Release candidate assembly
- Create/update release bound to the frozen boundary.
- Ensure release claim/evidence membership fully covers boundary feature scope.

8. Certify, promote, publish (strict order)
- `release certify --write-report` must pass before promotion.
- `release promote` must pass before publication.
- `release publish` is final progression gate.

9. Ending boundary closure verification
- Re-run `registry sync-statuses` and `validate --write-report`.
- Confirm boundary/release snapshots and certification/promotion/publication reports exist.
- Export registry and graph views for audit portability.

## Operating rules

- Fail closed at every gate. Do not advance if any required guard fails.
- Do not skip from `boundary freeze` straight to `release certify`; the expected middle is implementation plus real verification evidence.
- Treat `registry sync-statuses` as required after evidence updates and after publish.
- Do not force claim publication statuses manually; use release progression to advance them.
- If request scope broadens beyond release closure (for example ADR/SPEC authoring or major implementation planning), escalate to `$ssot-e2e-change-orchestrator`.

## Minimal command skeleton

```powershell
uv run ssot validate . --write-report
uv run ssot boundary freeze . --boundary-id bnd:example
# implement the frozen change and execute repo-native verification here
uv run ssot registry sync-statuses . --dry-run
uv run ssot registry sync-statuses .
uv run ssot validate . --write-report
uv run ssot release create . --id rel:example --version 0.1.0 --boundary-id bnd:example
uv run ssot release certify . --release-id rel:example --write-report
uv run ssot release promote . --release-id rel:example
uv run ssot release publish . --release-id rel:example
uv run ssot registry sync-statuses .
uv run ssot validate . --write-report
```

## References

- `references/boundary-to-boundary-checklist.md`
- `../ssot-e2e-change-orchestrator/references/dispatch-policy.md`
