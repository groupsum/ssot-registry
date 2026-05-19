from __future__ import annotations

import os
import subprocess
import sys
import unittest

from tests.helpers import (
    CLI_SRC_ROOT,
    CODEGEN_SRC_ROOT,
    CONFORMANCE_SRC_ROOT,
    CONTRACTS_SRC_ROOT,
    CORE_SRC_ROOT,
    PACK_CONTRACTS_SRC_ROOT,
    TUI_SRC_ROOT,
    VIEWS_SRC_ROOT,
)


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
            str(PACK_CONTRACTS_SRC_ROOT),
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
        output = result.stdout.strip().splitlines()
        self.assertEqual(output[0], "ssot-registry package versions:")
        package_names = {line.split(" ", 1)[0] for line in output[1:]}
        self.assertIn("ssot-cli", package_names)
        self.assertIn("ssot-core", package_names)
        self.assertIn("ssot-conformance", package_names)
        self.assertIn("ssot-contracts", package_names)
        self.assertIn("ssot-pack-contracts", package_names)


if __name__ == "__main__":
    unittest.main()
