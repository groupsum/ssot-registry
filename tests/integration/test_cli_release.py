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
        create_extra_boundary = run_cli(
            "boundary",
            "create",
            str(repo),
            "--id",
            "bnd:cli.release.extra",
            "--title",
            "CLI release extra boundary",
        )
        self.assertEqual(create_extra_boundary.returncode, 0, create_extra_boundary.stderr)

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
            "--boundary-ids",
            "bnd:cli.release.extra",
        )
        self.assertEqual(create_release.returncode, 0, create_release.stderr)

        get_result = run_cli("release", "get", str(repo), "--id", "rel:9.9.9")
        self.assertEqual(get_result.returncode, 0, get_result.stderr)
        release_payload = json.loads(get_result.stdout)
        self.assertEqual(release_payload["version"], "9.9.9")
        self.assertEqual(release_payload["boundary_id"], "bnd:cli.release")
        self.assertEqual(release_payload["boundary_ids"], ["bnd:cli.release", "bnd:cli.release.extra"])

        list_result = run_cli("release", "list", str(repo))
        self.assertEqual(list_result.returncode, 0, list_result.stderr)
        list_payload = json.loads(list_result.stdout)
        self.assertIsInstance(list_payload, list)
        ids = {row["id"] for row in list_payload}
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

        add_boundary = run_cli(
            "release",
            "add-boundary",
            str(repo),
            "--id",
            "rel:9.9.9",
            "--boundary-ids",
            "bnd:2026q2.core",
        )
        self.assertEqual(add_boundary.returncode, 0, add_boundary.stderr)

        remove_boundary = run_cli(
            "release",
            "remove-boundary",
            str(repo),
            "--id",
            "rel:9.9.9",
            "--boundary-ids",
            "bnd:2026q2.core",
        )
        self.assertEqual(remove_boundary.returncode, 0, remove_boundary.stderr)

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
        delete_extra_boundary = run_cli("boundary", "delete", str(repo), "--id", "bnd:cli.release.extra")
        self.assertEqual(delete_extra_boundary.returncode, 0, delete_extra_boundary.stderr)


if __name__ == "__main__":
    unittest.main()
