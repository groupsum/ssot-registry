---
name: ssot-e2e-portable-lifecycle
description: Run a robust, repeatable, and portable SSOT end-to-end workflow from feature creation through target setting, boundary freeze, test execution, status synchronization, certification, promotion, publication, and closure verification. Use when the user asks for full-lifecycle execution with CLI-grounded gates and fail-closed controls.
---

# SSOT E2E Portable Lifecycle

Use this skill when the user needs one strong workflow pattern that is accurate to the CLI/runtime behavior and portable across repositories.

## Command surface

- Core lifecycle: `feature`, `boundary`, `release`, `validate`
- Proof controls: `claim evaluate`, `evidence verify`, `profile evaluate`
- Fleet status synchronization: `registry sync-statuses`
- Evidence and exports: `evidence update`, `registry export`, `graph export`

## Canonical robust flow

1. Preflight environment
- Use local `uv` venv execution (`uv run ssot ...`) and run `ssot validate . --write-report`.
- Stop immediately on validation failure.

2. Define and target scope
- Create or update features and set planning targets with `feature plan`.
- Ensure target features are in `current` or `explicit` horizon before freeze.

3. Create and freeze boundary
- Create/update boundary membership from target features and profiles.
- Freeze with `boundary freeze` and keep scope stable after this point.

4. Execute tests using a test-runner adapter (test-framework agnostic)
- Enumerate SSOT tests (`test list`) and treat each row as the source of required verification.
- Execute each test row with the repository's native runner based on `test.kind` and `test.path` (do not hard-code a single test framework).
- Persist raw outputs and machine-readable summaries as evidence artifacts.

5. Ingest evidence outcomes and synchronize automated statuses
- Update evidence rows with actual artifact paths and statuses (`passed`/`failed`/`stale`/`collected`) from the real test run.
- Run `registry sync-statuses . --dry-run`, inspect proposed changes, then run `registry sync-statuses .`.
- This recalculates evidence/test/claim/feature/profile status fields from links and artifact truth.

6. Evaluate proof closure and blockers
- Run `claim evaluate` for in-scope claims and `profile evaluate` for boundary profiles.
- Run `evidence verify` for linked evidence.
- Require no open release-blocking issues and no active release-blocking risks for boundary scope.

7. Build release candidate
- Create or update release membership so release claims/evidence cover all boundary features.
- Validate again before certification.

8. Certify, promote, publish (fail-closed)
- `release certify --write-report` (must pass before promotion).
- `release promote` (must pass before publication).
- `release publish` (final publication gate).

9. Post-release status and artifact closure
- Re-run `registry sync-statuses .` and `validate --write-report`.
- Confirm generated snapshots/reports exist for boundary freeze, certification, promotion, and publication.
- Export registry/graph views for audit and portability.

## Operating rules

- Never advance stages when a guard fails.
- Treat `registry sync-statuses` as mandatory after test/evidence updates and after publish.
- Use release actions to advance release and claim publication states; do not force claim publication statuses manually unless recovery is explicitly required.
- Keep test execution adapter-specific, but SSOT commands invariant.

## Minimal command skeleton

```powershell
uv run ssot validate . --write-report
uv run ssot feature plan . --ids feat:example --horizon current --claim-tier T1 --target-lifecycle-stage active
uv run ssot boundary freeze . --boundary-id bnd:example
uv run ssot registry sync-statuses . --dry-run
uv run ssot registry sync-statuses .
uv run ssot release create . --id rel:example --version 0.1.0 --boundary-id bnd:example
uv run ssot release certify . --release-id rel:example --write-report
uv run ssot release promote . --release-id rel:example
uv run ssot release publish . --release-id rel:example
uv run ssot validate . --write-report
```

## References

- `references/portable-gates.md`
- `references/test-adapter-contract.md`

