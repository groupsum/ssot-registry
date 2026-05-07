# Boundary-to-Boundary Release Closure Checklist

Beginning boundary:

1. `validate --write-report` passes.
2. Feature targets are set for boundary scope.
3. Boundary scope is complete and frozen.

Post-freeze delivery:

4. Frozen-scope runtime implementation, schema, migration, and required test changes are actually landed.
5. Code-first and tests-first are both acceptable, but runtime code and required tests both exist before verification begins.
6. Required functional tests cover happy paths, unhappy paths, valid and invalid inputs, expected outputs, and observable behavior.
7. Required performance and conformance tests exist when requested, feature-required, or tier-required.
8. Feature implementation statuses match repo reality.

Pre-release proof:

9. Tests are executed from SSOT test rows.
10. Evidence rows are updated with real artifact status/path.
11. `registry sync-statuses --dry-run` then `registry sync-statuses`.
12. `claim evaluate`, `profile evaluate`, and `evidence verify` pass.
13. No open release-blocking issues and no active release-blocking risks in scope.

Release progression:

14. Release candidate exists and includes full claim/evidence coverage for boundary scope.
15. `release certify --write-report` passes.
16. `release promote` passes.
17. `release publish` passes.

Ending boundary:

18. `registry sync-statuses` and `validate --write-report` pass post-publish.
19. Boundary snapshot and release reports/snapshots exist and are auditable.
20. Registry and graph exports are generated for portability.
