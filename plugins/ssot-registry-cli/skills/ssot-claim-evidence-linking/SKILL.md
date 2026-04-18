---
name: ssot-claim-evidence-linking
description: Create, inspect, update, delete, evaluate, verify, link, and unlink claims and evidence, including their feature and test relationships. Use when Codex needs to connect claims to features, tests, and evidence, adjust claim status or tier, or verify whether proof chains are strong enough for release and certification workflows.
---

# SSOT Claim/Evidence Linking

Use this skill when the user is working on proof chains: what a feature claims, what tests exercise that claim, and what evidence supports it.

## Command surface

- Claims: `claim create|get|list|update|delete|link|unlink|evaluate|set-status|set-tier`
- Evidence: `evidence create|get|list|update|delete|link|unlink|verify`
- Companion entity often touched in the same flow: `test link|unlink`

## Workflow

1. Create or inspect the claim first; claims are the assertion layer attached to one or more features.
2. Create or inspect evidence rows with a concrete `--evidence-path` that exists in the repo.
3. Link claims to features, tests, and evidence in one pass when possible so the closure graph is complete.
4. Use `claim evaluate` to inspect whether a claim currently satisfies guards.
5. Use `evidence verify` to check that evidence rows are valid before claiming certification readiness.

## Operating rules

- Keep claim `status` and `tier` distinct; status is lifecycle progress, tier is proof strength.
- Evidence should describe an artifact path the repo can actually carry or regenerate.
- When a claim gains or loses supporting evidence, review linked tests at the same time; broken proof chains usually show up as stale links.
- Prefer unlink over delete when historical claim or evidence records should remain visible.
- If the user is trying to certify or publish a target, switch from isolated claim work to the E2E release-closure flow.

## Example

```powershell
ssot claim create . --id clm:demo.login.t1 --title "Login succeeds" --kind behavior --tier T1
ssot evidence create . --id evd:demo.login.pytest --title "Pytest login run" --kind test_run --evidence-path artifacts/login.json --tier T1
ssot claim link . --id clm:demo.login.t1 --feature-ids feat:demo.login --test-ids tst:demo.login.unit --evidence-ids evd:demo.login.pytest
ssot evidence verify . --evidence-id evd:demo.login.pytest
ssot claim evaluate . --claim-id clm:demo.login.t1
```

## Source of truth

- `README.md` claim and evidence sections
- `pkgs/ssot-contracts/src/ssot_contracts/templates/specs/SPEC-0604-claim-statuses.yaml`
- `pkgs/ssot-contracts/src/ssot_contracts/templates/specs/SPEC-0605-claim-tiers.yaml`
