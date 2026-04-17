<div align="center">
  <h1>🔷 ssot-registry</h1>
  <p><strong>Single Source of Truth for features, profiles, claims, tests, releases, ADRs, and specs.</strong></p>
</div>

<div align="center">
  <a href="https://pypi.org/project/ssot-registry/"><img src="https://img.shields.io/pypi/v/ssot-registry?label=PyPI%20version" alt="PyPI version" /></a>
  <a href="https://pypi.org/project/ssot-registry/"><img src="https://img.shields.io/pypi/pyversions/ssot-registry?label=Python" alt="Supported Python versions" /></a>
  <a href="https://pepy.tech/project/ssot-registry"><img src="https://static.pepy.tech/badge/ssot-registry" alt="Downloads" /></a>
  <a href="https://hits.sh/github.com/groupsum/ssot-registry/"><img src="https://hits.sh/github.com/groupsum/ssot-registry.svg?style=flat-square" alt="Hits" /></a>
</div>

`ssot-registry` is the core Python runtime package for SSOT.

It owns the canonical registry model, core APIs for loading and mutating registries, validation and guard logic, planning and release workflows, and the domain operations that `ssot-cli` and `ssot-tui` build on top of.

- GitHub: https://github.com/groupsum/ssot-registry

## Core model

`ssot-registry` treats `.ssot/registry.json` as the canonical machine-readable source of truth for:

- features
- profiles
- tests
- claims
- evidence
- issues
- risks
- boundaries
- releases
- ADRs
- specs

Everything else is derived from it.

### Boundaries vs releases

Boundaries are not releases.

- A boundary is the frozen scope of features and profiles for a delivery unit.
- Freezing a boundary validates the registry, locks that scope, and emits a boundary snapshot.
- A release references a frozen boundary and then bundles the claims and evidence used for certify, promote, publish, and revoke workflows.

If you omit this distinction, releases look redundant. They are not: boundaries freeze scope; releases attest and ship against that frozen scope.

## Canonical format

The canonical authored format is JSON. Markdown, CSV, DOT, SQLite, reports, and snapshots are derived projections.

## Install

```bash
python -m pip install ssot-registry   # core library/runtime
python -m pip install ssot-cli        # primary CLI distribution
python -m pip install ssot-tui        # Textual terminal UI
```

For local development:

```bash
python -m pip install -e pkgs/ssot-registry
```

`ssot-registry` remains the canonical import package. The preferred CLI distribution now ships from `ssot-cli`, including `ssot`, `ssot-cli`, and the compatibility alias `ssot-registry`.

## What this package owns

- the canonical `.ssot/registry.json` data model
- runtime APIs under `ssot_registry.api`
- validators, guards, graph builders, reports, and snapshot generation
- planning, profile evaluation, evidence verification, document lifecycle, and release gating logic

## Python API examples

Initialize and validate a repository:

```python
from ssot_registry.api import initialize_repo, validate_registry

initialize_repo(".", repo_id="demo-repo", repo_name="Demo Repo", version="0.1.0")
report = validate_registry(".")
print(report["passed"])
```

Load and save a registry:

```python
from ssot_registry.api import load_registry, save_registry

registry_path, repo_root, registry = load_registry(".")
save_registry(registry_path, registry)
```

Freeze a boundary and export a graph:

```python
from ssot_registry.api import export_graph, freeze_boundary

freeze_boundary(".", boundary_id="bnd:demo.v0")
graph_result = export_graph(".", "json")
print(graph_result["output_path"])
```

Representative API areas currently exposed from `ssot_registry.api` include:

- repository initialization, load, save, validate, and upgrade
- entity CRUD and linking operations
- document creation, synchronization, supersession, and reservations
- feature planning and lifecycle updates
- profile evaluation and profile resolution
- evidence verification and claim evaluation
- boundary freezing and release certification, promotion, publication, and revocation
- graph and registry export

## CLI quick reference

Install `ssot-cli` for the primary command surface. The same parser is available under:

- `ssot`
- `ssot-cli`
- `ssot-registry`

