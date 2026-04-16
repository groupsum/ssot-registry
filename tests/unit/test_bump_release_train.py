from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import patch

from tests.helpers import PROJECT_ROOT, workspace_tempdir

sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

import bump_release_train
from release_metadata import PackageInfo


def _write_pyproject(path: Path, name: str, version: str, dependencies: list[str]) -> None:
    deps_block = ""
    if dependencies:
        deps_lines = ",\n".join(f'  "{dependency}"' for dependency in dependencies)
        deps_block = f"dependencies = [\n{deps_lines},\n]\n"
    path.write_text(
        "\n".join(
            [
                "[project]",
                f'name = "{name}"',
                f'version = "{version}"',
                deps_block.rstrip(),
                "",
            ]
        ),
        encoding="utf-8",
    )


class BumpReleaseTrainTests(unittest.TestCase):
    def test_all_train_bump_updates_dependency_specs(self) -> None:
        with workspace_tempdir() as temp_dir:
            root = Path(temp_dir)
            packages = {
                "ssot-contracts": ("0.2.3", []),
                "ssot-views": ("0.2.3", ["ssot-contracts==0.2.3"]),
                "ssot-codegen": ("0.2.3", ["ssot-contracts==0.2.3", "ssot-views==0.2.3"]),
                "ssot-registry": ("0.2.3", ["ssot-contracts==0.2.3", "ssot-views==0.2.3"]),
                "ssot-cli": ("0.1.0", ["ssot-contracts>=0.2.3,<0.3.0", "ssot-registry>=0.2.3,<0.3.0"]),
                "ssot-tui": ("0.1.0", ["ssot-contracts>=0.2.3,<0.3.0", "ssot-registry>=0.2.3,<0.3.0"]),
            }
            package_infos: dict[str, PackageInfo] = {}
            for package_name, (version, dependencies) in packages.items():
                project_path = root / package_name
                project_path.mkdir(parents=True, exist_ok=True)
                _write_pyproject(project_path / "pyproject.toml", package_name, version, dependencies)
                package_infos[package_name] = PackageInfo(
                    name=package_name,
                    project_path=str(project_path),
                    workflow=f"publish-{package_name}.yml",
                    pypi_url=f"https://example.test/{package_name}",
                )

            with patch.object(bump_release_train, "PACKAGE_INFOS", package_infos):
                changed = bump_release_train.bump_train("all", "patch", None)

            changed_paths = {path.as_posix() for path in changed}
            self.assertEqual(len(changed_paths), 6)

            views_text = (root / "ssot-views" / "pyproject.toml").read_text(encoding="utf-8")
            codegen_text = (root / "ssot-codegen" / "pyproject.toml").read_text(encoding="utf-8")
            registry_text = (root / "ssot-registry" / "pyproject.toml").read_text(encoding="utf-8")
            cli_text = (root / "ssot-cli" / "pyproject.toml").read_text(encoding="utf-8")
            tui_text = (root / "ssot-tui" / "pyproject.toml").read_text(encoding="utf-8")

            self.assertIn('version = "0.2.4.dev1"', (root / "ssot-contracts" / "pyproject.toml").read_text(encoding="utf-8"))
            self.assertIn('version = "0.2.4.dev1"', views_text)
            self.assertIn('ssot-contracts==0.2.4.dev1', views_text)
            self.assertIn('ssot-contracts==0.2.4.dev1', codegen_text)
            self.assertIn('ssot-views==0.2.4.dev1', codegen_text)
            self.assertIn('ssot-contracts==0.2.4.dev1', registry_text)
            self.assertIn('ssot-views==0.2.4.dev1', registry_text)
            self.assertIn('version = "0.1.1.dev1"', cli_text)
            self.assertIn('ssot-contracts>=0.2.4.dev1,<0.3.0', cli_text)
            self.assertIn('ssot-registry>=0.2.4.dev1,<0.3.0', cli_text)
            self.assertIn('version = "0.1.1.dev1"', tui_text)
            self.assertIn('ssot-contracts>=0.2.4.dev1,<0.3.0', tui_text)
            self.assertIn('ssot-registry>=0.2.4.dev1,<0.3.0', tui_text)


if __name__ == "__main__":
    unittest.main()
