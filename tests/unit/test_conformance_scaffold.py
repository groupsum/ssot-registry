from __future__ import annotations

import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
for path in (
    REPO_ROOT / "pkgs" / "ssot-core" / "src",
    REPO_ROOT / "pkgs" / "ssot-codegen" / "src",
    REPO_ROOT / "pkgs" / "ssot-views" / "src",
    REPO_ROOT / "pkgs" / "ssot-contracts" / "src",
    REPO_ROOT / "pkgs" / "ssot-cli" / "src",
    REPO_ROOT / "pkgs" / "ssot-tui" / "src",
    REPO_ROOT / "pkgs" / "ssot-conformance" / "src",
):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from ssot_conformance.scaffold import apply_scaffold, plan_scaffold
from tests.helpers import temp_repo_from_fixture


class ConformanceScaffoldTests(unittest.TestCase):
    def test_dry_run_reports_missing_rows(self) -> None:
        temp_dir = temp_repo_from_fixture("repo_valid")
        self.addCleanup(temp_dir.cleanup)
        repo = Path(temp_dir.name) / "repo"

        plan = plan_scaffold(repo, profiles=["registry"])
        self.assertTrue(plan["passed"])
        self.assertIn("feat:conformance.registry-contract", plan["missing"]["features"])
        self.assertIn("tst:pytest.conformance.registry-contract", plan["blocked_tests"][0]["id"])

    def test_apply_can_create_claims_evidence_and_tests(self) -> None:
        temp_dir = temp_repo_from_fixture("repo_valid")
        self.addCleanup(temp_dir.cleanup)
        repo = Path(temp_dir.name) / "repo"

        result = apply_scaffold(repo, profiles=["registry"], include_claims=True, include_evidence=True)
        self.assertTrue(result["passed"], result)
        self.assertIn("feat:conformance.registry-contract", result["created"]["features"])
        self.assertIn("clm:conformance.registry-contract.t2", result["created"]["claims"])
        self.assertIn("evd:t2.conformance.registry-contract.pytest", result["created"]["evidence"])
        self.assertIn("tst:pytest.conformance.registry-contract", result["created"]["tests"])

        rerun = apply_scaffold(repo, profiles=["registry"], include_claims=True, include_evidence=True)
        self.assertTrue(rerun["passed"], rerun)
        self.assertEqual(rerun["created"]["features"], [])
        self.assertEqual(rerun["created"]["tests"], [])


if __name__ == "__main__":
    unittest.main()