Examples in the long-form reference below use `ssot-registry`, but every command can be invoked with any of the three executable names.

```bash
ssot --help
ssot-cli --help
ssot-registry --help
ssot-registry profile --help
ssot-registry feature --help
ssot-registry boundary --help
ssot-registry release --help
ssot-registry graph --help
ssot-registry registry --help
```

## CLI conventions

- Most commands accept `[path]` as an optional positional argument. Default is current directory (`.`).
- Prefer `ssot ...` in new automation and examples; `ssot-registry ...` remains a compatibility alias.
- IDs are normalized prefixed identifiers such as `feat:*`, `prf:*`, `clm:*`, `tst:*`, `evd:*`, `iss:*`, `rsk:*`, `bnd:*`, `rel:*`, `adr:*`, and `spc:*`.
- Commands emit JSON by default; use `--output-format {json,csv,df,yaml,toml}` for alternate renderings.
- Use `--output-file PATH` to save rendered command output to disk.
- Non-zero exit code indicates an operation failure or failed checks.

## Command surface

### Top-level commands

- `init`
- `validate`
- `upgrade`
- `adr`
- `spec`
- `feature`
- `profile`
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

- `create`, `get`, `list`, `update`, `set-status`, `supersede`, `delete`, `sync`
- `reserve create`, `reserve list`

```text
ssot-registry adr create [path]
  --title TITLE (required)
  --slug SLUG (required)
  --body-file BODY_FILE (required)
  --number NUMBER
  --status {draft,in_review,accepted,rejected,withdrawn,superseded,retired}
  --note NOTE
  --origin {repo-local,ssot-origin,ssot-core}
  --reserve-range RANGE_NAME

ssot-registry adr get [path]
  --id ID (required)

ssot-registry adr list [path]

ssot-registry adr update [path]
  --id ID (required)
  --title TITLE
  --body-file BODY_FILE
  --status {draft,in_review,accepted,rejected,withdrawn,superseded,retired}
  --note NOTE

ssot-registry adr set-status [path]
  --id ID (required)
  --status {draft,in_review,accepted,rejected,withdrawn,superseded,retired} (required)
  --note NOTE

ssot-registry adr supersede [path]
  --id ID (required)
  --supersedes IDS [IDS ...] (required)
  --note NOTE

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

- `create`, `get`, `list`, `update`, `set-status`, `supersede`, `delete`, `sync`
- `reserve create`, `reserve list`

```text
ssot-registry spec create [path]
  --title TITLE (required)
  --slug SLUG (required)
  --body-file BODY_FILE (required)
  --number NUMBER
  --origin {repo-local,ssot-origin,ssot-core}
  --kind {normative,operational,governance,local-policy}
  --status {draft,in_review,accepted,rejected,withdrawn,superseded,retired}
  --note NOTE
  --reserve-range RANGE_NAME

ssot-registry spec get [path]
  --id ID (required)

ssot-registry spec list [path]

ssot-registry spec update [path]
  --id ID (required)
  --title TITLE
  --body-file BODY_FILE
  --kind {normative,operational,governance,local-policy}
  --status {draft,in_review,accepted,rejected,withdrawn,superseded,retired}
  --note NOTE

ssot-registry spec set-status [path]
  --id ID (required)
  --status {draft,in_review,accepted,rejected,withdrawn,superseded,retired} (required)
  --note NOTE

ssot-registry spec supersede [path]
  --id ID (required)
  --supersedes IDS [IDS ...] (required)
  --note NOTE

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

- `create`, `get`, `list`, `update`, `delete`, `link`, `unlink`, `plan`
- `lifecycle set`

