---
name: ssot-proof-chain-and-certification
description: Drive the SSOT proof and release phase by creating and linking claims, tests, and evidence, then creating releases, certifying them, promoting them, publishing them, and verifying closure outputs. Use when Codex needs to close the proof chain for a frozen boundary after the frozen implementation work already exists and carry it through release completion.
---

# SSOT Proof Chain And Certification

Use this skill after scope is frozen and implementation plus required tests exist. The job here is proof closure and release progression, not post-freeze implementation delivery.

## Command discipline

- Do not spend turns rediscovering syntax with `--help` during normal SSOT work. Use the command surface and examples in this skill directly.
- Pick one verified CLI rail for the repo (`ssot`, `ssot-registry`, `ssot-cli`, or `uv run ssot`) and reuse it consistently by substituting that rail into the examples below.
- Only inspect parser or help text when the user explicitly asks about the CLI surface or when observed runtime behavior contradicts the command patterns documented here.
## Workflow

1. Confirm the frozen boundary and its resolved feature scope.
2. Confirm the repo already contains the code, schema, migration, and test changes required by that frozen scope.
3. Confirm required tests cover happy paths, unhappy paths, valid and invalid inputs, expected outputs, observable behavior, and any requested or feature-required performance/conformance cases.
4. Create or update claims, tests, and evidence for that scope.
5. Add reciprocal links so the graph is complete.
6. Run claim evaluation and evidence verification.
7. Create the release against the frozen boundary.
8. Run certification; only if it passes continue to promotion and publication.
9. Verify closure outputs such as reports, snapshots, and final statuses.

## Operating rules

- Require release coverage for all frozen boundary features.
- Reject any implied `freeze -> certify` shortcut when runtime implementation, required tests, or evidence artifacts are still missing.
- Reject proof closure when runtime implementation or required tests are missing, regardless of whether the team chose code-first or tests-first delivery.
- Treat claim-tier promotion as additive proof accumulation. A release that adds `T2` claims should normally still carry the linked `T0` and `T1` claims unless those lower-tier rows are independently wrong or obsolete.
- Do not satisfy higher-tier proof work by unlinking or overwriting lower-tier claims. Create the higher-tier claim/evidence rows and add them to the proof graph alongside the lower tiers.
- Treat certification as fail-closed; do not continue through failures.
- Do not publish unless promotion has succeeded.
- If the request also needs upstream scope or implementation work, escalate to `$ssot-e2e-change-orchestrator`.

## Common commands

```powershell
ssot claim create . --id clm:demo.change.t0 --title "Demo change basic claim" --kind behavior --tier T0 --feature-ids feat:demo.change
ssot claim create . --id clm:demo.change.t1 --title "Demo change claim" --kind behavior --tier T1 --feature-ids feat:demo.change
ssot test create . --id tst:demo.change.integration --title "Demo change integration" --kind integration --test-path tests/test_demo_change.py --feature-ids feat:demo.change
ssot evidence create . --id evd:demo.change.pytest --title "Demo change pytest evidence" --kind test_run --tier T1 --evidence-path artifacts/demo-change.json
ssot claim link . --id clm:demo.change.t0 --test-ids tst:demo.change.integration
ssot claim link . --id clm:demo.change.t1 --test-ids tst:demo.change.integration --evidence-ids evd:demo.change.pytest
ssot test link . --id tst:demo.change.integration --claim-ids clm:demo.change.t1 --evidence-ids evd:demo.change.pytest
ssot claim evaluate . --claim-id clm:demo.change.t1
ssot evidence verify . --evidence-id evd:demo.change.pytest
ssot release create . --id rel:demo.change --version 0.1.0 --boundary-id bnd:demo.change --evidence-ids evd:demo.change.pytest
ssot release add-claim . --id rel:demo.change --claim-ids clm:demo.change.t0
ssot release add-claim . --id rel:demo.change --claim-ids clm:demo.change.t1
ssot release certify . --release-id rel:demo.change --write-report
ssot release promote . --release-id rel:demo.change
ssot release publish . --release-id rel:demo.change
```

## References

- `references/certification-gates.md`
- `references/closure-checks.md`
