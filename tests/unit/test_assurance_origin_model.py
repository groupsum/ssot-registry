from __future__ import annotations

import unittest
from copy import deepcopy
from pathlib import Path

from ssot_registry.api.origin import sync_origin_assurance_rows
from ssot_registry.api.upgrade import migrate_v0_4_0_to_v0_5_0
from ssot_registry.api.validate import validate_registry_document
from ssot_registry.model.registry import build_minimal_registry
from tests.helpers import workspace_tempdir


def _repo_with_assurance(repo_kind: str = "repo-local") -> dict[str, object]:
    registry = build_minimal_registry("repo:origin-test", "origin-test", "0.1.0", repo_kind=repo_kind)
    registry["features"] = [
        {
            "id": "feat:local.behavior",
            "title": "Local behavior",
            "description": "Local behavior row.",
            "origin": "repo-local",
            "implementation_status": "partial",
            "lifecycle": {"stage": "active", "replacement_feature_ids": [], "note": None},
            "plan": {"horizon": "next", "slot": None, "target_claim_tier": "T1", "target_lifecycle_stage": "active"},
            "spec_ids": [],
            "claim_ids": [],
            "test_ids": [],
            "requires": [],
        }
    ]
    registry["tests"] = [
        {
            "id": "tst:local.behavior",
            "title": "Local behavior test",
            "origin": "repo-local",
            "status": "planned",
            "kind": "pytest",
            "path": "tests/test_local_behavior.py",
            "feature_ids": ["feat:local.behavior"],
            "claim_ids": ["clm:local.behavior.t1"],
            "evidence_ids": ["evd:local.behavior"],
        }
    ]
    registry["claims"] = [
        {
            "id": "clm:local.behavior.t1",
            "title": "Local behavior claim",
            "origin": "repo-local",
            "status": "proposed",
            "tier": "T1",
            "kind": "conformance",
            "description": "Local behavior claim.",
            "feature_ids": ["feat:local.behavior"],
            "test_ids": ["tst:local.behavior"],
            "evidence_ids": ["evd:local.behavior"],
            "depends_on_claim_ids": [],
        }
    ]
    registry["evidence"] = [
        {
            "id": "evd:local.behavior",
            "title": "Local behavior evidence",
            "origin": "repo-local",
            "status": "planned",
            "kind": "report",
            "tier": "T1",
            "path": ".ssot/evidence/local-behavior.json",
            "claim_ids": ["clm:local.behavior.t1"],
            "test_ids": ["tst:local.behavior"],
        }
    ]
    return registry


class AssuranceOriginModelTests(unittest.TestCase):
    def test_repo_local_registry_rejects_ssot_core_assurance_rows(self) -> None:
        temp_dir = workspace_tempdir()
        self.addCleanup(temp_dir.cleanup)
        repo_root = Path(temp_dir.name)
        registry = _repo_with_assurance()
        registry["features"][0]["origin"] = "ssot-core"

        report = validate_registry_document(registry, repo_root / ".ssot" / "registry.json", repo_root)

        self.assertFalse(report["passed"])
        self.assertIn("features.feat:local.behavior.origin cannot be ssot-core", "; ".join(report["failures"]))

    def test_migration_backfills_origin_from_repo_kind(self) -> None:
        registry = _repo_with_assurance(repo_kind="ssot-core")
        registry["schema_version"] = "0.4.0"
        for section in ("features", "tests", "claims", "evidence"):
            for row in registry[section]:
                row.pop("origin", None)

        migrated = migrate_v0_4_0_to_v0_5_0(registry, Path("."), previous_version="0.2.10", target_version="0.5.0")

        self.assertEqual("0.5.0", migrated["schema_version"])
        for section in ("features", "tests", "claims", "evidence"):
            self.assertEqual({"ssot-core"}, {row["origin"] for row in migrated[section]})

    def test_sync_origin_assurance_rows_imports_only_ssot_origin_rows(self) -> None:
        temp_dir = workspace_tempdir()
        self.addCleanup(temp_dir.cleanup)
        repo_root = Path(temp_dir.name)
        ssot_root = repo_root / ".ssot"
        ssot_root.mkdir(parents=True)
        target = _repo_with_assurance()
        target_path = ssot_root / "registry.json"
        (repo_root / "tests").mkdir()
        (repo_root / "tests" / "test_local_behavior.py").write_text("def test_local_behavior():\n    assert True\n", encoding="utf-8")
        (ssot_root / "evidence").mkdir()
        (ssot_root / "evidence" / "local-behavior.json").write_text("{}", encoding="utf-8")
        from ssot_registry.api.save import save_registry_unchecked

        save_registry_unchecked(target_path, target)

        source = deepcopy(target)
        source["features"][0]["id"] = "feat:origin.shared"
        source["features"][0]["origin"] = "ssot-origin"
        source["features"][0]["claim_ids"] = []
        source["features"][0]["test_ids"] = []
        source["tests"] = []
        source["claims"] = []
        source["evidence"] = []

        result = sync_origin_assurance_rows(target_path, source)

        self.assertTrue(result["passed"])
        self.assertEqual(["feat:origin.shared"], result["created"]["features"])


if __name__ == "__main__":
    unittest.main()
