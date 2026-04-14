<div align="center">
  <h1>🔷 ssot-registry</h1>
  <p><strong>Single Source of Truth for features, claims, tests, and releases.</strong></p>
</div>

<div align="center">
  <a href="https://pypi.org/project/ssot-registry/"><img src="https://img.shields.io/pypi/v/ssot-registry?label=PyPI%20version" alt="PyPI version" /></a>
  <a href="https://pypi.org/project/ssot-registry/"><img src="https://img.shields.io/pypi/pyversions/ssot-registry?label=Python" alt="Supported Python versions" /></a>
  <a href="https://pepy.tech/project/ssot-registry"><img src="https://static.pepy.tech/badge/ssot-registry" alt="Downloads" /></a>
  <a href="https://hits.sh/github.com/groupsum/ssot-registry/"><img src="https://hits.sh/github.com/groupsum/ssot-registry.svg?style=flat-square" alt="Hits" /></a>
</div>

`ssot-registry` is a portable, repository-agnostic single-source-of-truth system.

- GitHub: https://github.com/groupsum/ssot-registry

It provides a canonical registry for:

- features
- tests
- claims
- evidence
- issues
- risks
- frozen boundaries
- releases

The canonical machine-readable artifact is:

```text
.ssot/registry.json
```

Everything else is derived from it.

## Core model

- Features are the only targetable units.
- Features carry planning horizon and target claim tier.
- Claims assert properties of features.
- Tests verify claims.
- Evidence supports claims and is linked to tests.
- Issues and risks are plannable and can block certification, promotion, or publication.
- Boundaries freeze scope.
- Releases bundle claims and evidence against a frozen boundary.

## Canonical format

The canonical authored format is JSON. Markdown, CSV, DOT, SQLite, and reports are derived projections.

## Install

```bash
python -m pip install ssot-registry
# or for local development
python -m pip install -e .
```

## Community

Please review [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) before contributing.

## CLI quick reference

```bash
ssot-registry --help
ssot-registry init --help
ssot-registry validate --help
ssot-registry feature --help
ssot-registry test --help
ssot-registry issue --help
ssot-registry claim --help
ssot-registry evidence --help
ssot-registry risk --help
ssot-registry boundary --help
ssot-registry release --help
ssot-registry graph --help
ssot-registry registry --help
```

---

## CLI conventions

- Most commands accept `[path]` as an optional positional argument. Default is current directory (`.`).
- IDs are normalized prefixed identifiers (for example: `feat:*`, `clm:*`, `tst:*`, `evd:*`, `iss:*`, `rsk:*`, `bnd:*`, `rel:*`).
- Commands emit JSON by default; use `--output-format {json,csv,df,yaml,toml}` for alternate renderings.
- Use `--output-file PATH` to save rendered command output to disk.
- Non-zero exit code indicates an operation failure or failed checks.

---

## Command surface (all commands, subcommands, and flags)

### Top-level commands

- `init`
- `validate`
- `feature`
- `test`
- `issue`
- `claim`
- `evidence`
- `risk`
- `boundary`
- `release`
- `graph`
- `registry`

### `init`

```text
ssot-registry init [path]
  --repo-id REPO_ID
  --repo-name REPO_NAME
  --version VERSION
  --force
```

### `validate`

```text
ssot-registry validate [path]
  --write-report
```

### `feature`

Subcommands:

- `create`
- `get`
- `list`
- `update`
- `delete`
- `link`
- `unlink`
- `plan`
- `lifecycle set`

Flags per subcommand:

