---
name: ssot-cli
description: Use the published ssot-registry package and its CLI aliases to inspect, validate, and mutate SSOT registries.
---

# SSOT Registry CLI

Use this skill when the user wants to operate on an SSOT repository through the published `ssot-registry` package and its CLI aliases instead of editing `.ssot/registry.json` by hand.

This plugin is centered on the CLI exposed by the PyPI-published `ssot-registry` distribution. That bundle installs the canonical runtime plus the CLI aliases `ssot`, `ssot-cli`, and `ssot-registry`.

## What this skill covers

- Repository initialization with `init`
- Schema and consistency checks with `validate` and `upgrade`
- CRUD-style document and entity operations for `adr`, `spec`, `feature`, `profile`, `test`, `issue`, `claim`, `evidence`, `risk`, `boundary`, and `release`
- Export flows for `graph export` and `registry export`

## Command selection

- Prefer `ssot ...` in new commands and automation.
- Accept `ssot-registry ...` as a compatibility alias when the user explicitly names it.
- Treat `ssot-cli` as equivalent for help and parser inspection.
- Assume the user may have installed `ssot-registry` from PyPI rather than checked out this repository.

## Preferred installation path

Use the published package first:

```powershell
uv tool install ssot-registry
ssot --help
```

The published package installs:

- `ssot`
- `ssot-cli`
- `ssot-registry`

Prefer `ssot` in new commands unless the user explicitly wants the compatibility alias.

If the user wants a project-local environment instead of a global tool install, use:

```powershell
uv add ssot-registry
uv run ssot --help
```

## Local development fallback

If the user is working inside the `groupsum/ssot-registry` source tree and the package is not installed, use the same module-style entrypoint the integration tests use by supplying the workspace source roots on `PYTHONPATH` and running from the repository root:

```powershell
$env:PYTHONPATH='pkgs/ssot-core/src;pkgs/ssot-codegen/src;pkgs/ssot-views/src;pkgs/ssot-contracts/src;pkgs/ssot-cli/src;pkgs/ssot-tui/src'
python -m ssot_registry validate .
```

On Windows PowerShell, build that value with `[IO.Path]::PathSeparator` if needed rather than hard-coding machine-local absolute paths.

If you only need the CLI parser behavior, this fallback is sufficient and matches `tests/helpers.py`. This fallback is for maintainers of the source repo, not the default integration path.

## Operating rules

- Run commands from the repository root unless the user is targeting a different SSOT repo path.
- Prefer the installed package behavior over source-tree internals when the goal is to reflect what PyPI users experience.
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

- Published package docs: `pkgs/ssot-registry/README.md`
- Primary CLI docs: `pkgs/ssot-cli/README.md`
- Repo-level CLI overview: `README.md`
- Compatibility shim: `pkgs/ssot-registry/src/ssot_registry/cli/main.py`
- Test harness for local execution: `tests/helpers.py`

When help text and README examples disagree, trust the parser and current source over older prose.
