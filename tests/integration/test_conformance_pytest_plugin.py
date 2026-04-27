from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
import unittest
from pathlib import Path

from tests.helpers import temp_repo_from_fixture

REPO_ROOT = Path(__file__).resolve().parents[2]


@unittest.skipUnless(importlib.util.find_spec("pytest") is not None, "pytest is not installed")
class ConformancePytestPluginTests(unittest.TestCase):
    def test_plugin_writes_machine_readable_evidence(self) -> None:
        temp_dir = temp_repo_from_fixture("repo_valid")
        self.addCleanup(temp_dir.cleanup)
        repo = Path(temp_dir.name) / "repo"
        evidence_path = repo / ".ssot" / "evidence" / "conformance" / "plugin-evidence.json"

        env = os.environ.copy()
        env["PYTHONPATH"] = os.pathsep.join(
            [
                str(REPO_ROOT / "pkgs" / "ssot-core" / "src"),
                str(REPO_ROOT / "pkgs" / "ssot-codegen" / "src"),
                str(REPO_ROOT / "pkgs" / "ssot-views" / "src"),
                str(REPO_ROOT / "pkgs" / "ssot-contracts" / "src"),
                str(REPO_ROOT / "pkgs" / "ssot-cli" / "src"),
                str(REPO_ROOT / "pkgs" / "ssot-tui" / "src"),
                str(REPO_ROOT / "pkgs" / "ssot-conformance" / "src"),
            ]
        )
        env["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "pytest",
                str(REPO_ROOT / "pkgs" / "ssot-conformance" / "src" / "ssot_conformance" / "cases" / "test_registry_contract.py"),
                "-p",
                "ssot_conformance.plugin",
                f"--ssot-repo-root={repo}",
                "--ssot-conformance-profile=registry",
                f"--ssot-conformance-evidence-output={evidence_path}",
            ],
            cwd=str(REPO_ROOT),
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        payload = json.loads(evidence_path.read_text(encoding="utf-8"))
        self.assertEqual(payload["profiles"], ["registry"])
        self.assertEqual(payload["summary"]["total"], 1)


if __name__ == "__main__":
    unittest.main()
