from __future__ import annotations

import unittest
from pathlib import Path

from ssot_registry.api import sync_documents, validate_registry
from tests.helpers import temp_repo_from_fixture


class DocumentSyncTests(unittest.TestCase):
    def test_sync_restores_modified_ssot_document(self) -> None:
        temp_dir = temp_repo_from_fixture("repo_valid")
        self.addCleanup(temp_dir.cleanup)
        repo = Path(temp_dir.name) / "repo"

        target = repo / ".ssot" / "adr" / "ADR-0600-canonical-json-registry.json"
        target.write_text(target.read_text(encoding="utf-8") + "\nlocal edit\n", encoding="utf-8")

        report = validate_registry(repo)
        self.assertFalse(report["passed"])
        self.assertIn("content hash does not match file content", "\n".join(report["failures"]))

        sync_result = sync_documents(repo, "adr")
        self.assertIn("adr:0600", sync_result["updated"])

        report_after = validate_registry(repo)
        self.assertTrue(report_after["passed"], report_after)


if __name__ == "__main__":
    unittest.main()

