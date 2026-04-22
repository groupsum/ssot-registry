<div align="center">
  <h1>🔷 ssot-cli</h1>
  <p><strong>Primary command-line distribution for SSOT workflows.</strong></p>
</div>

<div align="center">
  <a href="https://pypi.org/project/ssot-cli/"><img src="https://img.shields.io/pypi/v/ssot-cli?label=PyPI%20version" alt="PyPI version" /></a>
  <a href="https://pypi.org/project/ssot-cli/"><img src="https://img.shields.io/pypi/pyversions/ssot-cli?label=Python" alt="Supported Python versions" /></a>
  <a href="https://pepy.tech/project/ssot-cli"><img src="https://static.pepy.tech/badge/ssot-cli" alt="Downloads" /></a>
  <a href="https://hits.sh/github.com/groupsum/ssot-registry/"><img src="https://hits.sh/github.com/groupsum/ssot-registry.svg?style=flat-square" alt="Repository hits" /></a>
</div>

`ssot-cli` is the primary command-line distribution for SSOT.

It installs `ssot`, `ssot-cli`, and `ssot-registry` as equivalent executables over the same parser and runtime. The command surface is implemented here, while domain logic lives in [ssot-core](https://pypi.org/project/ssot-core/) and shared contract metadata comes from [ssot-contracts](https://pypi.org/project/ssot-contracts/).

- GitHub: https://github.com/groupsum/ssot-registry

## What this package owns

- The primary end-user CLI distribution
- Argument parsing and command registration for the SSOT command surface
- Structured output rendering and file-output conventions for CLI workflows

## Install

```bash
python -m pip install ssot-cli
```

For local development:

```bash
python -m pip install -e pkgs/ssot-cli
```

This package depends on [ssot-core](https://pypi.org/project/ssot-core/) and [ssot-contracts](https://pypi.org/project/ssot-contracts/), so installing it gives you the full CLI runtime stack.

## Executable names

This package installs three equivalent console scripts:

- `ssot`
- `ssot-cli`
- `ssot-registry`

Prefer `ssot` in new automation and documentation. `ssot-registry` remains a compatibility alias. Every command block below can be invoked with any of the three names.

## Boundaries vs releases

Boundaries and releases are intentionally different:

- A boundary defines the scoped set of features and profiles that belong to a candidate delivery unit.
- Freezing a boundary locks that resolved scope and emits a boundary snapshot.
- A release points at a frozen boundary and then bundles claims and evidence for certify, promote, publish, and revoke workflows.

## Entity intent

Operators should read the top-level entity commands this way:

- `adr`: architectural decision records that capture why the system is designed the way it is.
- `spec`: specification documents that define normative, operational, governance, or local-policy contract.
- `feature`: implementation units that connect planning, delivery status, tests, claims, and SPEC coverage.
- `profile`: reusable capability or deployment bundles composed from features and nested profiles.
- `test`: verification rows that point at executable or procedural checks.
- `claim`: tiered statements about system behavior that must be supported by tests and evidence.
- `evidence`: concrete artifacts, reports, bundles, or logs that substantiate tests and claims.
- `issue`: plannable defects or work items that may block a release.
- `risk`: tracked exposure that must be mitigated, accepted, or retired.
- `boundary`: scoped delivery definition used to decide what a release is evaluated against.
- `release`: publication unit tied to a frozen boundary plus the claims and evidence needed for certification.
- `graph`: relationship export view of the registry.
- `registry`: full-document export view of the registry.

Each command's `--help` now describes not just what it does mechanically, but why an operator would use it and what each flag is meant to control.

## CLI quick reference

```bash
ssot --help
ssot-cli --help
ssot-registry --help
ssot profile --help
ssot feature --help
ssot boundary --help
ssot release --help
ssot graph --help
ssot registry --help
```

## Screenshots

Regenerate these assets with `python scripts/generate_cli_screenshots.py`.

![ssot top-level help](https://raw.githubusercontent.com/groupsum/ssot-registry/main/pkgs/ssot-cli/assets/ssot-cli-help.png)

Boundary command help:

![ssot boundary help](https://raw.githubusercontent.com/groupsum/ssot-registry/main/pkgs/ssot-cli/assets/ssot-cli-boundary-help.png)

## CLI conventions

- Most commands accept `[path]` as an optional positional argument. Default is current directory (`.`).
- Commands emit structured output by default.
- Global rendering flags apply to all commands:

```text
--output-format {json,csv,df,yaml,toml}
--output-file PATH
```

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

- `export`, `sync-statuses`

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

ssot-registry registry sync-statuses [path]
  --dry-run
```

## Example workflows

```bash
ssot init . --repo-id repo:demo.app --repo-name "Demo App" --version 0.1.0
ssot validate . --write-report
ssot feature list .
ssot profile list .
ssot boundary list .
```

```bash
ssot boundary create . --id bnd:demo.v0 --title "Demo v0 scope" --feature-ids feat:demo.login --profile-ids prf:demo.core
ssot boundary freeze . --boundary-id bnd:demo.v0
ssot release create . --id rel:0.1.0 --version 0.1.0 --boundary-id bnd:demo.v0 --claim-ids clm:demo.login.t1 --evidence-ids evd:demo.login.pytest
ssot release certify . --release-id rel:0.1.0 --write-report
```

## Package relationships

- Package type: CLI distribution
- Depends on: [ssot-core](https://pypi.org/project/ssot-core/), [ssot-contracts](https://pypi.org/project/ssot-contracts/)
- Related packages: [ssot-registry](https://pypi.org/project/ssot-registry/), [ssot-tui](https://pypi.org/project/ssot-tui/), [ssot-views](https://pypi.org/project/ssot-views/), [ssot-codegen](https://pypi.org/project/ssot-codegen/)

If you need the command-line interface, this is the package to install.
