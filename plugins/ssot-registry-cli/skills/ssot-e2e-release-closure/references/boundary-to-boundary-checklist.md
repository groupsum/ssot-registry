# Boundary-to-Boundary Release Closure Checklist

Beginning boundary:

1. `validate --write-report` passes.
2. Feature targets are set for boundary scope.
3. Boundary scope is complete and frozen.

Post-freeze delivery:

4. Frozen-scope implementation, schema, migration, and test changes are actually landed.
5. Feature implementation statuses match repo reality.

Pre-release proof:

6. Tests are executed from SSOT test rows.
7. Evidence rows are updated with real artifact status/path.
8. `registry sync-statuses --dry-run` then `registry sync-statuses`.
9. `claim evaluate`, `profile evaluate`, and `evidence verify` pass.
10. No open release-blocking issues and no active release-blocking risks in scope.

Release progression:

11. Release candidate exists and includes full claim/evidence coverage for boundary scope.
12. `release certify --write-report` passes.
13. `release promote` passes.
14. `release publish` passes.

Ending boundary:

15. `registry sync-statuses` and `validate --write-report` pass post-publish.
16. Boundary snapshot and release reports/snapshots exist and are auditable.
17. Registry and graph exports are generated for portability.
