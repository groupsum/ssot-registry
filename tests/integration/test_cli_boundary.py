from __future__ import annotations

import json
import unittest
from pathlib import Path

from tests.helpers import run_cli, temp_repo_from_fixture


class CliBoundarySurfaceTests(unittest.TestCase):
    def test_boundary_surface(self) -> None:
        temp_dir = temp_repo_from_fixture("repo_valid")
        self.addCleanup(temp_dir.cleanup)
        repo = Path(temp_dir.name) / "repo"

        create = run_cli(
            "boundary",
            "create",
            str(repo),
            "--id",
            "bnd:cli.generated",
            "--title",
            "CLI generated boundary",
        )
        self.assertEqual(create.returncode, 0, create.stderr)

        get_result = run_cli("boundary", "get", str(repo), "--id", "bnd:cli.generated")
        self.assertEqual(get_result.returncode, 0, get_result.stderr)
        self.assertEqual(json.loads(get_result.stdout)["id"], "bnd:cli.generated")

        list_result = run_cli("boundary", "list", str(repo))
        self.assertEqual(list_result.returncode, 0, list_result.stderr)
        list_payload = json.loads(list_result.stdout)
        self.assertIsInstance(list_payload, list)
        ids = {row["id"] for row in list_payload}
        self.assertIn("bnd:cli.generated", ids)

        update = run_cli(
            "boundary",
            "update",
            str(repo),
            "--id",
            "bnd:cli.generated",
            "--status",
            "active",
        )
        self.assertEqual(update.returncode, 0, update.stderr)

        add_feature = run_cli(
            "boundary",
            "add-feature",
            str(repo),
            "--id",
            "bnd:cli.generated",
            "--feature-ids",
            "feat:rfc.9000.connection-migration",
        )
        self.assertEqual(add_feature.returncode, 0, add_feature.stderr)

        remove_feature = run_cli(
            "boundary",
            "remove-feature",
            str(repo),
            "--id",
            "bnd:cli.generated",
            "--feature-ids",
            "feat:rfc.9000.connection-migration",
        )
        self.assertEqual(remove_feature.returncode, 0, remove_feature.stderr)

        freeze = run_cli("boundary", "freeze", str(repo), "--boundary-id", "bnd:cli.generated")
        self.assertEqual(freeze.returncode, 0, freeze.stderr)
        freeze_payload = json.loads(freeze.stdout)
        self.assertTrue(Path(freeze_payload["output_path"]).exists())

        delete = run_cli("boundary", "delete", str(repo), "--id", "bnd:cli.generated")
        self.assertEqual(delete.returncode, 0, delete.stderr)
        self.assertTrue(json.loads(delete.stdout)["passed"])


if __name__ == "__main__":
    unittest.main()
