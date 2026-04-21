#!/usr/bin/env bash
set -euo pipefail

# Runs the same unittest matrix as CI for every supported Python minor.

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if ! command -v uv >/dev/null 2>&1; then
  echo "error: uv is required but was not found on PATH." >&2
  exit 1
fi

SUPPORTED_PYTHON_VERSIONS=("3.10" "3.11" "3.12" "3.13")

mapfile -t RESOLVED_PYTHON_VERSIONS < <(
  python - <<'PY'
import pathlib
import re

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib

pyproject = pathlib.Path("pyproject.toml")
data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
constraint = data["tool"]["ssot"]["release"]["supported-python"]
match = re.fullmatch(r">=3\.(\d+),<3\.(\d+)", constraint)
if not match:
    raise SystemExit(
        f"Unsupported supported-python format: {constraint!r}. "
        "Expected format like '>=3.10,<3.14'."
    )
start_minor = int(match.group(1))
end_minor_exclusive = int(match.group(2))
for minor in range(start_minor, end_minor_exclusive):
    print(f"3.{minor}")
PY
)

if [[ "${RESOLVED_PYTHON_VERSIONS[*]}" != "${SUPPORTED_PYTHON_VERSIONS[*]}" ]]; then
  echo "error: supported versions mismatch." >&2
  echo "  expected: ${SUPPORTED_PYTHON_VERSIONS[*]}" >&2
  echo "  resolved: ${RESOLVED_PYTHON_VERSIONS[*]}" >&2
  exit 1
fi

PACKAGES=(
  "ssot-contracts"
  "ssot-views"
  "ssot-codegen"
  "ssot-core"
  "ssot-registry"
  "ssot-cli"
  "ssot-tui"
)

package_test_command() {
  case "$1" in
    ssot-contracts)
      echo "python -m unittest tests.unit.test_contracts_views_codegen tests.unit.test_release_metadata tests.unit.test_release_workflows tests.unit.test_pyproject_metadata -v"
      ;;
    ssot-views)
      echo "python -m unittest tests.unit.test_contracts_views_codegen tests.unit.test_release_metadata tests.unit.test_release_workflows tests.unit.test_pyproject_metadata -v"
      ;;
    ssot-codegen)
      echo "python -m unittest tests.unit.test_contracts_views_codegen tests.unit.test_release_metadata tests.unit.test_release_workflows tests.unit.test_pyproject_metadata -v"
      ;;
    ssot-core)
      echo "python -m unittest discover -s tests -v"
      ;;
    ssot-registry)
      echo "python -m unittest discover -s tests -v"
      ;;
    ssot-cli)
      echo "python -m unittest tests.integration.test_cli_init tests.integration.test_cli_global_flags tests.integration.test_cli_upgrade tests.unit.test_cli_package_layout tests.unit.test_release_workflows tests.unit.test_pyproject_metadata -v"
      ;;
    ssot-tui)
      echo "python -m unittest tests.unit.test_cli_package_layout tests.unit.test_release_workflows tests.unit.test_pyproject_metadata -v"
      ;;
    *)
      echo "error: unknown package '$1'" >&2
      exit 1
      ;;
  esac
}

echo "Running unittest matrix for Python versions: ${SUPPORTED_PYTHON_VERSIONS[*]}"
echo

for py_version in "${SUPPORTED_PYTHON_VERSIONS[@]}"; do
  echo "============================================================"
  echo "Python ${py_version}"
  echo "============================================================"

  uv python install "${py_version}"

  for package in "${PACKAGES[@]}"; do
    test_cmd="$(package_test_command "${package}")"

    echo
    echo "--- ${package} on Python ${py_version} ---"
    echo "> uv sync --python ${py_version} --package ${package}"
    uv sync --python "${py_version}" --package "${package}"

    if [[ "${package}" == "ssot-contracts" ]]; then
      echo "> uv run --python ${py_version} --package ${package} --no-sync python scripts/sync_packaged_docs.py --check"
      uv run --python "${py_version}" --package "${package}" --no-sync python scripts/sync_packaged_docs.py --check
    fi

    echo "> uv run --python ${py_version} --package ${package} --no-sync ${test_cmd}"
    uv run --python "${py_version}" --package "${package}" --no-sync ${test_cmd}
  done

  echo
  echo "Completed Python ${py_version}."
  echo

done

echo "All package unittests passed for Python 3.10, 3.11, 3.12, and 3.13."
