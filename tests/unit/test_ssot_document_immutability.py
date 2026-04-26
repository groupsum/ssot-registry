from __future__ import annotations

import unittest
from pathlib import Path

from ssot_registry.api import validate_registry
from tests.helpers import temp_repo_from_fixture


class SsotDocumentImmutabilityTests(unittest.TestCase):
    def test_direct_edit_of_ssot_managed_file_fails_validation(self) -> None:
        temp_dir = temp_repo_from_fixture("repo_valid")
        self.addCleanup(temp_dir.cleanup)
        repo = Path(temp_dir.name) / "repo"

        target = repo / ".ssot" / "specs" / "SPEC-0600-registry-core.yaml"
        target.write_text(target.read_text(encoding="utf-8") + "\nmutated\n", encoding="utf-8")

        report = validate_registry(repo)
        self.assertFalse(report["passed"])
        self.assertIn("content hash does not match file content", "\n".join(report["failures"]))


if __name__ == "__main__":
    unittest.main()


