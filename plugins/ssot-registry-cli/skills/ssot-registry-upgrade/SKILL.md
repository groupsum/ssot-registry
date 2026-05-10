---
name: ssot-registry-upgrade
description: Upgrade a repository to the latest PyPI `ssot-registry`, run the CLI schema migration, validate the migrated SSOT registry, and repair migration blockers such as Windows uv failures, non-canonical JSON, stale document metadata, and out-of-bounds disposition errors.
---

# SSOT Registry Upgrade

Use this skill for one bounded workflow: run the latest available `ssot-registry` CLI, upgrade `.ssot/registry.json`, validate with the same CLI rail, and repair validation blockers until the registry passes or a concrete blocker remains.

## Command Surface

Preferred global rail when already installed and current:

```powershell
Get-Command ssot
ssot validate --help
ssot upgrade . --sync-docs --write-report
ssot validate . --write-report
```

Use Python package metadata to verify the installed `ssot-registry` version. The CLI does not expose a root `ssot --version` or `ssot-registry --version` command, so do not use version flags as a rail check. If the global executable fails with launcher, canonicalization, or parser-bootstrap errors, treat it as unavailable and use the repo-local `uv` rail.

Preferred repo-local `uv` rail when the global CLI is unavailable, stale, or unverified:

```powershell
$env:UV_CACHE_DIR='.tmp\uv-cache'
$env:UV_LINK_MODE='copy'
uv venv
uv pip install --upgrade ssot-registry
uv run python -c "import importlib.metadata as m; print(m.version('ssot-registry'))"
uv run ssot upgrade . --sync-docs --write-report
uv run ssot validate . --write-report
```

Workspace fallback rail when `uv run`, `.venv\Scripts\python.exe`, or launcher shims are blocked:

```powershell
python -m pip install --upgrade --target .tmp\ssot-pypi-site ssot-registry
$env:PYTHONPATH='.tmp\ssot-pypi-site'
python -c "import importlib.metadata as m; print(m.version('ssot-registry'))"
python -m ssot_registry upgrade . --sync-docs --write-report
python -m ssot_registry validate . --write-report
```

Use absolute paths in `PYTHONPATH` only when required by the host shell; do not copy workstation-specific paths into shared docs or skills.

## Workflow

1. Confirm the repository root contains `.ssot/registry.json`.
2. Record current `schema_version`, `tooling.ssot_registry_version`, and package pin/lock state.
3. Verify the latest available CLI rail. Use a current global CLI if present; otherwise install the latest PyPI `ssot-registry` into the workspace with repo-local `uv` cache settings.
4. Verify the package version from the same execution rail that will run `upgrade`.
5. Run `ssot upgrade . --sync-docs --write-report`.
6. If upgrade fails, fix the concrete validation blockers and rerun upgrade.
7. Run `ssot validate . --write-report` with the same installed CLI.
8. Report package version, resulting registry `schema_version`, report paths, and any residual warnings separately.

## Corrective Actions

### Windows `uv` or venv failures

Set a repo-local cache before the first `uv` command on Windows, especially when prior runs showed cache or launcher access errors:

```powershell
$env:UV_CACHE_DIR='.tmp\uv-cache'
$env:UV_LINK_MODE='copy'
uv pip install --upgrade ssot-registry
```

If `uv` or `.venv\Scripts\python.exe` fails with `Access is denied`, use the workspace fallback rail. Do not keep retrying the same blocked interpreter.

### RFC 8785 JCS JSON failures

Newer SSOT versions may require every JSON file under `.ssot` to be canonical JSON: sorted keys, compact separators, no trailing newline, no non-finite numbers.

Repair mechanically and rerun upgrade:

```powershell
python - <<'PY'
import json
from pathlib import Path
for path in sorted(Path('.ssot').rglob('*.json')):
    data = json.loads(path.read_text(encoding='utf-8'))
    path.write_text(json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False), encoding='utf-8')
PY
```

In PowerShell, use a here-string piped into `python -` instead of Bash heredoc syntax.

### Out-of-bounds disposition failures

If validation reports `plan.out_of_bounds_disposition is not set`, inspect every feature with:

- `plan.horizon == "out_of_bounds"`
- `implementation_status in {"partial", "implemented"}`

Set one of:

- `tolerated`: non-targeted, non-certified implementation is accepted.
- `prohibited`: implementation leakage must be removed or quarantined.

A tolerated out-of-bounds feature needs a non-empty `lifecycle.note`. A prohibited out-of-bounds feature must target lifecycle `removed` and needs release-blocking issue/risk linkage while implementation remains non-absent.

### Document sync and hash failures

If ADR/SPEC document content changes, prefer the CLI sync path. If validation prevents sync from running, reconcile the document fields and registry row metadata together, then rerun `upgrade --sync-docs`.

Common checks:

- document `schema_version` is semver-style.
- SPEC document `adr_ids` matches the registry row.
- registry `content_sha256` matches the document content.
- packaged `ssot-origin`/`ssot-core` docs keep managed/immutable invariants.

## Operating Rules

- Run commands from the repository root unless the user targets another path.
- Use the same installed package rail for `upgrade` and `validate`.
- Prefer the CLI upgrade over hand-editing schema fields.
- Keep `.tmp` installs out of committed artifacts unless the repository explicitly tracks them.
- Do not claim success until validation passes after migration.
- If dependency locks cannot be refreshed because the interpreter is blocked, report that separately from registry migration success.

## Expected Output

Report these facts:

- PyPI package version installed.
- Starting and ending `schema_version`.
- Upgrade report path, usually `.ssot/reports/upgrade.report.json`.
- Validation report path, usually `.ssot/reports/validation.report.json`.
- Whether validation passed.
- Any warnings or blocked dependency metadata updates.
