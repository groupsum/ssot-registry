from __future__ import annotations

import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts" / "test_all_supported_pythons.sh"


class TestMatrixScriptTests(unittest.TestCase):
    def test_script_covers_expected_python_versions(self) -> None:
        script = SCRIPT_PATH.read_text(encoding="utf-8")
        self.assertIn('SUPPORTED_PYTHON_VERSIONS=("3.10" "3.11" "3.12" "3.13")', script)

    def test_script_uses_unittest_commands_not_pytest(self) -> None:
        script = SCRIPT_PATH.read_text(encoding="utf-8")
        self.assertIn("python -m unittest", script)
        self.assertNotIn(" pytest", script)


if __name__ == "__main__":
    unittest.main()