```text
ssot-registry feature create [path]
  --id ID (required)
  --title TITLE (required)
  --description DESCRIPTION
  --implementation-status {absent,implemented,partial}
  --lifecycle-stage {active,deprecated,obsolete,removed}
  --replacement-feature-id [REPLACEMENT_FEATURE_ID ...]
  --note NOTE
  --horizon {backlog,current,explicit,future,next,out_of_bounds}
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
  --implementation-status {absent,implemented,partial}

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
  --horizon {backlog,current,explicit,future,next,out_of_bounds} (required)
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

### `profile`

Subcommands:

- `create`, `get`, `list`, `update`, `delete`, `link`, `unlink`, `evaluate`, `verify`

```text
ssot-registry profile create [path]
  --id ID (required)
  --title TITLE (required)
  --description DESCRIPTION
  --status {draft,active,retired}
  --kind {capability,certification,deployment,interoperability}
  --feature-ids [FEATURE_IDS ...]
  --profile-ids [PROFILE_IDS ...]
  --claim-tier {T0,T1,T2,T3,T4}
  --allow-feature-override-tier | --no-allow-feature-override-tier

ssot-registry profile get [path]
  --id ID (required)

ssot-registry profile list [path]

ssot-registry profile update [path]
  --id ID (required)
  --title TITLE
  --description DESCRIPTION
  --status {draft,active,retired}
  --kind {capability,certification,deployment,interoperability}
  --claim-tier {T0,T1,T2,T3,T4}

ssot-registry profile delete [path]
  --id ID (required)

ssot-registry profile link [path]
  --id ID (required)
  --feature-ids [FEATURE_IDS ...]
  --profile-ids [PROFILE_IDS ...]

ssot-registry profile unlink [path]
  --id ID (required)
  --feature-ids [FEATURE_IDS ...]
  --profile-ids [PROFILE_IDS ...]

ssot-registry profile evaluate [path]
  --profile-id PROFILE_ID (required)

ssot-registry profile verify [path]
  --profile-id PROFILE_ID (required)
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

- `create`, `get`, `list`, `update`, `delete`
- `add-feature`, `remove-feature`, `add-profile`, `remove-profile`
- `freeze`

```text
ssot-registry boundary create [path]
  --id ID (required)
  --title TITLE (required)
  --status {draft,active,frozen,retired}
  --frozen | --no-frozen
  --feature-ids [FEATURE_IDS ...]
  --profile-ids [PROFILE_IDS ...]

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

ssot-registry boundary add-profile [path]
  --id ID (required)
  --profile-ids PROFILE_IDS [PROFILE_IDS ...] (required)

ssot-registry boundary remove-profile [path]
  --id ID (required)
  --profile-ids PROFILE_IDS [PROFILE_IDS ...] (required)

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

## End-to-end examples

### Initialize and inspect a repo

```bash
ssot-registry init . --repo-id repo:demo.app --repo-name "Demo App" --version 0.1.0
ssot-registry validate . --write-report
ssot-registry feature list .
ssot-registry profile list .
ssot-registry adr list .
ssot-registry spec list .
```

### Freeze scope and release against it

```bash
ssot-registry boundary create . --id bnd:demo.v0 --title "Demo v0 scope" --feature-ids feat:demo.login --profile-ids prf:demo.core
ssot-registry boundary freeze . --boundary-id bnd:demo.v0
ssot-registry release create . --id rel:0.1.0 --version 0.1.0 --boundary-id bnd:demo.v0 --claim-ids clm:demo.login.t1 --evidence-ids evd:demo.login.pytest
ssot-registry release certify . --release-id rel:0.1.0 --write-report
ssot-registry release promote . --release-id rel:0.1.0
ssot-registry release publish . --release-id rel:0.1.0
```

### Graphs and exports

```bash
ssot-registry graph export . --format json --output .ssot/graphs/registry.graph.json
ssot-registry graph export . --format dot --output .ssot/graphs/registry.graph.dot
ssot-registry registry export . --format toml --output .ssot/exports/registry.toml
```

## Documentation map

- Specifications: `docs/specs/`
- Architecture decisions: `docs/adr/`
- Examples: `examples/`
- Source code: `pkgs/*/src/`

## Package relationships

- Package type: core runtime/library package
- Depends on: `ssot-contracts`, `ssot-views`
- Consumed by: `ssot-cli`, `ssot-tui`, direct Python integrations, and automation

If you are embedding SSOT behavior inside Python code, this is the package to import. If you need the primary CLI distribution, install `ssot-cli` alongside it.
