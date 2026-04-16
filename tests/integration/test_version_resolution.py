from __future__ import annotations

import json
import os
import subprocess
import sys
import unittest
from pathlib import Path

from tests.helpers import PROJECT_ROOT, workspace_tempdir


REGISTRY_PROJECT_ROOT = PROJECT_ROOT / "pkgs" / "ssot-registry"
REGISTRY_SRC_ROOT = REGISTRY_PROJECT_ROOT / "src"
CONTRACTS_SRC_ROOT = PROJECT_ROOT / "pkgs" / "ssot-contracts" / "src"
VIEWS_SRC_ROOT = PROJECT_ROOT / "pkgs" / "ssot-views" / "src"
CODEGEN_SRC_ROOT = PROJECT_ROOT / "pkgs" / "ssot-codegen" / "src"
CLI_SRC_ROOT = PROJECT_ROOT / "pkgs" / "ssot-cli" / "src"
TUI_SRC_ROOT = PROJECT_ROOT / "pkgs" / "ssot-tui" / "src"
ROOT_SRC_ROOT = PROJECT_ROOT / "src"


def _project_version() -> str:
    pyproject = REGISTRY_PROJECT_ROOT / "pyproject.toml"
    in_project_section = False

    for line in pyproject.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith("[") and stripped.endswith("]"):
            in_project_section = stripped == "[project]"
            continue
        if in_project_section and stripped.startswith("version"):
            return stripped.split("=", 1)[1].strip().strip('"')

    raise RuntimeError("Unable to resolve version from registry package pyproject.toml")


def _package_pythonpath() -> str:
    return os.pathsep.join(
        [
            str(REGISTRY_SRC_ROOT),
            str(CODEGEN_SRC_ROOT),
            str(VIEWS_SRC_ROOT),
            str(CONTRACTS_SRC_ROOT),
            str(CLI_SRC_ROOT),
            str(TUI_SRC_ROOT),
            str(ROOT_SRC_ROOT),
        ]
    )


class VersionResolutionTests(unittest.TestCase):
    def test_registry_package_pyproject_version_matches_runtime_version(self) -> None:
        expected = _project_version()
        env = dict(os.environ, PYTHONPATH=_package_pythonpath())
        result = subprocess.run(
            [
                sys.executable,
                "-c",
                "import ssot_registry; import ssot_registry.version; "
                "print(ssot_registry.__version__); print(ssot_registry.version.__version__)",
            ],
            check=True,
            text=True,
            capture_output=True,
            env=env,
        )

        versions = result.stdout.strip().splitlines()
        self.assertEqual(versions, [expected, expected])

    def test_subprocess_import_uses_registry_package_path(self) -> None:
        expected = _project_version()
        env = dict(os.environ, PYTHONPATH=_package_pythonpath())
        result = subprocess.run(
            [sys.executable, "-c", "import ssot_registry.version as v; print(v.__version__)"],
            check=True,
            text=True,
            capture_output=True,
            cwd=str(PROJECT_ROOT),
            env=env,
        )

        self.assertEqual(result.stdout.strip(), expected)

    def test_python_m_ssot_registry_sets_tooling_version_from_registry_package(self) -> None:
        expected = _project_version()
        env = dict(os.environ, PYTHONPATH=_package_pythonpath())

        with workspace_tempdir() as temp_dir:
            repo = Path(temp_dir) / "repo"
            subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "ssot_registry",
                    "init",
                    str(repo),
                    "--repo-id",
                    "repo:package-version",
                    "--repo-name",
                    "package-version-repo",
                    "--version",
                    "1.0.0",
                ],
                check=True,
                text=True,
                capture_output=True,
                cwd=str(PROJECT_ROOT),
                env=env,
            )
            registry = json.loads((repo / ".ssot" / "registry.json").read_text(encoding="utf-8"))

        self.assertEqual(registry["tooling"]["ssot_registry_version"], expected)


if __name__ == "__main__":
    unittest.main()
