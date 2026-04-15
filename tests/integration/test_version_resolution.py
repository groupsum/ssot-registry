from __future__ import annotations

import json
import shutil
import subprocess
import sys
import unittest
from pathlib import Path

from tests.helpers import PROJECT_ROOT, workspace_tempdir


def _project_version() -> str:
    pyproject = PROJECT_ROOT / "pyproject.toml"
    in_project_section = False

    for line in pyproject.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith("[") and stripped.endswith("]"):
            in_project_section = stripped == "[project]"
            continue
        if in_project_section and stripped.startswith("version"):
            return stripped.split("=", 1)[1].strip().strip('"')

    raise RuntimeError("Unable to resolve version from pyproject.toml")


class VersionResolutionTests(unittest.TestCase):
    def test_direct_install_exposes_expected_dunder_version(self) -> None:
        expected = _project_version()

        with workspace_tempdir() as temp_dir:
            venv_dir = Path(temp_dir) / "venv"
            subprocess.run([sys.executable, "-m", "venv", str(venv_dir)], check=True)

            python_bin = venv_dir / ("Scripts" if sys.platform == "win32" else "bin") / "python"
            subprocess.run(
                [str(python_bin), "-m", "pip", "install", str(PROJECT_ROOT)],
                check=True,
                text=True,
                capture_output=True,
            )

            result = subprocess.run(
                [
                    str(python_bin),
                    "-c",
                    "import ssot_registry; import ssot_registry.version; "
                    "print(ssot_registry.__version__); "
                    "print(ssot_registry.version.__version__)",
                ],
                check=True,
                text=True,
                capture_output=True,
            )

        versions = result.stdout.strip().splitlines()
        self.assertEqual(versions, [expected, expected])

    def test_uv_run_with_project_path_resolves_expected_version(self) -> None:
        if shutil.which("uv") is None:
            self.skipTest("uv is not installed")

        expected = _project_version()
        result = subprocess.run(
            [
                "uv",
                "run",
                "--no-project",
                "--with",
                str(PROJECT_ROOT),
                "python",
                "-c",
                "import ssot_registry.version as v; print(v.__version__)",
            ],
            check=True,
            text=True,
            capture_output=True,
            cwd=str(PROJECT_ROOT.parent),
        )

        self.assertEqual(result.stdout.strip(), expected)

    def test_uvx_from_project_path_sets_tooling_version(self) -> None:
        if shutil.which("uvx") is None:
            self.skipTest("uvx is not installed")

        expected = _project_version()

        with workspace_tempdir() as temp_dir:
            repo = Path(temp_dir) / "uvx_repo"
            subprocess.run(
                [
                    "uvx",
                    "--from",
                    str(PROJECT_ROOT),
                    "ssot-registry",
                    "init",
                    str(repo),
                    "--repo-id",
                    "repo:uvx",
                    "--repo-name",
                    "uvx-repo",
                    "--version",
                    "1.0.0",
                ],
                check=True,
                text=True,
                capture_output=True,
                cwd=str(PROJECT_ROOT.parent),
            )

            registry = json.loads((repo / ".ssot" / "registry.json").read_text(encoding="utf-8"))

        self.assertEqual(registry["tooling"]["ssot_registry_version"], expected)


if __name__ == "__main__":
    unittest.main()
