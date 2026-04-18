from __future__ import annotations

import json
import unittest
from pathlib import Path

from tests.helpers import run_cli, temp_repo_from_fixture


class CliRiskSurfaceTests(unittest.TestCase):
    def test_risk_surface(self) -> None:
        temp_dir = temp_repo_from_fixture("repo_valid")
        self.addCleanup(temp_dir.cleanup)
        repo = Path(temp_dir.name) / "repo"

        issue_create = run_cli(
            "issue",
            "create",
            str(repo),
            "--id",
            "iss:cli.risk-link",
            "--title",
            "Issue linked to risk",
            "--description",
            "supporting issue",
        )
        self.assertEqual(issue_create.returncode, 0, issue_create.stderr)

        create = run_cli(
            "risk",
            "create",
            str(repo),
            "--id",
            "rsk:cli.generated",
            "--title",
            "CLI generated risk",
            "--severity",
            "high",
            "--description",
            "generated risk",
            "--feature-ids",
            "feat:rfc.9000.connection-migration",
        )
        self.assertEqual(create.returncode, 0, create.stderr)

        get_result = run_cli("risk", "get", str(repo), "--id", "rsk:cli.generated")
        self.assertEqual(get_result.returncode, 0, get_result.stderr)
        self.assertEqual(json.loads(get_result.stdout)["status"], "active")

        list_result = run_cli("risk", "list", str(repo))
        self.assertEqual(list_result.returncode, 0, list_result.stderr)
        list_payload = json.loads(list_result.stdout)
        self.assertIsInstance(list_payload, list)
        ids = {row["id"] for row in list_payload}
        self.assertIn("rsk:cli.generated", ids)

        update = run_cli(
            "risk",
            "update",
            str(repo),
            "--id",
            "rsk:cli.generated",
            "--description",
            "updated risk",
            "--release-blocking",
        )
        self.assertEqual(update.returncode, 0, update.stderr)

        link = run_cli("risk", "link", str(repo), "--id", "rsk:cli.generated", "--issue-ids", "iss:cli.risk-link")
        self.assertEqual(link.returncode, 0, link.stderr)

        unlink = run_cli("risk", "unlink", str(repo), "--id", "rsk:cli.generated", "--issue-ids", "iss:cli.risk-link")
        self.assertEqual(unlink.returncode, 0, unlink.stderr)

        relink = run_cli("risk", "link", str(repo), "--id", "rsk:cli.generated", "--issue-ids", "iss:cli.risk-link")
        self.assertEqual(relink.returncode, 0, relink.stderr)

        mitigate = run_cli("risk", "mitigate", str(repo), "--id", "rsk:cli.generated")
        self.assertEqual(mitigate.returncode, 0, mitigate.stderr)

        accept = run_cli("risk", "accept", str(repo), "--id", "rsk:cli.generated")
        self.assertEqual(accept.returncode, 0, accept.stderr)

        retire = run_cli("risk", "retire", str(repo), "--id", "rsk:cli.generated")
        self.assertEqual(retire.returncode, 0, retire.stderr)

        delete_risk = run_cli("risk", "delete", str(repo), "--id", "rsk:cli.generated")
        self.assertEqual(delete_risk.returncode, 0, delete_risk.stderr)

        delete_issue = run_cli("issue", "delete", str(repo), "--id", "iss:cli.risk-link")
        self.assertEqual(delete_issue.returncode, 0, delete_issue.stderr)
        self.assertTrue(json.loads(delete_issue.stdout)["passed"])


if __name__ == "__main__":
    unittest.main()
