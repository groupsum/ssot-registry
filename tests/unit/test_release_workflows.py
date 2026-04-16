from __future__ import annotations

import tomllib
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def _read(path: str) -> str:
    return (REPO_ROOT / path).read_text(encoding="utf-8")


class ReleaseWorkflowTests(unittest.TestCase):
    def test_root_pyproject_is_workspace_only(self) -> None:
        data = tomllib.loads((REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
        self.assertIn("tool", data)
        self.assertIn("uv", data["tool"])
        self.assertNotIn("project", data)

    def test_ci_uses_reusable_package_ci_and_package_roots(self) -> None:
        workflow = _read(".github/workflows/ci.yml")
        self.assertIn("./.github/workflows/_package-ci.yml", workflow)
        self.assertIn("pkgs/ssot-registry", workflow)
        self.assertNotIn("run: uv build\n", workflow)

    def test_release_workflow_targets_package_publish_wrappers(self) -> None:
        workflow = _read(".github/workflows/release.yml")
        self.assertIn("release_train", workflow)
        self.assertIn("publish-ssot-contracts.yml", workflow)
        self.assertIn("publish-ssot-registry.yml", workflow)
        self.assertIn("publish-ssot-cli.yml", workflow)

    def test_publish_workflows_exist_for_all_packages(self) -> None:
        for filename in (
            ".github/workflows/publish-ssot-contracts.yml",
            ".github/workflows/publish-ssot-views.yml",
            ".github/workflows/publish-ssot-codegen.yml",
            ".github/workflows/publish-ssot-registry.yml",
            ".github/workflows/publish-ssot-cli.yml",
            ".github/workflows/publish-ssot-tui.yml",
        ):
            self.assertTrue((REPO_ROOT / filename).exists(), filename)

    def test_prepare_release_uses_package_aware_bump_script(self) -> None:
        workflow = _read(".github/workflows/prepare-release.yml")
        self.assertIn("scripts/bump_release_train.py", workflow)
        self.assertNotIn("python scripts/bump_pyproject_version.py --bump \"$BUMP_TYPE\" pyproject.toml", workflow)

    def test_sync_packaged_docs_uses_contract_package_templates(self) -> None:
        script = _read("scripts/sync_packaged_docs.py")
        self.assertIn("pkgs", script)
        self.assertIn("ssot_contracts", script)
        self.assertNotIn('PROJECT_ROOT / "src" / "ssot_registry" / "templates"', script)


if __name__ == "__main__":
    unittest.main()
