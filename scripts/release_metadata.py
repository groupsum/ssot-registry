#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CORE_PACKAGES = ("ssot-contracts", "ssot-views", "ssot-codegen", "ssot-registry")
RELEASE_ORDER = (
    "ssot-contracts",
    "ssot-views",
    "ssot-codegen",
    "ssot-registry",
    "ssot-cli",
    "ssot-tui",
)


@dataclass(frozen=True)
class PackageInfo:
    name: str
    project_path: str
    workflow: str
    pypi_url: str


PACKAGE_INFOS: dict[str, PackageInfo] = {
    "ssot-contracts": PackageInfo(
        name="ssot-contracts",
        project_path="pkgs/ssot-contracts",
        workflow="publish-ssot-contracts.yml",
        pypi_url="https://pypi.org/p/ssot-contracts",
    ),
    "ssot-views": PackageInfo(
        name="ssot-views",
        project_path="pkgs/ssot-views",
        workflow="publish-ssot-views.yml",
        pypi_url="https://pypi.org/p/ssot-views",
    ),
    "ssot-codegen": PackageInfo(
        name="ssot-codegen",
        project_path="pkgs/ssot-codegen",
        workflow="publish-ssot-codegen.yml",
        pypi_url="https://pypi.org/p/ssot-codegen",
    ),
    "ssot-registry": PackageInfo(
        name="ssot-registry",
        project_path="pkgs/ssot-registry",
        workflow="publish-ssot-registry.yml",
        pypi_url="https://pypi.org/p/ssot-registry",
    ),
    "ssot-cli": PackageInfo(
        name="ssot-cli",
        project_path="pkgs/ssot-cli",
        workflow="publish-ssot-cli.yml",
        pypi_url="https://pypi.org/p/ssot-cli",
    ),
    "ssot-tui": PackageInfo(
        name="ssot-tui",
        project_path="pkgs/ssot-tui",
        workflow="publish-ssot-tui.yml",
        pypi_url="https://pypi.org/p/ssot-tui",
    ),
}


def _load_pyproject(package_name: str) -> dict:
    package = PACKAGE_INFOS[package_name]
    path = PROJECT_ROOT / package.project_path / "pyproject.toml"
    return tomllib.loads(path.read_text(encoding="utf-8"))


def _package_dependencies(pyproject: dict) -> dict[str, str]:
    result: dict[str, str] = {}
    for dependency in pyproject.get("project", {}).get("dependencies", []):
        for package_name in PACKAGE_INFOS:
            if dependency.startswith(f"{package_name}==") or dependency.startswith(f"{package_name}>="):
                result[package_name] = dependency
    return result


def _next_minor_upper_bound(version: str) -> str:
    match = re.match(r"^(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)", version)
    if match is None:
        raise ValueError(f"Unsupported version format: {version}")
    major = int(match.group("major"))
    minor = int(match.group("minor"))
    return f"{major}.{minor + 1}.0"


def collect_metadata() -> dict[str, object]:
    packages: dict[str, dict[str, object]] = {}
    for package_name, info in PACKAGE_INFOS.items():
        pyproject = _load_pyproject(package_name)
        version = pyproject["project"]["version"]
        packages[package_name] = {
            "name": package_name,
            "project_path": info.project_path,
            "workflow": info.workflow,
            "pypi_url": info.pypi_url,
            "version": version,
            "tag": f"{package_name}=={version}",
            "dependencies": _package_dependencies(pyproject),
            "group": "core" if package_name in CORE_PACKAGES else "surface",
        }
    return {
        "release_order": list(RELEASE_ORDER),
        "core_packages": list(CORE_PACKAGES),
        "packages": packages,
    }


def resolve_targets(train: str, selected_packages: str | None) -> list[str]:
    if train == "core":
        return list(CORE_PACKAGES)
    if train == "ssot-cli":
        return ["ssot-cli"]
    if train == "ssot-tui":
        return ["ssot-tui"]
    if train != "selected":
        raise ValueError(f"Unsupported release train: {train}")
    if not selected_packages:
        raise ValueError("selected release train requires --packages")
    targets = [part.strip() for part in selected_packages.split(",") if part.strip()]
    if not targets:
        raise ValueError("selected release train requires at least one package")
    unknown = [target for target in targets if target not in PACKAGE_INFOS]
    if unknown:
        raise ValueError(f"Unknown package(s): {', '.join(unknown)}")
    seen: set[str] = set()
    deduped: list[str] = []
    for target in targets:
        if target in seen:
            continue
        seen.add(target)
        deduped.append(target)
    return deduped


