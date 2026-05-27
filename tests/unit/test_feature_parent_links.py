from __future__ import annotations

import json
import unittest
from pathlib import Path

from ssot_registry.api import audit_feature_parent_links, certify_release, migrate_feature_parent_audit_edge, validate_registry
from ssot_registry.util.jsonio import stable_json_dumps
from ssot_registry.validators.feature_parent_links import validate_feature_parent_links
from ssot_registry.validators.identity import build_index
from tests.helpers import temp_repo_from_fixture


class FeatureParentLinkValidationTests(unittest.TestCase):
    def test_rejects_self_parent_duplicate_and_cycle_links(self) -> None:
        registry = {
            "features": [
                {"id": "feat:demo.parent", "parent_feature_ids": ["feat:demo.child"]},
                {"id": "feat:demo.child", "parent_feature_ids": ["feat:demo.parent", "feat:demo.parent"]},
                {"id": "feat:demo.self", "parent_feature_ids": ["feat:demo.self"]},
            ]
        }
        failures: list[str] = []
        index = build_index(registry, failures)

        validate_feature_parent_links(index, failures)

        self.assertTrue(any("features.feat:demo.self.parent_feature_ids must not include itself" in failure for failure in failures))
        self.assertTrue(any("features.feat:demo.child.parent_feature_ids contains duplicate ids" in failure for failure in failures))
        self.assertTrue(any("Feature parent cycle detected:" in failure for failure in failures))

    def test_parent_links_do_not_affect_release_certification(self) -> None:
        temp_dir = temp_repo_from_fixture("repo_valid")
        self.addCleanup(temp_dir.cleanup)
        repo = Path(temp_dir.name) / "repo"
        registry_path = repo / ".ssot" / "registry.json"
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
        registry["features"].append(
            {
                "id": "feat:inventory.parent.partial",
                "title": "Inventory parent partial",
                "description": "Partial inventory parent only.",
                "origin": "repo-local",
                "implementation_status": "partial",
                "lifecycle": {"stage": "active", "replacement_feature_ids": [], "note": None},
                "plan": {"horizon": "backlog", "slot": None, "target_claim_tier": None, "target_lifecycle_stage": "active"},
                "spec_ids": [],
                "claim_ids": [],
                "test_ids": [],
                "requires": [],
                "parent_feature_ids": [],
            }
        )
        feature = next(row for row in registry["features"] if row["id"] == "feat:rfc.9000.connection-migration")
        feature["parent_feature_ids"] = ["feat:inventory.parent.partial"]
        registry_path.write_text(stable_json_dumps(registry), encoding="utf-8")

        validation = validate_registry(repo)
        self.assertTrue(validation["passed"], validation)
        certification = certify_release(repo, release_id="rel:1.2.0")
        self.assertTrue(certification["passed"])

    def test_parent_audit_reports_without_mutating_registry(self) -> None:
        temp_dir = temp_repo_from_fixture("repo_valid")
        self.addCleanup(temp_dir.cleanup)
        repo = Path(temp_dir.name) / "repo"
        registry_path = repo / ".ssot" / "registry.json"
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
        registry["features"].append(
            {
                "id": "feat:dependency.parent.partial",
                "title": "Dependency parent partial",
                "description": "Parent dependency before child can pass.",
                "origin": "repo-local",
                "implementation_status": "partial",
                "lifecycle": {"stage": "active", "replacement_feature_ids": [], "note": None},
                "plan": {"horizon": "backlog", "slot": None, "target_claim_tier": None, "target_lifecycle_stage": "active"},
                "spec_ids": [],
                "claim_ids": [],
                "test_ids": [],
                "requires": [],
                "parent_feature_ids": [],
            }
        )
        feature = next(row for row in registry["features"] if row["id"] == "feat:rfc.9000.connection-migration")
        feature["parent_feature_ids"] = ["feat:dependency.parent.partial"]
        before = stable_json_dumps(registry)
        registry_path.write_text(before, encoding="utf-8")

        report = audit_feature_parent_links(repo)
        after = registry_path.read_text(encoding="utf-8")
        self.assertEqual(before, after)
        self.assertTrue(report["passed"])
        self.assertEqual(report["summary"]["finding_count"], 1)
        finding = report["findings"][0]
        self.assertEqual(finding["feature_id"], "feat:rfc.9000.connection-migration")
        self.assertEqual(finding["parent_feature_id"], "feat:dependency.parent.partial")
        self.assertEqual(
            finding["suggested_requires_edge"],
            {"feature_id": "feat:rfc.9000.connection-migration", "requires": "feat:dependency.parent.partial"},
        )

    def test_parent_audit_migration_adds_requires_and_optionally_removes_parent_link(self) -> None:
        temp_dir = temp_repo_from_fixture("repo_valid")
        self.addCleanup(temp_dir.cleanup)
        repo = Path(temp_dir.name) / "repo"
        registry_path = repo / ".ssot" / "registry.json"
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
        registry["features"].append(
            {
                "id": "feat:migrate.parent.partial",
                "title": "Migrate parent partial",
                "description": "Partial parent that must be migrated explicitly.",
                "origin": "repo-local",
                "implementation_status": "partial",
                "lifecycle": {"stage": "active", "replacement_feature_ids": [], "note": None},
                "plan": {"horizon": "backlog", "slot": None, "target_claim_tier": None, "target_lifecycle_stage": "active"},
                "spec_ids": [],
                "claim_ids": [],
                "test_ids": [],
                "requires": [],
                "parent_feature_ids": [],
            }
        )
        feature = next(row for row in registry["features"] if row["id"] == "feat:rfc.9000.connection-migration")
        feature["parent_feature_ids"] = ["feat:migrate.parent.partial"]
        registry_path.write_text(stable_json_dumps(registry), encoding="utf-8")

        kept = migrate_feature_parent_audit_edge(repo, "feat:rfc.9000.connection-migration", "feat:migrate.parent.partial")
        self.assertTrue(kept["added_requires"])
        self.assertFalse(kept["removed_parent_link"])
        self.assertIn("feat:migrate.parent.partial", kept["entity"]["requires"])
        self.assertIn("feat:migrate.parent.partial", kept["entity"]["parent_feature_ids"])

        removed = migrate_feature_parent_audit_edge(
            repo,
            "feat:rfc.9000.connection-migration",
            "feat:migrate.parent.partial",
            remove_parent_link=True,
        )
        self.assertFalse(removed["added_requires"])
        self.assertTrue(removed["removed_parent_link"])
        self.assertIn("feat:migrate.parent.partial", removed["entity"]["requires"])
        self.assertNotIn("feat:migrate.parent.partial", removed["entity"]["parent_feature_ids"])


if __name__ == "__main__":
    unittest.main()
