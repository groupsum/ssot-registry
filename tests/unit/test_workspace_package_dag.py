from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python 3.10 fallback
    import tomli as tomllib


REPO_ROOT = Path(__file__).resolve().parents[2]


def _load_toml(path: str) -> dict:
    return tomllib.loads((REPO_ROOT / path).read_text(encoding="utf-8"))


class WorkspacePackageDagTests(unittest.TestCase):
    def test_workspace_members_match_governed_package_set(self) -> None:
        root = _load_toml("pyproject.toml")
        self.assertEqual(
            root["tool"]["uv"]["workspace"]["members"],
            [
                "pkgs/ssot-contracts",
                "pkgs/ssot-views",
                "pkgs/ssot-codegen",
                "pkgs/ssot-core",
                "pkgs/ssot-conformance",
                "pkgs/ssot-registry",
                "pkgs/ssot-cli",
                "pkgs/ssot-tui",
            ],
        )

    def test_workspace_package_dependency_edges_match_governed_dag(self) -> None:
        packages = {
            "ssot-contracts": "pkgs/ssot-contracts/pyproject.toml",
            "ssot-views": "pkgs/ssot-views/pyproject.toml",
            "ssot-codegen": "pkgs/ssot-codegen/pyproject.toml",
            "ssot-core": "pkgs/ssot-core/pyproject.toml",
            "ssot-conformance": "pkgs/ssot-conformance/pyproject.toml",
            "ssot-registry": "pkgs/ssot-registry/pyproject.toml",
            "ssot-cli": "pkgs/ssot-cli/pyproject.toml",
            "ssot-tui": "pkgs/ssot-tui/pyproject.toml",
        }
        edges: set[tuple[str, str]] = set()
        for package_name, path in packages.items():
            dependencies = _load_toml(path)["project"].get("dependencies", [])
            for dependency in dependencies:
                for candidate in packages:
                    if dependency.startswith(candidate):
                        edges.add((package_name, candidate))

        self.assertEqual(
            edges,
            {
                ("ssot-views", "ssot-contracts"),
                ("ssot-codegen", "ssot-contracts"),
                ("ssot-codegen", "ssot-views"),
                ("ssot-core", "ssot-contracts"),
                ("ssot-core", "ssot-views"),
                ("ssot-conformance", "ssot-contracts"),
                ("ssot-conformance", "ssot-core"),
                ("ssot-cli", "ssot-contracts"),
                ("ssot-cli", "ssot-conformance"),
                ("ssot-cli", "ssot-core"),
                ("ssot-tui", "ssot-contracts"),
                ("ssot-tui", "ssot-core"),
                ("ssot-registry", "ssot-contracts"),
                ("ssot-registry", "ssot-core"),
                ("ssot-registry", "ssot-cli"),
            },
        )

    def test_release_metadata_targets_follow_workspace_dag_order(self) -> None:
        payload = subprocess.run(
            [sys.executable, "scripts/release_metadata.py", "targets", "--train", "all"],
            cwd=str(REPO_ROOT),
            text=True,
            capture_output=True,
            check=True,
        )
        self.assertEqual(
            json.loads(payload.stdout),
            ["ssot-contracts", "ssot-views", "ssot-codegen", "ssot-core", "ssot-conformance", "ssot-cli", "ssot-tui", "ssot-registry"],
        )
