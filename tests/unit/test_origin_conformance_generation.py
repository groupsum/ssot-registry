from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
for path in (
    REPO_ROOT / "pkgs" / "ssot-core" / "src",
    REPO_ROOT / "pkgs" / "ssot-contracts" / "src",
    REPO_ROOT / "pkgs" / "ssot-conformance" / "src",
):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from ssot_conformance.origin import (
    GENERATED_MARKER,
    apply_origin_conformance,
    discover_origin_obligations,
    list_origin_templates,
    plan_origin_conformance,
)
from tests.helpers import run_cli, temp_repo_from_fixture


class OriginConformanceGenerationTests(unittest.TestCase):
    def _repo(self) -> Path:
        temp_dir = temp_repo_from_fixture("repo_valid")
        self.addCleanup(temp_dir.cleanup)
        return Path(temp_dir.name) / "repo"

    def test_template_catalog_and_obligation_discovery_cover_origin_adrs_and_specs(self) -> None:
        repo = self._repo()
        templates = {row["id"]: row for row in list_origin_templates()}
        self.assertEqual({"origin-adr-compliance", "origin-spec-compliance"}, set(templates))

        obligations = discover_origin_obligations(repo)
        self.assertTrue(any(row["kind"] == "adr" for row in obligations))
        self.assertTrue(any(row["kind"] == "spec" for row in obligations))
        self.assertTrue(all(row["template_id"] in templates for row in obligations))

    def test_dry_run_reports_files_and_missing_rows_without_mutating_repo(self) -> None:
        repo = self._repo()
        plan = plan_origin_conformance(repo, kinds=["adr"], include_claims=True, include_evidence=True)

        self.assertTrue(plan["passed"], plan)
        self.assertGreater(len(plan["generated_files"]), 0)
        self.assertGreater(len(plan["missing"]["features"]), 0)
        self.assertFalse((repo / plan["generated_files"][0]["path"]).exists())

    def test_apply_generates_rows_files_execution_metadata_report_and_is_idempotent(self) -> None:
        repo = self._repo()
        result = apply_origin_conformance(repo, kinds=["adr"], include_claims=True, include_evidence=True)
        self.assertTrue(result["passed"], result)
        self.assertGreater(len(result["created"]["files"]), 0)
        generated_path = repo / result["created"]["files"][0]
        self.assertTrue(generated_path.read_text(encoding="utf-8").startswith(GENERATED_MARKER))

        registry = json.loads((repo / ".ssot" / "registry.json").read_text(encoding="utf-8"))
        created_feature_ids = set(result["created"]["features"])
        created_test_ids = set(result["created"]["tests"])
        created_evidence_ids = set(result["created"]["evidence"])
        self.assertTrue(created_feature_ids)
        self.assertTrue(created_test_ids)
        self.assertTrue(created_evidence_ids)
        generated_tests = [row for row in registry["tests"] if row["id"] in created_test_ids]
        self.assertTrue(all(row["status"] == "passing" for row in generated_tests))
        self.assertTrue(all(row["execution"]["argv"][:3] == ["python", "-m", "pytest"] for row in generated_tests))

        report_path = repo / result["report_path"]
        report = json.loads(report_path.read_text(encoding="utf-8"))
        self.assertTrue(report["passed"])
        self.assertEqual(report["created"]["features"], result["created"]["features"])

        rerun = apply_origin_conformance(repo, kinds=["adr"], include_claims=True, include_evidence=True)
        self.assertEqual(rerun["created"]["features"], [])
        self.assertEqual(rerun["created"]["files"], [])
        self.assertEqual(set(rerun["unchanged"]["features"]), created_feature_ids)

    def test_apply_refuses_to_overwrite_locally_edited_generated_target(self) -> None:
        repo = self._repo()
        result = apply_origin_conformance(repo, kinds=["spec"], include_claims=True, include_evidence=True)
        generated_path = repo / result["created"]["files"][0]
        generated_path.write_text("def test_local_edit():\n    assert True\n", encoding="utf-8")

        with self.assertRaisesRegex(ValueError, "Refusing to overwrite"):
            apply_origin_conformance(repo, kinds=["spec"], include_claims=True, include_evidence=True)

    def test_cli_origin_generation_surface(self) -> None:
        repo = self._repo()
        plan = run_cli("conformance", "origin", str(repo), "--kinds", "adr", "--include-claims", "--include-evidence")
        self.assertEqual(plan.returncode, 0, plan.stderr)
        self.assertTrue(json.loads(plan.stdout)["passed"])

        apply = run_cli(
            "conformance",
            "origin",
            str(repo),
            "--kinds",
            "adr",
            "--apply",
            "--include-claims",
            "--include-evidence",
        )
        self.assertEqual(apply.returncode, 0, apply.stderr)
        payload = json.loads(apply.stdout)
        self.assertTrue(payload["passed"], payload)
        self.assertGreater(len(payload["created"]["tests"]), 0)


if __name__ == "__main__":
    unittest.main()
