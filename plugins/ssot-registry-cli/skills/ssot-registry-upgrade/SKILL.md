---
name: ssot-registry-upgrade
description: Upgrade the local `uv` environment to the latest PyPI `ssot-registry` package, then upgrade `.ssot/registry.json` to the latest schema version using the CLI. Use when the user asks for package+schema upgrade as one dedicated operation.
---

# SSOT Registry Upgrade

Use this skill for one bounded workflow: upgrade the installed PyPI CLI/runtime in a local `uv` venv, then upgrade the repository registry schema with `ssot upgrade`.

## Command surface

- Environment/package upgrade:
  - `uv venv`
  - `uv pip install --upgrade ssot-registry`
- Registry schema upgrade:
  - `uv run ssot upgrade [path] --sync-docs --write-report`
  - Optional pin: `--target-version VERSION`
- Post-upgrade verification:
  - `uv run ssot validate [path] --write-report`

## Workflow

1. Confirm repository root contains `.ssot/registry.json`.
2. Ensure local `uv` venv exists (`uv venv`).
3. Upgrade PyPI package in that local venv (`uv pip install --upgrade ssot-registry`).
4. Verify installed package version from local venv.
5. Run schema upgrade (`uv run ssot upgrade . --sync-docs --write-report`).
6. Validate repository after upgrade (`uv run ssot validate . --write-report`).
7. Report both outcomes separately: package version and resulting `schema_version`.

## Operating rules

- Use local `uv` venv only; do not use global installs.
- Prefer `uv run ssot ...` so command resolution stays local and deterministic.
- Do not hand-edit `.ssot/registry.json`; use CLI upgrade.
- If the user requests a specific target schema, pass `--target-version`.
- If `uv` cache permissions fail on Windows, set `UV_CACHE_DIR` to a repo-local path and retry.

## Example

```powershell
uv venv
uv pip install --upgrade ssot-registry
uv run python -c "import importlib.metadata as m; print(m.version('ssot-registry'))"
uv run ssot upgrade . --sync-docs --write-report
uv run ssot validate . --write-report
uv run python -c "import json, pathlib; print(json.loads(pathlib.Path('.ssot/registry.json').read_text(encoding='utf-8'))['schema_version'])"
```

## Source of truth

- `README.md` upgrade section
- `pkgs/ssot-cli/README.md` (`upgrade`, `validate`)
- `pkgs/ssot-registry/README.md` (`upgrade`)
