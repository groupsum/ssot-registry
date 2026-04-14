from __future__ import annotations

import json
import unittest
from pathlib import Path

from tests.helpers import run_cli, temp_repo_from_fixture


class CliReleaseSurfaceTests(unittest.TestCase):
    def test_release_surface(self) -> None:
        temp_dir = temp_repo_from_fixture("repo_valid")
        self.addCleanup(temp_dir.cleanup)
        repo = Path(temp_dir.name) / "repo"

        create_boundary = run_cli(
            "boundary",
            "create",
            str(repo),
            "--id",
            "bnd:cli.release",
            "--title",
            "CLI release boundary",
        )
        self.assertEqual(create_boundary.returncode, 0, create_boundary.stderr)

        create_release = run_cli(
            "release",
            "create",
            str(repo),
            "--id",
            "rel:9.9.9",
            "--version",
            "9.9.9",
            "--boundary-id",
            "bnd:cli.release",
        )
        self.assertEqual(create_release.returncode, 0, create_release.stderr)

        get_result = run_cli("release", "get", str(repo), "--id", "rel:9.9.9")
        self.assertEqual(get_result.returncode, 0, get_result.stderr)
        self.assertEqual(json.loads(get_result.stdout)["entity"]["version"], "9.9.9")

        list_result = run_cli("release", "list", str(repo))
        self.assertEqual(list_result.returncode, 0, list_result.stderr)
        ids = {row["id"] for row in json.loads(list_result.stdout)["entities"]}
        self.assertIn("rel:9.9.9", ids)

        update = run_cli(
            "release",
            "update",
            str(repo),
            "--id",
            "rel:9.9.9",
            "--status",
            "candidate",
        )
        self.assertEqual(update.returncode, 0, update.stderr)

        add_claim = run_cli(
            "release",
            "add-claim",
            str(repo),
            "--id",
            "rel:9.9.9",
            "--claim-ids",
            "clm:rfc.9000.connection-migration.t3",
        )
        self.assertEqual(add_claim.returncode, 0, add_claim.stderr)

        add_evidence = run_cli(
            "release",
            "add-evidence",
            str(repo),
            "--id",
            "rel:9.9.9",
            "--evidence-ids",
            "evd:t3.rfc.9000.connection-migration.bundle",
        )
        self.assertEqual(add_evidence.returncode, 0, add_evidence.stderr)

        remove_claim = run_cli(
            "release",
            "remove-claim",
            str(repo),
            "--id",
            "rel:9.9.9",
            "--claim-ids",
            "clm:rfc.9000.connection-migration.t3",
        )
        self.assertEqual(remove_claim.returncode, 0, remove_claim.stderr)

        remove_evidence = run_cli(
            "release",
            "remove-evidence",
            str(repo),
            "--id",
            "rel:9.9.9",
            "--evidence-ids",
            "evd:t3.rfc.9000.connection-migration.bundle",
        )
        self.assertEqual(remove_evidence.returncode, 0, remove_evidence.stderr)

        revoke = run_cli(
            "release",
            "revoke",
            str(repo),
            "--release-id",
            "rel:9.9.9",
            "--reason",
            "test revocation",
        )
        self.assertEqual(revoke.returncode, 0, revoke.stderr)
        self.assertTrue(json.loads(revoke.stdout)["passed"])

        delete = run_cli("release", "delete", str(repo), "--id", "rel:9.9.9")
        self.assertEqual(delete.returncode, 0, delete.stderr)
        self.assertTrue(json.loads(delete.stdout)["passed"])

        delete_boundary = run_cli("boundary", "delete", str(repo), "--id", "bnd:cli.release")
        self.assertEqual(delete_boundary.returncode, 0, delete_boundary.stderr)


if __name__ == "__main__":
    unittest.main()
