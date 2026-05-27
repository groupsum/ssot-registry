from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

from packaging.version import Version


REPO_ROOT = Path(__file__).resolve().parents[2]


def _run_release_metadata(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "scripts/release_metadata.py", *args],
        cwd=str(REPO_ROOT),
        text=True,
        capture_output=True,
        check=True,
    )


class ReleaseMetadataTests(unittest.TestCase):
    def test_show_reports_current_core_version(self) -> None:
        payload = json.loads(_run_release_metadata("show").stdout)
        core_versions = [
            payload["packages"][name]["version"]
            for name in ("ssot-contracts", "ssot-views", "ssot-codegen", "ssot-core", "ssot-registry")
        ]
        self.assertEqual(len(set(core_versions)), 1)

    def test_show_reports_core_package_root(self) -> None:
        payload = json.loads(_run_release_metadata("show").stdout)
        self.assertEqual(payload["packages"]["ssot-core"]["project_path"], "pkgs/ssot-core")
        self.assertEqual(payload["packages"]["ssot-core"]["workflow"], "publish-ssot-core.yml")

    def test_validate_core_train_enforces_lockstep_group(self) -> None:
        payload = json.loads(_run_release_metadata("validate-train", "--train", "core").stdout)
        self.assertEqual(payload["targets"], ["ssot-contracts", "ssot-views", "ssot-codegen", "ssot-core"])
        show_payload = json.loads(_run_release_metadata("show").stdout)
        self.assertEqual(payload["core_version"], show_payload["packages"]["ssot-contracts"]["version"])

    def test_validate_pack_contracts_train_is_not_core_lockstep_bound(self) -> None:
        payload = json.loads(_run_release_metadata("validate-train", "--train", "ssot-pack-contracts").stdout)
        self.assertEqual(payload["targets"], ["ssot-pack-contracts"])

    def test_validate_all_train_confirms_local_dependency_versions_are_satisfiable(self) -> None:
        payload = json.loads(_run_release_metadata("validate-train", "--train", "all").stdout)
        self.assertEqual(
            payload["targets"],
            [
                "ssot-contracts",
                "ssot-pack-contracts",
                "ssot-views",
                "ssot-codegen",
                "ssot-core",
                "ssot-conformance",
                "ssot-cli",
                "ssot-mcp",
                "ssot-tui",
                "ssot-registry",
            ],
        )

    def test_all_train_resolves_to_canonical_release_order(self) -> None:
        payload = json.loads(_run_release_metadata("targets", "--train", "all").stdout)
        self.assertEqual(
            payload,
            [
                "ssot-contracts",
                "ssot-pack-contracts",
                "ssot-views",
                "ssot-codegen",
                "ssot-core",
                "ssot-conformance",
                "ssot-cli",
                "ssot-mcp",
                "ssot-tui",
                "ssot-registry",
            ],
        )

    def test_selected_targets_follow_release_order(self) -> None:
        payload = json.loads(
            _run_release_metadata("targets", "--train", "selected", "--packages", "ssot-contracts,ssot-core").stdout
        )
        self.assertEqual(payload, ["ssot-contracts", "ssot-core"])

    def test_each_package_has_a_direct_release_train(self) -> None:
        for package_name in (
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
        ):
            payload = json.loads(_run_release_metadata("targets", "--train", package_name).stdout)
            self.assertEqual(payload, [package_name])

    def test_tag_uses_package_equals_equals_version_format(self) -> None:
        payload = json.loads(_run_release_metadata("show").stdout)
        for package_name, package in payload["packages"].items():
            self.assertEqual(package["tag"], f"{package_name}=={package['version']}")

    def test_pack_contracts_and_tui_compatibility_floors_track_current_versions(self) -> None:
        payload = json.loads(_run_release_metadata("show").stdout)
        pack_contracts_version = payload["packages"]["ssot-pack-contracts"]["version"]
        registry_version = payload["packages"]["ssot-registry"]["version"]
        mcp_version = payload["packages"]["ssot-mcp"]["version"]
        tui_version = payload["packages"]["ssot-tui"]["version"]
        self.assertLessEqual(Version(pack_contracts_version).release, Version(registry_version).release)
        self.assertEqual(
            payload["packages"]["ssot-core"]["dependencies"]["ssot-pack-contracts"],
            f"ssot-pack-contracts>={pack_contracts_version},<0.3.0",
        )
        self.assertEqual(
            payload["packages"]["ssot-registry"]["dependencies"]["ssot-pack-contracts"],
            f"ssot-pack-contracts>={pack_contracts_version},<0.3.0",
        )
        self.assertEqual(
            payload["packages"]["ssot-cli"]["dependencies"]["ssot-pack-contracts"],
            f"ssot-pack-contracts>={pack_contracts_version},<0.3.0",
        )
        self.assertEqual(
            payload["packages"]["ssot-registry"]["dependencies"]["ssot-tui"],
            f"ssot-tui>={tui_version},<0.2.0",
        )
        self.assertEqual(
            payload["packages"]["ssot-registry"]["dependencies"]["ssot-mcp"],
            f"ssot-mcp>={mcp_version},<0.2.0",
        )


if __name__ == "__main__":
    unittest.main()
