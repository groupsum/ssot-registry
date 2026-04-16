from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


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
    def test_show_reports_registry_package_root(self) -> None:
        payload = json.loads(_run_release_metadata("show").stdout)
        self.assertEqual(payload["packages"]["ssot-registry"]["project_path"], "pkgs/ssot-registry")
        self.assertEqual(payload["packages"]["ssot-registry"]["workflow"], "publish-ssot-registry.yml")

    def test_validate_core_train_enforces_lockstep_group(self) -> None:
        payload = json.loads(_run_release_metadata("validate-train", "--train", "core").stdout)
        self.assertEqual(payload["targets"], ["ssot-contracts", "ssot-views", "ssot-codegen", "ssot-registry"])
        self.assertEqual(payload["core_version"], "0.2.3")

    def test_selected_targets_follow_release_order(self) -> None:
        payload = json.loads(
            _run_release_metadata("targets", "--train", "selected", "--packages", "ssot-contracts,ssot-registry").stdout
        )
        self.assertEqual(payload, ["ssot-contracts", "ssot-registry"])

    def test_each_package_has_a_direct_release_train(self) -> None:
        for package_name in (
            "ssot-contracts",
            "ssot-views",
            "ssot-codegen",
            "ssot-registry",
            "ssot-cli",
            "ssot-tui",
        ):
            payload = json.loads(_run_release_metadata("targets", "--train", package_name).stdout)
            self.assertEqual(payload, [package_name])


if __name__ == "__main__":
    unittest.main()
