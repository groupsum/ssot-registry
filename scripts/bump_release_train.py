#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from bump_pyproject_version import bump_version, read_project_version, write_project_version
from release_metadata import CORE_PACKAGES, PACKAGE_INFOS, expected_dependency_specs, resolve_targets

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python 3.10 fallback
    import tomli as tomllib


def _read_project_dependencies(pyproject_path: Path) -> dict[str, str]:
    payload = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))
    result: dict[str, str] = {}
    for dependency in payload.get("project", {}).get("dependencies", []):
        for package_name in PACKAGE_INFOS:
            if dependency.startswith(f"{package_name}==") or dependency.startswith(f"{package_name}>="):
                result[package_name] = dependency
    return result


def _rewrite_dependency(pyproject_path: Path, dependency_name: str, expected_spec: str) -> bool:
    dependencies = _read_project_dependencies(pyproject_path)
    current_spec = dependencies.get(dependency_name)
    if current_spec is None or current_spec == expected_spec:
        return False
    content = pyproject_path.read_text(encoding="utf-8")
    updated = content.replace(f'"{current_spec}"', f'"{expected_spec}"', 1)
    if updated == content:
        raise RuntimeError(f"Failed to update {dependency_name} dependency in {pyproject_path}")
    pyproject_path.write_text(updated, encoding="utf-8")
    return True


def sync_release_dependencies() -> list[Path]:
    updated_files: list[Path] = []
    core_version = read_project_version(Path(PACKAGE_INFOS["ssot-contracts"].project_path) / "pyproject.toml")
    cli_version = read_project_version(Path(PACKAGE_INFOS["ssot-cli"].project_path) / "pyproject.toml")
    for package_name, expectations in expected_dependency_specs(core_version, cli_version=cli_version).items():
        pyproject_path = Path(PACKAGE_INFOS[package_name].project_path) / "pyproject.toml"
        changed = False
        for dependency_name, expected_spec in expectations.items():
            changed = _rewrite_dependency(pyproject_path, dependency_name, expected_spec) or changed
        if changed:
            updated_files.append(pyproject_path)
    return updated_files


def bump_train(train: str, bump_type: str, selected_packages: str | None) -> list[Path]:
    targets = resolve_targets(train, selected_packages)
    updated_files: list[Path] = []
    if train in {"core", "all"}:
        source_package = targets[0]
        current_version = read_project_version(Path(PACKAGE_INFOS[source_package].project_path) / "pyproject.toml")
        new_version = bump_version(current_version, bump_type)
        for package_name in CORE_PACKAGES:
            pyproject_path = Path(PACKAGE_INFOS[package_name].project_path) / "pyproject.toml"
            package_current = read_project_version(pyproject_path)
            write_project_version(pyproject_path, package_current, new_version)
            updated_files.append(pyproject_path)
        registry_pyproject = Path(PACKAGE_INFOS["ssot-registry"].project_path) / "pyproject.toml"
        registry_current = read_project_version(registry_pyproject)
        write_project_version(registry_pyproject, registry_current, new_version)
        updated_files.append(registry_pyproject)
        if train == "all":
            for package_name in targets:
                if package_name in (*CORE_PACKAGES, "ssot-registry"):
                    continue
                pyproject_path = Path(PACKAGE_INFOS[package_name].project_path) / "pyproject.toml"
                current_version = read_project_version(pyproject_path)
                next_version = bump_version(current_version, bump_type)
                write_project_version(pyproject_path, current_version, next_version)
                updated_files.append(pyproject_path)
        for path in sync_release_dependencies():
            if path not in updated_files:
                updated_files.append(path)
        return updated_files

    for package_name in targets:
        pyproject_path = Path(PACKAGE_INFOS[package_name].project_path) / "pyproject.toml"
        current_version = read_project_version(pyproject_path)
        new_version = bump_version(current_version, bump_type)
        write_project_version(pyproject_path, current_version, new_version)
        updated_files.append(pyproject_path)
    for path in sync_release_dependencies():
        if path not in updated_files:
            updated_files.append(path)
    return updated_files


def main() -> int:
    parser = argparse.ArgumentParser(description="Bump versions for a release train.")
    parser.add_argument(
        "--train",
        required=True,
        choices=["core", "all", "ssot-contracts", "ssot-views", "ssot-codegen", "ssot-core", "ssot-registry", "ssot-cli", "ssot-tui", "selected"],
    )
    parser.add_argument("--bump", required=True, choices=["major", "minor", "patch", "finalize"])
    parser.add_argument("--packages", help="Comma-separated package list when --train=selected")
    args = parser.parse_args()

    updated = bump_train(args.train, args.bump, args.packages)
    for path in updated:
        print(path.as_posix())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
