from __future__ import annotations

import json
import unittest
from pathlib import Path

from tests.helpers import run_cli, temp_repo_from_fixture


class CliProfileSurfaceTests(unittest.TestCase):
    def test_profile_crud_and_evaluate_surface(self) -> None:
        temp_dir = temp_repo_from_fixture("repo_valid")
        self.addCleanup(temp_dir.cleanup)
        repo = Path(temp_dir.name) / "repo"

        create = run_cli(
            "profile",
            "create",
            str(repo),
            "--id",
            "prf:http3-core",
            "--title",
            "HTTP/3 Core",
            "--description",
            "Core bundle",
            "--status",
            "active",
            "--kind",
            "capability",
            "--claim-tier",
            "T3",
            "--feature-ids",
            "feat:rfc.9000.connection-migration",
        )
        self.assertEqual(create.returncode, 0, create.stderr)

        get_result = run_cli("profile", "get", str(repo), "--id", "prf:http3-core")
        self.assertEqual(get_result.returncode, 0, get_result.stderr)
        self.assertEqual(json.loads(get_result.stdout)["entity"]["id"], "prf:http3-core")

        list_result = run_cli("profile", "list", str(repo))
        self.assertEqual(list_result.returncode, 0, list_result.stderr)
        ids = {row["id"] for row in json.loads(list_result.stdout)["entities"]}
        self.assertIn("prf:http3-core", ids)

        update = run_cli("profile", "update", str(repo), "--id", "prf:http3-core", "--title", "HTTP/3 core updated")
        self.assertEqual(update.returncode, 0, update.stderr)

        link = run_cli("profile", "link", str(repo), "--id", "prf:http3-core", "--profile-ids", "prf:http3-core")
        self.assertNotEqual(link.returncode, 0, "self-cycle link should fail validation")

        evaluate = run_cli("profile", "evaluate", str(repo), "--profile-id", "prf:http3-core")
        self.assertEqual(evaluate.returncode, 0, evaluate.stderr)
        self.assertTrue(json.loads(evaluate.stdout)["profile"]["passed"])

        delete = run_cli("profile", "delete", str(repo), "--id", "prf:http3-core")
        self.assertEqual(delete.returncode, 0, delete.stderr)

    def test_boundary_add_profile_surface(self) -> None:
        temp_dir = temp_repo_from_fixture("repo_valid")
        self.addCleanup(temp_dir.cleanup)
        repo = Path(temp_dir.name) / "repo"

        run_cli(
            "profile",
            "create",
            str(repo),
            "--id",
            "prf:http3-core",
            "--title",
            "HTTP/3 Core",
            "--description",
            "Core bundle",
            "--status",
            "active",
            "--kind",
            "capability",
            "--claim-tier",
            "T3",
            "--feature-ids",
            "feat:rfc.9000.connection-migration",
        )
        create_boundary = run_cli("boundary", "create", str(repo), "--id", "bnd:cli.profiles", "--title", "Boundary with profile")
        self.assertEqual(create_boundary.returncode, 0, create_boundary.stderr)

        add_profile = run_cli(
            "boundary",
            "add-profile",
            str(repo),
            "--id",
            "bnd:cli.profiles",
            "--profile-ids",
            "prf:http3-core",
        )
        self.assertEqual(add_profile.returncode, 0, add_profile.stderr)

        remove_profile = run_cli(
            "boundary",
            "remove-profile",
            str(repo),
            "--id",
            "bnd:cli.profiles",
            "--profile-ids",
            "prf:http3-core",
        )
        self.assertEqual(remove_profile.returncode, 0, remove_profile.stderr)

        freeze = run_cli("boundary", "freeze", str(repo), "--boundary-id", "bnd:cli.profiles")
        self.assertEqual(freeze.returncode, 0, freeze.stderr)


if __name__ == "__main__":
    unittest.main()
