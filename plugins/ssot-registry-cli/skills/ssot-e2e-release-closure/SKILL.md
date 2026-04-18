---
name: ssot-e2e-release-closure
description: Drive SSOT end-to-end workflows from ADR/SPEC setup through feature planning, proof-chain wiring, boundary freeze, release certification, promotion, publication, and final closure checks. Use when Codex needs to orchestrate a whole target lifecycle instead of a single entity CRUD operation.
---

# SSOT E2E Release Closure

Use this skill for full SSOT flows where the request spans multiple entity types and gates. The goal is to move from intent and scope definition to a frozen, certifiable, publishable release without skipping guard checks.

## End-to-end order

1. Create or sync the ADRs and SPECs that define the target and operating rules.
2. Create the target features and set their planning and lifecycle fields.
3. Create and link the supporting claims, tests, and evidence.
4. Evaluate claims and verify evidence before freezing scope.
5. Create the boundary, add the in-scope features, and run `boundary freeze`.
6. Create the release with the frozen boundary plus claim and evidence IDs.
7. Run `release certify`; if it passes, continue to `release promote` and `release publish`.
8. Re-check outputs such as reports, release status, and any final closure expectations the user asked for.

## Operating rules

- Prefer failing early over pushing through broken guards; certification is supposed to fail closed.
- Validate or inspect the registry before certification if the repo state is uncertain.
- Freeze only after feature scope is correct; boundary churn after freeze is a signal to revisit scope.
- Treat release certification as a proof-chain check over the frozen boundary, linked claims, linked tests, and linked evidence.
- If the user asks for "closure" of a target, interpret that as more than publish: confirm the final release state, linked proof artifacts, and any requested report output.

## Example skeleton

```powershell
ssot adr sync .
ssot spec sync .
ssot feature create . --id feat:demo.login --title "User login"
ssot claim create . --id clm:demo.login.t1 --title "Login succeeds" --kind behavior --tier T1
ssot test create . --id tst:demo.login.unit --title "Login unit" --kind unit --test-path tests/test_login.py
ssot evidence create . --id evd:demo.login.pytest --title "Pytest login run" --kind test_run --evidence-path artifacts/login.json --tier T1
ssot claim evaluate . --claim-id clm:demo.login.t1
ssot evidence verify . --evidence-id evd:demo.login.pytest
ssot boundary create . --id bnd:demo.v0 --title "Demo v0 scope" --feature-ids feat:demo.login
ssot boundary freeze . --boundary-id bnd:demo.v0
ssot release create . --id rel:0.1.0 --version 0.1.0 --boundary-id bnd:demo.v0 --claim-ids clm:demo.login.t1 --evidence-ids evd:demo.login.pytest
ssot release certify . --release-id rel:0.1.0 --write-report
ssot release promote . --release-id rel:0.1.0
ssot release publish . --release-id rel:0.1.0
```

## Source of truth

- `README.md` end-to-end examples
- `examples/e2e-three-releases.md`
- `pkgs/ssot-core/src/ssot_registry/api/release.py`
- `pkgs/ssot-contracts/src/ssot_contracts/templates/specs/SPEC-0608-gates-and-fences.yaml`
