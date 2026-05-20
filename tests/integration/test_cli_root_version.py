from __future__ import annotations

import os
import subprocess
import sys
import unittest
from pathlib import Path

from tests.helpers import (
    CLI_SRC_ROOT,
    CODEGEN_SRC_ROOT,
    CONFORMANCE_SRC_ROOT,
    CONTRACTS_SRC_ROOT,
    CORE_SRC_ROOT,
    MCP_SRC_ROOT,
    PACK_CONTRACTS_SRC_ROOT,
    TUI_SRC_ROOT,
    VIEWS_SRC_ROOT,
)

EXPECTED_SOURCE_TREE_PACKAGES = {
    "ssot-cli",
    "ssot-codegen",
    "ssot-conformance",
    "ssot-contracts",
    "ssot-core",
    "ssot-mcp",
    "ssot-pack-contracts",
    "ssot-registry",
    "ssot-tui",
    "ssot-views",
}


def _package_pythonpath() -> str:
    pythonpath_parts = [
        str(CORE_SRC_ROOT),
        str(CODEGEN_SRC_ROOT),
        str(VIEWS_SRC_ROOT),
        str(CONTRACTS_SRC_ROOT),
        str(CLI_SRC_ROOT),
        str(MCP_SRC_ROOT),
        str(TUI_SRC_ROOT),
        str(CONFORMANCE_SRC_ROOT),
        str(PACK_CONTRACTS_SRC_ROOT),
    ]
    existing = os.environ.get("PYTHONPATH")
    if existing:
        pythonpath_parts.append(existing)
    return os.pathsep.join(pythonpath_parts)


def _project_version(pyproject_path: Path) -> str:
    in_project_section = False
    for line in pyproject_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith("[") and stripped.endswith("]"):
            in_project_section = stripped == "[project]"
            continue
        if in_project_section and stripped.startswith("version"):
            return stripped.split("=", 1)[1].strip().strip('"')
    raise RuntimeError(f"Unable to resolve version from {pyproject_path}")


def _expected_source_tree_versions() -> dict[str, str]:
    packages_root = CLI_SRC_ROOT.parents[1]
    return {
        package_dir.name: _project_version(package_dir / "pyproject.toml")
        for package_dir in packages_root.glob("ssot-*")
        if (package_dir / "pyproject.toml").exists()
    }


class CliRootVersionTests(unittest.TestCase):
    def test_python_module_root_version_reports_package_versions_without_subcommand(self) -> None:
        env = dict(os.environ, PYTHONPATH=_package_pythonpath())

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
        package_versions = dict(line.split(" ", 1) for line in output[1:])
        self.assertEqual(set(package_versions), EXPECTED_SOURCE_TREE_PACKAGES)
        self.assertEqual(package_versions, _expected_source_tree_versions())

    def test_root_version_flag_reports_each_console_alias_without_subcommand(self) -> None:
        env = dict(os.environ, PYTHONPATH=_package_pythonpath())
        runner = (
            "import sys; "
            "from ssot_cli.main import main; "
            "sys.argv[0] = sys.argv[1]; "
            "raise SystemExit(main(['--version']))"
        )

        for alias in ("ssot", "ssot-cli", "ssot-registry"):
            with self.subTest(alias=alias):
                result = subprocess.run(
                    [sys.executable, "-c", runner, alias],
                    text=True,
                    capture_output=True,
                    check=False,
                    env=env,
                )

                self.assertEqual(result.returncode, 0, result.stderr)
                output = result.stdout.strip().splitlines()
                self.assertEqual(output[0], f"{alias} package versions:")
                package_versions = dict(line.split(" ", 1) for line in output[1:])
                self.assertEqual(set(package_versions), EXPECTED_SOURCE_TREE_PACKAGES)
                self.assertEqual(package_versions, _expected_source_tree_versions())


if __name__ == "__main__":
    unittest.main()
