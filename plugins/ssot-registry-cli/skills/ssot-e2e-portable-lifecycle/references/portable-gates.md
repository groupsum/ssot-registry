# Portable Lifecycle Gates

Use these gates in order:

1. `validate` passes before scope edits.
2. Target features are planned (`current` or `explicit`) before freeze.
3. Boundary is frozen before release creation.
4. Test executions produce evidence artifacts, then `registry sync-statuses` persists derived statuses.
5. Claim/profile/evidence evaluations pass before certify.
6. Release certify must pass before promote.
7. Release promote must pass before publish.
8. `validate` and exports run after publish for closure.

Fail-closed behavior:

- If any gate fails, stop progression and fix upstream data, links, evidence, or blockers first.
- Do not skip from certify directly to publish.

