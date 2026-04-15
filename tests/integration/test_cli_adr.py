from __future__ import annotations

import json
import unittest
from pathlib import Path

from tests.helpers import run_cli, workspace_tempdir


class CliAdrTests(unittest.TestCase):
    def test_adr_surface_and_immutability(self) -> None:
        with workspace_tempdir() as temp_dir:
            repo = Path(temp_dir) / "repo"
            repo.mkdir()
            init = run_cli("init", str(repo), "--repo-id", "repo:adr-cli", "--repo-name", "adr-cli", "--version", "1.0.0")
            self.assertEqual(init.returncode, 0, init.stderr)

            body = repo / "adr-body.md"
            body.write_text("Local ADR body.\n", encoding="utf-8")
            create = run_cli(
                "adr",
                "create",
                str(repo),
                "--title",
                "Local decision",
                "--slug",
                "local-decision",
                "--body-file",
                str(body),
            )
            self.assertEqual(create.returncode, 0, create.stderr)
            payload = json.loads(create.stdout)
            self.assertEqual(payload["document"]["id"], "adr:1000")
            self.assertTrue((repo / ".ssot" / "adr" / "ADR-1000-local-decision.md").exists())

            get_result = run_cli("adr", "get", str(repo), "--id", "adr:1000")
            self.assertEqual(get_result.returncode, 0, get_result.stderr)
            self.assertEqual(json.loads(get_result.stdout)["document"]["title"], "Local decision")

            body.write_text("Updated ADR body.\n", encoding="utf-8")
            update = run_cli("adr", "update", str(repo), "--id", "adr:1000", "--title", "Local decision updated", "--body-file", str(body))
            self.assertEqual(update.returncode, 0, update.stderr)
            self.assertEqual(json.loads(update.stdout)["document"]["title"], "Local decision updated")

            delete_ssot = run_cli("adr", "delete", str(repo), "--id", "adr:0001")
            self.assertEqual(delete_ssot.returncode, 1)
            self.assertIn("immutable", delete_ssot.stdout)

            delete_local = run_cli("adr", "delete", str(repo), "--id", "adr:1000")
            self.assertEqual(delete_local.returncode, 0, delete_local.stderr)
            self.assertFalse((repo / ".ssot" / "adr" / "ADR-1000-local-decision.md").exists())

    def test_adr_create_inside_ssot_range_fails(self) -> None:
        with workspace_tempdir() as temp_dir:
            repo = Path(temp_dir) / "repo"
            repo.mkdir()
            init = run_cli("init", str(repo), "--repo-id", "repo:adr-range", "--repo-name", "adr-range", "--version", "1.0.0")
            self.assertEqual(init.returncode, 0, init.stderr)

            body = repo / "adr-body.md"
            body.write_text("Local ADR body.\n", encoding="utf-8")
            create = run_cli(
                "adr",
                "create",
                str(repo),
                "--title",
                "Conflicting decision",
                "--slug",
                "conflicting-decision",
                "--body-file",
                str(body),
                "--number",
                "7",
            )
            self.assertEqual(create.returncode, 1)
            self.assertIn("non-assignable reservation", create.stdout)


if __name__ == "__main__":
    unittest.main()
