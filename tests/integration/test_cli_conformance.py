from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path

from tests.helpers import run_cli, temp_repo_from_fixture


class CliConformanceSurfaceTests(unittest.TestCase):
    def test_cli_conformance_surface(self) -> None:
        temp_dir = temp_repo_from_fixture("repo_valid")
        self.addCleanup(temp_dir.cleanup)
        repo = Path(temp_dir.name) / "repo"

        profile_list = run_cli("conformance", "profile", "list", str(repo))
        self.assertEqual(profile_list.returncode, 0, profile_list.stderr)
        profiles = json.loads(profile_list.stdout)["profiles"]
        self.assertTrue(any(row["profile"] == "registry" for row in profiles))

        discover = run_cli("conformance", "discover", str(repo), "--profiles", "registry")
        self.assertEqual(discover.returncode, 0, discover.stderr)
        discover_payload = json.loads(discover.stdout)
        self.assertEqual(discover_payload["families"], ["registry"])
        self.assertEqual(discover_payload["cases"][0]["kind"], "pytest")

        plan = run_cli("conformance", "scaffold", str(repo), "--profiles", "registry", "--include-claims", "--include-evidence")
        self.assertEqual(plan.returncode, 0, plan.stderr)
        plan_payload = json.loads(plan.stdout)
        self.assertIn("feat:conformance.registry-contract", plan_payload["missing"]["features"])

        apply = run_cli(
            "conformance",
            "scaffold",
            str(repo),
            "--profiles",
            "registry",
            "--apply",
            "--include-claims",
            "--include-evidence",
        )
        self.assertEqual(apply.returncode, 0, apply.stderr)
        apply_payload = json.loads(apply.stdout)
        self.assertTrue(apply_payload["passed"], apply_payload)

    @unittest.skipUnless(importlib.util.find_spec("pytest") is not None, "pytest is not installed")
    def test_cli_conformance_run_emits_evidence(self) -> None:
        temp_dir = temp_repo_from_fixture("repo_valid")
        self.addCleanup(temp_dir.cleanup)
        repo = Path(temp_dir.name) / "repo"
        evidence_path = repo / ".ssot" / "evidence" / "conformance" / "cli-run-evidence.json"

        result = run_cli(
            "conformance",
            "run",
            str(repo),
            "--profiles",
            "registry",
            "--evidence-output",
            str(evidence_path),
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["passed"], payload)
        self.assertEqual(payload["profiles"], ["registry"])
        evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
        self.assertEqual(evidence["profiles"], ["registry"])
        self.assertEqual(evidence["summary"]["passed"], 1)

    def test_cli_conformance_run_command_emits_evidence(self) -> None:
        temp_dir = temp_repo_from_fixture("repo_valid")
        self.addCleanup(temp_dir.cleanup)
        repo = Path(temp_dir.name) / "repo"
        evidence_path = repo / ".ssot" / "evidence" / "conformance" / "cli-command-evidence.json"

        result = run_cli(
            "conformance",
            "run",
            str(repo),
            "--profiles",
            "registry",
            "--runner",
            "command",
            "--evidence-output",
            str(evidence_path),
            "--command",
            sys.executable,
            "-c",
            "print('command runner ok')",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["passed"], payload)
        self.assertEqual(payload["runner"], "command")
        self.assertEqual(payload["command_exit_code"], 0)
        evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
        self.assertEqual(evidence["summary"]["passed"], 1)
        self.assertEqual(evidence["cases"][0]["runner"], "command")


if __name__ == "__main__":
    unittest.main()
