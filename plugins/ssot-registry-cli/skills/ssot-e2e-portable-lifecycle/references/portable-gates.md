# Portable Lifecycle Gates

Use these gates in order:

1. `validate` passes before scope edits.
2. Target features are planned (`current` or `explicit`) before freeze.
3. Boundary is frozen before release creation.
4. Post-freeze runtime implementation, migration work, and required tests are complete before verification begins.
5. Test executions produce evidence artifacts, then `registry sync-statuses` persists derived statuses.
6. Claim/profile/evidence evaluations pass before certify.
7. Release certify must pass before promote.
8. Release promote must pass before publish.
9. `validate` and exports run after publish for closure.

Fail-closed behavior:

- If any gate fails, stop progression and fix upstream data, links, evidence, or blockers first.
- Code-first and tests-first are both valid, but both runtime code and required tests must exist before verification, proof closure, or certification.
- Required tests cover happy paths, unhappy paths, valid and invalid inputs, expected outputs, and observable behavior. Include performance and conformance tests when requested or required by the feature or claim tier.
- Do not skip from freeze directly to verify, proof closure, or certify.
- Do not skip from certify directly to publish.
