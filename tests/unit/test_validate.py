from __future__ import annotations

import json
import unittest
from pathlib import Path

from ssot_registry.api import validate_registry
from ssot_registry.util.jsonio import stable_json_dumps
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

    def test_evidence_without_claim_is_reported(self) -> None:
        temp_dir = temp_repo_from_fixture("repo_valid")
        self.addCleanup(temp_dir.cleanup)
        repo = Path(temp_dir.name) / "repo"
        registry_path = repo / ".ssot" / "registry.json"
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
        registry["evidence"][0]["claim_ids"] = []
        registry_path.write_text(stable_json_dumps(registry), encoding="utf-8")

        report = validate_registry(repo)

        self.assertFalse(report["passed"])
        self.assertIn("evidence.evd:t3.rfc.9000.connection-migration.bundle has no linked claims", report["failures"])

    def test_test_can_link_to_evidence_without_direct_claim_link(self) -> None:
        temp_dir = temp_repo_from_fixture("repo_valid")
        self.addCleanup(temp_dir.cleanup)
        repo = Path(temp_dir.name) / "repo"
        registry_path = repo / ".ssot" / "registry.json"
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
        registry["claims"][0]["test_ids"] = []
        registry["claims"][0]["evidence_ids"] = []
        registry["tests"][0]["claim_ids"] = []
        registry_path.write_text(stable_json_dumps(registry), encoding="utf-8")

        report = validate_registry(repo)

        self.assertTrue(report["passed"], report)


if __name__ == "__main__":
    unittest.main()
