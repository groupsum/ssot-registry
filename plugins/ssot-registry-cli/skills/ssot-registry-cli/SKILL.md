---
name: ssot-registry-cli
description: Use the local ssot CLI surface to inspect, validate, and mutate SSOT registries in this workspace.
---

# SSOT Registry CLI

Use this skill when the user wants to operate on an SSOT repository through the `ssot` command surface instead of editing `.ssot/registry.json` by hand.

This plugin is centered on the CLI that ships from `pkgs/ssot-cli` and is re-exported by `ssot-registry`.

## What this skill covers

- Repository initialization with `init`
- Schema and consistency checks with `validate` and `upgrade`
- CRUD-style document and entity operations for `adr`, `spec`, `feature`, `profile`, `test`, `issue`, `claim`, `evidence`, `risk`, `boundary`, and `release`
- Export flows for `graph export` and `registry export`

## Command selection

- Prefer `ssot ...` in new commands and automation.
- Accept `ssot-registry ...` as a compatibility alias when the user explicitly names it.
- Treat `ssot-cli` as equivalent for help and parser inspection.

## Local workspace invocation

In this repository, the command surface lives in `pkgs/ssot-cli`, while the `python -m ssot_registry` module path is a compatibility shim that forwards into `ssot_cli`.

Use one of these approaches:

1. If the executable is already installed in the environment, run:

```powershell
ssot --help
```

2. If the executable is not installed, prefer the same module-style entrypoint the integration tests use by supplying the workspace source roots on `PYTHONPATH` and running:

```powershell
$env:PYTHONPATH='E:\swarmauri_github\ssot-registry\pkgs\ssot-core\src;E:\swarmauri_github\ssot-registry\pkgs\ssot-codegen\src;E:\swarmauri_github\ssot-registry\pkgs\ssot-views\src;E:\swarmauri_github\ssot-registry\pkgs\ssot-contracts\src;E:\swarmauri_github\ssot-registry\pkgs\ssot-cli\src;E:\swarmauri_github\ssot-registry\pkgs\ssot-tui\src'
python -m ssot_registry validate .
```

If you only need the CLI parser behavior, this fallback is sufficient and matches `tests/helpers.py`.

## Operating rules

- Run commands from the repository root unless the user is targeting a different SSOT repo path.
- Prefer read-only inspection commands before mutation commands when the current state is unclear.
- Keep outputs structured. The CLI defaults to JSON; use `--output-format` only when the user asks for another rendering.
- When mutating entities, prefer the CLI over manual edits so IDs, links, lifecycle fields, and derived artifacts stay normalized.
- For release and boundary flows, inspect the current boundary or release first before adding or removing linked records.

## Common flows

### Initialize a repository

```powershell
ssot init . --repo-id repo:demo.app --repo-name "Demo App" --version 0.1.0
```

### Validate and write a report

```powershell
ssot validate . --write-report
```

### Inspect a specific entity

```powershell
ssot feature get . --id feat:demo.login
ssot claim get . --id clm:demo.login.t1
ssot profile get . --id prf:demo.core
```

### Export machine-readable artifacts

```powershell
ssot graph export . --format json --output .ssot/graphs/registry.graph.json
ssot registry export . --format yaml --output .ssot/exports/registry.yaml
```

### Freeze and certify a release

```powershell
ssot boundary freeze . --boundary-id bnd:demo.v0
ssot release certify . --release-id rel:0.1.0 --write-report
```

## Source of truth for command surface

- Primary CLI docs: `pkgs/ssot-cli/README.md`
- Repo-level CLI overview: `README.md`
- Compatibility shim: `pkgs/ssot-registry/src/ssot_registry/cli/main.py`
- Test harness for local execution: `tests/helpers.py`

When help text and README examples disagree, trust the parser and current source over older prose.
