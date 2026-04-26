from __future__ import annotations

import json
import unittest
from pathlib import Path

from tests.helpers import run_cli, temp_repo_from_fixture


class CliTestSurfaceTests(unittest.TestCase):
    def test_test_surface(self) -> None:
        temp_dir = temp_repo_from_fixture("repo_valid")
        self.addCleanup(temp_dir.cleanup)
        repo = Path(temp_dir.name) / "repo"
        generated_path = repo / "tests" / "test_cli_generated_surface.py"
        generated_path.write_text("def test_generated_surface():\n    assert True\n", encoding="utf-8")

        create = run_cli(
            "test",
            "create",
            str(repo),
            "--id",
            "tst:pytest.cli.generated-surface",
            "--title",
            "CLI generated test",
            "--status",
            "passing",
            "--kind",
            "pytest",
            "--test-path",
            "tests/test_cli_generated_surface.py",
            "--feature-ids",
            "feat:rfc.9000.connection-migration",
            "--claim-ids",
            "clm:rfc.9000.connection-migration.t3",
            "--evidence-ids",
            "evd:t3.rfc.9000.connection-migration.bundle",
            "--execution-json",
            json.dumps(
                {
                    "mode": "command",
                    "argv": ["python", "-m", "pytest", "tests/test_cli_generated_surface.py", "-q"],
                    "cwd": ".",
                    "env": {},
                    "timeout_seconds": 600,
                    "success": {"type": "exit_code", "expected": 0},
                }
            ),
        )
        self.assertEqual(create.returncode, 0, create.stderr)

        get_result = run_cli("test", "get", str(repo), "--id", "tst:pytest.cli.generated-surface")
        self.assertEqual(get_result.returncode, 0, get_result.stderr)
        get_payload = json.loads(get_result.stdout)
        self.assertEqual(get_payload["kind"], "pytest")
        self.assertEqual(get_payload["execution"]["mode"], "command")

        list_result = run_cli("test", "list", str(repo))
        self.assertEqual(list_result.returncode, 0, list_result.stderr)
        list_payload = json.loads(list_result.stdout)
        self.assertIsInstance(list_payload, list)
        ids = {row["id"] for row in list_payload}
        self.assertIn("tst:pytest.cli.generated-surface", ids)

        update = run_cli(
            "test",
            "update",
            str(repo),
            "--id",
            "tst:pytest.cli.generated-surface",
            "--title",
            "CLI generated test updated",
        )
        self.assertEqual(update.returncode, 0, update.stderr)

        unlink = run_cli(
            "test",
            "unlink",
            str(repo),
            "--id",
            "tst:pytest.cli.generated-surface",
            "--feature-ids",
            "feat:rfc.9000.connection-migration",
        )
        self.assertEqual(unlink.returncode, 0, unlink.stderr)

        relink = run_cli(
            "test",
            "link",
            str(repo),
            "--id",
            "tst:pytest.cli.generated-surface",
            "--feature-ids",
            "feat:rfc.9000.connection-migration",
        )
        self.assertEqual(relink.returncode, 0, relink.stderr)

        delete = run_cli("test", "delete", str(repo), "--id", "tst:pytest.cli.generated-surface")
        self.assertEqual(delete.returncode, 0, delete.stderr)
        self.assertTrue(json.loads(delete.stdout)["passed"])


if __name__ == "__main__":
    unittest.main()
