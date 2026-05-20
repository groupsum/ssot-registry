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

    def test_release_workflow_builds_once_and_publishes_layers(self) -> None:
        workflow = _read(".github/workflows/release.yml")
        self.assertIn("release_train", workflow)
        self.assertIn("- all", workflow)
        self.assertIn("- ssot-contracts", workflow)
        self.assertIn("- ssot-pack-contracts", workflow)
        self.assertIn("- ssot-views", workflow)
        self.assertIn("- ssot-codegen", workflow)
        self.assertIn("- ssot-core", workflow)
        self.assertIn("- ssot-conformance", workflow)
        self.assertIn("- ssot-registry", workflow)
        self.assertIn("publish_layer_1", workflow)
        self.assertIn("build-distributions:", workflow)
        self.assertIn("release-distributions", workflow)
        self.assertIn("publish-ssot-contracts:", workflow)
        self.assertIn("publish-ssot-codegen:", workflow)
        self.assertIn("publish-ssot-cli:", workflow)
        self.assertIn("needs.publish-ssot-pack-contracts.result", workflow)
        self.assertIn("./.github/workflows/_publish-built-package.yml", workflow)
        self.assertEqual(workflow.count("./.github/workflows/_publish-built-package.yml"), 9)
        self.assertIn("package_name: ssot-contracts", workflow)
        self.assertIn("package_name: ssot-pack-contracts", workflow)
        self.assertIn("package_name: ssot-registry", workflow)
        self.assertNotIn("if package_name in target_set", workflow)
        self.assertNotIn("./.github/workflows/publish-ssot-", workflow)

    def test_ci_runs_shared_suite_once_per_python_version(self) -> None:
        workflow = _read(".github/workflows/ci.yml")
        self.assertIn("shared-tests:", workflow)
        self.assertEqual(workflow.count("python -m unittest discover -s tests -v"), 1)
        self.assertIn("release-build-smoke:", workflow)
        self.assertIn("uv build --project pkgs/ssot-contracts", workflow)

    def test_ci_workflow_covers_each_package_across_supported_python_versions(self) -> None:
        workflow = _read(".github/workflows/ci.yml")
        self.assertIn('python_version: ["3.10", "3.11", "3.12", "3.13", "3.14"]', workflow)
        for package_name in (
            "ssot-contracts",
            "ssot-pack-contracts",
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
            ".github/workflows/publish-ssot-pack-contracts.yml",
            ".github/workflows/publish-ssot-views.yml",
            ".github/workflows/publish-ssot-codegen.yml",
            ".github/workflows/publish-ssot-core.yml",
            ".github/workflows/publish-ssot-conformance.yml",
            ".github/workflows/publish-ssot-registry.yml",
            ".github/workflows/publish-ssot-cli.yml",
            ".github/workflows/publish-ssot-tui.yml",
        ):
            self.assertTrue((REPO_ROOT / filename).exists(), filename)

    def test_publish_wrappers_grant_oidc_for_trusted_publishing(self) -> None:
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
            workflow = _read(filename)
            self.assertIn("permissions:", workflow, filename)
            self.assertIn("contents: write", workflow, filename)
            self.assertIn("id-token: write", workflow, filename)
            self.assertIn("uses: ./.github/workflows/release.yml", workflow, filename)
            self.assertIn("publish_to_pypi: ${{ inputs.publish_to_pypi }}", workflow, filename)
            self.assertNotIn("uv publish", workflow, filename)
            self.assertNotIn("PYPI_API_TOKEN", workflow, filename)

    def test_reusable_publish_workflow_uses_tag_as_release_title(self) -> None:
        workflow = _read(".github/workflows/_package-publish.yml")
        self.assertIn("gh release create", workflow)
        self.assertIn("--title \"$TAG\"", workflow)

    def test_built_package_publish_workflow_consumes_release_artifacts(self) -> None:
        workflow = _read(".github/workflows/_publish-built-package.yml")
        self.assertIn("actions/download-artifact@v6", workflow)
        self.assertIn("release-distributions", workflow)
        self.assertIn("gh release create", workflow)
        self.assertIn("uv publish --trusted-publishing always --check-url https://pypi.org/simple/ release-dist/$PACKAGE_NAME/*.whl release-dist/$PACKAGE_NAME/*.tar.gz", workflow)
        self.assertNotIn("PYPI_API_TOKEN", workflow)
        self.assertNotIn("trusted-publishing never", workflow)

    def test_prepare_release_uses_package_aware_bump_script(self) -> None:
        workflow = _read(".github/workflows/prepare-release.yml")
        self.assertIn("- all", workflow)
        self.assertIn("- ssot-pack-contracts", workflow)
        self.assertIn("- ssot-conformance", workflow)
        self.assertIn("scripts/bump_release_train.py", workflow)
        self.assertIn("steps.bump_version.outputs.changed_files != ''", workflow)
        self.assertNotIn("scripts/release_metadata.py validate-train", workflow)
        self.assertNotIn("python scripts/bump_pyproject_version.py --bump \"$BUMP_TYPE\" pyproject.toml", workflow)

    def test_sync_packaged_docs_uses_contract_package_templates(self) -> None:
        script = _read("scripts/sync_packaged_docs.py")
        self.assertIn("pkgs", script)
        self.assertIn("ssot_contracts", script)
        self.assertIn("ssot_registry", script)
        self.assertIn("validate_number_ranges", script)


if __name__ == "__main__":
    unittest.main()
