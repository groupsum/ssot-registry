from __future__ import annotations

import json
import unittest
from pathlib import Path

from tests.helpers import run_cli, workspace_tempdir


class CliInitTests(unittest.TestCase):
    def test_init_and_validate(self) -> None:
        with workspace_tempdir() as temp_dir:
            repo = Path(temp_dir) / "new-repo"
            repo.mkdir()
            result = run_cli("init", str(repo), "--repo-id", "repo:new-repo", "--repo-name", "new-repo", "--version", "0.1.0")
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertTrue(payload["passed"], payload)
            registry = json.loads((repo / ".ssot" / "registry.json").read_text(encoding="utf-8"))
            self.assertTrue(registry["adrs"])
            self.assertTrue(registry["specs"])
            self.assertEqual({"ssot-origin"}, {row["origin"] for row in registry["adrs"]})
            self.assertEqual({"ssot-origin"}, {row["origin"] for row in registry["specs"]})
            first_adr = repo / registry["adrs"][0]["path"]
            self.assertTrue(first_adr.read_text(encoding="utf-8").lstrip().startswith("{"))

            validate = run_cli("validate", str(repo))
            self.assertEqual(validate.returncode, 0, validate.stderr)
            validate_payload = json.loads(validate.stdout)
            self.assertTrue(validate_payload["passed"], validate_payload)

    def test_init_force_overwrites_existing_registry(self) -> None:
        with workspace_tempdir() as temp_dir:
            repo = Path(temp_dir) / "new-repo"
            repo.mkdir()

            first_init = run_cli("init", str(repo), "--repo-id", "repo:first", "--repo-name", "first", "--version", "0.1.0")
            self.assertEqual(first_init.returncode, 0, first_init.stderr)

            without_force = run_cli("init", str(repo), "--repo-id", "repo:second", "--repo-name", "second", "--version", "0.2.0")
            self.assertEqual(without_force.returncode, 1)
            without_force_payload = json.loads(without_force.stdout)
            self.assertIn("Registry already exists", without_force_payload["error"])

            with_force = run_cli(
                "init",
                str(repo),
                "--repo-id",
                "repo:second",
                "--repo-name",
                "second",
                "--version",
                "0.2.0",
                "--force",
            )
            self.assertEqual(with_force.returncode, 0, with_force.stderr)

            registry_path = repo / ".ssot" / "registry.json"
            registry = json.loads(registry_path.read_text(encoding="utf-8"))
            self.assertEqual(registry["repo"]["id"], "repo:second")
            self.assertEqual(registry["repo"]["name"], "second")
            self.assertEqual(registry["repo"]["version"], "0.2.0")


if __name__ == "__main__":
    unittest.main()
