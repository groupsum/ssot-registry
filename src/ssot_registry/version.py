from __future__ import annotations

import re
from importlib.metadata import PackageNotFoundError, version as package_version
from pathlib import Path

__all__ = ["__version__"]

_DISTRIBUTION_NAME = "ssot-registry"
_PYPROJECT_PATH = Path(__file__).resolve().parents[2] / "pyproject.toml"
_VERSION_PATTERN = re.compile(r'^version\s*=\s*"(?P<version>[^"]+)"\s*$')


def _read_version_from_pyproject(pyproject_path: Path = _PYPROJECT_PATH) -> str:
    in_project_section = False

    for line in pyproject_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()

        if stripped.startswith("[") and stripped.endswith("]"):
            in_project_section = stripped == "[project]"
            continue

        if not in_project_section:
            continue

        match = _VERSION_PATTERN.match(stripped)
        if match:
            return match.group("version")

    raise RuntimeError(f"Unable to locate [project].version in {pyproject_path}")


def _resolve_version() -> str:
    try:
        return package_version(_DISTRIBUTION_NAME)
    except PackageNotFoundError:
        return _read_version_from_pyproject()


__version__ = _resolve_version()
