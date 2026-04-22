# Boundary-to-Boundary Release Closure Checklist

Beginning boundary:

1. `validate --write-report` passes.
2. Feature targets are set for boundary scope.
3. Boundary scope is complete and frozen.

Pre-release proof:

4. Tests are executed from SSOT test rows.
5. Evidence rows are updated with real artifact status/path.
6. `registry sync-statuses --dry-run` then `registry sync-statuses`.
7. `claim evaluate`, `profile evaluate`, and `evidence verify` pass.
8. No open release-blocking issues and no active release-blocking risks in scope.

Release progression:

9. Release candidate exists and includes full claim/evidence coverage for boundary scope.
10. `release certify --write-report` passes.
11. `release promote` passes.
12. `release publish` passes.

Ending boundary:

13. `registry sync-statuses` and `validate --write-report` pass post-publish.
14. Boundary snapshot and release reports/snapshots exist and are auditable.
15. Registry and graph exports are generated for portability.

