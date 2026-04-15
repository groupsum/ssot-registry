from __future__ import annotations

import json
import unittest
from pathlib import Path

from tests.helpers import run_cli, workspace_tempdir


class CliSpecTests(unittest.TestCase):
    def test_spec_surface_and_immutability(self) -> None:
        with workspace_tempdir() as temp_dir:
            repo = Path(temp_dir) / "repo"
            repo.mkdir()
            init = run_cli("init", str(repo), "--repo-id", "repo:spec-cli", "--repo-name", "spec-cli", "--version", "1.0.0")
            self.assertEqual(init.returncode, 0, init.stderr)

            body = repo / "spec-body.md"
            body.write_text("Local spec body.\n", encoding="utf-8")
            create = run_cli(
                "spec",
                "create",
                str(repo),
                "--title",
                "Local operating spec",
                "--slug",
                "local-operating-spec",
                "--body-file",
                str(body),
                "--kind",
                "operational",
            )
            self.assertEqual(create.returncode, 0, create.stderr)
            payload = json.loads(create.stdout)
            self.assertEqual(payload["document"]["id"], "spc:1000")
            self.assertTrue((repo / ".ssot" / "specs" / "SPEC-1000-local-operating-spec.md").exists())

            update = run_cli("spec", "update", str(repo), "--id", "spc:1000", "--title", "Local operating spec updated")
            self.assertEqual(update.returncode, 0, update.stderr)
            self.assertEqual(json.loads(update.stdout)["document"]["title"], "Local operating spec updated")

            delete_ssot = run_cli("spec", "delete", str(repo), "--id", "spc:0001")
            self.assertEqual(delete_ssot.returncode, 1)
            self.assertIn("immutable", delete_ssot.stdout)

    def test_spec_create_inside_ssot_range_fails(self) -> None:
        with workspace_tempdir() as temp_dir:
            repo = Path(temp_dir) / "repo"
            repo.mkdir()
            init = run_cli("init", str(repo), "--repo-id", "repo:spec-range", "--repo-name", "spec-range", "--version", "1.0.0")
            self.assertEqual(init.returncode, 0, init.stderr)

            body = repo / "spec-body.md"
            body.write_text("Local spec body.\n", encoding="utf-8")
            create = run_cli(
                "spec",
                "create",
                str(repo),
                "--title",
                "Conflicting spec",
                "--slug",
                "conflicting-spec",
                "--body-file",
                str(body),
                "--number",
                "9",
            )
            self.assertEqual(create.returncode, 1)
            self.assertIn("non-assignable reservation", create.stdout)


if __name__ == "__main__":
    unittest.main()