```text
ssot-registry feature create [path]
  --id ID (required)
  --title TITLE (required)
  --description DESCRIPTION
  --implementation-status {absent,partial,implemented}
  --lifecycle-stage {active,deprecated,obsolete,removed}
  --replacement-feature-id [REPLACEMENT_FEATURE_ID ...]
  --note NOTE
  --horizon {current,next,future,explicit,backlog,out_of_bounds}
  --claim-tier {T0,T1,T2,T3,T4}
  --target-lifecycle-stage {active,deprecated,obsolete,removed}
  --slot SLOT
  --claim-ids [CLAIM_IDS ...]
  --test-ids [TEST_IDS ...]
  --requires [REQUIRES ...]

ssot-registry feature get [path]
  --id ID (required)

ssot-registry feature list [path]

ssot-registry feature update [path]
  --id ID (required)
  --title TITLE
  --description DESCRIPTION
  --implementation-status {absent,partial,implemented}

ssot-registry feature delete [path]
  --id ID (required)

ssot-registry feature link [path]
  --id ID (required)
  --claim-ids [CLAIM_IDS ...]
  --test-ids [TEST_IDS ...]
  --requires [REQUIRES ...]

ssot-registry feature unlink [path]
  --id ID (required)
  --claim-ids [CLAIM_IDS ...]
  --test-ids [TEST_IDS ...]
  --requires [REQUIRES ...]

ssot-registry feature plan [path]
  --ids IDS [IDS ...] (required)
  --horizon {current,next,future,explicit,backlog,out_of_bounds} (required)
  --claim-tier {T0,T1,T2,T3,T4}
  --target-lifecycle-stage {active,deprecated,obsolete,removed}
  --slot SLOT

ssot-registry feature lifecycle set [path]
  --ids IDS [IDS ...] (required)
  --stage {active,deprecated,obsolete,removed} (required)
  --replacement-feature-id [REPLACEMENT_FEATURE_ID ...]
  --effective-release-id EFFECTIVE_RELEASE_ID
  --note NOTE
```

### `test`

Subcommands:

- `create`, `get`, `list`, `update`, `delete`, `link`, `unlink`

```text
ssot-registry test create [path]
  --id ID (required)
  --title TITLE (required)
  --status {planned,passing,failing,blocked,skipped}
  --kind KIND (required)
  --test-path TEST_PATH (required)
  --feature-ids [FEATURE_IDS ...]
  --claim-ids [CLAIM_IDS ...]
  --evidence-ids [EVIDENCE_IDS ...]

ssot-registry test get [path]
  --id ID (required)

ssot-registry test list [path]

ssot-registry test update [path]
  --id ID (required)
  --title TITLE
  --status {planned,passing,failing,blocked,skipped}
  --kind KIND
  --test-path TEST_PATH

ssot-registry test delete [path]
  --id ID (required)

ssot-registry test link [path]
  --id ID (required)
  --feature-ids [FEATURE_IDS ...]
  --claim-ids [CLAIM_IDS ...]
  --evidence-ids [EVIDENCE_IDS ...]

ssot-registry test unlink [path]
  --id ID (required)
  --feature-ids [FEATURE_IDS ...]
  --claim-ids [CLAIM_IDS ...]
  --evidence-ids [EVIDENCE_IDS ...]
```

### `issue`

Subcommands:

- `create`, `get`, `list`, `update`, `delete`, `link`, `unlink`, `plan`, `close`, `reopen`

```text
ssot-registry issue create [path]
  --id ID (required)
  --title TITLE (required)
  --status {open,in_progress,blocked,resolved,closed}
  --severity {low,medium,high,critical}
  --description DESCRIPTION
  --horizon {current,next,future,explicit,backlog,out_of_bounds}
  --slot SLOT
  --feature-ids [FEATURE_IDS ...]
  --claim-ids [CLAIM_IDS ...]
  --test-ids [TEST_IDS ...]
  --evidence-ids [EVIDENCE_IDS ...]
  --risk-ids [RISK_IDS ...]
  --release-blocking | --no-release-blocking

ssot-registry issue get [path]
  --id ID (required)

ssot-registry issue list [path]

ssot-registry issue update [path]
  --id ID (required)
  --title TITLE
  --severity {low,medium,high,critical}
  --description DESCRIPTION
  --release-blocking | --no-release-blocking

ssot-registry issue delete [path]
  --id ID (required)

ssot-registry issue link [path]
  --id ID (required)
  --feature-ids [FEATURE_IDS ...]
  --claim-ids [CLAIM_IDS ...]
  --test-ids [TEST_IDS ...]
  --evidence-ids [EVIDENCE_IDS ...]
  --risk-ids [RISK_IDS ...]

ssot-registry issue unlink [path]
  --id ID (required)
  --feature-ids [FEATURE_IDS ...]
  --claim-ids [CLAIM_IDS ...]
  --test-ids [TEST_IDS ...]
  --evidence-ids [EVIDENCE_IDS ...]
  --risk-ids [RISK_IDS ...]

ssot-registry issue plan [path]
  --ids IDS [IDS ...] (required)
  --horizon {current,next,future,explicit,backlog,out_of_bounds} (required)
  --slot SLOT

ssot-registry issue close [path]
  --id ID (required)

ssot-registry issue reopen [path]
  --id ID (required)
```

