from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

from tests.helpers import temp_repo_from_fixture

REPO_ROOT = Path(__file__).resolve().parents[2]
for path in (
    REPO_ROOT / "pkgs" / "ssot-core" / "src",
    REPO_ROOT / "pkgs" / "ssot-contracts" / "src",
):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from ssot_registry.api import run_tests
from ssot_registry.api.validate import validate_registry_document
from ssot_registry.util.jsonio import load_json
from ssot_registry.util.fs import resolve_registry_path, repo_root_from_registry_path


class RegistryTestExecutionTests(unittest.TestCase):
    def test_run_tests_returns_command_case_and_summary(self) -> None:
        temp_dir = temp_repo_from_fixture("repo_valid")
        self.addCleanup(temp_dir.cleanup)
        repo = Path(temp_dir.name) / "repo"

        payload = run_tests(repo, test_ids=["tst:pytest.rfc.9000.connection-migration"])
        self.assertTrue(payload["passed"], payload)
        self.assertEqual(payload["summary"]["passed"], 1)
        self.assertEqual(payload["cases"][0]["runner"], "command")
        self.assertEqual(payload["cases"][0]["command"][1:3], ["-m", "pytest"])

    def test_run_tests_dry_run_reports_execution_contract(self) -> None:
        temp_dir = temp_repo_from_fixture("repo_valid")
        self.addCleanup(temp_dir.cleanup)
        repo = Path(temp_dir.name) / "repo"

        payload = run_tests(repo, test_ids=["tst:pytest.rfc.9000.connection-migration"], dry_run=True)
        self.assertTrue(payload["dry_run"], payload)
        self.assertEqual(payload["resolved_tests"][0]["execution"]["mode"], "command")

    def test_validate_registry_document_rejects_malformed_execution(self) -> None:
        temp_dir = temp_repo_from_fixture("repo_valid")
        self.addCleanup(temp_dir.cleanup)
        repo = Path(temp_dir.name) / "repo"
        registry_path = resolve_registry_path(repo)
        repo_root = repo_root_from_registry_path(registry_path)
        registry = load_json(registry_path)
        registry["tests"][0]["execution"] = {
            "mode": "command",
            "argv": [],
            "cwd": ".",
            "env": {},
            "timeout_seconds": 600,
            "success": {"type": "exit_code", "expected": 0},
        }

        report = validate_registry_document(registry, registry_path, repo_root)
        self.assertFalse(report["passed"], json.dumps(report, indent=2))
        self.assertTrue(
            any("tests.tst:pytest.rfc.9000.connection-migration.execution.argv" in failure for failure in report["failures"])
        )


if __name__ == "__main__":
    unittest.main()
