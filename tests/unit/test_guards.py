from __future__ import annotations

import unittest
from pathlib import Path

from ssot_registry.api import evaluate_claims, verify_evidence_rows
from tests.helpers import temp_repo_from_fixture


class GuardEvaluationTests(unittest.TestCase):
    def test_claim_evaluation_passes_on_valid_fixture(self) -> None:
        temp_dir = temp_repo_from_fixture("repo_valid")
        self.addCleanup(temp_dir.cleanup)
        repo = Path(temp_dir.name) / "repo"
        result = evaluate_claims(repo, claim_id="clm:rfc.9000.connection-migration.t3")
        self.assertTrue(result["passed"], result)

    def test_evidence_verification_passes_on_valid_fixture(self) -> None:
        temp_dir = temp_repo_from_fixture("repo_valid")
        self.addCleanup(temp_dir.cleanup)
        repo = Path(temp_dir.name) / "repo"
        result = verify_evidence_rows(repo, evidence_id="evd:t3.rfc.9000.connection-migration.bundle")
        self.assertTrue(result["passed"], result)


if __name__ == "__main__":
    unittest.main()
