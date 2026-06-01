---
name: ssot-cli
description: Use the latest available `ssot-registry` CLI, either from a current global install or from a repo-local `uv` environment with a repo-local cache, to inspect, validate, and mutate SSOT registries. Use when Codex should operate through the CLI instead of editing `.ssot/registry.json` by hand.
---

# SSOT Registry CLI

Use this skill when the user wants to operate on an SSOT repository through the `ssot-registry` CLI and its aliases instead of editing `.ssot/registry.json` by hand.

This plugin is centered on the CLI exposed by the PyPI-published `ssot-registry` distribution. The preferred execution path is the latest available CLI. Use a verified current global `ssot`/`ssot-registry` executable when present; otherwise create or refresh a repo-local `uv` environment with repo-local cache settings before invoking `uv run ssot ...`.

## Command discipline

- Do not spend turns rediscovering syntax with `--help` during normal SSOT work. Use the command surface and examples in this skill directly.
- Pick one verified CLI rail for the repo (`ssot`, `ssot-registry`, `ssot-cli`, or `uv run ssot`) and reuse it consistently by substituting that rail into the examples below.
- Only inspect parser or help text when the user explicitly asks about the CLI surface or when observed runtime behavior contradicts the command patterns documented here.
## What this skill covers

- Repository initialization with `init`
- Schema and consistency checks with `validate` and `upgrade`
- CRUD-style document and entity operations for `adr`, `spec`, `feature`, `profile`, `test`, `issue`, `claim`, `evidence`, `risk`, `boundary`, and `release`
- Automated status convergence with `registry sync-statuses`
- Export flows for `graph export` and `registry export`
- SSOT MCP worker-campaign routing for pull-lease maturation work targeting `T1`, `T2`, or `T3`

## Skill routing table

Use these focused skills by default:

- Package/schema upgrade:
  - Upgrade PyPI package + registry schema: `$ssot-registry-upgrade`
- Phase-focused lifecycle work:
  - Decision through initial target rows: `$ssot-decision-to-scope`
  - Scoped pre-freeze ADR/SPEC/feature/test flow: `$ssot-decision-to-scope` then `$ssot-feature-test-linking`
  - Target setting through frozen boundary: `$ssot-scope-to-frozen-boundary`
  - Post-freeze runtime implementation and required-test delivery: `$ssot-implementation-and-migration-delivery`
  - Proof closure and release gates after implementation plus required tests exist: `$ssot-proof-chain-and-certification`
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
- SSOT MCP worker campaigns:
  - T1 direct verification slices: `$ssot-mcp-t1-worker-campaign`
  - T2 robustness verification slices: `$ssot-mcp-t2-worker-campaign`
  - T3 certification-closure slices: `$ssot-mcp-t3-worker-campaign`
- Multi-phase lifecycle orchestration: `$ssot-e2e-change-orchestrator` or `$ssot-e2e-portable-lifecycle`

## Command selection

- Prefer the latest verified CLI available on the machine. A current global `ssot ...` or `ssot-registry ...` rail is acceptable.
- If the global rail is missing, stale, or unverified, use repo-local `uv run ssot ...` with repo-local cache settings.
- Accept `ssot-registry ...` as a compatibility alias.
- Treat `ssot-cli` as equivalent to `ssot` for command execution.

## Preferred command rails

First check whether a global CLI is already available and current enough for the requested operation:

```powershell
Get-Command ssot
```

Use Python package metadata to verify the installed `ssot-registry` version. The CLI does not expose a root `ssot --version` or `ssot-registry --version` command, so do not use version flags as a rail check. If the global executable fails with launcher, canonicalization, or parser-bootstrap errors, treat it as unavailable and use the repo-local `uv` rail.

When a global CLI is unavailable or stale, create or refresh a local virtual environment with repo-local cache settings, then install the PyPI package into it:

