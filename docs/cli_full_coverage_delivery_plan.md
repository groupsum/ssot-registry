# CLI Full-Coverage Delivery Plan

Date: 2026-04-16  
Scope: Reach full integration-test coverage for all public CLI surfaces in `ssot-registry` (commands, subcommands, global flags, command flags, and subcommand flags).

## 1) Coverage objective and definition of done

Full coverage means each public surface is exercised at least once by integration tests:

1. Every top-level command (`init`, `validate`, `upgrade`, `feature`, ...).
2. Every subcommand path (`spec reserve create`, `feature lifecycle set`, ...).
3. Every global flag (`--output-format`, `--output-file`).
4. Every command-level flag (`init --force`, `upgrade --target-version`).
5. Every subcommand flag (`profile create --allow-feature-override-tier`, etc.).

### Acceptance criteria

- `docs/cli_test_gap_report.md` has no remaining untested items.
- A repeatable coverage-audit script runs in CI and fails if any new CLI surface ships without at least one integration test invocation.
- New tests are deterministic and isolated (fixture-backed temp repos, no network).

## 2) Workstream breakdown

## WS-A: Baseline tooling and guardrail (Day 1)

### A1. Add machine-readable CLI-surface extraction helper
- Create a helper script in `scripts/` that introspects argparse registrations and emits:
  - all leaf command paths,
  - flags by path,
  - global flags.
- Keep output JSON for easy diffing in CI.

### A2. Add invocation extractor for integration tests
- Parse `tests/integration/test_cli*.py` for `run_cli(...)` and `_run_ok(...)` string-argument invocations.
- Emit observed command paths and observed flags.

### A3. Add coverage comparator
- Compare WS-A outputs and emit gaps.
- Non-zero exit code if gaps exist.

### A4. Wire into CI
- Add a lightweight check target in `Makefile` and CI to run the comparator.

Deliverable: automated anti-regression check for CLI-surface coverage.

## WS-B: Close untested subcommand paths (Day 1–2)

Add targeted tests for currently untested subcommands:

1. `tests/integration/test_cli_adr.py`
   - Add cases for:
     - `adr list`
     - `adr sync`
     - `adr reserve create`
     - `adr reserve list`
2. `tests/integration/test_cli_spec.py`
   - Add cases for:
     - `spec list`
     - `spec sync`
     - `spec reserve create`
     - `spec reserve list`
3. `tests/integration/test_cli_profile.py`
   - Add cases for:
     - `profile unlink`
     - `profile verify`

Deliverable: zero untested subcommand paths.

## WS-C: Close untested global and command-level flags (Day 2)

1. `tests/integration/test_cli_output_formats.py`
   - Add `--output-file` case:
     - invoke a representative command with `--output-file <tmp path>` and assert file written + payload shape.

2. `tests/integration/test_cli_init.py`
   - Add `init --force` overwrite case:
     - initialize once, mutate registry sentinel, re-run with `--force`, assert overwrite semantics.

3. `tests/integration/test_cli_upgrade.py`
   - Add `upgrade --target-version` case:
     - test a valid target and at least one invalid/redundant target path.

Deliverable: zero untested global/command flags.

## WS-D: Close subcommand-flag gaps by domain (Day 2–4)

Use one focused domain file per entity to keep maintenance clear.

### D1. ADR + SPEC docs lifecycle flags
- `tests/integration/test_cli_adr.py`
  - cover: `adr create --note --origin --reserve-range`
  - cover: `adr update --status --note`
- `tests/integration/test_cli_spec.py`
  - cover: `spec create --origin --note --reserve-range`
  - cover: `spec update --body-file --kind --status --note`

### D2. Feature planning/lifecycle flags
- `tests/integration/test_cli_feature.py`
  - cover `feature create` optional flags:
    `--lifecycle-stage --replacement-feature-id --note --horizon --claim-tier --target-lifecycle-stage --slot --claim-ids --test-ids`
  - cover `feature lifecycle set --replacement-feature-id --effective-release-id`
  - cover `feature link --requires`
  - cover `feature update --description`

