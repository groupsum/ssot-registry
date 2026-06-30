from __future__ import annotations

import json
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

from tests.helpers import PROJECT_ROOT, workspace_tempdir

sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

import bump_release_train
from release_metadata import NpmPackageInfo, PackageInfo


def _write_pyproject(path: Path, name: str, version: str, dependencies: list[str]) -> None:
    deps_block = ""
    if dependencies:
        deps_lines = ",\n".join(f'  "{dependency}"' for dependency in dependencies)
        deps_block = f"dependencies = [\n{deps_lines},\n]\n"
    path.write_text(
        "\n".join(
            [
                "[project]",
                f'name = "{name}"',
                f'version = "{version}"',
                deps_block.rstrip(),
                "",
            ]
        ),
        encoding="utf-8",
    )


def _write_npm_fixture(root: Path, version: str) -> dict[str, NpmPackageInfo]:
    package_path = root / "packages" / "ssot-lineage-graph"
    package_path.mkdir(parents=True, exist_ok=True)
    (package_path / "package.json").write_text(
        json.dumps(
            {
                "name": "@ssot-registry/lineage-graph",
                "version": version,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (package_path / "package-lock.json").write_text(
        json.dumps(
            {
                "name": "@ssot-registry/lineage-graph",
                "version": version,
                "lockfileVersion": 3,
                "packages": {"": {"name": "@ssot-registry/lineage-graph", "version": version}},
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    manifest_path = root / "pkgs" / "ssot-core" / "src" / "ssot_registry" / "assets" / "lineage_graph"
    manifest_path.mkdir(parents=True, exist_ok=True)
    (manifest_path / "manifest.json").write_text(
        json.dumps(
            {
                "package": "@ssot-registry/lineage-graph",
                "version": version,
                "js": "ssot-lineage-graph.js",
                "css": "ssot-lineage-graph.css",
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return {
        "ssot-lineage-graph": NpmPackageInfo(
            name="ssot-lineage-graph",
            package_name="@ssot-registry/lineage-graph",
            project_path=str(package_path),
            npm_url="https://example.test/@ssot-registry/lineage-graph",
        )
    }


class BumpReleaseTrainTests(unittest.TestCase):
    def test_all_train_finalize_skips_already_final_versions(self) -> None:
        with workspace_tempdir() as temp_dir:
            root = Path(temp_dir)
            packages = {
                "ssot-contracts": ("0.2.3", []),
                "ssot-pack-contracts": ("0.2.3", []),
                "ssot-views": ("0.2.3", ["ssot-contracts==0.2.3"]),
                "ssot-codegen": ("0.2.3", ["ssot-contracts==0.2.3", "ssot-views==0.2.3"]),
                "ssot-core": ("0.2.3", ["ssot-contracts==0.2.3", "ssot-pack-contracts>=0.2.3,<0.3.0", "ssot-views==0.2.3"]),
                "ssot-conformance": ("0.2.3", ["ssot-contracts==0.2.3", "ssot-core==0.2.3"]),
                "ssot-registry": (
                    "0.2.3",
                    [
                        "ssot-contracts==0.2.3",
                        "ssot-pack-contracts>=0.2.3,<0.3.0",
                        "ssot-core==0.2.3",
                        "ssot-cli>=0.1.0,<0.2.0",
                        "ssot-mcp>=0.1.0,<0.2.0",
                        "ssot-tui>=0.1.0,<0.2.0",
                    ],
                ),
                "ssot-cli": ("0.1.0", ["ssot-contracts>=0.2.3,<0.3.0"]),
                "ssot-mcp": ("0.1.0", ["ssot-core>=0.2.3,<0.3.0"]),
                "ssot-tui": (
                    "0.1.0",
                    [
                        "ssot-contracts>=0.2.3,<0.3.0",
                        "ssot-core>=0.2.3,<0.3.0",
                    ],
                ),
            }
            package_infos: dict[str, PackageInfo] = {}
            for package_name, (version, dependencies) in packages.items():
                project_path = root / package_name
                project_path.mkdir(parents=True, exist_ok=True)
                _write_pyproject(project_path / "pyproject.toml", package_name, version, dependencies)
                package_infos[package_name] = PackageInfo(
                    name=package_name,
                    project_path=str(project_path),
                    workflow=f"publish-{package_name}.yml",
                    pypi_url=f"https://example.test/{package_name}",
                )
            npm_package_infos = _write_npm_fixture(root, "0.2.3")

            original_cwd = Path.cwd()
            try:
                os.chdir(root)
                with (
                    patch.object(bump_release_train, "PACKAGE_INFOS", package_infos),
                    patch.object(bump_release_train, "NPM_PACKAGE_INFOS", npm_package_infos),
                ):
                    changed = bump_release_train.bump_train("all", "finalize", None)
            finally:
                os.chdir(original_cwd)

            self.assertEqual(changed, [])
            self.assertIn('version = "0.2.3"', (root / "ssot-contracts" / "pyproject.toml").read_text(encoding="utf-8"))
            self.assertIn('version = "0.1.0"', (root / "ssot-cli" / "pyproject.toml").read_text(encoding="utf-8"))

    def test_all_train_bump_updates_dependency_specs(self) -> None:
        with workspace_tempdir() as temp_dir:
            root = Path(temp_dir)
            packages = {
                "ssot-contracts": ("0.2.3", []),
                "ssot-pack-contracts": ("0.2.3", []),
                "ssot-views": ("0.2.3", ["ssot-contracts==0.2.3"]),
                "ssot-codegen": ("0.2.3", ["ssot-contracts==0.2.3", "ssot-views==0.2.3"]),
                "ssot-core": ("0.2.3", ["ssot-contracts==0.2.3", "ssot-pack-contracts>=0.2.3,<0.3.0", "ssot-views==0.2.3"]),
                "ssot-conformance": ("0.2.3", ["ssot-contracts==0.2.3", "ssot-core==0.2.3"]),
                "ssot-registry": (
                    "0.2.3",
                    [
                        "ssot-contracts==0.2.3",
                        "ssot-pack-contracts>=0.2.3,<0.3.0",
                        "ssot-core==0.2.3",
                        "ssot-cli>=0.1.0,<0.2.0",
                        "ssot-mcp>=0.1.0,<0.2.0",
                        "ssot-tui>=0.1.0,<0.2.0",
                    ],
                ),
                "ssot-cli": (
                    "0.1.0",
                    [
                        "ssot-contracts>=0.2.3,<0.3.0",
                        "ssot-pack-contracts>=0.2.3,<0.3.0",
                        "ssot-core>=0.2.3,<0.3.0",
                        "ssot-conformance>=0.2.3,<0.3.0",
                    ],
                ),
                "ssot-mcp": ("0.1.0", ["ssot-core>=0.2.3,<0.3.0"]),
                "ssot-tui": ("0.1.0", ["ssot-contracts>=0.2.3,<0.3.0", "ssot-core>=0.2.3,<0.3.0"]),
            }
            package_infos: dict[str, PackageInfo] = {}
            for package_name, (version, dependencies) in packages.items():
                project_path = root / package_name
                project_path.mkdir(parents=True, exist_ok=True)
                _write_pyproject(project_path / "pyproject.toml", package_name, version, dependencies)
                package_infos[package_name] = PackageInfo(
                    name=package_name,
                    project_path=str(project_path),
                    workflow=f"publish-{package_name}.yml",
                    pypi_url=f"https://example.test/{package_name}",
                )
            npm_package_infos = _write_npm_fixture(root, "0.2.3")

            original_cwd = Path.cwd()
            try:
                os.chdir(root)
                with (
                    patch.object(bump_release_train, "PACKAGE_INFOS", package_infos),
                    patch.object(bump_release_train, "NPM_PACKAGE_INFOS", npm_package_infos),
                ):
                    changed = bump_release_train.bump_train("all", "patch", None)
            finally:
                os.chdir(original_cwd)

            changed_paths = {path.as_posix() for path in changed}
            self.assertEqual(len(changed_paths), 12)

            pack_contracts_text = (root / "ssot-pack-contracts" / "pyproject.toml").read_text(encoding="utf-8")
            views_text = (root / "ssot-views" / "pyproject.toml").read_text(encoding="utf-8")
            codegen_text = (root / "ssot-codegen" / "pyproject.toml").read_text(encoding="utf-8")
            core_text = (root / "ssot-core" / "pyproject.toml").read_text(encoding="utf-8")
            conformance_text = (root / "ssot-conformance" / "pyproject.toml").read_text(encoding="utf-8")
            registry_text = (root / "ssot-registry" / "pyproject.toml").read_text(encoding="utf-8")
            cli_text = (root / "ssot-cli" / "pyproject.toml").read_text(encoding="utf-8")
            mcp_text = (root / "ssot-mcp" / "pyproject.toml").read_text(encoding="utf-8")
            tui_text = (root / "ssot-tui" / "pyproject.toml").read_text(encoding="utf-8")

            self.assertIn('version = "0.2.4.dev1"', (root / "ssot-contracts" / "pyproject.toml").read_text(encoding="utf-8"))
            self.assertIn('version = "0.2.3"', pack_contracts_text)
            self.assertIn('version = "0.2.4.dev1"', views_text)
            self.assertIn('ssot-contracts==0.2.4.dev1', views_text)
            self.assertIn('ssot-contracts==0.2.4.dev1', codegen_text)
            self.assertIn('ssot-views==0.2.4.dev1', codegen_text)
            self.assertIn('version = "0.2.4.dev1"', core_text)
            self.assertIn('ssot-contracts==0.2.4.dev1', core_text)
            self.assertIn('ssot-pack-contracts>=0.2.3,<0.3.0', core_text)
            self.assertIn('ssot-views==0.2.4.dev1', core_text)
            self.assertIn('version = "0.2.4.dev1"', conformance_text)
            self.assertIn('ssot-contracts==0.2.4.dev1', conformance_text)
            self.assertIn('ssot-core==0.2.4.dev1', conformance_text)
            self.assertIn('ssot-contracts==0.2.4.dev1', registry_text)
            self.assertIn('ssot-pack-contracts>=0.2.3,<0.3.0', registry_text)
            self.assertIn('ssot-core==0.2.4.dev1', registry_text)
            self.assertIn('ssot-cli>=0.1.1.dev1,<0.2.0', registry_text)
            self.assertIn('ssot-mcp>=0.1.1.dev1,<0.2.0', registry_text)
            self.assertIn('ssot-tui>=0.1.1.dev1,<0.2.0', registry_text)
            self.assertIn('version = "0.1.1.dev1"', cli_text)
            self.assertIn('ssot-contracts>=0.2.4.dev1,<0.3.0', cli_text)
            self.assertIn('ssot-pack-contracts>=0.2.3,<0.3.0', cli_text)
            self.assertIn('ssot-core>=0.2.4.dev1,<0.3.0', cli_text)
            self.assertIn('ssot-conformance>=0.2.4.dev1,<0.3.0', cli_text)
            self.assertIn('version = "0.1.1.dev1"', mcp_text)
            self.assertIn('ssot-core>=0.2.4.dev1,<0.3.0', mcp_text)
            self.assertIn('version = "0.1.1.dev1"', tui_text)
            self.assertIn('ssot-contracts>=0.2.4.dev1,<0.3.0', tui_text)
            self.assertIn('ssot-core>=0.2.4.dev1,<0.3.0', tui_text)
            self.assertIn(
                '"version": "0.2.4-dev.1"',
                (root / "packages" / "ssot-lineage-graph" / "package.json").read_text(encoding="utf-8"),
            )
            self.assertIn(
                '"version": "0.2.4-dev.1"',
                (
                    root
                    / "pkgs"
                    / "ssot-core"
                    / "src"
                    / "ssot_registry"
                    / "assets"
                    / "lineage_graph"
                    / "manifest.json"
                ).read_text(encoding="utf-8"),
            )

    def test_pack_contracts_bump_cannot_lead_registry_release_number(self) -> None:
        with workspace_tempdir() as temp_dir:
            root = Path(temp_dir)
            packages = {
                "ssot-contracts": ("0.2.3", []),
                "ssot-pack-contracts": ("0.2.3", []),
                "ssot-views": ("0.2.3", []),
                "ssot-codegen": ("0.2.3", []),
                "ssot-core": ("0.2.3", []),
                "ssot-conformance": ("0.2.3", []),
                "ssot-registry": ("0.2.3", []),
                "ssot-cli": ("0.1.0", []),
                "ssot-mcp": ("0.1.0", []),
                "ssot-tui": ("0.1.0", []),
            }
            package_infos: dict[str, PackageInfo] = {}
            for package_name, (version, dependencies) in packages.items():
                project_path = root / package_name
                project_path.mkdir(parents=True, exist_ok=True)
                _write_pyproject(project_path / "pyproject.toml", package_name, version, dependencies)
                package_infos[package_name] = PackageInfo(
                    name=package_name,
                    project_path=str(project_path),
                    workflow=f"publish-{package_name}.yml",
                    pypi_url=f"https://example.test/{package_name}",
                )

            with patch.object(bump_release_train, "PACKAGE_INFOS", package_infos):
                with self.assertRaisesRegex(ValueError, "ssot-pack-contracts must trail ssot-registry"):
                    bump_release_train.bump_train("ssot-pack-contracts", "patch", None)


if __name__ == "__main__":
    unittest.main()
