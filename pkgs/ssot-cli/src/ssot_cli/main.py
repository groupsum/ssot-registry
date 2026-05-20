from __future__ import annotations

import argparse
import re
import sys
from importlib.metadata import (
    PackageNotFoundError,
    distributions as package_distributions,
    version as package_version,
)
from pathlib import Path
from typing import Any

from ssot_contracts.generated.python.cli_metadata import OUTPUT_FORMATS
from ssot_registry.util.errors import GuardError, RegistryError, ValidationError
from ssot_registry.util.formatting import render_payload

from .adr_cmd import register_adr
from .boundary_cmd import register_boundary
from .campaign_cmd import register_campaign
from .claim_cmd import register_claim
from .conformance_cmd import register_conformance
from .config_cmd import register_config
from .evidence_cmd import register_evidence
from .feature_cmd import register_feature
from .graph_cmd import register_graph
from .init_cmd import register_init
from .issue_cmd import register_issue
from .leases_cmd import register_leases
from .maturity_cmd import register_maturity
from .pack_cmd import register_pack
from .profile_cmd import register_profile
from .registry_cmd import register_registry
from .release_cmd import register_release
from .repo_watch_cmd import register_repo_watch
from .risk_cmd import register_risk
from .spec_cmd import register_spec
from .test_cmd import register_test
from .upgrade_cmd import register_upgrade
from .validate_cmd import register_validate
from .worker_cmd import register_worker

_PACKAGE_NAME = "ssot-cli"
_PYPROJECT_PATH = Path(__file__).resolve().parents[2] / "pyproject.toml"
_PACKAGES_ROOT = _PYPROJECT_PATH.parent.parent
_VERSION_PATTERN = re.compile(r'^version\s*=\s*"(?P<version>[^"]+)"\s*$')
_NAME_PATTERN = re.compile(r'^name\s*=\s*"(?P<name>[^"]+)"\s*$')


def _default_prog() -> str:
    executable = Path(sys.argv[0]).name
    for suffix in (".exe", ".py"):
        if executable.endswith(suffix):
            executable = executable[: -len(suffix)]
            break
    if executable in {"", "__main__", "-m"}:
        return "ssot-registry"
    return executable


def _read_project_field_from_pyproject(field_pattern: re.Pattern[str], pyproject_path: Path) -> str:
    in_project_section = False

    for line in pyproject_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()

        if stripped.startswith("[") and stripped.endswith("]"):
            in_project_section = stripped == "[project]"
            continue

        if not in_project_section:
            continue

        match = field_pattern.match(stripped)
        if match is not None:
            return next(value for value in match.groupdict().values() if value is not None)

    raise RuntimeError(f"Unable to locate requested [project] field in {pyproject_path}")


def _read_version_from_pyproject(pyproject_path: Path = _PYPROJECT_PATH) -> str:
    return _read_project_field_from_pyproject(_VERSION_PATTERN, pyproject_path)


def _cli_version() -> str:
    if _PYPROJECT_PATH.exists():
        return _read_version_from_pyproject()
    try:
        return package_version(_PACKAGE_NAME)
    except PackageNotFoundError:
        return _read_version_from_pyproject()


def _normalize_distribution_name(name: str) -> str:
    return name.strip().lower().replace("_", "-")


def _installed_ssot_package_versions() -> list[tuple[str, str]]:
    packages: dict[str, str] = {}
    for distribution in package_distributions():
        name = distribution.metadata.get("Name")
        if not name:
            continue
        normalized_name = _normalize_distribution_name(name)
        if normalized_name.startswith("ssot-"):
            packages[normalized_name] = distribution.version
    return sorted(packages.items())


def _source_tree_ssot_package_versions() -> list[tuple[str, str]]:
    if not _PACKAGES_ROOT.exists():
        return []

    packages: dict[str, str] = {}
    for pyproject_path in _PACKAGES_ROOT.glob("ssot-*/pyproject.toml"):
        name = _read_project_field_from_pyproject(_NAME_PATTERN, pyproject_path)
        normalized_name = _normalize_distribution_name(name)
        if normalized_name.startswith("ssot-"):
            packages[normalized_name] = _read_version_from_pyproject(pyproject_path)
    return sorted(packages.items())


def _ssot_package_versions() -> list[tuple[str, str]]:
    packages = dict(_installed_ssot_package_versions())
    packages.update(_source_tree_ssot_package_versions())
    if _PACKAGE_NAME not in packages:
        packages[_PACKAGE_NAME] = _cli_version()
    return sorted(packages.items())


def _version_report(prog: str) -> str:
    lines = [f"{prog} package versions:"]
    lines.extend(f"{name} {version}" for name, version in _ssot_package_versions())
    return "\n".join(lines)


class _VersionReportAction(argparse.Action):
    def __init__(
        self,
        option_strings: list[str],
        dest: str = argparse.SUPPRESS,
        **kwargs: Any,
    ) -> None:
        super().__init__(option_strings=option_strings, dest=dest, nargs=0, **kwargs)

    def __call__(
        self,
        parser: argparse.ArgumentParser,
        namespace: argparse.Namespace,
        values: str | None,
        option_string: str | None = None,
    ) -> None:
        parser._print_message(_version_report(parser.prog) + "\n", sys.stdout)
        parser.exit()


def build_parser(*, prog: str | None = None) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog=prog or _default_prog(),
        allow_abbrev=False,
        description=(
            "Operate an SSOT registry that tracks architecture documents, scoped delivery boundaries, "
            "implementation features, verification artifacts, and publication-ready releases."
        ),
    )
    parser.add_argument(
        "--version",
        action=_VersionReportAction,
        help="Print installed SSOT package versions and exit.",
    )
    parser.add_argument(
        "--output-format",
        default="json",
        choices=OUTPUT_FORMATS,
        help="Render command results as this format for operators or downstream tooling.",
    )
    parser.add_argument(
        "--output-file",
        default=None,
        help="Write the rendered command output to this file instead of only printing to stdout.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    register_init(subparsers)
    register_validate(subparsers)
    register_upgrade(subparsers)
    register_config(subparsers)
    register_campaign(subparsers)
    register_leases(subparsers)
    register_maturity(subparsers)
    register_repo_watch(subparsers)
    register_worker(subparsers)
    register_adr(subparsers)
    register_spec(subparsers)
    register_feature(subparsers)
    register_profile(subparsers)
    register_test(subparsers)
    register_issue(subparsers)
    register_pack(subparsers)
    register_claim(subparsers)
    register_conformance(subparsers)
    register_evidence(subparsers)
    register_risk(subparsers)
    register_boundary(subparsers)
    register_release(subparsers)
    register_graph(subparsers)
    register_registry(subparsers)
    return parser


def _print(payload: Any, output_format: str) -> None:
    print(render_payload(payload, output_format), end="")


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        payload = args.func(args)
    except (RegistryError, ValidationError, GuardError, ValueError, FileNotFoundError) as exc:
        _print({"passed": False, "error": str(exc)}, args.output_format)
        return 1

    rendered = render_payload(payload, args.output_format)
    if args.output_file is not None:
        path = Path(args.output_file)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    if isinstance(payload, dict):
        return 0 if payload.get("passed", True) else 1
    return 0
