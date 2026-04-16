#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from bump_pyproject_version import bump_version, read_project_version, write_project_version
from release_metadata import PACKAGE_INFOS, resolve_targets


def bump_train(train: str, bump_type: str, selected_packages: str | None) -> list[Path]:
    targets = resolve_targets(train, selected_packages)
    if train == "core":
        source_package = targets[0]
        current_version = read_project_version(Path(PACKAGE_INFOS[source_package].project_path) / "pyproject.toml")
        new_version = bump_version(current_version, bump_type)
        updated_files: list[Path] = []
        for package_name in targets:
            pyproject_path = Path(PACKAGE_INFOS[package_name].project_path) / "pyproject.toml"
            package_current = read_project_version(pyproject_path)
            write_project_version(pyproject_path, package_current, new_version)
            updated_files.append(pyproject_path)
        return updated_files

    updated_files = []
    for package_name in targets:
        pyproject_path = Path(PACKAGE_INFOS[package_name].project_path) / "pyproject.toml"
        current_version = read_project_version(pyproject_path)
        new_version = bump_version(current_version, bump_type)
        write_project_version(pyproject_path, current_version, new_version)
        updated_files.append(pyproject_path)
    return updated_files


def main() -> int:
    parser = argparse.ArgumentParser(description="Bump versions for a release train.")
    parser.add_argument("--train", required=True, choices=["core", "ssot-cli", "ssot-tui", "selected"])
    parser.add_argument("--bump", required=True, choices=["major", "minor", "patch", "finalize"])
    parser.add_argument("--packages", help="Comma-separated package list when --train=selected")
    args = parser.parse_args()

    updated = bump_train(args.train, args.bump, args.packages)
    for path in updated:
        print(path.as_posix())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
