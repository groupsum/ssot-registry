from __future__ import annotations

import unittest
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover
    import tomli as tomllib


REPO_ROOT = Path(__file__).resolve().parents[2]


class ConformancePackageLayoutTests(unittest.TestCase):
    def test_workspace_includes_conformance_package(self) -> None:
        root = tomllib.loads((REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
        self.assertIn("pkgs/ssot-conformance", root["tool"]["uv"]["workspace"]["members"])
        self.assertIn("ssot-conformance", root["tool"]["uv"]["sources"])

    def test_conformance_package_declares_pytest_plugin_entrypoint(self) -> None:
        data = tomllib.loads((REPO_ROOT / "pkgs" / "ssot-conformance" / "pyproject.toml").read_text(encoding="utf-8"))
        self.assertEqual(data["project"]["readme"], "README.md")
        self.assertEqual(data["project"]["requires-python"], ">=3.10,<3.14")
        self.assertEqual(data["project"]["entry-points"]["pytest11"]["ssot-conformance"], "ssot_conformance.plugin")

    def test_conformance_package_files_exist(self) -> None:
        expected = [
            REPO_ROOT / "pkgs" / "ssot-conformance" / "README.md",
            REPO_ROOT / "pkgs" / "ssot-conformance" / "src" / "ssot_conformance" / "__init__.py",
            REPO_ROOT / "pkgs" / "ssot-conformance" / "src" / "ssot_conformance" / "catalog.py",
            REPO_ROOT / "pkgs" / "ssot-conformance" / "src" / "ssot_conformance" / "plugin.py",
        ]
        for path in expected:
            self.assertTrue(path.exists(), path.as_posix())


if __name__ == "__main__":
    unittest.main()