### `claim`

Subcommands:

- `create`, `get`, `list`, `update`, `delete`, `link`, `unlink`, `evaluate`, `set-status`, `set-tier`

```text
ssot-registry claim create [path]
  --id ID (required)
  --title TITLE (required)
  --status {proposed,declared,implemented,asserted,evidenced,certified,promoted,published,blocked,retired}
  --tier {T0,T1,T2,T3,T4}
  --kind KIND (required)
  --description DESCRIPTION
  --feature-ids [FEATURE_IDS ...]
  --test-ids [TEST_IDS ...]
  --evidence-ids [EVIDENCE_IDS ...]

ssot-registry claim get [path]
  --id ID (required)

ssot-registry claim list [path]

ssot-registry claim update [path]
  --id ID (required)
  --title TITLE
  --kind KIND
  --description DESCRIPTION

ssot-registry claim delete [path]
  --id ID (required)

ssot-registry claim link [path]
  --id ID (required)
  --feature-ids [FEATURE_IDS ...]
  --test-ids [TEST_IDS ...]
  --evidence-ids [EVIDENCE_IDS ...]

ssot-registry claim unlink [path]
  --id ID (required)
  --feature-ids [FEATURE_IDS ...]
  --test-ids [TEST_IDS ...]
  --evidence-ids [EVIDENCE_IDS ...]

ssot-registry claim evaluate [path]
  --claim-id CLAIM_ID

ssot-registry claim set-status [path]
  --id ID (required)
  --status {proposed,declared,implemented,asserted,evidenced,certified,promoted,published,blocked,retired} (required)

ssot-registry claim set-tier [path]
  --id ID (required)
  --tier {T0,T1,T2,T3,T4} (required)
```

### `evidence`

Subcommands:

- `create`, `get`, `list`, `update`, `delete`, `link`, `unlink`, `verify`

```text
ssot-registry evidence create [path]
  --id ID (required)
  --title TITLE (required)
  --status {planned,collected,passed,failed,stale}
  --kind KIND (required)
  --tier {T0,T1,T2,T3,T4}
  --evidence-path EVIDENCE_PATH (required)
  --claim-ids [CLAIM_IDS ...]
  --test-ids [TEST_IDS ...]

ssot-registry evidence get [path]
  --id ID (required)

ssot-registry evidence list [path]

ssot-registry evidence update [path]
  --id ID (required)
  --title TITLE
  --status {planned,collected,passed,failed,stale}
  --kind KIND
  --tier {T0,T1,T2,T3,T4}
  --evidence-path EVIDENCE_PATH

ssot-registry evidence delete [path]
  --id ID (required)

ssot-registry evidence link [path]
  --id ID (required)
  --claim-ids [CLAIM_IDS ...]
  --test-ids [TEST_IDS ...]

ssot-registry evidence unlink [path]
  --id ID (required)
  --claim-ids [CLAIM_IDS ...]
  --test-ids [TEST_IDS ...]

ssot-registry evidence verify [path]
  --evidence-id EVIDENCE_ID
```

### `risk`

Subcommands:

- `create`, `get`, `list`, `update`, `delete`, `link`, `unlink`, `mitigate`, `accept`, `retire`

```text
ssot-registry risk create [path]
  --id ID (required)
  --title TITLE (required)
  --status {active,mitigated,accepted,retired}
  --severity {low,medium,high,critical}
  --description DESCRIPTION
  --feature-ids [FEATURE_IDS ...]
  --claim-ids [CLAIM_IDS ...]
  --test-ids [TEST_IDS ...]
  --evidence-ids [EVIDENCE_IDS ...]
  --issue-ids [ISSUE_IDS ...]
  --release-blocking | --no-release-blocking

ssot-registry risk get [path]
  --id ID (required)

ssot-registry risk list [path]

ssot-registry risk update [path]
  --id ID (required)
  --title TITLE
  --severity {low,medium,high,critical}
  --description DESCRIPTION
  --release-blocking | --no-release-blocking

ssot-registry risk delete [path]
  --id ID (required)

ssot-registry risk link [path]
  --id ID (required)
  --feature-ids [FEATURE_IDS ...]
  --claim-ids [CLAIM_IDS ...]
  --test-ids [TEST_IDS ...]
  --evidence-ids [EVIDENCE_IDS ...]
  --issue-ids [ISSUE_IDS ...]

ssot-registry risk unlink [path]
  --id ID (required)
  --feature-ids [FEATURE_IDS ...]
  --claim-ids [CLAIM_IDS ...]
  --test-ids [TEST_IDS ...]
  --evidence-ids [EVIDENCE_IDS ...]
  --issue-ids [ISSUE_IDS ...]

ssot-registry risk mitigate [path]
  --id ID (required)

ssot-registry risk accept [path]
  --id ID (required)

ssot-registry risk retire [path]
  --id ID (required)
```

