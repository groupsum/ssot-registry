# End-to-end CLI usage: init → rel:3.0.0 (three release rails)

This walkthrough demonstrates a strict sequence:

1. initialize a repository
2. add features and targets
3. add tests/claims/evidence
4. freeze boundaries
5. run three releases (`rel:1.0.0`, `rel:2.0.0`, `rel:3.0.0`) through `certify -> promote -> publish`

```bash
repo=/tmp/ssot-usage-example
mkdir -p "$repo"

ssot-registry init "$repo" --repo-id repo:usage-example --repo-name usage-example --version 1.0.0

mkdir -p "$repo/tests" "$repo/evidence"
printf 'def test_r1():\n    assert True\n' > "$repo/tests/test_r1.py"
printf 'def test_r2():\n    assert True\n' > "$repo/tests/test_r2.py"
printf 'def test_r3():\n    assert True\n' > "$repo/tests/test_r3.py"
printf '{"ok": true}\n' > "$repo/evidence/r1.json"
printf '{"ok": true}\n' > "$repo/evidence/r2.json"
printf '{"ok": true}\n' > "$repo/evidence/r3.json"

ssot-registry feature create "$repo" --id feat:usage.alpha --title "Alpha feature" --implementation-status partial
ssot-registry feature create "$repo" --id feat:usage.beta --title "Beta feature" --implementation-status partial
ssot-registry feature create "$repo" --id feat:usage.gamma --title "Gamma feature" --implementation-status partial
ssot-registry claim create "$repo" --id clm:usage.r1 --title "Release 1 claim" --kind quality --tier T1 --status asserted --feature-ids feat:usage.alpha
ssot-registry claim create "$repo" --id clm:usage.r2 --title "Release 2 claim" --kind quality --tier T1 --status asserted --feature-ids feat:usage.beta
ssot-registry claim create "$repo" --id clm:usage.r3 --title "Release 3 claim" --kind quality --tier T1 --status asserted --feature-ids feat:usage.gamma
ssot-registry evidence create "$repo" --id evd:usage.r1 --title "R1 evidence" --status passed --kind ci --tier T1 --evidence-path evidence/r1.json --claim-ids clm:usage.r1
ssot-registry evidence create "$repo" --id evd:usage.r2 --title "R2 evidence" --status passed --kind ci --tier T1 --evidence-path evidence/r2.json --claim-ids clm:usage.r2
ssot-registry evidence create "$repo" --id evd:usage.r3 --title "R3 evidence" --status passed --kind ci --tier T1 --evidence-path evidence/r3.json --claim-ids clm:usage.r3
ssot-registry test create "$repo" --id tst:usage.r1 --title "R1 test" --status passing --kind unit --test-path tests/test_r1.py --feature-ids feat:usage.alpha --claim-ids clm:usage.r1 --evidence-ids evd:usage.r1
ssot-registry test create "$repo" --id tst:usage.r2 --title "R2 test" --status passing --kind integration --test-path tests/test_r2.py --feature-ids feat:usage.beta --claim-ids clm:usage.r2 --evidence-ids evd:usage.r2
ssot-registry test create "$repo" --id tst:usage.r3 --title "R3 test" --status passing --kind e2e --test-path tests/test_r3.py --feature-ids feat:usage.gamma --claim-ids clm:usage.r3 --evidence-ids evd:usage.r3
ssot-registry claim link "$repo" --id clm:usage.r1 --test-ids tst:usage.r1 --evidence-ids evd:usage.r1
ssot-registry claim link "$repo" --id clm:usage.r2 --test-ids tst:usage.r2 --evidence-ids evd:usage.r2
ssot-registry claim link "$repo" --id clm:usage.r3 --test-ids tst:usage.r3 --evidence-ids evd:usage.r3
ssot-registry evidence link "$repo" --id evd:usage.r1 --test-ids tst:usage.r1
ssot-registry evidence link "$repo" --id evd:usage.r2 --test-ids tst:usage.r2
ssot-registry evidence link "$repo" --id evd:usage.r3 --test-ids tst:usage.r3
ssot-registry feature link "$repo" --id feat:usage.alpha --claim-ids clm:usage.r1 --test-ids tst:usage.r1
ssot-registry feature link "$repo" --id feat:usage.beta --claim-ids clm:usage.r2 --test-ids tst:usage.r2
ssot-registry feature link "$repo" --id feat:usage.gamma --claim-ids clm:usage.r3 --test-ids tst:usage.r3
ssot-registry feature plan "$repo" --ids feat:usage.alpha --horizon current --claim-tier T1
ssot-registry feature plan "$repo" --ids feat:usage.beta --horizon current --claim-tier T1
ssot-registry feature plan "$repo" --ids feat:usage.gamma --horizon explicit --slot r3 --claim-tier T1
ssot-registry feature update "$repo" --id feat:usage.alpha --implementation-status implemented
ssot-registry feature update "$repo" --id feat:usage.beta --implementation-status implemented
ssot-registry feature update "$repo" --id feat:usage.gamma --implementation-status implemented

ssot-registry boundary create "$repo" --id bnd:rel1 --title "Release 1 boundary" --feature-ids feat:usage.alpha
ssot-registry release add-claim "$repo" --id rel:1.0.0 --claim-ids clm:usage.r1
ssot-registry release add-evidence "$repo" --id rel:1.0.0 --evidence-ids evd:usage.r1
ssot-registry boundary freeze "$repo" --boundary-id bnd:rel1
ssot-registry release update "$repo" --id rel:1.0.0 --boundary-id bnd:rel1
ssot-registry release certify "$repo" --release-id rel:1.0.0
ssot-registry release promote "$repo" --release-id rel:1.0.0
ssot-registry release publish "$repo" --release-id rel:1.0.0

ssot-registry boundary create "$repo" --id bnd:rel2 --title "Release 2 boundary" --feature-ids feat:usage.alpha feat:usage.beta
ssot-registry boundary freeze "$repo" --boundary-id bnd:rel2
ssot-registry release create "$repo" --id rel:2.0.0 --version 2.0.0 --boundary-id bnd:rel2 --claim-ids clm:usage.r1 clm:usage.r2 --evidence-ids evd:usage.r1 evd:usage.r2
ssot-registry release certify "$repo" --release-id rel:2.0.0
ssot-registry release promote "$repo" --release-id rel:2.0.0
ssot-registry release publish "$repo" --release-id rel:2.0.0

ssot-registry boundary create "$repo" --id bnd:rel3 --title "Release 3 boundary" --feature-ids feat:usage.alpha feat:usage.beta feat:usage.gamma
ssot-registry boundary freeze "$repo" --boundary-id bnd:rel3
ssot-registry release create "$repo" --id rel:3.0.0 --version 3.0.0 --boundary-id bnd:rel3 --claim-ids clm:usage.r1 clm:usage.r2 clm:usage.r3 --evidence-ids evd:usage.r1 evd:usage.r2 evd:usage.r3
ssot-registry release certify "$repo" --release-id rel:3.0.0
ssot-registry release promote "$repo" --release-id rel:3.0.0
ssot-registry release publish "$repo" --release-id rel:3.0.0
```

Sequence validity is enforced in guards:

- certification requires release status to be `draft` or `candidate`
- promotion requires release status to be `certified`
- publication requires release status to be `promoted`
