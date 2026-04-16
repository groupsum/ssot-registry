from __future__ import annotations

import json
import unittest
from pathlib import Path

from tests.helpers import run_cli, temp_repo_from_fixture


class CliInvalidFlagValuesTests(unittest.TestCase):
    def _prepare_repo(self) -> Path:
        temp_dir = temp_repo_from_fixture("repo_valid")
        self.addCleanup(temp_dir.cleanup)
        return Path(temp_dir.name) / "repo"

    def test_invalid_status_values_fail_fast(self) -> None:
        repo = self._prepare_repo()
        invalid_status = run_cli(
            "claim",
            "create",
            str(repo),
            "--id",
            "clm:cli.invalid-status",
            "--title",
            "Invalid status claim",
            "--status",
            "ship_it",
            "--tier",
            "T1",
            "--kind",
            "conformance",
        )
        self.assertNotEqual(invalid_status.returncode, 0)
        self.assertIn("invalid choice", invalid_status.stderr)
        self.assertIn("--status", invalid_status.stderr)

    def test_invalid_tier_and_claim_tier_values_fail_fast(self) -> None:
        repo = self._prepare_repo()
        invalid_tier = run_cli(
            "claim",
            "create",
            str(repo),
            "--id",
            "clm:cli.invalid-tier",
            "--title",
            "Invalid tier claim",
            "--status",
            "asserted",
            "--tier",
            "T9",
            "--kind",
            "conformance",
        )
        self.assertNotEqual(invalid_tier.returncode, 0)
        self.assertIn("invalid choice", invalid_tier.stderr)
        self.assertIn("--tier", invalid_tier.stderr)

        invalid_claim_tier = run_cli(
            "feature",
            "plan",
            str(repo),
            "--ids",
            "feat:rfc.9000.connection-migration",
            "--horizon",
            "current",
            "--claim-tier",
            "TX",
        )
        self.assertNotEqual(invalid_claim_tier.returncode, 0)
        self.assertIn("invalid choice", invalid_claim_tier.stderr)
        self.assertIn("--claim-tier", invalid_claim_tier.stderr)

    def test_invalid_horizon_slot_combinations_fail_validation_payload(self) -> None:
        repo = self._prepare_repo()
        plan = run_cli(
            "feature",
            "plan",
            str(repo),
            "--ids",
            "feat:rfc.9000.connection-migration",
            "--horizon",
            "explicit",
            "--claim-tier",
            "T3",
        )
        self.assertEqual(plan.returncode, 1, plan.stderr)
        payload = json.loads(plan.stdout)
        self.assertFalse(payload["passed"])
        self.assertIn("Registry validation failed after attempted mutation", payload["error"])

    def test_unsupported_export_formats_return_choice_errors(self) -> None:
        repo = self._prepare_repo()

        invalid_registry_export = run_cli("registry", "export", str(repo), "--format", "xml")
        self.assertNotEqual(invalid_registry_export.returncode, 0)
        self.assertIn("invalid choice", invalid_registry_export.stderr)
        self.assertIn("--format", invalid_registry_export.stderr)

        invalid_graph_export = run_cli("graph", "export", str(repo), "--format", "gif")
        self.assertNotEqual(invalid_graph_export.returncode, 0)
        self.assertIn("invalid choice", invalid_graph_export.stderr)
        self.assertIn("--format", invalid_graph_export.stderr)


if __name__ == "__main__":
    unittest.main()