### `boundary`

Subcommands:

- `create`, `get`, `list`, `update`, `delete`, `add-feature`, `remove-feature`, `freeze`

```text
ssot-registry boundary create [path]
  --id ID (required)
  --title TITLE (required)
  --status {draft,active,frozen,retired}
  --frozen | --no-frozen
  --feature-ids [FEATURE_IDS ...]

ssot-registry boundary get [path]
  --id ID (required)

ssot-registry boundary list [path]

ssot-registry boundary update [path]
  --id ID (required)
  --title TITLE
  --status {draft,active,frozen,retired}
  --frozen | --no-frozen

ssot-registry boundary delete [path]
  --id ID (required)

ssot-registry boundary add-feature [path]
  --id ID (required)
  --feature-ids FEATURE_IDS [FEATURE_IDS ...] (required)

ssot-registry boundary remove-feature [path]
  --id ID (required)
  --feature-ids FEATURE_IDS [FEATURE_IDS ...] (required)

ssot-registry boundary freeze [path]
  --boundary-id BOUNDARY_ID
```

### `release`

Subcommands:

- `create`, `get`, `list`, `update`, `delete`
- `add-claim`, `remove-claim`, `add-evidence`, `remove-evidence`
- `certify`, `promote`, `publish`, `revoke`

```text
ssot-registry release create [path]
  --id ID (required)
  --version VERSION (required)
  --status {draft,candidate,certified,promoted,published,revoked}
  --boundary-id BOUNDARY_ID (required)
  --claim-ids [CLAIM_IDS ...]
  --evidence-ids [EVIDENCE_IDS ...]

ssot-registry release get [path]
  --id ID (required)

ssot-registry release list [path]

ssot-registry release update [path]
  --id ID (required)
  --version VERSION
  --status {draft,candidate,certified,promoted,published,revoked}
  --boundary-id BOUNDARY_ID

ssot-registry release delete [path]
  --id ID (required)

ssot-registry release add-claim [path]
  --id ID (required)
  --claim-ids CLAIM_IDS [CLAIM_IDS ...] (required)

ssot-registry release remove-claim [path]
  --id ID (required)
  --claim-ids CLAIM_IDS [CLAIM_IDS ...] (required)

ssot-registry release add-evidence [path]
  --id ID (required)
  --evidence-ids EVIDENCE_IDS [EVIDENCE_IDS ...] (required)

ssot-registry release remove-evidence [path]
  --id ID (required)
  --evidence-ids EVIDENCE_IDS [EVIDENCE_IDS ...] (required)

ssot-registry release certify [path]
  --release-id RELEASE_ID
  --write-report

ssot-registry release promote [path]
  --release-id RELEASE_ID

ssot-registry release publish [path]
  --release-id RELEASE_ID

ssot-registry release revoke [path]
  --release-id RELEASE_ID (required)
  --reason REASON (required)
```

### `graph`

Subcommands:

- `export`

```text
ssot-registry graph export [path]
  --format {json,dot,png,svg} (required)
  --output OUTPUT
```

### `registry`

Subcommands:

- `export`

```text
ssot-registry registry export [path]
  --format {json,csv,df,yaml,toml} (required)
  --output OUTPUT
```

---

## End-to-end usage examples

### E2E example 1: initialize and validate a repo

```bash
# Initialize registry under current repo
ssot-registry init . --repo-id rep:demo.app --repo-name "Demo App" --version 0.1.0

# Validate and write machine-readable report
ssot-registry validate . --write-report

# Inspect top-level entities
ssot-registry feature list .
ssot-registry claim list .
ssot-registry test list .
```

### E2E example 2: plan + implementation lifecycle + release flow

