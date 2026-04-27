from __future__ import annotations

import unittest
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python 3.10 fallback
    try:
        import tomli as tomllib
    except ModuleNotFoundError:
        from pip._vendor import tomli as tomllib


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
        self.assertIn("- all", workflow)
        self.assertIn("- ssot-contracts", workflow)
        self.assertIn("- ssot-views", workflow)
        self.assertIn("- ssot-codegen", workflow)
        self.assertIn("- ssot-core", workflow)
        self.assertIn("- ssot-conformance", workflow)
        self.assertIn("- ssot-registry", workflow)
        self.assertIn("publish-ssot-contracts.yml", workflow)
        self.assertIn("publish-ssot-views.yml", workflow)
        self.assertIn("publish-ssot-codegen.yml", workflow)
        self.assertIn("publish-ssot-core.yml", workflow)
        self.assertIn("publish-ssot-conformance.yml", workflow)
        self.assertIn("publish-ssot-registry.yml", workflow)
        self.assertIn("publish-ssot-cli.yml", workflow)
        self.assertIn("publish-ssot-tui.yml", workflow)

    def test_ci_workflow_covers_each_package_across_supported_python_versions(self) -> None:
        workflow = _read(".github/workflows/ci.yml")
        self.assertIn('python_version: ["3.10", "3.11", "3.12", "3.13"]', workflow)
        for package_name in (
            "ssot-contracts",
            "ssot-views",
            "ssot-codegen",
            "ssot-core",
            "ssot-conformance",
            "ssot-registry",
            "ssot-cli",
            "ssot-tui",
        ):
            self.assertIn(f"          - {package_name}", workflow)
            self.assertIn(f"          - package_name: {package_name}", workflow)

    def test_publish_workflows_exist_for_all_packages(self) -> None:
        for filename in (
            ".github/workflows/publish-ssot-contracts.yml",
            ".github/workflows/publish-ssot-views.yml",
            ".github/workflows/publish-ssot-codegen.yml",
            ".github/workflows/publish-ssot-core.yml",
            ".github/workflows/publish-ssot-conformance.yml",
            ".github/workflows/publish-ssot-registry.yml",
            ".github/workflows/publish-ssot-cli.yml",
            ".github/workflows/publish-ssot-tui.yml",
        ):
            self.assertTrue((REPO_ROOT / filename).exists(), filename)

    def test_reusable_publish_workflow_uses_tag_as_release_title(self) -> None:
        workflow = _read(".github/workflows/_package-publish.yml")
        self.assertIn("tag_name: ${{ steps.release_meta.outputs.tag }}", workflow)
        self.assertIn("name: ${{ steps.release_meta.outputs.tag }}", workflow)

    def test_prepare_release_uses_package_aware_bump_script(self) -> None:
        workflow = _read(".github/workflows/prepare-release.yml")
        self.assertIn("- all", workflow)
        self.assertIn("- ssot-conformance", workflow)
        self.assertIn("scripts/bump_release_train.py", workflow)
        self.assertNotIn("python scripts/bump_pyproject_version.py --bump \"$BUMP_TYPE\" pyproject.toml", workflow)

    def test_sync_packaged_docs_uses_contract_package_templates(self) -> None:
        script = _read("scripts/sync_packaged_docs.py")
        self.assertIn("pkgs", script)
        self.assertIn("ssot_contracts", script)
        self.assertIn("ssot_registry", script)
        self.assertIn("validate_number_ranges", script)


if __name__ == "__main__":
    unittest.main()
