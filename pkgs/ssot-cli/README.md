<div align="center">
  <h1>🔷 ssot-cli</h1>
  <p><strong>Primary command-line distribution for SSOT workflows.</strong></p>
</div>

<div align="center">
  <a href="https://pypi.org/project/ssot-cli/"><img src="https://img.shields.io/pypi/v/ssot-cli?label=PyPI%20version" alt="PyPI version" /></a>
  <a href="https://pypi.org/project/ssot-cli/"><img src="https://img.shields.io/pypi/pyversions/ssot-cli?label=Python" alt="Supported Python versions" /></a>
  <a href="https://pepy.tech/project/ssot-cli"><img src="https://static.pepy.tech/badge/ssot-cli" alt="Downloads" /></a>
  <a href="https://hits.sh/github.com/groupsum/ssot-registry/"><img src="https://hits.sh/github.com/groupsum/ssot-registry.svg?style=flat-square" alt="Repository hits" /></a>
<!-- ssot-schema-badges:start -->
  <img src="https://img.shields.io/badge/schema_version-0.7.0-blue" alt="schema_version 0.7.0" />
  <img src="https://img.shields.io/badge/migration%20coverage-14%2F14-brightgreen" alt="Migration coverage 14/14" />
<!-- ssot-schema-badges:end -->
</div>

`ssot-cli` is the primary command-line distribution for SSOT.

