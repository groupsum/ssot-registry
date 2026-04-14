from __future__ import annotations

import json
import unittest
from pathlib import Path

from tests.helpers import run_cli, temp_repo_from_fixture


class CliValidateTests(unittest.TestCase):
    def test_validate_surface(self) -> None:
        temp_dir = temp_repo_from_fixture("repo_valid")
        self.addCleanup(temp_dir.cleanup)
        repo = Path(temp_dir.name) / "repo"

        validate = run_cli("validate", str(repo), "--write-report")
        self.assertEqual(validate.returncode, 0, validate.stderr)
        payload = json.loads(validate.stdout)
        self.assertTrue(payload["passed"], payload)
        self.assertTrue((repo / ".ssot" / "reports" / "validation.report.json").exists())

    def test_validate_failure_fixture(self) -> None:
        temp_dir = temp_repo_from_fixture("repo_invalid_missing_claim")
        self.addCleanup(temp_dir.cleanup)
        repo = Path(temp_dir.name) / "repo"

        validate = run_cli("validate", str(repo))
        self.assertEqual(validate.returncode, 1, validate.stderr)
        payload = json.loads(validate.stdout)
        self.assertFalse(payload["passed"])
        self.assertTrue(any("missing claim" in failure for failure in payload["failures"]))


if __name__ == "__main__":
    unittest.main()
