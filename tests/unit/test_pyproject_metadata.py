from __future__ import annotations

import tomllib
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def _load_toml(path: str) -> dict:
    return tomllib.loads((REPO_ROOT / path).read_text(encoding="utf-8"))


class PyprojectMetadataTests(unittest.TestCase):
    def test_all_publishable_packages_declare_python_3_10_through_3_13_support(self) -> None:
        expected_classifiers = {
            "Programming Language :: Python :: 3.10",
            "Programming Language :: Python :: 3.11",
            "Programming Language :: Python :: 3.12",
            "Programming Language :: Python :: 3.13",
        }
        for path in (
            "pkgs/ssot-contracts/pyproject.toml",
            "pkgs/ssot-views/pyproject.toml",
            "pkgs/ssot-codegen/pyproject.toml",
            "pkgs/ssot-registry/pyproject.toml",
            "pkgs/ssot-cli/pyproject.toml",
            "pkgs/ssot-tui/pyproject.toml",
        ):
            project = _load_toml(path)["project"]
            self.assertEqual(project["requires-python"], ">=3.10")
            self.assertTrue(expected_classifiers.issubset(set(project["classifiers"])), path)

    def test_workspace_root_defines_dev_dependency_group(self) -> None:
        data = _load_toml("pyproject.toml")
        self.assertIn("dependency-groups", data)
        self.assertIn("dev", data["dependency-groups"])
        self.assertIn("textual>=8.2.3", data["dependency-groups"]["dev"])

    def test_registry_package_does_not_ship_cli_scripts(self) -> None:
        data = _load_toml("pkgs/ssot-registry/pyproject.toml")
        self.assertNotIn("scripts", data["project"])

    def test_cli_package_owns_all_cli_entry_points(self) -> None:
        data = _load_toml("pkgs/ssot-cli/pyproject.toml")
        scripts = data["project"]["scripts"]
        self.assertEqual(scripts["ssot"], "ssot_cli.main:main")
        self.assertEqual(scripts["ssot-cli"], "ssot_cli.main:main")
        self.assertEqual(scripts["ssot-registry"], "ssot_cli.main:main")

    def test_cli_and_tui_declare_direct_contract_dependencies(self) -> None:
        cli = _load_toml("pkgs/ssot-cli/pyproject.toml")["project"]["dependencies"]
        tui = _load_toml("pkgs/ssot-tui/pyproject.toml")["project"]["dependencies"]
        self.assertIn("ssot-contracts>=0.2.3,<0.3.0", cli)
        self.assertIn("ssot-registry>=0.2.3,<0.3.0", cli)
        self.assertIn("ssot-contracts>=0.2.3,<0.3.0", tui)
        self.assertIn("ssot-registry>=0.2.3,<0.3.0", tui)
        self.assertIn("textual>=8.2.3", tui)

    def test_core_train_packages_remain_lockstep(self) -> None:
        versions = []
        for path in (
            "pkgs/ssot-contracts/pyproject.toml",
            "pkgs/ssot-views/pyproject.toml",
            "pkgs/ssot-codegen/pyproject.toml",
            "pkgs/ssot-registry/pyproject.toml",
        ):
            versions.append(_load_toml(path)["project"]["version"])
        self.assertEqual(versions, ["0.2.3", "0.2.3", "0.2.3", "0.2.3"])

    def test_all_publishable_packages_have_urls_and_readmes(self) -> None:
        for path in (
            "pkgs/ssot-contracts/pyproject.toml",
            "pkgs/ssot-views/pyproject.toml",
            "pkgs/ssot-codegen/pyproject.toml",
            "pkgs/ssot-registry/pyproject.toml",
            "pkgs/ssot-cli/pyproject.toml",
            "pkgs/ssot-tui/pyproject.toml",
        ):
            data = _load_toml(path)
            self.assertEqual(data["project"]["readme"], "README.md")
            self.assertIn("urls", data["project"])
            self.assertIn("Homepage", data["project"]["urls"])


if __name__ == "__main__":
    unittest.main()
