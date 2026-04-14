from __future__ import annotations

import json
import unittest
from pathlib import Path

from tests.helpers import run_cli, temp_repo_from_fixture


class CliIssueSurfaceTests(unittest.TestCase):
    def test_issue_surface(self) -> None:
        temp_dir = temp_repo_from_fixture("repo_valid")
        self.addCleanup(temp_dir.cleanup)
        repo = Path(temp_dir.name) / "repo"

        create = run_cli(
            "issue",
            "create",
            str(repo),
            "--id",
            "iss:cli.generated",
            "--title",
            "CLI generated issue",
            "--severity",
            "high",
            "--description",
            "generated issue",
            "--horizon",
            "backlog",
            "--feature-ids",
            "feat:rfc.9000.connection-migration",
            "--claim-ids",
            "clm:rfc.9000.connection-migration.t3",
            "--test-ids",
            "tst:pytest.rfc.9000.connection-migration",
            "--evidence-ids",
            "evd:t3.rfc.9000.connection-migration.bundle",
            "--release-blocking",
        )
        self.assertEqual(create.returncode, 0, create.stderr)

        get_result = run_cli("issue", "get", str(repo), "--id", "iss:cli.generated")
        self.assertEqual(get_result.returncode, 0, get_result.stderr)
        self.assertEqual(json.loads(get_result.stdout)["entity"]["severity"], "high")

        list_result = run_cli("issue", "list", str(repo))
        self.assertEqual(list_result.returncode, 0, list_result.stderr)
        ids = {row["id"] for row in json.loads(list_result.stdout)["entities"]}
        self.assertIn("iss:cli.generated", ids)

        update = run_cli(
            "issue",
            "update",
            str(repo),
            "--id",
            "iss:cli.generated",
            "--description",
            "updated issue description",
            "--no-release-blocking",
        )
        self.assertEqual(update.returncode, 0, update.stderr)

        plan = run_cli("issue", "plan", str(repo), "--ids", "iss:cli.generated", "--horizon", "current")
        self.assertEqual(plan.returncode, 0, plan.stderr)

        close = run_cli("issue", "close", str(repo), "--id", "iss:cli.generated")
        self.assertEqual(close.returncode, 0, close.stderr)

        reopen = run_cli("issue", "reopen", str(repo), "--id", "iss:cli.generated")
        self.assertEqual(reopen.returncode, 0, reopen.stderr)

        unlink = run_cli("issue", "unlink", str(repo), "--id", "iss:cli.generated", "--feature-ids", "feat:rfc.9000.connection-migration")
        self.assertEqual(unlink.returncode, 0, unlink.stderr)

        relink = run_cli("issue", "link", str(repo), "--id", "iss:cli.generated", "--feature-ids", "feat:rfc.9000.connection-migration")
        self.assertEqual(relink.returncode, 0, relink.stderr)

        delete = run_cli("issue", "delete", str(repo), "--id", "iss:cli.generated")
        self.assertEqual(delete.returncode, 0, delete.stderr)
        self.assertTrue(json.loads(delete.stdout)["passed"])


if __name__ == "__main__":
    unittest.main()
