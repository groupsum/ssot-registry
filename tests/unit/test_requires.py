from __future__ import annotations

import json
import unittest
from pathlib import Path

from ssot_registry.api import certify_release, promote_release, publish_release, validate_registry
from ssot_registry.util.errors import GuardError
from ssot_registry.util.jsonio import stable_json_dumps
from tests.helpers import temp_repo_from_fixture


class FeatureRequiresValidationTests(unittest.TestCase):
    def test_requires_warns_when_dependency_is_not_passing(self) -> None:
        temp_dir = temp_repo_from_fixture("repo_valid")
        self.addCleanup(temp_dir.cleanup)
        repo = Path(temp_dir.name) / "repo"
        registry_path = repo / ".ssot" / "registry.json"
        registry = json.loads(registry_path.read_text(encoding="utf-8"))

        registry["features"].append(
            {
                "id": "feat:dependency.not-passing",
                "title": "Dependency not passing",
                "description": "dependency",
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
        registry["features"].append(
            {
                "id": "feat:dependent.current",
                "title": "Dependent current feature",
                "description": "dependent",
                "origin": "repo-local",
                "implementation_status": "partial",
                "lifecycle": {"stage": "active", "replacement_feature_ids": [], "note": None},
                "plan": {"horizon": "next", "slot": None, "target_claim_tier": "T3", "target_lifecycle_stage": "active"},
                "spec_ids": [],
                "claim_ids": [],
                "test_ids": [],
                "requires": ["feat:dependency.not-passing"],
                "parent_feature_ids": [],
            }
        )
        registry_path.write_text(stable_json_dumps(registry), encoding="utf-8")

        report = validate_registry(repo)
        self.assertTrue(report["passed"], report)
        joined = "\n".join(report["warnings"])
        self.assertIn("requires feat:dependency.not-passing to be passing", joined)

    def test_requires_readiness_is_enforced_by_release_certification(self) -> None:
        temp_dir = temp_repo_from_fixture("repo_valid")
        self.addCleanup(temp_dir.cleanup)
        repo = Path(temp_dir.name) / "repo"
        registry_path = repo / ".ssot" / "registry.json"
        registry = json.loads(registry_path.read_text(encoding="utf-8"))

        registry["features"].append(
            {
                "id": "feat:dependency.not-passing",
                "title": "Dependency not passing",
                "description": "dependency",
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
        feature["requires"] = ["feat:dependency.not-passing"]
        registry_path.write_text(stable_json_dumps(registry), encoding="utf-8")

        validation = validate_registry(repo)
        self.assertTrue(validation["passed"], validation)
        with self.assertRaisesRegex(GuardError, "requires feat:dependency.not-passing to be passing"):
            certify_release(repo, release_id="rel:1.2.0")

        release = next(row for row in registry["releases"] if row["id"] == "rel:1.2.0")
        release["status"] = "certified"
        registry_path.write_text(stable_json_dumps(registry), encoding="utf-8")
        with self.assertRaisesRegex(GuardError, "requires feat:dependency.not-passing to be passing"):
            promote_release(repo, release_id="rel:1.2.0")

        release["status"] = "promoted"
        registry_path.write_text(stable_json_dumps(registry), encoding="utf-8")
        with self.assertRaisesRegex(GuardError, "requires feat:dependency.not-passing to be passing"):
            publish_release(repo, release_id="rel:1.2.0")

    def test_requires_is_not_parent_leaf_composition(self) -> None:
        temp_dir = temp_repo_from_fixture("repo_valid")
        self.addCleanup(temp_dir.cleanup)
        repo = Path(temp_dir.name) / "repo"
        registry_path = repo / ".ssot" / "registry.json"
        registry = json.loads(registry_path.read_text(encoding="utf-8"))

        registry["features"].append(
            {
                "id": "feat:umbrella.operator-surface",
                "title": "Operator surface umbrella",
                "description": "inventory grouping row",
                "origin": "repo-local",
                "implementation_status": "partial",
                "lifecycle": {"stage": "active", "replacement_feature_ids": [], "note": None},
                "plan": {"horizon": "next", "slot": None, "target_claim_tier": "T3", "target_lifecycle_stage": "active"},
                "spec_ids": [],
                "claim_ids": [],
                "test_ids": [],
                "requires": ["feat:umbrella.operator-surface.leaf"],
                "parent_feature_ids": [],
            }
        )
        registry["features"].append(
            {
                "id": "feat:umbrella.operator-surface.leaf",
                "title": "Operator surface leaf",
                "description": "leaf inventory row",
                "origin": "repo-local",
                "implementation_status": "absent",
                "lifecycle": {"stage": "active", "replacement_feature_ids": [], "note": None},
                "plan": {"horizon": "backlog", "slot": None, "target_claim_tier": None, "target_lifecycle_stage": "active"},
                "spec_ids": [],
                "claim_ids": [],
                "test_ids": [],
                "requires": [],
                "parent_feature_ids": ["feat:umbrella.operator-surface"],
            }
        )
        registry_path.write_text(stable_json_dumps(registry), encoding="utf-8")

        report = validate_registry(repo)
        self.assertTrue(report["passed"], report)
        joined = "\n".join(report["warnings"])
        self.assertIn("requires feat:umbrella.operator-surface.leaf to be passing", joined)

    def test_requires_cycle_is_reported(self) -> None:
        temp_dir = temp_repo_from_fixture("repo_valid")
        self.addCleanup(temp_dir.cleanup)
        repo = Path(temp_dir.name) / "repo"
        registry_path = repo / ".ssot" / "registry.json"
        registry = json.loads(registry_path.read_text(encoding="utf-8"))

        registry["features"].append(
            {
                "id": "feat:cycle.a",
                "title": "Cycle A",
                "description": "cycle a",
                "origin": "repo-local",
                "implementation_status": "absent",
                "lifecycle": {"stage": "active", "replacement_feature_ids": [], "note": None},
                "plan": {"horizon": "backlog", "slot": None, "target_claim_tier": None, "target_lifecycle_stage": "active"},
                "spec_ids": [],
                "claim_ids": [],
                "test_ids": [],
                "requires": ["feat:cycle.b"],
                "parent_feature_ids": [],
            }
        )
        registry["features"].append(
            {
                "id": "feat:cycle.b",
                "title": "Cycle B",
                "description": "cycle b",
                "origin": "repo-local",
                "implementation_status": "absent",
                "lifecycle": {"stage": "active", "replacement_feature_ids": [], "note": None},
                "plan": {"horizon": "backlog", "slot": None, "target_claim_tier": None, "target_lifecycle_stage": "active"},
                "spec_ids": [],
                "claim_ids": [],
                "test_ids": [],
                "requires": ["feat:cycle.a"],
                "parent_feature_ids": [],
            }
        )
        registry_path.write_text(stable_json_dumps(registry), encoding="utf-8")

        report = validate_registry(repo)
        self.assertFalse(report["passed"])
        joined = "\n".join(report["warnings"] + report["failures"])
        self.assertIn("Feature requirement cycle detected", joined)


if __name__ == "__main__":
    unittest.main()
