<div align="center">
  <h1>ðŸ”· ssot-registry</h1>
  <p><strong>Single Source of Truth for features, claims, tests, releases, ADRs, and specs.</strong></p>
</div>

<div align="center">
  <a href="https://pypi.org/project/ssot-registry/"><img src="https://img.shields.io/pypi/v/ssot-registry?label=PyPI%20version" alt="PyPI version" /></a>
  <a href="https://pypi.org/project/ssot-registry/"><img src="https://img.shields.io/pypi/pyversions/ssot-registry?label=Python" alt="Supported Python versions" /></a>
  <a href="https://pepy.tech/project/ssot-registry"><img src="https://static.pepy.tech/badge/ssot-registry" alt="Downloads" /></a>
  <a href="https://hits.sh/github.com/groupsum/ssot-registry/"><img src="https://hits.sh/github.com/groupsum/ssot-registry.svg?style=flat-square" alt="Hits" /></a>
<!-- ssot-schema-badges:start -->
  <img src="https://img.shields.io/badge/schema_version-0.2.0-blue" alt="schema_version 0.2.0" />
  <img src="https://img.shields.io/badge/migration%20coverage-9%2F9-brightgreen" alt="Migration coverage 9/9" />
<!-- ssot-schema-badges:end -->
</div>

`ssot-registry` is a portable, repository-agnostic single-source-of-truth system built from [ssot-core](https://pypi.org/project/ssot-core/), [ssot-cli](https://pypi.org/project/ssot-cli/), [ssot-contracts](https://pypi.org/project/ssot-contracts/), [ssot-views](https://pypi.org/project/ssot-views/), [ssot-tui](https://pypi.org/project/ssot-tui/), and [ssot-codegen](https://pypi.org/project/ssot-codegen/).

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
- ADRs
- specs

The canonical machine-readable artifact is:

```text
.ssot/registry.json
```

Everything else is derived from it.

<!-- ssot-schema-version:start -->
Current registry `schema_version`: `0.2.0`.
<!-- ssot-schema-version:end -->

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

`.ssot/registry.json` remains the canonical machine-readable registry.

ADR and SPEC companion documents are canonically authored as JSON under `.ssot/adr/` and `.ssot/specs/`. Generated Markdown, CSV, DOT, SQLite, reports, and other rendered views are derived projections for human readability and MUST NOT be treated as authoritative SSOT inputs.

## Schema 4

Schema `4` introduces first-class ADR and spec sections in `.ssot/registry.json`:

- `tooling`
- `document_id_reservations`
- `adrs`
- `specs`

Packaged SSOT documents are manifest-driven, immutable, and synced into reserved SSOT-owned ranges. Repository-local ADRs and specs are created in separate non-overlapping ranges so local numbering cannot collide with SSOT-managed documents.

## Install

```bash
python -m pip install ssot-registry         # [ssot-core](https://pypi.org/project/ssot-core/) + [ssot-cli](https://pypi.org/project/ssot-cli/)
python -m pip install "ssot-registry[tui]"  # add optional [ssot-tui](https://pypi.org/project/ssot-tui/)
python -m pip install ssot-core             # runtime only
python -m pip install ssot-cli              # primary CLI distribution
python -m pip install ssot-tui              # Textual TUI only
# or for local development
python -m pip install -e pkgs/ssot-core
```

`ssot_registry` remains the canonical import package. The runtime now ships from [ssot-core](https://pypi.org/project/ssot-core/), while CLI entry points ship from [ssot-cli](https://pypi.org/project/ssot-cli/), including both `ssot` and the compatibility alias `ssot-registry`.

The repository root is workspace tooling only. Canonical release artifacts are built from package roots under `pkgs/`, and the canonical Python runtime release target is `pkgs/ssot-core`.

If you already have a repository initialized on schema `3`, upgrade it explicitly after installing the new package:

```bash
ssot upgrade . --sync-docs --write-report
# compatibility alias
ssot-registry upgrade . --sync-docs --write-report
```

## Community

Please review [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) before contributing.

## CLI quick reference

Install `ssot-cli` for the primary command surface. You can invoke the CLI with `ssot`, and `ssot-registry` remains supported as a compatibility alias.

```bash
ssot --help
ssot-cli --help
ssot-registry --help
ssot-registry init --help
ssot-registry validate --help
ssot-registry upgrade --help
ssot-registry adr --help
ssot-registry spec --help
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

## Screenshots

CLI screenshots from [ssot-cli](https://pypi.org/project/ssot-cli/):

![ssot top-level help](https://raw.githubusercontent.com/groupsum/ssot-registry/main/pkgs/ssot-cli/assets/ssot-cli-help.png)

![ssot boundary help](https://raw.githubusercontent.com/groupsum/ssot-registry/main/pkgs/ssot-cli/assets/ssot-cli-boundary-help.png)

TUI screenshots from [ssot-tui](https://pypi.org/project/ssot-tui/):

![SSOT TUI browser](https://raw.githubusercontent.com/groupsum/ssot-registry/main/pkgs/ssot-tui/assets/ssot-tui-browser.png)

![SSOT TUI ADR browser](https://raw.githubusercontent.com/groupsum/ssot-registry/main/pkgs/ssot-tui/assets/ssot-tui-adrs.png)

![SSOT TUI spec browser](https://raw.githubusercontent.com/groupsum/ssot-registry/main/pkgs/ssot-tui/assets/ssot-tui-specs.png)

![SSOT TUI validation status](https://raw.githubusercontent.com/groupsum/ssot-registry/main/pkgs/ssot-tui/assets/ssot-tui-validated.png)

---

## CLI conventions

- Most commands accept `[path]` as an optional positional argument. Default is current directory (`.`).
- Prefer `ssot ...` in new documentation and automation; `ssot-registry ...` is a compatibility alias.
- IDs are normalized prefixed identifiers (for example: `feat:*`, `clm:*`, `tst:*`, `evd:*`, `iss:*`, `rsk:*`, `bnd:*`, `rel:*`).
- Commands emit JSON by default; use `--output-format {json,csv,df,yaml,toml}` for alternate renderings.
- Use `--output-file PATH` to save rendered command output to disk.
- Non-zero exit code indicates an operation failure or failed checks.

---

## Command surface (all commands, subcommands, and flags)

### Top-level commands

- `init`
- `validate`
- `upgrade`
- `adr`
- `spec`
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

### `upgrade`

```text
ssot-registry upgrade [path]
  --target-version VERSION
  --sync-docs
  --write-report
```

### `adr`

Subcommands:

- `create`, `get`, `list`, `update`, `delete`, `sync`
- `reserve create`, `reserve list`

```text
ssot-registry adr create [path]
  --title TITLE (required)
  --slug SLUG (required)
  --body-file BODY_FILE (required)
  --number NUMBER
  --status {proposed,accepted,superseded,retired}
  --origin {repo-local}
  --reserve-range RANGE_NAME

ssot-registry adr get [path]
  --id ID (required)

ssot-registry adr list [path]

ssot-registry adr update [path]
  --id ID (required)
  --title TITLE
  --body-file BODY_FILE
  --status {proposed,accepted,superseded,retired}

ssot-registry adr delete [path]
  --id ID (required)

ssot-registry adr sync [path]

ssot-registry adr reserve create [path]
  --name NAME (required)
  --start START (required)
  --end END (required)

ssot-registry adr reserve list [path]
```

### `spec`

Subcommands:

- `create`, `get`, `list`, `update`, `delete`, `sync`
- `reserve create`, `reserve list`

```text
ssot-registry spec create [path]
  --title TITLE (required)
  --slug SLUG (required)
  --body-file BODY_FILE (required)
  --number NUMBER
  --origin {repo-local}
  --kind {normative,operational,repo-local}
  --reserve-range RANGE_NAME

ssot-registry spec get [path]
  --id ID (required)

ssot-registry spec list [path]

ssot-registry spec update [path]
  --id ID (required)
  --title TITLE
  --body-file BODY_FILE
  --kind {normative,operational,repo-local}

ssot-registry spec delete [path]
  --id ID (required)

ssot-registry spec sync [path]

ssot-registry spec reserve create [path]
  --name NAME (required)
  --start START (required)
  --end END (required)

ssot-registry spec reserve list [path]
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
  --out-of-bounds-disposition {prohibited,tolerated}
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
  --out-of-bounds-disposition {prohibited,tolerated}
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
ssot-registry init . --repo-id repo:demo.app --repo-name "Demo App" --version 0.1.0

# Validate and write machine-readable report
ssot-registry validate . --write-report

# Inspect top-level entities
ssot-registry feature list .
ssot-registry claim list .
ssot-registry test list .
ssot-registry adr list .
ssot-registry spec list .
```

### E2E example 1b: create repo-local ADRs and specs

```bash
# Create local ADR/spec bodies
cat > adr-body.json <<'EOF'
{"body":"Adopt local numbering for repository-owned decisions."}
EOF

cat > spec-body.json <<'EOF'
{"body":"Repository-local operational conventions for maintainers."}
EOF

# Create repo-local documents from the local reservation range
ssot-registry adr create . --title "Use repo-local ADR numbering" --slug use-repo-local-adr-numbering --body-file adr-body.json
ssot-registry spec create . --title "Maintainer operating conventions" --slug maintainer-operating-conventions --body-file spec-body.json --kind operational

# Inspect or sync the document sets
ssot-registry adr list .
ssot-registry spec list .
ssot-registry adr sync .
ssot-registry spec sync .
```

### E2E example 1c: pre-freeze scope ADRs, SPECs, features, and tests

```bash
# 1) Inspect existing scoped identifiers if the target change is unclear
ssot-registry adr list .
ssot-registry spec list .
ssot-registry feature list .
ssot-registry test list .

# 2) Create repo-local ADR and SPEC bodies for the proposed change
cat > adr-body.yaml <<'EOF'
body: |-
  Scope the login rollout before boundary freeze.
EOF

cat > spec-body.yaml <<'EOF'
body: |-
  Define the pre-freeze login contract and coverage expectations.
EOF

# 3) Create governance documents and connect the SPEC back to the ADR
ssot-registry adr create . --title "Scope login rollout" --slug scope-login-rollout --body-file adr-body.yaml
ssot-registry spec create . --title "Login pre-freeze contract" --slug login-pre-freeze-contract --body-file spec-body.yaml --kind operational --adr-ids adr:1000

# 4) Create and plan the scoped feature against that SPEC.
# If the repo already has claim/evidence rows for this capability, attach them now so later test registration validates cleanly.
ssot-registry feature create . --id feat:demo.login --title "User login" --spec-ids spc:1000 --claim-ids clm:demo.login.t1
ssot-registry feature plan . --ids feat:demo.login --horizon current --claim-tier T1 --target-lifecycle-stage active

# 5) Create the scoped test and wire the feature/test edge bidirectionally.
# Reuse existing claim/evidence rows when the repo validates complete verification edges for every test row.
mkdir -p tests
cat > tests/test_login.py <<'EOF'
def test_login():
    assert True
EOF
ssot-registry test create . --id tst:demo.login.unit --title "Login unit" --status passing --kind unit --test-path tests/test_login.py --feature-ids feat:demo.login --claim-ids clm:demo.login.t1 --evidence-ids evd:demo.login.pytest
ssot-registry feature link . --id feat:demo.login --test-ids tst:demo.login.unit

# Stop here for the pre-freeze scoped flow.
# Boundary freeze, implementation, migration, and release proof happen later.
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

## Documentation map (core vs origin)

- Canonical upstream `ssot-core` docs (`.ssot/`)
  - Upstream ADR inventory: `.ssot/adr/`
  - Upstream spec inventory: `.ssot/specs/`

- Canonical upstream governance docs (`.ssot/`)
  - Package topology and release order: `.ssot/specs/SPEC-0500-package-topology-and-release-order.yaml`
  - Canonical release targets: `.ssot/specs/SPEC-0510-canonical-release-targets-and-tag-naming.yaml`
  - Origin/core boundary rules: `.ssot/specs/SPEC-0512-document-origin-boundaries-and-id-ranges.yaml`
  - Architecture decisions for package layout and release flow: `.ssot/adr/`

- Public operator `ssot-origin` templates (`pkgs/ssot-contracts/src/ssot_contracts/templates/`)
  - ADRs copied into downstream repos: `pkgs/ssot-contracts/src/ssot_contracts/templates/adr/`
  - Specs copied into downstream repos: `pkgs/ssot-contracts/src/ssot_contracts/templates/specs/`

- Examples (`examples/`)
  - Minimal repo fixtures, advanced/e2e examples, and format/export workflows (`examples/formats-and-exports.md`).

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

- Specs: `.ssot/specs/`
- ADRs: `.ssot/adr/`
- Examples: `examples/`
- Source code: `pkgs/*/src/`

## Development

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e pkgs/ssot-registry
python -m unittest discover -s tests -v
```
