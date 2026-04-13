from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from tests.helpers import run_cli


class CliInitTests(unittest.TestCase):
    def test_init_and_validate(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = Path(temp_dir) / "new-repo"
            repo.mkdir()
            result = run_cli("init", str(repo), "--repo-id", "repo:new-repo", "--repo-name", "new-repo", "--version", "0.1.0")
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertTrue(payload["passed"], payload)

            validate = run_cli("validate", str(repo))
            self.assertEqual(validate.returncode, 0, validate.stderr)
            validate_payload = json.loads(validate.stdout)
            self.assertTrue(validate_payload["passed"], validate_payload)


if __name__ == "__main__":
    unittest.main()