```powershell
$env:UV_CACHE_DIR='.tmp\uv-cache'
$env:UV_LINK_MODE='copy'
uv venv
uv pip install --upgrade ssot-registry
uv run python -c "import importlib.metadata as m; print(m.version('ssot-registry'))"
```

This keeps execution inside the repository workspace while still exercising the published package from PyPI. Always set `UV_CACHE_DIR` before the first `uv` command on Windows when the user cache or launcher path has shown access errors.

If `uv run` reaches `.venv\Scripts\python.exe` and fails with `Access is denied`, stop retrying `uv` and use the local development fallback below or the workspace fallback rail from `$ssot-registry-upgrade`.

Available CLI names inside that environment:

- `ssot`
- `ssot-cli`
- `ssot-registry`

Prefer the already-verified rail consistently within a workflow. Do not switch between global and local CLI versions during a mutation sequence unless the first rail fails before touching repo state.

## Local development fallback

If the local `uv` venv is unavailable and you only need a source-tree fallback while developing this repository, use the same module-style entrypoint the integration tests use by supplying the workspace source roots on `PYTHONPATH` and running from the repository root:

```powershell
$env:PYTHONPATH='pkgs/ssot-core/src;pkgs/ssot-codegen/src;pkgs/ssot-views/src;pkgs/ssot-contracts/src;pkgs/ssot-cli/src;pkgs/ssot-tui/src'
python -m ssot_registry validate .
```

On Windows PowerShell, build that value with `[IO.Path]::PathSeparator` if needed rather than hard-coding machine-local absolute paths.

If you only need the source-tree execution path, this fallback is sufficient and matches `tests/helpers.py`. This fallback is for maintainers debugging the source tree, not the default integration path.

## Operating rules

- Run commands from the repository root unless the user is targeting a different SSOT repo path.
- Do not recommend `pipx` or a bare global `pip install` for this skill.
- A preexisting or user-requested global `ssot`/`ssot-registry` install is acceptable after verifying the installed package version through Python package metadata.
- Prefer repo-local `UV_CACHE_DIR` and `UV_LINK_MODE=copy` for any `uv` command before diagnosing registry logic.
- Prefer read-only inspection commands before mutation commands when the current state is unclear.
- Keep outputs structured. The CLI defaults to JSON; use `--output-format` only when the user asks for another rendering.
- When mutating entities, prefer the CLI over manual edits so IDs, links, lifecycle fields, and derived artifacts stay normalized.
- For release and boundary flows, inspect the current boundary or release first before adding or removing linked records.
- Treat `boundary freeze` as a scope checkpoint, not as an implementation-complete signal. In normal workflows, runtime implementation, migration work, required functional tests, and requested/required performance or conformance tests still happen after freeze and before verification or certification.
- For pre-freeze scoping work that includes ADRs, SPECs, features, and tests, chain `$ssot-decision-to-scope` into `$ssot-feature-test-linking` and stop before `$ssot-scope-to-frozen-boundary`.

## Common flows

### Create the local CLI environment

```powershell
$env:UV_CACHE_DIR='.tmp\uv-cache'
$env:UV_LINK_MODE='copy'
uv venv
uv pip install --upgrade ssot-registry
uv run python -c "import importlib.metadata as m; print(m.version('ssot-registry'))"
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

### Freeze, implement, and then certify a release

```powershell
uv run ssot boundary freeze . --boundary-id bnd:demo.v0
# implement runtime code and required tests; run verification and collect evidence here
uv run ssot release certify . --release-id rel:0.1.0 --write-report
```

## Source of truth for command surface

- Published package docs: `pkgs/ssot-registry/README.md`
- Primary CLI docs: `pkgs/ssot-cli/README.md`
- Repo-level CLI overview: `README.md`
- Compatibility shim: `pkgs/ssot-registry/src/ssot_registry/cli/main.py`
- Test harness for local execution: `tests/helpers.py`

When README examples disagree with current source, trust the current source and the command patterns documented in these skills over older prose.
