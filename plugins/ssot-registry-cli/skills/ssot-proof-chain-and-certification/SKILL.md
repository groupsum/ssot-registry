---
name: ssot-proof-chain-and-certification
description: Drive the SSOT proof and release phase by creating and linking claims, tests, and evidence, then creating releases, certifying them, promoting them, publishing them, and verifying closure outputs. Use when Codex needs to close the proof chain for a frozen boundary after the frozen implementation work already exists and carry it through release completion.
---

# SSOT Proof Chain And Certification

Use this skill after scope is frozen and implementation exists. The job here is proof closure and release progression, not post-freeze implementation delivery.

## Workflow

1. Confirm the frozen boundary and its resolved feature scope.
2. Confirm the repo already contains the code, schema, migration, and test changes required by that frozen scope.
3. Create or update claims, tests, and evidence for that scope.
4. Add reciprocal links so the graph is complete.
5. Run claim evaluation and evidence verification.
6. Create the release against the frozen boundary.
7. Run certification; only if it passes continue to promotion and publication.
8. Verify closure outputs such as reports, snapshots, and final statuses.

## Operating rules

- Require release coverage for all frozen boundary features.
- Reject any implied `freeze -> certify` shortcut when implementation or verification artifacts are still missing.
- Treat certification as fail-closed; do not continue through failures.
- Do not publish unless promotion has succeeded.
- If the request also needs upstream scope or implementation work, escalate to `$ssot-e2e-change-orchestrator`.

## Common commands

```powershell
ssot claim create . --id clm:demo.change.t1 --title "Demo change claim" --kind behavior --tier T1 --feature-ids feat:demo.change
ssot test create . --id tst:demo.change.integration --title "Demo change integration" --kind integration --test-path tests/test_demo_change.py --feature-ids feat:demo.change
ssot evidence create . --id evd:demo.change.pytest --title "Demo change pytest evidence" --kind test_run --tier T1 --evidence-path artifacts/demo-change.json
ssot claim link . --id clm:demo.change.t1 --test-ids tst:demo.change.integration --evidence-ids evd:demo.change.pytest
ssot test link . --id tst:demo.change.integration --claim-ids clm:demo.change.t1 --evidence-ids evd:demo.change.pytest
ssot claim evaluate . --claim-id clm:demo.change.t1
ssot evidence verify . --evidence-id evd:demo.change.pytest
ssot release create . --id rel:demo.change --version 0.1.0 --boundary-id bnd:demo.change --claim-ids clm:demo.change.t1 --evidence-ids evd:demo.change.pytest
ssot release certify . --release-id rel:demo.change --write-report
ssot release promote . --release-id rel:demo.change
ssot release publish . --release-id rel:demo.change
```

## References

- `references/certification-gates.md`
- `references/closure-checks.md`
