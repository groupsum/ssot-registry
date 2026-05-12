from __future__ import annotations

import os
import subprocess
import sys
import unittest

from tests.helpers import CLI_SRC_ROOT, CODEGEN_SRC_ROOT, CONFORMANCE_SRC_ROOT, CONTRACTS_SRC_ROOT, CORE_SRC_ROOT, TUI_SRC_ROOT, VIEWS_SRC_ROOT


class CliRootVersionTests(unittest.TestCase):
    def test_root_version_flag_reports_cli_package_version_without_subcommand(self) -> None:
        env = os.environ.copy()
        pythonpath_parts = [
            str(CORE_SRC_ROOT),
            str(CODEGEN_SRC_ROOT),
            str(VIEWS_SRC_ROOT),
            str(CONTRACTS_SRC_ROOT),
            str(CLI_SRC_ROOT),
            str(TUI_SRC_ROOT),
            str(CONFORMANCE_SRC_ROOT),
        ]
        existing = env.get("PYTHONPATH")
        if existing:
            pythonpath_parts.append(existing)
        env["PYTHONPATH"] = os.pathsep.join(pythonpath_parts)

        result = subprocess.run(
            [sys.executable, "-m", "ssot_registry", "--version"],
            text=True,
            capture_output=True,
            check=False,
            env=env,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertRegex(result.stdout.strip(), r"^ssot-registry \d+\.\d+\.\d+(?:[.-][A-Za-z0-9]+)*$")


if __name__ == "__main__":
    unittest.main()
