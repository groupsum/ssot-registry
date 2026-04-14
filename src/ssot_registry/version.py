from __future__ import annotations

import re
from pathlib import Path

__all__ = ["__version__"]

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


__version__ = _read_version_from_pyproject()