def validate_train(train: str, selected_packages: str | None) -> dict[str, object]:
    metadata = collect_metadata()
    packages = metadata["packages"]  # type: ignore[assignment]
    assert isinstance(packages, dict)
    targets = resolve_targets(train, selected_packages)
    order_positions = {name: index for index, name in enumerate(RELEASE_ORDER)}

    ordered_targets = sorted(targets, key=order_positions.__getitem__)
    if ordered_targets != targets:
        raise ValueError("Selected packages must follow canonical release order.")

    core_versions = {packages[name]["version"] for name in CORE_PACKAGES}  # type: ignore[index]
    if len(core_versions) != 1:
        raise ValueError("Core packages are not in lockstep version alignment.")
    core_version = next(iter(core_versions))

    expected_core_dependencies = {
        "ssot-views": {"ssot-contracts": f"ssot-contracts=={core_version}"},
        "ssot-codegen": {
            "ssot-contracts": f"ssot-contracts=={core_version}",
            "ssot-views": f"ssot-views=={core_version}",
        },
        "ssot-registry": {
            "ssot-contracts": f"ssot-contracts=={core_version}",
            "ssot-views": f"ssot-views=={core_version}",
        },
    }
    for package_name, expectations in expected_core_dependencies.items():
        actual_dependencies = packages[package_name]["dependencies"]  # type: ignore[index]
        assert isinstance(actual_dependencies, dict)
        for dependency_name, expected_value in expectations.items():
            actual_value = actual_dependencies.get(dependency_name)
            if actual_value != expected_value:
                raise ValueError(
                    f"{package_name} dependency mismatch for {dependency_name}: expected {expected_value!r}, got {actual_value!r}"
                )

    expected_surface_dependency = f">={core_version},<{_next_minor_upper_bound(core_version)}"
    for package_name in ("ssot-cli", "ssot-tui"):
        actual_dependencies = packages[package_name]["dependencies"]  # type: ignore[index]
        assert isinstance(actual_dependencies, dict)
        for dependency_name in ("ssot-contracts", "ssot-registry"):
            actual_value = actual_dependencies.get(dependency_name, "")
            if expected_surface_dependency not in actual_value:
                raise ValueError(
                    f"{package_name} must depend on a compatible {dependency_name} range containing {expected_surface_dependency!r}."
                )

    for package_name in targets:
        dependencies = packages[package_name]["dependencies"]  # type: ignore[index]
        assert isinstance(dependencies, dict)
        for dependency_name in dependencies:
            if dependency_name in targets and order_positions[dependency_name] > order_positions[package_name]:
                raise ValueError(
                    f"{package_name} depends on {dependency_name}, but selected targets are not ordered correctly."
                )

    return {
        "targets": targets,
        "core_version": core_version,
    }


def _json_dump(payload: object) -> None:
    print(json.dumps(payload, indent=2, sort_keys=True))


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspect and validate multi-package release metadata.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    show_parser = subparsers.add_parser("show", help="Show package metadata as JSON.")
    show_parser.add_argument("--train", choices=["core", "ssot-cli", "ssot-tui", "selected"])
    show_parser.add_argument("--packages", help="Comma-separated package list for selected train.")

    version_parser = subparsers.add_parser("version", help="Print the version for a package.")
    version_parser.add_argument("--package", required=True, choices=sorted(PACKAGE_INFOS))

    tag_parser = subparsers.add_parser("tag", help="Print the release tag for a package.")
    tag_parser.add_argument("--package", required=True, choices=sorted(PACKAGE_INFOS))

    targets_parser = subparsers.add_parser("targets", help="Print release targets for a train.")
    targets_parser.add_argument("--train", required=True, choices=["core", "ssot-cli", "ssot-tui", "selected"])
    targets_parser.add_argument("--packages", help="Comma-separated package list for selected train.")

    validate_parser = subparsers.add_parser("validate-train", help="Validate release policy for a train.")
    validate_parser.add_argument("--train", required=True, choices=["core", "ssot-cli", "ssot-tui", "selected"])
    validate_parser.add_argument("--packages", help="Comma-separated package list for selected train.")

    args = parser.parse_args()

    if args.command == "show":
        payload = collect_metadata()
        if args.train:
            payload["selected_targets"] = resolve_targets(args.train, getattr(args, "packages", None))
        _json_dump(payload)
        return 0

    if args.command == "version":
        payload = collect_metadata()
        print(payload["packages"][args.package]["version"])  # type: ignore[index]
        return 0

    if args.command == "tag":
        payload = collect_metadata()
        print(payload["packages"][args.package]["tag"])  # type: ignore[index]
        return 0

    if args.command == "targets":
        _json_dump(resolve_targets(args.train, args.packages))
        return 0

    if args.command == "validate-train":
        _json_dump(validate_train(args.train, args.packages))
        return 0

    raise AssertionError("unreachable")


if __name__ == "__main__":
    sys.exit(main())
