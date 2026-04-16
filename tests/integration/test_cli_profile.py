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
            "prf:cli.generated",
            "--title",
            "CLI profile",
            "--description",
            "Generated profile",
            "--status",
            "active",
            "--kind",
            "capability",
            "--feature-ids",
            "feat:rfc.9000.connection-migration",
            "--claim-tier",
            "T3",
        )
        self.assertEqual(create.returncode, 0, create.stderr)

        get_result = run_cli("profile", "get", str(repo), "--id", "prf:cli.generated")
        self.assertEqual(get_result.returncode, 0, get_result.stderr)
        self.assertEqual(json.loads(get_result.stdout)["entity"]["id"], "prf:cli.generated")

        list_result = run_cli("profile", "list", str(repo))
        self.assertEqual(list_result.returncode, 0, list_result.stderr)
        ids = {row["id"] for row in json.loads(list_result.stdout)["entities"]}
        self.assertIn("prf:cli.generated", ids)

        update = run_cli("profile", "update", str(repo), "--id", "prf:cli.generated", "--kind", "deployment")
        self.assertEqual(update.returncode, 0, update.stderr)

        link = run_cli(
            "profile",
            "link",
            str(repo),
            "--id",
            "prf:cli.generated",
            "--feature-ids",
            "feat:rfc.9000.connection-migration",
        )
        self.assertEqual(link.returncode, 0, link.stderr)

        unlink = run_cli(
            "profile",
            "unlink",
            str(repo),
            "--id",
            "prf:cli.generated",
            "--feature-ids",
            "feat:rfc.9000.connection-migration",
        )
        self.assertEqual(unlink.returncode, 0, unlink.stderr)

        evaluate = run_cli("profile", "evaluate", str(repo), "--profile-id", "prf:cli.generated")
        self.assertEqual(evaluate.returncode, 0, evaluate.stderr)

        delete = run_cli("profile", "delete", str(repo), "--id", "prf:cli.generated")
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
            "prf:scope",
            "--title",
            "Scope",
            "--description",
            "Boundary scope profile",
            "--status",
            "active",
            "--kind",
            "capability",
            "--feature-ids",
            "feat:rfc.9000.connection-migration",
            "--claim-tier",
            "T3",
        )

        create_boundary = run_cli(
            "boundary",
            "create",
            str(repo),
            "--id",
            "bnd:cli.profile",
            "--title",
            "Boundary with profile",
        )
        self.assertEqual(create_boundary.returncode, 0, create_boundary.stderr)

        add_profile = run_cli(
            "boundary",
            "add-profile",
            str(repo),
            "--id",
            "bnd:cli.profile",
            "--profile-ids",
            "prf:scope",
        )
        self.assertEqual(add_profile.returncode, 0, add_profile.stderr)

        remove_profile = run_cli(
            "boundary",
            "remove-profile",
            str(repo),
            "--id",
            "bnd:cli.profile",
            "--profile-ids",
            "prf:scope",
        )
        self.assertEqual(remove_profile.returncode, 0, remove_profile.stderr)

        freeze = run_cli("boundary", "freeze", str(repo), "--boundary-id", "bnd:cli.profile")
        self.assertEqual(freeze.returncode, 0, freeze.stderr)


if __name__ == "__main__":
    unittest.main()
