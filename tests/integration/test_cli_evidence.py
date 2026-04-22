from __future__ import annotations

import json
import unittest
from pathlib import Path

from tests.helpers import run_cli, temp_repo_from_fixture


class CliEvidenceSurfaceTests(unittest.TestCase):
    def test_evidence_surface(self) -> None:
        temp_dir = temp_repo_from_fixture("repo_valid")
        self.addCleanup(temp_dir.cleanup)
        repo = Path(temp_dir.name) / "repo"
        evidence_dir = repo / ".ssot" / "evidence" / "bundles" / "evd__cli.generated.bundle"
        evidence_dir.mkdir(parents=True, exist_ok=True)
        (evidence_dir / "manifest.json").write_text("{}", encoding="utf-8")

        create = run_cli(
            "evidence",
            "create",
            str(repo),
            "--id",
            "evd:t2.cli.generated.bundle",
            "--title",
            "CLI generated evidence",
            "--status",
            "passed",
            "--kind",
            "bundle",
            "--tier",
            "T2",
            "--evidence-path",
            ".ssot/evidence/bundles/evd__cli.generated.bundle",
            "--claim-ids",
            "clm:rfc.9000.connection-migration.t3",
            "--test-ids",
            "tst:pytest.rfc.9000.connection-migration",
        )
        self.assertEqual(create.returncode, 0, create.stderr)

        get_result = run_cli("evidence", "get", str(repo), "--id", "evd:t2.cli.generated.bundle")
        self.assertEqual(get_result.returncode, 0, get_result.stderr)
        self.assertEqual(json.loads(get_result.stdout)["tier"], "T2")

        list_result = run_cli("evidence", "list", str(repo))
        self.assertEqual(list_result.returncode, 0, list_result.stderr)
        list_payload = json.loads(list_result.stdout)
        self.assertIsInstance(list_payload, list)
        ids = {row["id"] for row in list_payload}
        self.assertIn("evd:t2.cli.generated.bundle", ids)

        update = run_cli(
            "evidence",
            "update",
            str(repo),
            "--id",
            "evd:t2.cli.generated.bundle",
            "--title",
            "CLI generated evidence updated",
        )
        self.assertEqual(update.returncode, 0, update.stderr)

        verify = run_cli("evidence", "verify", str(repo), "--evidence-id", "evd:t2.cli.generated.bundle")
        self.assertEqual(verify.returncode, 1, verify.stderr)
        self.assertIn("below linked claim tier", verify.stdout)

        set_tier = run_cli(
            "evidence",
            "update",
            str(repo),
            "--id",
            "evd:t2.cli.generated.bundle",
            "--tier",
            "T3",
        )
        self.assertEqual(set_tier.returncode, 0, set_tier.stderr)

        verify_pass = run_cli("evidence", "verify", str(repo), "--evidence-id", "evd:t2.cli.generated.bundle")
        self.assertEqual(verify_pass.returncode, 0, verify_pass.stderr)
        self.assertTrue(json.loads(verify_pass.stdout)["passed"])

        unlink = run_cli("evidence", "unlink", str(repo), "--id", "evd:t2.cli.generated.bundle", "--claim-ids", "clm:rfc.9000.connection-migration.t3")
        self.assertEqual(unlink.returncode, 0, unlink.stderr)

        relink = run_cli("evidence", "link", str(repo), "--id", "evd:t2.cli.generated.bundle", "--claim-ids", "clm:rfc.9000.connection-migration.t3")
        self.assertEqual(relink.returncode, 0, relink.stderr)

        delete = run_cli("evidence", "delete", str(repo), "--id", "evd:t2.cli.generated.bundle")
        self.assertEqual(delete.returncode, 0, delete.stderr)
        self.assertTrue(json.loads(delete.stdout)["passed"])


if __name__ == "__main__":
    unittest.main()
