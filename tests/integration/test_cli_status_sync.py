from __future__ import annotations

import json
import unittest
from pathlib import Path

from ssot_registry.util.jsonio import stable_json_dumps
from tests.helpers import run_cli, temp_repo_from_fixture


class CliStatusSyncTests(unittest.TestCase):
    def test_registry_sync_statuses_updates_all_automated_entity_sections(self) -> None:
        temp_dir = temp_repo_from_fixture("repo_valid")
        self.addCleanup(temp_dir.cleanup)
        repo = Path(temp_dir.name) / "repo"
        registry_path = repo / ".ssot" / "registry.json"
        registry = json.loads(registry_path.read_text(encoding="utf-8"))

        registry["features"][0]["implementation_status"] = "absent"
        registry["tests"][0]["status"] = "planned"
        registry["claims"][0]["status"] = "declared"
        registry["evidence"][0]["status"] = "collected"
        registry["profiles"].append(
            {
                "id": "prf:cli.status-sync",
                "title": "Status sync profile",
                "description": "Profile used by status sync integration coverage.",
                "status": "draft",
                "kind": "certification",
                "feature_ids": [registry["features"][0]["id"]],
                "profile_ids": [],
                "claim_tier": "T3",
                "evaluation": {
                    "mode": "all_features_must_pass",
                    "allow_feature_override_tier": True,
                },
            }
        )
        registry_path.write_text(stable_json_dumps(registry), encoding="utf-8")

        dry_run = run_cli("registry", "sync-statuses", str(repo), "--dry-run")
        self.assertEqual(dry_run.returncode, 0, dry_run.stderr)
        dry_payload = json.loads(dry_run.stdout)
        self.assertTrue(dry_payload["dry_run"])
        self.assertEqual(dry_payload["changed"], 5)
        unchanged = json.loads(registry_path.read_text(encoding="utf-8"))
        self.assertEqual(unchanged["features"][0]["implementation_status"], "absent")
        self.assertEqual(unchanged["profiles"][0]["status"], "draft")

        result = run_cli("registry", "sync-statuses", str(repo))
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["changed"], 5)

        updated = json.loads(registry_path.read_text(encoding="utf-8"))
        self.assertEqual(updated["evidence"][0]["status"], "passed")
        self.assertEqual(updated["tests"][0]["status"], "passing")
        self.assertEqual(updated["claims"][0]["status"], "certified")
        self.assertEqual(updated["features"][0]["implementation_status"], "implemented")
        self.assertEqual(updated["profiles"][0]["status"], "active")

    def test_registry_sync_statuses_keeps_planned_placeholders_planned(self) -> None:
        temp_dir = temp_repo_from_fixture("repo_valid")
        self.addCleanup(temp_dir.cleanup)
        repo = Path(temp_dir.name) / "repo"
        registry_path = repo / ".ssot" / "registry.json"
        registry = json.loads(registry_path.read_text(encoding="utf-8"))

        test_path = repo / "tests" / "planned" / "test_placeholder.py"
        evidence_path = repo / ".ssot" / "evidence" / "planned" / "placeholder.json"
        test_path.parent.mkdir(parents=True, exist_ok=True)
        evidence_path.parent.mkdir(parents=True, exist_ok=True)
        test_path.write_text("def test_placeholder():\n    assert True\n", encoding="utf-8")
        evidence_path.write_text("{}", encoding="utf-8")

        feature_id = "feat:planned.placeholder"
        claim_id = "clm:planned.placeholder.t1"
        test_id = "tst:planned.placeholder"
        evidence_id = "evd:planned.placeholder"
        registry["features"].append(
            {
                "id": feature_id,
                "title": "Planned placeholder feature",
                "description": "Feature with planned placeholder support.",
                "implementation_status": "absent",
                "lifecycle": {"stage": "active", "replacement_feature_ids": [], "note": None},
                "plan": {"horizon": "next", "slot": None, "target_claim_tier": "T1", "target_lifecycle_stage": "active"},
                "requires": [],
                "spec_ids": [],
                "claim_ids": [claim_id],
                "test_ids": [test_id],
            }
        )
        registry["claims"].append(
            {
                "id": claim_id,
                "title": "Planned placeholder claim",
                "status": "proposed",
                "tier": "T1",
                "kind": "conformance",
                "description": "Planned placeholder support must not certify.",
                "feature_ids": [feature_id],
                "test_ids": [test_id],
                "evidence_ids": [evidence_id],
            }
        )
        registry["tests"].append(
            {
                "id": test_id,
                "title": "Planned placeholder test",
                "status": "planned",
                "kind": "conformance",
                "path": "tests/planned/test_placeholder.py",
                "feature_ids": [feature_id],
                "claim_ids": [claim_id],
                "evidence_ids": [evidence_id],
            }
        )
        registry["evidence"].append(
            {
                "id": evidence_id,
                "title": "Planned placeholder evidence",
                "status": "planned",
                "kind": "report",
                "tier": "T1",
                "path": ".ssot/evidence/planned/placeholder.json",
                "claim_ids": [claim_id],
                "test_ids": [test_id],
            }
        )
        registry_path.write_text(stable_json_dumps(registry), encoding="utf-8")

        result = run_cli("registry", "sync-statuses", str(repo))
        self.assertEqual(result.returncode, 0, result.stderr)

        updated = json.loads(registry_path.read_text(encoding="utf-8"))
        feature = next(row for row in updated["features"] if row["id"] == feature_id)
        claim = next(row for row in updated["claims"] if row["id"] == claim_id)
        test = next(row for row in updated["tests"] if row["id"] == test_id)
        evidence = next(row for row in updated["evidence"] if row["id"] == evidence_id)
        self.assertEqual(feature["implementation_status"], "absent")
        self.assertEqual(claim["status"], "proposed")
        self.assertEqual(test["status"], "planned")
        self.assertEqual(evidence["status"], "planned")


if __name__ == "__main__":
    unittest.main()
