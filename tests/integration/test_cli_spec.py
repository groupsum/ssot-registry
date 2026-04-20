from __future__ import annotations

import json
import unittest
from pathlib import Path

from tests.helpers import run_cli, workspace_tempdir


class CliSpecTests(unittest.TestCase):
    def test_spec_surface_and_immutability(self) -> None:
        with workspace_tempdir() as temp_dir:
            repo = Path(temp_dir) / "repo"
            repo.mkdir()
            init = run_cli("init", str(repo), "--repo-id", "repo:spec-cli", "--repo-name", "spec-cli", "--version", "1.0.0")
            self.assertEqual(init.returncode, 0, init.stderr)

            body = repo / "spec-body.md"
            body.write_text("Local spec body.\n", encoding="utf-8")
            create = run_cli(
                "spec",
                "create",
                str(repo),
                "--title",
                "Local operating spec",
                "--slug",
                "local-operating-spec",
                "--body-file",
                str(body),
                "--kind",
                "operational",
            )
            self.assertEqual(create.returncode, 0, create.stderr)
            payload = json.loads(create.stdout)
            self.assertEqual(payload["document"]["id"], "spc:1000")
            created_path = repo / ".ssot" / "specs" / "SPEC-1000-local-operating-spec.yaml"
            self.assertTrue(created_path.exists())
            self.assertFalse(created_path.read_text(encoding="utf-8").lstrip().startswith("{"))

            get_result = run_cli("spec", "get", str(repo), "--id", "spc:1000")
            self.assertEqual(get_result.returncode, 0, get_result.stderr)
            get_payload = json.loads(get_result.stdout)
            self.assertEqual(get_payload["title"], "Local operating spec")
            self.assertNotIn("feature_ids", get_payload)
            self.assertNotIn("payload", get_payload)

            feature_create = run_cli(
                "feature",
                "create",
                str(repo),
                "--id",
                "feat:spec-linked",
                "--title",
                "Spec linked feature",
                "--spec-ids",
                "spc:1000",
            )
            self.assertEqual(feature_create.returncode, 0, feature_create.stderr)
            feature_payload = json.loads(feature_create.stdout)
            self.assertEqual(feature_payload["entity"]["spec_ids"], ["spc:1000"])

            delete_referenced = run_cli("spec", "delete", str(repo), "--id", "spc:1000")
            self.assertEqual(delete_referenced.returncode, 1)
            self.assertIn("features.feat:spec-linked.spec_ids", delete_referenced.stdout)

            update = run_cli("spec", "update", str(repo), "--id", "spc:1000", "--title", "Local operating spec updated")
            self.assertEqual(update.returncode, 0, update.stderr)
            self.assertEqual(json.loads(update.stdout)["document"]["title"], "Local operating spec updated")
            set_status = run_cli("spec", "set-status", str(repo), "--id", "spc:1000", "--status", "in_review", "--note", "review")
            self.assertEqual(set_status.returncode, 0, set_status.stderr)
            self.assertEqual(json.loads(set_status.stdout)["document"]["status"], "in_review")

            body2 = repo / "spec-body-2.md"
            body2.write_text("Local replacement spec body.\n", encoding="utf-8")
            create2 = run_cli(
                "spec",
                "create",
                str(repo),
                "--title",
                "Replacement spec",
                "--slug",
                "replacement-spec",
                "--body-file",
                str(body2),
                "--kind",
                "operational",
                "--status",
                "accepted",
            )
            self.assertEqual(create2.returncode, 0, create2.stderr)
            supersede = run_cli("spec", "supersede", str(repo), "--id", "spc:1001", "--supersedes", "spc:1000", "--note", "newer")
            self.assertEqual(supersede.returncode, 0, supersede.stderr)
            superseded_doc = json.loads(run_cli("spec", "get", str(repo), "--id", "spc:1000").stdout)
            self.assertEqual(superseded_doc["status"], "superseded")

            delete_ssot = run_cli("spec", "delete", str(repo), "--id", "spc:0600")
            self.assertEqual(delete_ssot.returncode, 1)
            self.assertIn("immutable", delete_ssot.stdout)

    def test_spec_create_inside_ssot_range_fails(self) -> None:
        with workspace_tempdir() as temp_dir:
            repo = Path(temp_dir) / "repo"
            repo.mkdir()
            init = run_cli("init", str(repo), "--repo-id", "repo:spec-range", "--repo-name", "spec-range", "--version", "1.0.0")
            self.assertEqual(init.returncode, 0, init.stderr)

            body = repo / "spec-body.md"
            body.write_text("Local spec body.\n", encoding="utf-8")
            create = run_cli(
                "spec",
                "create",
                str(repo),
                "--title",
                "Conflicting spec",
                "--slug",
                "conflicting-spec",
                "--body-file",
                str(body),
                "--number",
                "9",
            )
            self.assertEqual(create.returncode, 1)
            self.assertIn("non-assignable reservation", create.stdout)

    def test_spec_list_sync_and_reservations(self) -> None:
        with workspace_tempdir() as temp_dir:
            repo = Path(temp_dir) / "repo"
            repo.mkdir()
            init = run_cli("init", str(repo), "--repo-id", "repo:spec-sync", "--repo-name", "spec-sync", "--version", "1.0.0")
            self.assertEqual(init.returncode, 0, init.stderr)

            list_result = run_cli("spec", "list", str(repo))
            self.assertEqual(list_result.returncode, 0, list_result.stderr)
            list_payload = json.loads(list_result.stdout)
            self.assertIsInstance(list_payload, list)
            baseline_count = len(list_payload)

            sync_result = run_cli("spec", "sync", str(repo))
            self.assertEqual(sync_result.returncode, 0, sync_result.stderr)
            sync_payload = json.loads(sync_result.stdout)
            self.assertTrue(sync_payload["passed"])

            list_after_sync = run_cli("spec", "list", str(repo))
            self.assertEqual(list_after_sync.returncode, 0, list_after_sync.stderr)
            list_after_sync_payload = json.loads(list_after_sync.stdout)
            self.assertIsInstance(list_after_sync_payload, list)
            self.assertGreaterEqual(len(list_after_sync_payload), baseline_count)
            synced_ids = set(sync_payload["created"] + sync_payload["updated"] + sync_payload["unchanged"])
            listed_ids = {row["id"] for row in list_after_sync_payload}
            self.assertTrue(synced_ids.issubset(listed_ids))

            reserve_create = run_cli("spec", "reserve", "create", str(repo), "--name", "origin:repo-test", "--start", "5200", "--end", "5299")
            self.assertEqual(reserve_create.returncode, 0, reserve_create.stderr)
            reserve_payload = json.loads(reserve_create.stdout)
            self.assertTrue(reserve_payload["passed"])
            self.assertEqual(reserve_payload["reservation"]["owner"], "origin:repo-test")

            reserve_list = run_cli("spec", "reserve", "list", str(repo))
            self.assertEqual(reserve_list.returncode, 0, reserve_list.stderr)
            reserve_list_payload = json.loads(reserve_list.stdout)
            self.assertTrue(reserve_list_payload["passed"])
            reservation_rows = reserve_list_payload["reservations"]
            self.assertIn(
                {"owner": "origin:repo-test", "start": 5200, "end": 5299, "immutable": False, "deletable": True, "assignable_by_repo": True},
                reservation_rows,
            )


if __name__ == "__main__":
    unittest.main()
