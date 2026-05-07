# Test Adapter Contract

This workflow is test-framework agnostic. Keep the adapter contract stable:

Inputs from SSOT:

- `test.id`
- `test.kind`
- `test.path`
- linked `feature_ids`, `claim_ids`, `evidence_ids`

Adapter responsibilities:

1. Confirm the frozen-scope runtime implementation and required test files exist before verification starts.
2. Resolve the repository's runner strategy for each test row.
3. Execute the test and capture machine-readable result + logs.
4. Write artifacts to stable paths referenced by SSOT evidence rows.
5. Produce normalized outcome values: `passed`, `failed`, `stale`, or `collected`.

Required functional coverage:

- happy paths
- unhappy paths
- valid and invalid inputs
- expected outputs
- observable behavior
- performance and conformance cases when requested, feature-required, or tier-required

Downstream SSOT updates:

1. `evidence update` to set `status`, `tier` (if needed), and `evidence-path`.
2. `registry sync-statuses --dry-run` then `registry sync-statuses`.
3. Re-run `validate` before release certification.
