from __future__ import annotations

import unittest
from pathlib import Path

from ssot_registry.api import validate_registry
from tests.helpers import temp_repo_from_fixture


class ValidationTests(unittest.TestCase):
    def test_valid_fixture_passes(self) -> None:
        temp_dir = temp_repo_from_fixture("repo_valid")
        self.addCleanup(temp_dir.cleanup)
        repo = Path(temp_dir.name) / "repo"
        report = validate_registry(repo)
        self.assertTrue(report["passed"], report)

    def test_missing_claim_is_reported(self) -> None:
        temp_dir = temp_repo_from_fixture("repo_invalid_missing_claim")
        self.addCleanup(temp_dir.cleanup)
        repo = Path(temp_dir.name) / "repo"
        report = validate_registry(repo)
        self.assertFalse(report["passed"])
        joined = "\n".join(report["failures"])
        self.assertIn("references missing claim", joined)

    def test_missing_evidence_row_is_reported(self) -> None:
        temp_dir = temp_repo_from_fixture("repo_invalid_missing_evidence")
        self.addCleanup(temp_dir.cleanup)
        repo = Path(temp_dir.name) / "repo"
        report = validate_registry(repo)
        self.assertFalse(report["passed"])
        joined = "\n".join(report["failures"])
        self.assertIn("references missing evidence", joined)

    def test_claim_missing_feature_is_reported(self) -> None:
        temp_dir = temp_repo_from_fixture("repo_invalid_missing_feature")
        self.addCleanup(temp_dir.cleanup)
        repo = Path(temp_dir.name) / "repo"
        report = validate_registry(repo)
        self.assertFalse(report["passed"])
        joined = "\n".join(report["failures"])
        self.assertIn("references missing feature", joined)


if __name__ == "__main__":
    unittest.main()
