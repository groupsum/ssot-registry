from __future__ import annotations

import json
import unittest
from pathlib import Path

from ssot_registry.api import validate_registry
from tests.helpers import temp_repo_from_fixture


class FeatureRequiresValidationTests(unittest.TestCase):
    def test_requires_fails_when_dependency_is_not_passing(self) -> None:
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
                "implementation_status": "partial",
                "lifecycle": {"stage": "active", "replacement_feature_ids": [], "note": None},
                "plan": {"horizon": "backlog", "slot": None, "target_claim_tier": None, "target_lifecycle_stage": "active"},
                "spec_ids": [],
                "claim_ids": [],
                "test_ids": [],
                "requires": [],
            }
        )
        registry["features"].append(
            {
                "id": "feat:dependent.current",
                "title": "Dependent current feature",
                "description": "dependent",
                "implementation_status": "implemented",
                "lifecycle": {"stage": "active", "replacement_feature_ids": [], "note": None},
                "plan": {"horizon": "current", "slot": None, "target_claim_tier": "T3", "target_lifecycle_stage": "active"},
                "spec_ids": [],
                "claim_ids": ["clm:rfc.9000.connection-migration.t3"],
                "test_ids": ["tst:pytest.rfc.9000.connection-migration"],
                "requires": ["feat:dependency.not-passing"],
            }
        )
        registry_path.write_text(json.dumps(registry, indent=2) + "\n", encoding="utf-8")

        report = validate_registry(repo)
        self.assertFalse(report["passed"])
        joined = "\n".join(report["failures"])
        self.assertIn("requires feat:dependency.not-passing to be passing", joined)

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
                "implementation_status": "absent",
                "lifecycle": {"stage": "active", "replacement_feature_ids": [], "note": None},
                "plan": {"horizon": "backlog", "slot": None, "target_claim_tier": None, "target_lifecycle_stage": "active"},
                "spec_ids": [],
                "claim_ids": [],
                "test_ids": [],
                "requires": ["feat:cycle.b"],
            }
        )
        registry["features"].append(
            {
                "id": "feat:cycle.b",
                "title": "Cycle B",
                "description": "cycle b",
                "implementation_status": "absent",
                "lifecycle": {"stage": "active", "replacement_feature_ids": [], "note": None},
                "plan": {"horizon": "backlog", "slot": None, "target_claim_tier": None, "target_lifecycle_stage": "active"},
                "spec_ids": [],
                "claim_ids": [],
                "test_ids": [],
                "requires": ["feat:cycle.a"],
            }
        )
        registry_path.write_text(json.dumps(registry, indent=2) + "\n", encoding="utf-8")

        report = validate_registry(repo)
        self.assertFalse(report["passed"])
        joined = "\n".join(report["warnings"] + report["failures"])
        self.assertIn("Feature requirement cycle detected", joined)


if __name__ == "__main__":
    unittest.main()
