from __future__ import annotations

import json
import unittest
from pathlib import Path

from tests.helpers import run_cli, temp_repo_from_fixture


class CliFeatureTests(unittest.TestCase):
    def test_feature_surface(self) -> None:
        temp_dir = temp_repo_from_fixture("repo_valid")
        self.addCleanup(temp_dir.cleanup)
        repo = Path(temp_dir.name) / "repo"

        create = run_cli(
            "feature",
            "create",
            str(repo),
            "--id",
            "feat:cli.generated",
            "--title",
            "CLI generated feature",
            "--description",
            "generated from cli test",
            "--implementation-status",
            "partial",
            "--requires",
            "feat:rfc.9000.connection-migration",
        )
        self.assertEqual(create.returncode, 0, create.stderr)
        self.assertTrue(json.loads(create.stdout)["passed"])

        get_result = run_cli("feature", "get", str(repo), "--id", "feat:cli.generated")
        self.assertEqual(get_result.returncode, 0, get_result.stderr)
        get_payload = json.loads(get_result.stdout)
        self.assertEqual(get_payload["entity"]["id"], "feat:cli.generated")

        list_result = run_cli("feature", "list", str(repo))
        self.assertEqual(list_result.returncode, 0, list_result.stderr)
        list_payload = json.loads(list_result.stdout)
        ids = {row["id"] for row in list_payload["entities"]}
        self.assertIn("feat:cli.generated", ids)

        update = run_cli(
            "feature",
            "update",
            str(repo),
            "--id",
            "feat:cli.generated",
            "--title",
            "CLI generated feature updated",
        )
        self.assertEqual(update.returncode, 0, update.stderr)
        self.assertEqual(json.loads(update.stdout)["entity"]["title"], "CLI generated feature updated")

        link = run_cli(
            "feature",
            "link",
            str(repo),
            "--id",
            "feat:cli.generated",
            "--claim-ids",
            "clm:rfc.9000.connection-migration.t3",
            "--test-ids",
            "tst:pytest.rfc.9000.connection-migration",
        )
        self.assertEqual(link.returncode, 0, link.stderr)

        implement = run_cli(
            "feature",
            "update",
            str(repo),
            "--id",
            "feat:cli.generated",
            "--implementation-status",
            "implemented",
        )
        self.assertEqual(implement.returncode, 0, implement.stderr)

        plan = run_cli(
            "feature",
            "plan",
            str(repo),
            "--ids",
            "feat:cli.generated",
            "--horizon",
            "current",
            "--claim-tier",
            "T3",
            "--target-lifecycle-stage",
            "active",
        )
        self.assertEqual(plan.returncode, 0, plan.stderr)

        lifecycle = run_cli(
            "feature",
            "lifecycle",
            "set",
            str(repo),
            "--ids",
            "feat:cli.generated",
            "--stage",
            "deprecated",
            "--note",
            "sunsetting test feature",
        )
        self.assertEqual(lifecycle.returncode, 0, lifecycle.stderr)

        backlog = run_cli(
            "feature",
            "plan",
            str(repo),
            "--ids",
            "feat:cli.generated",
            "--horizon",
            "backlog",
            "--target-lifecycle-stage",
            "deprecated",
        )
        self.assertEqual(backlog.returncode, 0, backlog.stderr)

        deimplement = run_cli(
            "feature",
            "update",
            str(repo),
            "--id",
            "feat:cli.generated",
            "--implementation-status",
            "partial",
        )
        self.assertEqual(deimplement.returncode, 0, deimplement.stderr)

        unlink = run_cli(
            "feature",
            "unlink",
            str(repo),
            "--id",
            "feat:cli.generated",
            "--claim-ids",
            "clm:rfc.9000.connection-migration.t3",
            "--test-ids",
            "tst:pytest.rfc.9000.connection-migration",
            "--requires",
            "feat:rfc.9000.connection-migration",
        )
        self.assertEqual(unlink.returncode, 0, unlink.stderr)

        delete = run_cli("feature", "delete", str(repo), "--id", "feat:cli.generated")
        self.assertEqual(delete.returncode, 0, delete.stderr)
        self.assertTrue(json.loads(delete.stdout)["passed"])


if __name__ == "__main__":
    unittest.main()
