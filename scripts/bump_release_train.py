#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

try:
    from packaging.version import Version
except ModuleNotFoundError:  # pragma: no cover
    try:
        from setuptools._vendor.packaging.version import Version
    except ModuleNotFoundError:  # pragma: no cover
        from pip._vendor.packaging.version import Version

from bump_pyproject_version import bump_version, read_project_version, write_project_version
from release_metadata import CORE_PACKAGES, NPM_PACKAGE_INFOS, PACKAGE_INFOS, expected_dependency_specs, resolve_npm_targets, resolve_targets

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python 3.10 fallback
    import tomli as tomllib


def _read_project_dependencies(pyproject_path: Path) -> dict[str, str]:
    payload = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))
    result: dict[str, str] = {}
    dependencies = list(payload.get("project", {}).get("dependencies", []))
    optional_dependencies = payload.get("project", {}).get("optional-dependencies", {})
    for values in optional_dependencies.values():
        dependencies.extend(values)
    for dependency in dependencies:
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
    updated = content.replace(f'"{current_spec}"', f'"{expected_spec}"')
    if updated == content:
        raise RuntimeError(f"Failed to update {dependency_name} dependency in {pyproject_path}")
    pyproject_path.write_text(updated, encoding="utf-8")
    return True


def _next_version(current_version: str, bump_type: str) -> str:
    if bump_type != "finalize":
        return bump_version(current_version, bump_type)
    if ".dev" not in current_version:
        return current_version
    return bump_version(current_version, bump_type)


def _write_version_if_changed(pyproject_path: Path, current_version: str, new_version: str) -> bool:
    if current_version == new_version:
        return False
    write_project_version(pyproject_path, current_version, new_version)
    return True


def _python_to_npm_version(version: str) -> str:
    return version.replace(".dev", "-dev.")


def _read_npm_version(package_json_path: Path) -> str:
    return json.loads(package_json_path.read_text(encoding="utf-8"))["version"]


def _write_npm_version(package_json_path: Path, current_version: str, new_version: str) -> bool:
    if current_version == new_version:
        return False
    content = package_json_path.read_text(encoding="utf-8")
    updated = content.replace(f'"version": "{current_version}"', f'"version": "{new_version}"')
    if updated == content:
        raise RuntimeError(f"Failed to update npm version in {package_json_path}")
    package_json_path.write_text(updated, encoding="utf-8")
    return True


def _write_npm_lock_version(package_lock_path: Path, new_version: str) -> bool:
    if not package_lock_path.exists():
        return False
    payload = json.loads(package_lock_path.read_text(encoding="utf-8"))
    changed = False
    if payload.get("version") != new_version:
        payload["version"] = new_version
        changed = True
    root_package = payload.get("packages", {}).get("")
    if isinstance(root_package, dict) and root_package.get("version") != new_version:
        root_package["version"] = new_version
        changed = True
    if changed:
        package_lock_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return changed


def _write_lineage_graph_manifest_version(new_version: str) -> Path | None:
    manifest_path = Path("pkgs/ssot-core/src/ssot_registry/assets/lineage_graph/manifest.json")
    if not manifest_path.exists():
        return None
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    if payload.get("version") == new_version:
        return None
    payload["version"] = new_version
    manifest_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return manifest_path


def _sync_npm_release_files(package_name: str, new_version: str) -> list[Path]:
    package_path = Path(NPM_PACKAGE_INFOS[package_name].project_path)
    updated_files: list[Path] = []
    package_lock = package_path / "package-lock.json"
    if _write_npm_lock_version(package_lock, new_version):
        updated_files.append(package_lock)
    if package_name == "ssot-lineage-graph":
        manifest_path = _write_lineage_graph_manifest_version(new_version)
        if manifest_path is not None:
            updated_files.append(manifest_path)
    return updated_files


def _append_unique(paths: list[Path], path: Path) -> None:
    if path not in paths:
        paths.append(path)


def sync_release_dependencies() -> list[Path]:
    updated_files: list[Path] = []
    core_version = read_project_version(Path(PACKAGE_INFOS["ssot-contracts"].project_path) / "pyproject.toml")
    pack_contracts_version = read_project_version(Path(PACKAGE_INFOS["ssot-pack-contracts"].project_path) / "pyproject.toml")
    cli_version = read_project_version(Path(PACKAGE_INFOS["ssot-cli"].project_path) / "pyproject.toml")
    mcp_version = read_project_version(Path(PACKAGE_INFOS["ssot-mcp"].project_path) / "pyproject.toml")
    tui_version = read_project_version(Path(PACKAGE_INFOS["ssot-tui"].project_path) / "pyproject.toml")
    for package_name, expectations in expected_dependency_specs(
        core_version,
        cli_version=cli_version,
        mcp_version=mcp_version,
        pack_contracts_version=pack_contracts_version,
        tui_version=tui_version,
    ).items():
        pyproject_path = Path(PACKAGE_INFOS[package_name].project_path) / "pyproject.toml"
        changed = False
        for dependency_name, expected_spec in expectations.items():
            changed = _rewrite_dependency(pyproject_path, dependency_name, expected_spec) or changed
        if changed:
            updated_files.append(pyproject_path)
    return updated_files