```bash
# 1) Create feature, claim, test, and evidence
ssot-registry feature create . --id feat:demo.login --title "User login"
ssot-registry claim create . --id clm:demo.login.t1 --title "Login succeeds" --kind behavior --tier T1
ssot-registry test create . --id tst:demo.login.unit --title "Login unit" --kind unit --test-path tests/test_login.py
ssot-registry evidence create . --id evd:demo.login.pytest --title "Pytest login run" --kind test_run --evidence-path artifacts/login.json --tier T1

# 2) Wire references
ssot-registry feature link . --id feat:demo.login --claim-ids clm:demo.login.t1 --test-ids tst:demo.login.unit
ssot-registry claim link . --id clm:demo.login.t1 --feature-ids feat:demo.login --test-ids tst:demo.login.unit --evidence-ids evd:demo.login.pytest
ssot-registry test link . --id tst:demo.login.unit --feature-ids feat:demo.login --claim-ids clm:demo.login.t1 --evidence-ids evd:demo.login.pytest

# 3) Plan and set lifecycle
ssot-registry feature plan . --ids feat:demo.login --horizon current --claim-tier T1 --target-lifecycle-stage active
ssot-registry feature lifecycle set . --ids feat:demo.login --stage active --note "Initial rollout"

# 4) Freeze boundary and create release
ssot-registry boundary create . --id bnd:demo.v0 --title "Demo v0 scope" --feature-ids feat:demo.login
ssot-registry boundary freeze . --boundary-id bnd:demo.v0
ssot-registry release create . --id rel:0.1.0 --version 0.1.0 --boundary-id bnd:demo.v0 --claim-ids clm:demo.login.t1 --evidence-ids evd:demo.login.pytest

# 5) Gate progression
ssot-registry release certify . --release-id rel:0.1.0 --write-report
ssot-registry release promote . --release-id rel:0.1.0
ssot-registry release publish . --release-id rel:0.1.0
```

### E2E example 3: graph exports and focused checks

```bash
# Evaluate one claim
ssot-registry claim evaluate . --claim-id clm:demo.login.t1

# Verify one evidence row
ssot-registry evidence verify . --evidence-id evd:demo.login.pytest

# Export graph in JSON, DOT, and PNG formats
ssot-registry graph export . --format json --output .ssot/graphs/registry.graph.json
ssot-registry graph export . --format dot --output .ssot/graphs/registry.graph.dot
ssot-registry graph export . --format png --output .ssot/graphs/registry.graph.png

# Render list output as YAML/CSV and export full registry as TOML
ssot-registry --output-format yaml feature list .
ssot-registry --output-format csv claim list .
ssot-registry registry export . --format toml --output .ssot/exports/registry.toml
```

---

## Documentation map (pointers to docs subdirectories)

- Specifications (`docs/specs/`)
  - CLI contract: `docs/specs/cli.md`
  - Registry core: `docs/specs/registry-core.md`
  - Graph model: `docs/specs/graph-model.md`
  - Lifecycle: `docs/specs/feature-lifecycle.md`
  - Claims and tiers: `docs/specs/claim-statuses.md`, `docs/specs/claim-tiers.md`
  - Boundaries/releases/snapshots: `docs/specs/snapshots-and-reports.md`
  - Validation policy: `docs/specs/repo-policy.md`, `docs/specs/gates-and-fences.md`
  - IDs and file tree: `docs/specs/id-normalization.md`, `docs/specs/file-tree.md`

- Architecture decisions (`docs/adr/`)
  - Rationale and decision history for the model and release flow.

- Examples (`docs/examples/`)
  - Minimal repo walkthrough, advanced/e2e examples, and format/export workflows (`docs/examples/formats-and-exports.md`).

- Root reference docs
  - Verification notes: `VERIFICATION.md`
  - Changelog: `CHANGELOG.md`

## Public operator surfaces

- Canonical JSON registry: `.ssot/registry.json`
- JSON Schema pack
- Noun-scoped CLI emitting JSON by default (with optional CSV/DF/YAML/TOML renderers)
- Python API under `ssot_registry.api`
- Derived graph, report, and snapshot artifacts

## Repository layout

- Specs: `docs/specs/`
- ADRs: `docs/adr/`
- Examples: `docs/examples/` and `examples/`
- Source code: `src/ssot_registry/`

## Development

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
python -m unittest discover -s tests -v
```
