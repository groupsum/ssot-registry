---
name: ssot-cli
description: Use a `uv`-managed virtual environment with the PyPI-published `ssot-registry` package to run the SSOT CLI and its aliases for inspecting, validating, and mutating SSOT registries. Use when Codex should operate through `uv run ssot ...` from a local venv instead of editing `.ssot/registry.json` by hand or relying on a global tool install.
---

# SSOT Registry CLI

Use this skill when the user wants to operate on an SSOT repository through a local `uv` virtual environment and CLI aliases instead of editing `.ssot/registry.json` by hand.

This plugin is centered on the CLI exposed by the PyPI-published `ssot-registry` distribution. The preferred execution path is a local `.venv` managed by `uv`, with `ssot-registry` installed into that environment and invoked with `uv run ssot ...`.

## What this skill covers

- Repository initialization with `init`
- Schema and consistency checks with `validate` and `upgrade`
- CRUD-style document and entity operations for `adr`, `spec`, `feature`, `profile`, `test`, `issue`, `claim`, `evidence`, `risk`, `boundary`, and `release`
- Automated status convergence with `registry sync-statuses`
- Export flows for `graph export` and `registry export`

## Skill routing table

Use these focused skills by default:

- Package/schema upgrade:
  - Upgrade PyPI package + registry schema: `$ssot-registry-upgrade`
- Entity-focused operations:
  - ADR: `$ssot-adr`
  - SPEC: `$ssot-spec`
  - Feature: `$ssot-feature`
  - Profile: `$ssot-profile`
  - Test: `$ssot-test`
  - Issue: `$ssot-issue`
  - Claim: `$ssot-claim`
  - Evidence: `$ssot-evidence`
  - Risk: `$ssot-risk`
  - Boundary: `$ssot-boundary`
  - Release: `$ssot-release`
- Cross-entity read wrappers: `$ssot-entity-get`, `$ssot-entity-list`, `$ssot-entity-review`, `$ssot-entity-analyze`
- Multi-phase lifecycle orchestration: `$ssot-e2e-change-orchestrator` or `$ssot-e2e-portable-lifecycle`

## Command selection

- Prefer `uv run ssot ...` in new commands and automation.
- Accept `ssot-registry ...` as a compatibility alias when the user explicitly names it.
- Treat `ssot-cli` as equivalent for help and parser inspection.
- Prefer a local `uv` venv over any globally installed copy, even when running inside this repository.

## Preferred local environment

Create or refresh a local virtual environment, then install the PyPI package into it:

```powershell
uv venv
uv pip install ssot-registry
uv run ssot --help
```

This keeps execution inside a local `uv`-managed venv while still exercising the published package from PyPI.

Available CLI names inside that environment:

- `ssot`
- `ssot-cli`
- `ssot-registry`

Prefer `uv run ssot ...` in new commands unless the user explicitly wants the compatibility alias.

## Local development fallback

If the local `uv` venv is unavailable and you only need a source-tree fallback while developing this repository, use the same module-style entrypoint the integration tests use by supplying the workspace source roots on `PYTHONPATH` and running from the repository root:

```powershell
$env:PYTHONPATH='pkgs/ssot-core/src;pkgs/ssot-codegen/src;pkgs/ssot-views/src;pkgs/ssot-contracts/src;pkgs/ssot-cli/src;pkgs/ssot-tui/src'
python -m ssot_registry validate .
```

On Windows PowerShell, build that value with `[IO.Path]::PathSeparator` if needed rather than hard-coding machine-local absolute paths.

If you only need the CLI parser behavior, this fallback is sufficient and matches `tests/helpers.py`. This fallback is for maintainers debugging the source tree, not the default integration path.

## Operating rules

- Run commands from the repository root unless the user is targeting a different SSOT repo path.
- Never recommend `uv tool install`, `pipx`, or a bare global `pip install` for this skill.
- Prefer `uv run ssot ...` over bare `ssot ...` so the command resolves through the local venv rather than a machine-global install.
- Prefer read-only inspection commands before mutation commands when the current state is unclear.
- Keep outputs structured. The CLI defaults to JSON; use `--output-format` only when the user asks for another rendering.
- When mutating entities, prefer the CLI over manual edits so IDs, links, lifecycle fields, and derived artifacts stay normalized.
- For release and boundary flows, inspect the current boundary or release first before adding or removing linked records.

## Common flows

### Create the local CLI environment

```powershell
uv venv
uv pip install ssot-registry
uv run ssot --help
```

### Initialize a repository

```powershell
uv run ssot init . --repo-id repo:demo.app --repo-name "Demo App" --version 0.1.0
```

### Validate and write a report

```powershell
uv run ssot validate . --write-report
```

### Inspect a specific entity

```powershell
uv run ssot feature get . --id feat:demo.login
uv run ssot claim get . --id clm:demo.login.t1
uv run ssot profile get . --id prf:demo.core
```

### Export machine-readable artifacts

```powershell
uv run ssot graph export . --format json --output .ssot/graphs/registry.graph.json
uv run ssot registry export . --format yaml --output .ssot/exports/registry.yaml
```

### Sync derived statuses

```powershell
uv run ssot registry sync-statuses . --dry-run
uv run ssot registry sync-statuses .
uv run ssot validate . --write-report
```

### Freeze and certify a release

```powershell
uv run ssot boundary freeze . --boundary-id bnd:demo.v0
uv run ssot release certify . --release-id rel:0.1.0 --write-report
```

## Source of truth for command surface

- Published package docs: `pkgs/ssot-registry/README.md`
- Primary CLI docs: `pkgs/ssot-cli/README.md`
- Repo-level CLI overview: `README.md`
- Compatibility shim: `pkgs/ssot-registry/src/ssot_registry/cli/main.py`
- Test harness for local execution: `tests/helpers.py`

When help text and README examples disagree, trust the parser and current source over older prose.