def bump_train(train: str, bump_type: str, selected_packages: str | None) -> list[Path]:
    targets = resolve_targets(train, selected_packages)
    npm_targets = resolve_npm_targets(train, selected_packages)
    updated_files: list[Path] = []
    if train in {"core", "all"}:
        source_package = targets[0]
        current_version = read_project_version(Path(PACKAGE_INFOS[source_package].project_path) / "pyproject.toml")
        new_version = _next_version(current_version, bump_type)
        for package_name in CORE_PACKAGES:
            pyproject_path = Path(PACKAGE_INFOS[package_name].project_path) / "pyproject.toml"
            package_current = read_project_version(pyproject_path)
            if _write_version_if_changed(pyproject_path, package_current, new_version):
                updated_files.append(pyproject_path)
        registry_pyproject = Path(PACKAGE_INFOS["ssot-registry"].project_path) / "pyproject.toml"
        registry_current = read_project_version(registry_pyproject)
        if _write_version_if_changed(registry_pyproject, registry_current, new_version):
            updated_files.append(registry_pyproject)
        if train == "all":
            for package_name in targets:
                if package_name in (*CORE_PACKAGES, "ssot-pack-contracts", "ssot-registry"):
                    continue
                pyproject_path = Path(PACKAGE_INFOS[package_name].project_path) / "pyproject.toml"
                current_version = read_project_version(pyproject_path)
                next_version = _next_version(current_version, bump_type)
                if _write_version_if_changed(pyproject_path, current_version, next_version):
                    updated_files.append(pyproject_path)
        for path in sync_release_dependencies():
            if path not in updated_files:
                updated_files.append(path)
        if npm_targets:
            npm_version = _python_to_npm_version(new_version)
            for package_name in npm_targets:
                package_json = Path(NPM_PACKAGE_INFOS[package_name].project_path) / "package.json"
                current = _read_npm_version(package_json)
                if _write_npm_version(package_json, current, npm_version):
                    _append_unique(updated_files, package_json)
                for path in _sync_npm_release_files(package_name, npm_version):
                    _append_unique(updated_files, path)
        return updated_files

    if not targets and npm_targets:
        for package_name in npm_targets:
            package_json = Path(NPM_PACKAGE_INFOS[package_name].project_path) / "package.json"
            current = _read_npm_version(package_json)
            new_version = _next_version(current.replace("-dev.", ".dev"), bump_type)
            npm_version = _python_to_npm_version(new_version)
            if _write_npm_version(package_json, current, npm_version):
                _append_unique(updated_files, package_json)
            for path in _sync_npm_release_files(package_name, npm_version):
                _append_unique(updated_files, path)
        return updated_files

    for package_name in targets:
        pyproject_path = Path(PACKAGE_INFOS[package_name].project_path) / "pyproject.toml"
        current_version = read_project_version(pyproject_path)
        new_version = _next_version(current_version, bump_type)
        if package_name == "ssot-pack-contracts":
            registry_version = read_project_version(Path(PACKAGE_INFOS["ssot-registry"].project_path) / "pyproject.toml")
            if Version(new_version).release > Version(registry_version).release:
                raise ValueError(
                    "ssot-pack-contracts must trail ssot-registry: "
                    f"next pack-contracts {new_version!r}, registry {registry_version!r}"
                )
        if _write_version_if_changed(pyproject_path, current_version, new_version):
            updated_files.append(pyproject_path)
    for path in sync_release_dependencies():
        if path not in updated_files:
            updated_files.append(path)
    for package_name in npm_targets:
        package_json = Path(NPM_PACKAGE_INFOS[package_name].project_path) / "package.json"
        current = _read_npm_version(package_json)
        new_version = _next_version(current.replace("-dev.", ".dev"), bump_type)
        npm_version = _python_to_npm_version(new_version)
        if _write_npm_version(package_json, current, npm_version):
            _append_unique(updated_files, package_json)
        for path in _sync_npm_release_files(package_name, npm_version):
            _append_unique(updated_files, path)
    return updated_files


def main() -> int:
    parser = argparse.ArgumentParser(description="Bump versions for a release train.")
    parser.add_argument(
        "--train",
        required=True,
        choices=[
            "core",
            "all",
            "ssot-contracts",
            "ssot-pack-contracts",
            "ssot-views",
            "ssot-codegen",
            "ssot-core",
            "ssot-conformance",
            "ssot-registry",
            "ssot-cli",
            "ssot-mcp",
            "ssot-tui",
            "ssot-lineage-graph",
            "selected",
        ],
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