It installs `ssot`, `ssot-cli`, and `ssot-registry` as equivalent executables over the same parser and runtime. The command surface is implemented here, while domain logic lives in [ssot-core](https://pypi.org/project/ssot-core/), reusable conformance checks come from [ssot-conformance](https://pypi.org/project/ssot-conformance/), shared contract metadata comes from [ssot-contracts](https://pypi.org/project/ssot-contracts/), and governance pack interoperability contracts come from [ssot-pack-contracts](https://pypi.org/project/ssot-pack-contracts/).

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

This package depends on [ssot-core](https://pypi.org/project/ssot-core/), [ssot-conformance](https://pypi.org/project/ssot-conformance/), [ssot-contracts](https://pypi.org/project/ssot-contracts/), and [ssot-pack-contracts](https://pypi.org/project/ssot-pack-contracts/), so installing it gives you the full CLI runtime stack for registry operations and governance pack contract checks.

The CLI tracks the current core release train through compatible `<0.3.0` ranges and uses the current `ssot-pack-contracts` floor. That keeps pack-aware CLI behavior compatible with the latest contract package without forcing unrelated surface packages into core lockstep.

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

The screenshots below are generated from the current parser help. Regenerate them with `python scripts/generate_cli_screenshots.py`, or regenerate the CLI and TUI assets together with `python scripts/generate_terminal_screenshots.py`.

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

## Registry-driven test execution

Tests are the executable SSOT entities. Specs and boundaries resolve to tests through registry links, and runnable tests carry an `execution` object that stores the command, cwd, environment, timeout, and success rule.

Examples:

```bash
ssot test run . --id tst:pytest.conformance.registry-contract
ssot spec run-tests . --id spc:0525
ssot boundary run-tests . --id bnd:full-cert
ssot conformance run . --profiles registry
```

`ssot conformance run` remains a compatibility wrapper for packaged conformance families. The primary operator story is now registry-driven execution through `test`, `spec`, and `boundary`.

## Command surface

### Complete parser manifest

This table is generated from the live `argparse` parser and is checked by integration tests against the current CLI implementation.

Global flags: `--output-file`, `--output-format`, `--version`

| Command path | Flags |
| --- | --- |
| `ssot-registry adr` | none |
| `ssot-registry adr create` | `--body`, `--body-file`, `--note`, `--number`, `--origin`, `--reserve-range`, `--slug`, `--status`, `--title` |
| `ssot-registry adr delete` | `--id` |
| `ssot-registry adr get` | `--id` |
| `ssot-registry adr list` | `--ids` |
| `ssot-registry adr reserve` | none |
| `ssot-registry adr reserve create` | `--end`, `--name`, `--start` |
| `ssot-registry adr reserve list` | none |
| `ssot-registry adr set-status` | `--id`, `--note`, `--status` |
| `ssot-registry adr supersede` | `--id`, `--note`, `--supersedes` |
| `ssot-registry adr sync` | none |
| `ssot-registry adr update` | `--body`, `--body-file`, `--id`, `--note`, `--status`, `--title` |
| `ssot-registry boundary` | none |
| `ssot-registry boundary add-feature` | `--feature-ids`, `--id` |
| `ssot-registry boundary add-profile` | `--id`, `--profile-ids` |
| `ssot-registry boundary create` | `--body`, `--body-file`, `--feature-ids`, `--frozen`, `--id`, `--no-frozen`, `--profile-ids`, `--status`, `--title` |
| `ssot-registry boundary delete` | `--id` |
| `ssot-registry boundary freeze` | `--boundary-id` |
| `ssot-registry boundary get` | `--id` |
| `ssot-registry boundary list` | `--ids` |
| `ssot-registry boundary remove-feature` | `--feature-ids`, `--id` |
| `ssot-registry boundary remove-profile` | `--id`, `--profile-ids` |
| `ssot-registry boundary run-tests` | `--dry-run`, `--evidence-output`, `--id` |
| `ssot-registry boundary update` | `--body`, `--body-file`, `--frozen`, `--id`, `--no-frozen`, `--status`, `--title` |
| `ssot-registry campaign` | none |
| `ssot-registry campaign status` | `--campaign-id`, `--target-tier` |
| `ssot-registry claim` | none |
| `ssot-registry claim create` | `--body`, `--body-file`, `--depends-on-claim-ids`, `--description`, `--evidence-ids`, `--feature-ids`, `--id`, `--kind`, `--origin`, `--status`, `--test-ids`, `--tier`, `--title` |
| `ssot-registry claim delete` | `--id` |
| `ssot-registry claim evaluate` | `--claim-id`, `--include-tier-gate` |
| `ssot-registry claim get` | `--id` |
| `ssot-registry claim link` | `--depends-on-claim-ids`, `--evidence-ids`, `--feature-ids`, `--id`, `--test-ids` |
| `ssot-registry claim list` | `--ids`, `--origin` |
| `ssot-registry claim set-status` | `--id`, `--status` |
| `ssot-registry claim set-tier` | `--id`, `--tier` |
| `ssot-registry claim unlink` | `--depends-on-claim-ids`, `--evidence-ids`, `--feature-ids`, `--id`, `--test-ids` |
| `ssot-registry claim update` | `--body`, `--body-file`, `--description`, `--id`, `--kind`, `--origin`, `--title` |
| `ssot-registry config` | none |
| `ssot-registry config init` | `--force` |
| `ssot-registry config show` | none |
| `ssot-registry config validate` | none |
| `ssot-registry conformance` | none |
| `ssot-registry conformance discover` | `--profiles` |
| `ssot-registry conformance origin` | `--apply`, `--include-claims`, `--include-evidence`, `--kinds`, `--overwrite`, `--report-output` |
| `ssot-registry conformance profile` | none |
| `ssot-registry conformance profile list` | none |
| `ssot-registry conformance run` | `--dry-run`, `--evidence-output`, `--profiles` |
| `ssot-registry conformance scaffold` | `--apply`, `--include-claims`, `--include-evidence`, `--profiles` |
| `ssot-registry evidence` | none |
| `ssot-registry evidence create` | `--body`, `--body-file`, `--claim-ids`, `--evidence-path`, `--id`, `--kind`, `--origin`, `--status`, `--test-ids`, `--tier`, `--title` |
| `ssot-registry evidence delete` | `--id` |
| `ssot-registry evidence get` | `--id` |
| `ssot-registry evidence link` | `--claim-ids`, `--id`, `--test-ids` |
| `ssot-registry evidence list` | `--ids`, `--origin` |
| `ssot-registry evidence unlink` | `--claim-ids`, `--id`, `--test-ids` |
| `ssot-registry evidence update` | `--body`, `--body-file`, `--evidence-path`, `--id`, `--kind`, `--origin`, `--status`, `--tier`, `--title` |
| `ssot-registry evidence verify` | `--evidence-id` |
| `ssot-registry feature` | none |
| `ssot-registry feature children` | none |
| `ssot-registry feature children add` | `--child-ids`, `--id` |
| `ssot-registry feature children list` | `--id` |
| `ssot-registry feature children remove` | `--child-ids`, `--id` |
| `ssot-registry feature create` | `--body`, `--body-file`, `--claim-ids`, `--claim-tier`, `--description`, `--horizon`, `--id`, `--implementation-status`, `--lifecycle-stage`, `--note`, `--origin`, `--out-of-bounds-disposition`, `--parent-feature-ids`, `--replacement-feature-id`, `--requires`, `--slot`, `--spec-ids`, `--target-lifecycle-stage`, `--test-ids`, `--title` |
| `ssot-registry feature delete` | `--id` |
| `ssot-registry feature get` | `--id` |
| `ssot-registry feature lifecycle` | none |
| `ssot-registry feature lifecycle set` | `--effective-release-id`, `--ids`, `--note`, `--replacement-feature-id`, `--stage` |
| `ssot-registry feature link` | `--claim-ids`, `--id`, `--requires`, `--spec-ids`, `--test-ids` |
| `ssot-registry feature list` | `--ids`, `--origin` |
| `ssot-registry feature parent` | none |
| `ssot-registry feature parent add` | `--ids`, `--parent-ids` |
| `ssot-registry feature parent clear` | `--ids` |
| `ssot-registry feature parent remove` | `--ids`, `--parent-ids` |
| `ssot-registry feature parent set` | `--ids`, `--parent-ids` |
| `ssot-registry feature plan` | `--claim-tier`, `--horizon`, `--ids`, `--out-of-bounds-disposition`, `--slot`, `--target-lifecycle-stage` |
| `ssot-registry feature unlink` | `--claim-ids`, `--id`, `--requires`, `--spec-ids`, `--test-ids` |
| `ssot-registry feature update` | `--body`, `--body-file`, `--description`, `--id`, `--implementation-status`, `--origin`, `--title` |
| `ssot-registry graph` | none |
| `ssot-registry graph export` | `--format`, `--output` |
| `ssot-registry init` | `--force`, `--repo-id`, `--repo-name`, `--version` |
| `ssot-registry issue` | none |
| `ssot-registry issue close` | `--id` |
| `ssot-registry issue create` | `--body`, `--body-file`, `--claim-ids`, `--description`, `--evidence-ids`, `--feature-ids`, `--horizon`, `--id`, `--no-release-blocking`, `--release-blocking`, `--risk-ids`, `--severity`, `--slot`, `--status`, `--test-ids`, `--title` |
| `ssot-registry issue delete` | `--id` |
| `ssot-registry issue get` | `--id` |
| `ssot-registry issue link` | `--claim-ids`, `--evidence-ids`, `--feature-ids`, `--id`, `--risk-ids`, `--test-ids` |
| `ssot-registry issue list` | `--ids` |
| `ssot-registry issue plan` | `--horizon`, `--ids`, `--slot` |
| `ssot-registry issue reopen` | `--id` |
| `ssot-registry issue unlink` | `--claim-ids`, `--evidence-ids`, `--feature-ids`, `--id`, `--risk-ids`, `--test-ids` |
| `ssot-registry issue update` | `--body`, `--body-file`, `--description`, `--id`, `--no-release-blocking`, `--release-blocking`, `--severity`, `--title` |
| `ssot-registry leases` | none |
| `ssot-registry leases expire` | none |
| `ssot-registry leases inspect` | `--lease-id` |
| `ssot-registry leases list` | `--status` |
| `ssot-registry maturity` | none |
| `ssot-registry maturity current-tier` | `--feature-id` |
| `ssot-registry maturity next-slice` | `--target-tier` |
| `ssot-registry pack` | none |
| `ssot-registry pack inspect` | `--manifest` |
| `ssot-registry pack preflight` | `--all`, `--kind`, `--manifest`, `--pin`, `--resolved`, `--trusted-only` |
| `ssot-registry pack sync` | `--all`, `--dry-run`, `--kind`, `--manifest`, `--no-sync`, `--pin`, `--preflight-only`, `--prune-stale`, `--reservations`, `--resolved`, `--trust`, `--trusted-only`, `--yes` |
| `ssot-registry profile` | none |
| `ssot-registry profile create` | `--allow-feature-override-tier`, `--body`, `--body-file`, `--claim-tier`, `--description`, `--feature-ids`, `--id`, `--kind`, `--no-allow-feature-override-tier`, `--profile-ids`, `--status`, `--title` |
| `ssot-registry profile delete` | `--id` |
| `ssot-registry profile evaluate` | `--profile-id` |
| `ssot-registry profile get` | `--id` |
| `ssot-registry profile link` | `--feature-ids`, `--id`, `--profile-ids` |
| `ssot-registry profile list` | `--ids` |
| `ssot-registry profile unlink` | `--feature-ids`, `--id`, `--profile-ids` |
| `ssot-registry profile update` | `--body`, `--body-file`, `--claim-tier`, `--description`, `--id`, `--kind`, `--status`, `--title` |
| `ssot-registry profile verify` | `--profile-id` |
| `ssot-registry registry` | none |
| `ssot-registry registry export` | `--format`, `--output` |
| `ssot-registry registry repair-doc-hashes` | `--ids` |
| `ssot-registry registry sync-statuses` | `--dry-run` |
| `ssot-registry release` | none |
| `ssot-registry release add-boundary` | `--boundary-ids`, `--id` |
| `ssot-registry release add-claim` | `--claim-ids`, `--id` |
| `ssot-registry release add-evidence` | `--evidence-ids`, `--id` |
| `ssot-registry release certify` | `--release-id`, `--write-report` |
| `ssot-registry release create` | `--body`, `--body-file`, `--boundary-id`, `--boundary-ids`, `--claim-ids`, `--evidence-ids`, `--id`, `--status`, `--version` |
| `ssot-registry release delete` | `--id` |
| `ssot-registry release get` | `--id` |
| `ssot-registry release list` | `--ids` |
| `ssot-registry release promote` | `--release-id` |
| `ssot-registry release publish` | `--release-id` |
| `ssot-registry release remove-boundary` | `--boundary-ids`, `--id` |
| `ssot-registry release remove-claim` | `--claim-ids`, `--id` |
| `ssot-registry release remove-evidence` | `--evidence-ids`, `--id` |
| `ssot-registry release revoke` | `--reason`, `--release-id` |
| `ssot-registry release update` | `--body`, `--body-file`, `--boundary-id`, `--boundary-ids`, `--id`, `--status`, `--version` |
| `ssot-registry release verify-local` | `--blocking`, `--no-write-artifacts`, `--path-policy`, `--release-id` |
| `ssot-registry repo-watch` | none |
| `ssot-registry repo-watch scan` | `--no-emit-events` |
| `ssot-registry risk` | none |
| `ssot-registry risk accept` | `--id` |
| `ssot-registry risk create` | `--body`, `--body-file`, `--claim-ids`, `--description`, `--evidence-ids`, `--feature-ids`, `--id`, `--issue-ids`, `--no-release-blocking`, `--release-blocking`, `--severity`, `--status`, `--test-ids`, `--title` |
| `ssot-registry risk delete` | `--id` |
| `ssot-registry risk get` | `--id` |
| `ssot-registry risk link` | `--claim-ids`, `--evidence-ids`, `--feature-ids`, `--id`, `--issue-ids`, `--test-ids` |
| `ssot-registry risk list` | `--ids` |
| `ssot-registry risk mitigate` | `--id` |
| `ssot-registry risk retire` | `--id` |
| `ssot-registry risk unlink` | `--claim-ids`, `--evidence-ids`, `--feature-ids`, `--id`, `--issue-ids`, `--test-ids` |
| `ssot-registry risk update` | `--body`, `--body-file`, `--description`, `--id`, `--no-release-blocking`, `--release-blocking`, `--severity`, `--title` |
| `ssot-registry spec` | none |
| `ssot-registry spec create` | `--adr-ids`, `--body`, `--body-file`, `--kind`, `--note`, `--number`, `--origin`, `--reserve-range`, `--slug`, `--status`, `--title` |
| `ssot-registry spec delete` | `--id` |
| `ssot-registry spec get` | `--id` |
| `ssot-registry spec link` | `--adr-ids`, `--id` |
| `ssot-registry spec list` | `--ids` |
| `ssot-registry spec reserve` | none |
| `ssot-registry spec reserve create` | `--end`, `--name`, `--start` |
| `ssot-registry spec reserve list` | none |
| `ssot-registry spec run-tests` | `--dry-run`, `--evidence-output`, `--id` |
| `ssot-registry spec set-status` | `--id`, `--note`, `--status` |
| `ssot-registry spec supersede` | `--id`, `--note`, `--supersedes` |
| `ssot-registry spec sync` | none |
| `ssot-registry spec unlink` | `--adr-ids`, `--id` |
| `ssot-registry spec update` | `--adr-ids`, `--body`, `--body-file`, `--id`, `--kind`, `--note`, `--status`, `--title` |
| `ssot-registry test` | none |
| `ssot-registry test create` | `--body`, `--body-file`, `--claim-ids`, `--evidence-ids`, `--execution-file`, `--execution-json`, `--feature-ids`, `--id`, `--kind`, `--origin`, `--status`, `--test-path`, `--title` |
| `ssot-registry test delete` | `--id` |
| `ssot-registry test get` | `--id` |
| `ssot-registry test link` | `--claim-ids`, `--evidence-ids`, `--feature-ids`, `--id` |
| `ssot-registry test list` | `--ids`, `--origin` |
| `ssot-registry test run` | `--dry-run`, `--evidence-output`, `--id`, `--ids` |
| `ssot-registry test unlink` | `--claim-ids`, `--evidence-ids`, `--feature-ids`, `--id` |
| `ssot-registry test update` | `--body`, `--body-file`, `--execution-file`, `--execution-json`, `--id`, `--kind`, `--origin`, `--status`, `--test-path`, `--title` |
| `ssot-registry upgrade` | `--sync-docs`, `--target-version`, `--write-report` |
| `ssot-registry validate` | `--write-report` |
| `ssot-registry worker` | none |
| `ssot-registry worker abandon` | `--fencing-token`, `--lease-id`, `--reason`, `--worker-id` |
| `ssot-registry worker ack-events` | `--action`, `--event-ids`, `--worker-id` |
| `ssot-registry worker claim-next` | `--campaign-id`, `--os-user`, `--target-tier`, `--ttl-seconds`, `--worker-id` |
| `ssot-registry worker events` | `--after-event-id`, `--campaign-id`, `--limit`, `--worker-id` |
| `ssot-registry worker register` | `--os-user`, `--worker-id` |
| `ssot-registry worker renew` | `--fencing-token`, `--lease-id`, `--ttl-seconds`, `--worker-id` |

### Top-level commands

- `init`
- `validate`
- `upgrade`
- `config`
- `campaign`
- `leases`
- `maturity`
- `repo-watch`
- `worker`
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
- `parent add`, `parent set`, `parent remove`, `parent clear`
- `children add`, `children remove`, `children list`
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
  --out-of-bounds-disposition {prohibited,tolerated}
  --claim-tier {T0,T1,T2,T3,T4}
  --target-lifecycle-stage {active,deprecated,obsolete,removed}
  --slot SLOT
  --claim-ids [CLAIM_IDS ...]
  --test-ids [TEST_IDS ...]
  --requires [REQUIRES ...]
  --parent-feature-ids [PARENT_FEATURE_IDS ...]

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

ssot-registry feature parent add [path]
  --ids IDS [IDS ...] (required)
  --parent-ids PARENT_IDS [PARENT_IDS ...] (required)

ssot-registry feature parent set [path]
  --ids IDS [IDS ...] (required)
  --parent-ids PARENT_IDS [PARENT_IDS ...] (required)

ssot-registry feature parent remove [path]
  --ids IDS [IDS ...] (required)
  --parent-ids PARENT_IDS [PARENT_IDS ...] (required)

ssot-registry feature parent clear [path]
  --ids IDS [IDS ...] (required)

ssot-registry feature children add [path]
  --id ID (required)
  --child-ids CHILD_IDS [CHILD_IDS ...] (required)

ssot-registry feature children remove [path]
  --id ID (required)
  --child-ids CHILD_IDS [CHILD_IDS ...] (required)

ssot-registry feature children list [path]
  --id ID (required)
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
- Depends on: [ssot-core](https://pypi.org/project/ssot-core/), [ssot-conformance](https://pypi.org/project/ssot-conformance/), [ssot-contracts](https://pypi.org/project/ssot-contracts/), [ssot-pack-contracts](https://pypi.org/project/ssot-pack-contracts/)
- Related packages: [ssot-registry](https://pypi.org/project/ssot-registry/), [ssot-tui](https://pypi.org/project/ssot-tui/), [ssot-views](https://pypi.org/project/ssot-views/), [ssot-codegen](https://pypi.org/project/ssot-codegen/)

If you need the command-line interface, this is the package to install.
