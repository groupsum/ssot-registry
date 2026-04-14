from __future__ import annotations

import json
import unittest
from pathlib import Path

from tests.helpers import run_cli, temp_repo_from_fixture


class CliClaimSurfaceTests(unittest.TestCase):
    def test_claim_surface(self) -> None:
        temp_dir = temp_repo_from_fixture("repo_valid")
        self.addCleanup(temp_dir.cleanup)
        repo = Path(temp_dir.name) / "repo"

        create = run_cli(
            "claim",
            "create",
            str(repo),
            "--id",
            "clm:cli.generated.t1",
            "--title",
            "CLI generated claim",
            "--status",
            "asserted",
            "--tier",
            "T1",
            "--kind",
            "conformance",
            "--description",
            "generated claim",
            "--feature-ids",
            "feat:rfc.9000.connection-migration",
            "--test-ids",
            "tst:pytest.rfc.9000.connection-migration",
            "--evidence-ids",
            "evd:t3.rfc.9000.connection-migration.bundle",
        )
        self.assertEqual(create.returncode, 0, create.stderr)

        get_result = run_cli("claim", "get", str(repo), "--id", "clm:cli.generated.t1")
        self.assertEqual(get_result.returncode, 0, get_result.stderr)
        self.assertEqual(json.loads(get_result.stdout)["entity"]["tier"], "T1")

        list_result = run_cli("claim", "list", str(repo))
        self.assertEqual(list_result.returncode, 0, list_result.stderr)
        ids = {row["id"] for row in json.loads(list_result.stdout)["entities"]}
        self.assertIn("clm:cli.generated.t1", ids)

        update = run_cli(
            "claim",
            "update",
            str(repo),
            "--id",
            "clm:cli.generated.t1",
            "--description",
            "updated generated claim",
        )
        self.assertEqual(update.returncode, 0, update.stderr)

        set_status = run_cli("claim", "set-status", str(repo), "--id", "clm:cli.generated.t1", "--status", "evidenced")
        self.assertEqual(set_status.returncode, 0, set_status.stderr)

        set_tier = run_cli("claim", "set-tier", str(repo), "--id", "clm:cli.generated.t1", "--tier", "T3")
        self.assertEqual(set_tier.returncode, 0, set_tier.stderr)

        evaluate = run_cli("claim", "evaluate", str(repo), "--claim-id", "clm:cli.generated.t1")
        self.assertEqual(evaluate.returncode, 0, evaluate.stderr)
        self.assertTrue(json.loads(evaluate.stdout)["passed"])

        unlink = run_cli("claim", "unlink", str(repo), "--id", "clm:cli.generated.t1", "--feature-ids", "feat:rfc.9000.connection-migration")
        self.assertEqual(unlink.returncode, 0, unlink.stderr)

        relink = run_cli("claim", "link", str(repo), "--id", "clm:cli.generated.t1", "--feature-ids", "feat:rfc.9000.connection-migration")
        self.assertEqual(relink.returncode, 0, relink.stderr)

        delete = run_cli("claim", "delete", str(repo), "--id", "clm:cli.generated.t1")
        self.assertEqual(delete.returncode, 0, delete.stderr)
        self.assertTrue(json.loads(delete.stdout)["passed"])


if __name__ == "__main__":
    unittest.main()
