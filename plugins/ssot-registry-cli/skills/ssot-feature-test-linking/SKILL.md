---
name: ssot-feature-test-linking
description: Create features, create tests, and link them bidirectionally with their immediate verification edges. Use when Codex needs to add new coverage units end-to-end instead of only wiring pre-existing rows.
---

# SSOT Feature/Test Linking

Use this skill when the user asks to create features and tests and connect them. The main job is delivering an end-to-end coverage unit: feature row, test row, and reciprocal links.

## Command surface

- Features: `feature create|link|unlink|get|list`
- Tests: `test create|get|list|update|delete|link|unlink`
- Companion edges often needed in the same change: `claim link|unlink`, `evidence link|unlink`

## Linking order

1. Confirm whether the feature row exists; create it when missing.
2. Confirm whether the test row exists; create it when missing.
3. Link the feature to the test with `feature link --test-ids ...`.
4. Link the test back to the feature with `test link --feature-ids ...`.
5. If the test proves a claim or produces evidence, add those reciprocal links in the same pass rather than leaving a half-wired graph.
6. Re-read the affected rows with `get` if the user needs confirmation.

## Operating rules

- Treat feature-test work as creation plus bidirectional graph maintenance, not a single-row edit.
- Prefer creating the feature and test in the same pass when the user requests new capability coverage.
- Prefer explicit `--test-path` and `--kind` when creating tests so downstream evidence and release reports remain interpretable.
- When removing coverage, unlink before deleting the test row.
- If one command already accepts related IDs at create time, use that to reduce follow-up mutations, then fill any missing reciprocal edges.
- If the request expands from feature/test coverage into claim closure or release readiness, switch to `$ssot-proof-chain-and-certification` or `$ssot-e2e-change-orchestrator`.

## Example

```powershell
ssot feature create . --id feat:demo.login --title "User login"
ssot test create . --id tst:demo.login.unit --title "Login unit" --kind unit --test-path tests/test_login.py
ssot feature link . --id feat:demo.login --test-ids tst:demo.login.unit
ssot test link . --id tst:demo.login.unit --feature-ids feat:demo.login --claim-ids clm:demo.login.t1 --evidence-ids evd:demo.login.pytest
```

## Source of truth

- `README.md` feature and test sections
- `README.md` end-to-end example that links feature, claim, test, and evidence
- `examples/e2e-three-releases.md`