### D3. Profile flags
- `tests/integration/test_cli_profile.py`
  - cover `profile create --profile-ids --allow-feature-override-tier`
  - cover `profile create --no-allow-feature-override-tier`
  - cover `profile link --feature-ids`
  - cover `profile unlink --id --feature-ids --profile-ids`
  - cover `profile update --description --status --kind --claim-tier`
  - cover `profile verify --profile-id`

### D4. Boundary/release/registry/graph flags
- `tests/integration/test_cli_boundary.py`
  - cover `boundary create --status --frozen --profile-ids`
  - cover `boundary update --title --frozen`
  - add explicit `--no-frozen` case.
- `tests/integration/test_cli_release.py`
  - cover `release create --status`
  - cover `release update --version`
- `tests/integration/test_cli_output_formats.py` or `test_cli_graph.py`
  - cover `graph export --output`
- `tests/integration/test_cli_output_formats.py`
  - cover `registry export --output`

### D5. Claim/evidence/test linking flags
- `tests/integration/test_cli_claim.py`
  - cover `claim unlink --test-ids --evidence-ids`
  - cover `claim update --title --kind`
- `tests/integration/test_cli_evidence.py`
  - cover `evidence unlink --test-ids`
  - cover `evidence update --status --kind --evidence-path`
- `tests/integration/test_cli_test.py`
  - cover `test link --claim-ids --evidence-ids`
  - cover `test unlink --claim-ids --evidence-ids`
  - cover `test update --status --kind --test-path`

### D6. Issue/risk safety and linking flags
- `tests/integration/test_cli_issue.py`
  - cover `issue create --status --slot --risk-ids --no-release-blocking`
  - cover `issue link --claim-ids --test-ids --evidence-ids --risk-ids`
  - cover `issue plan --slot`
  - cover `issue unlink --claim-ids --test-ids --evidence-ids --risk-ids`
  - cover `issue update --title --severity --release-blocking`
- `tests/integration/test_cli_risk.py`
  - cover `risk create --status --claim-ids --test-ids --evidence-ids --issue-ids --release-blocking --no-release-blocking`
  - cover `risk link --feature-ids --claim-ids --test-ids --evidence-ids`
  - cover `risk unlink --feature-ids --claim-ids --test-ids --evidence-ids`
  - cover `risk update --title --severity --no-release-blocking`

Deliverable: zero untested subcommand flags.

## 3) Sequencing and ownership

1. **Phase 1 (Day 1):** WS-A + WS-B (highest signal, lowest coupling).
2. **Phase 2 (Day 2):** WS-C + D1/D3.
3. **Phase 3 (Day 3):** D2 + D4.
4. **Phase 4 (Day 4):** D5 + D6 and cleanup/refactor.
5. **Phase 5 (Day 5):** run full suite in CI, stabilize flakes, update docs.

Recommended ownership split:
- Engineer A: parser tooling + ADR/SPEC + profile
- Engineer B: feature + boundary + release + graph/registry
- Engineer C: issue/risk + claim/evidence/test

## 4) Test design standards (apply to every new case)

- One assertion block per surface under test (avoid mega-tests).
- Use explicit IDs per test for traceability (`*.coverage.*`).
- Verify both `returncode` and semantic payload fields.
- Where boolean optional flags exist, include both positive and negative form tests when behavior can differ.
- Keep fixtures local and deterministic; no external services.

## 5) Risk controls

- Avoid brittle assertions on full serialized output; assert stable keys/values.
- Reuse helper builders for repeated setup flows (repo init, entities).
- Gate merges on coverage comparator to prevent regression.

## 6) Exit checklist

- [ ] All items currently listed in `docs/cli_test_gap_report.md` are covered by tests.
- [ ] Coverage comparator returns no gaps.
- [ ] CI includes comparator check.
- [ ] CLI docs/examples updated where new explicit flag behavior is validated.
