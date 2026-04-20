---
name: ssot-feature-test-linking
description: Create, inspect, update, delete, link, and unlink SSOT features and tests together with their immediate verification edges. Use when Codex needs to wire feature-to-test coverage, add or remove test paths, or keep feature, test, claim, and evidence links symmetric enough for evaluation and release guards.
---

# SSOT Feature/Test Linking

Use this skill when the user is focused on coverage wiring between features and tests. This is narrower than general feature CRUD: the main job is keeping verification edges coherent after adding or changing tests.

## Command surface

- Features: `feature link|unlink|get|list`
- Tests: `test create|get|list|update|delete|link|unlink`
- Companion edges often needed in the same change: `claim link|unlink`, `evidence link|unlink`

## Linking order

1. Confirm the feature and test rows exist; create the test row first if needed.
2. Link the feature to the test with `feature link --test-ids ...`.
3. Link the test back to the feature with `test link --feature-ids ...`.
4. If the test is proving a claim or producing evidence, add those reciprocal links in the same pass rather than leaving a half-wired graph.
5. Re-read the affected rows with `get` if the user needs confirmation.

## Operating rules

- Treat feature-test work as bidirectional graph maintenance, not a single-row edit.
- Prefer explicit `--test-path` and `--kind` when creating tests so downstream evidence and release reports remain interpretable.
- When removing coverage, unlink before deleting the test row.
- If one command already accepts related IDs at create time, use that to reduce follow-up mutations, then fill any missing reciprocal edges.
- If the request expands from feature/test coverage into claim closure or release readiness, switch to `$ssot-proof-chain-and-certification` or `$ssot-e2e-change-orchestrator`.

## Example

```powershell
ssot test create . --id tst:demo.login.unit --title "Login unit" --kind unit --test-path tests/test_login.py
ssot feature link . --id feat:demo.login --test-ids tst:demo.login.unit
ssot test link . --id tst:demo.login.unit --feature-ids feat:demo.login --claim-ids clm:demo.login.t1 --evidence-ids evd:demo.login.pytest
```

## Source of truth

- `README.md` feature and test sections
- `README.md` end-to-end example that links feature, claim, test, and evidence
- `examples/e2e-three-releases.md`
