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


if __name__ == "__main__":
    unittest.main()
