#!/usr/bin/env python3
"""Bump or finalize project version in pyproject.toml.

Supported bump types:
- major -> X+1.0.0.dev1
- minor -> X.Y+1.0.dev1
- patch -> if stable: X.Y.Z+1.dev1, if dev: X.Y.Z.devN+1
- finalize -> X.Y.Z (from X.Y.Z.devN only)
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python 3.10 fallback
    import tomli as tomllib

_VERSION_RE = re.compile(r"^(?P<major>0|[1-9]\d*)\.(?P<minor>0|[1-9]\d*)\.(?P<patch>0|[1-9]\d*)(?:\.dev(?P<dev>0|[1-9]\d*))?$")
_PYPROJECT_VERSION_LINE_RE = re.compile(r'^(?P<prefix>version\s*=\s*")(?P<version>[^"]+)(?P<suffix>"\s*)$', re.MULTILINE)


def parse_version(value: str) -> tuple[int, int, int, int | None]:
    match = _VERSION_RE.match(value.strip())
    if not match:
        raise ValueError(f"Unsupported version format: {value!r}")
    major = int(match.group("major"))
    minor = int(match.group("minor"))
    patch = int(match.group("patch"))
    dev_group = match.group("dev")
    dev = int(dev_group) if dev_group is not None else None
    return major, minor, patch, dev


def bump_version(current_version: str, bump_type: str) -> str:
    major, minor, patch, dev = parse_version(current_version)
    is_dev = dev is not None

    if bump_type == "finalize":
        if not is_dev:
            raise ValueError("Cannot finalize a non-dev version.")
        return f"{major}.{minor}.{patch}"

    if bump_type == "major":
        return f"{major + 1}.0.0.dev1"

    if bump_type == "minor":
        return f"{major}.{minor + 1}.0.dev1"

    if bump_type == "patch":
        if is_dev:
            return f"{major}.{minor}.{patch}.dev{dev + 1}"
        return f"{major}.{minor}.{patch + 1}.dev1"

    raise ValueError("bump_type must be one of: major, minor, patch, finalize")


def read_project_version(pyproject_path: Path) -> str:
    data = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))
    try:
        return data["project"]["version"]
    except KeyError as exc:
        raise KeyError("Missing [project].version in pyproject.toml") from exc


def write_project_version(pyproject_path: Path, current_version: str, new_version: str) -> None:
    content = pyproject_path.read_text(encoding="utf-8")

    def _replace(match: re.Match[str]) -> str:
        found = match.group("version")
        if found != current_version:
            return match.group(0)
        return f'{match.group("prefix")}{new_version}{match.group("suffix")}'

    updated, count = _PYPROJECT_VERSION_LINE_RE.subn(_replace, content, count=1)
    if count == 0 or updated == content:
        raise RuntimeError("Failed to update version line in pyproject.toml")
    pyproject_path.write_text(updated, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Bump a pyproject.toml version.")
    parser.add_argument("file", type=Path, help="Path to pyproject.toml")
    parser.add_argument("--bump", choices=["major", "minor", "patch", "finalize"], required=True)
    args = parser.parse_args()

    pyproject_path: Path = args.file
    current_version = read_project_version(pyproject_path)
    new_version = bump_version(current_version, args.bump)
    write_project_version(pyproject_path, current_version, new_version)

    print(f"Bumped version from {current_version} to {new_version} in {pyproject_path}.")


if __name__ == "__main__":
    main()
