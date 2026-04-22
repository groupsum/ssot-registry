from __future__ import annotations

import json
import unittest
from pathlib import Path

from tests.helpers import run_cli, workspace_tempdir


class CliAdrTests(unittest.TestCase):
    def test_adr_surface_and_immutability(self) -> None:
        with workspace_tempdir() as temp_dir:
            repo = Path(temp_dir) / "repo"
            repo.mkdir()
            init = run_cli("init", str(repo), "--repo-id", "repo:adr-cli", "--repo-name", "adr-cli", "--version", "1.0.0")
            self.assertEqual(init.returncode, 0, init.stderr)

            body = repo / "adr-body.yaml"
            body.write_text('body: |-\n  Local ADR body.\n', encoding="utf-8")
            create = run_cli(
                "adr",
                "create",
                str(repo),
                "--title",
                "Local decision",
                "--slug",
                "local-decision",
                "--body-file",
                str(body),
            )
            self.assertEqual(create.returncode, 0, create.stderr)
            payload = json.loads(create.stdout)
            self.assertEqual(payload["document"]["id"], "adr:1000")
            created_path = repo / ".ssot" / "adr" / "ADR-1000-local-decision.yaml"
            self.assertTrue(created_path.exists())
            self.assertFalse(created_path.read_text(encoding="utf-8").lstrip().startswith("{"))

            get_result = run_cli("adr", "get", str(repo), "--id", "adr:1000")
            self.assertEqual(get_result.returncode, 0, get_result.stderr)
            get_payload = json.loads(get_result.stdout)
            self.assertEqual(get_payload["title"], "Local decision")
            self.assertNotIn("payload", get_payload)

            body.write_text('body: |-\n  Updated ADR body.\n', encoding="utf-8")
            update = run_cli("adr", "update", str(repo), "--id", "adr:1000", "--title", "Local decision updated", "--body-file", str(body))
            self.assertEqual(update.returncode, 0, update.stderr)
            self.assertEqual(json.loads(update.stdout)["document"]["title"], "Local decision updated")
            set_status = run_cli("adr", "set-status", str(repo), "--id", "adr:1000", "--status", "in_review", "--note", "ready")
            self.assertEqual(set_status.returncode, 0, set_status.stderr)
            self.assertEqual(json.loads(set_status.stdout)["document"]["status"], "in_review")

            body2 = repo / "adr-body-2.yaml"
            body2.write_text('body: |-\n  Another ADR.\n', encoding="utf-8")
            create2 = run_cli(
                "adr",
                "create",
                str(repo),
                "--title",
                "Second local decision",
                "--slug",
                "second-local-decision",
                "--body-file",
                str(body2),
                "--status",
                "accepted",
            )
            self.assertEqual(create2.returncode, 0, create2.stderr)
            list_by_ids = run_cli("adr", "list", str(repo), "--ids", "adr:1000", "adr:1001")
            self.assertEqual(list_by_ids.returncode, 0, list_by_ids.stderr)
            list_by_ids_payload = json.loads(list_by_ids.stdout)
            self.assertEqual([row["id"] for row in list_by_ids_payload], ["adr:1000", "adr:1001"])

            supersede = run_cli("adr", "supersede", str(repo), "--id", "adr:1001", "--supersedes", "adr:1000", "--note", "replaced")
            self.assertEqual(supersede.returncode, 0, supersede.stderr)
            superseded_doc = json.loads(run_cli("adr", "get", str(repo), "--id", "adr:1000").stdout)
            self.assertEqual(superseded_doc["status"], "superseded")

            delete_ssot = run_cli("adr", "delete", str(repo), "--id", "adr:0600")
            self.assertEqual(delete_ssot.returncode, 1)
            self.assertIn("immutable", delete_ssot.stdout)

            delete_local = run_cli("adr", "delete", str(repo), "--id", "adr:1000")
            self.assertEqual(delete_local.returncode, 1)

    def test_adr_create_inside_ssot_range_fails(self) -> None:
        with workspace_tempdir() as temp_dir:
            repo = Path(temp_dir) / "repo"
            repo.mkdir()
            init = run_cli("init", str(repo), "--repo-id", "repo:adr-range", "--repo-name", "adr-range", "--version", "1.0.0")
            self.assertEqual(init.returncode, 0, init.stderr)

            body = repo / "adr-body.yaml"
            body.write_text('body: |-\n  Local ADR body.\n', encoding="utf-8")
            create = run_cli(
                "adr",
                "create",
                str(repo),
                "--title",
                "Conflicting decision",
                "--slug",
                "conflicting-decision",
                "--body-file",
                str(body),
                "--number",
                "7",
            )
            self.assertEqual(create.returncode, 1)
            self.assertIn("non-assignable reservation", create.stdout)

    def test_adr_list_sync_and_reservations(self) -> None:
        with workspace_tempdir() as temp_dir:
            repo = Path(temp_dir) / "repo"
            repo.mkdir()
            init = run_cli("init", str(repo), "--repo-id", "repo:adr-sync", "--repo-name", "adr-sync", "--version", "1.0.0")
            self.assertEqual(init.returncode, 0, init.stderr)

            list_result = run_cli("adr", "list", str(repo))
            self.assertEqual(list_result.returncode, 0, list_result.stderr)
            list_payload = json.loads(list_result.stdout)
            self.assertIsInstance(list_payload, list)
            baseline_count = len(list_payload)

            sync_result = run_cli("adr", "sync", str(repo))
            self.assertEqual(sync_result.returncode, 0, sync_result.stderr)
            sync_payload = json.loads(sync_result.stdout)
            self.assertTrue(sync_payload["passed"])

            list_after_sync = run_cli("adr", "list", str(repo))
            self.assertEqual(list_after_sync.returncode, 0, list_after_sync.stderr)
            list_after_sync_payload = json.loads(list_after_sync.stdout)
            self.assertIsInstance(list_after_sync_payload, list)
            self.assertGreaterEqual(len(list_after_sync_payload), baseline_count)
            synced_ids = set(sync_payload["created"] + sync_payload["updated"] + sync_payload["unchanged"])
            listed_ids = {row["id"] for row in list_after_sync_payload}
            self.assertTrue(synced_ids.issubset(listed_ids))

            reserve_create = run_cli("adr", "reserve", "create", str(repo), "--name", "origin:repo-test", "--start", "5100", "--end", "5199")
            self.assertEqual(reserve_create.returncode, 0, reserve_create.stderr)
            reserve_payload = json.loads(reserve_create.stdout)
            self.assertTrue(reserve_payload["passed"])
            self.assertEqual(reserve_payload["reservation"]["owner"], "origin:repo-test")

            reserve_list = run_cli("adr", "reserve", "list", str(repo))
            self.assertEqual(reserve_list.returncode, 0, reserve_list.stderr)
            reserve_list_payload = json.loads(reserve_list.stdout)
            self.assertTrue(reserve_list_payload["passed"])
            reservation_rows = reserve_list_payload["reservations"]
            self.assertIn(
                {"owner": "origin:repo-test", "start": 5100, "end": 5199, "immutable": False, "deletable": True, "assignable_by_repo": True},
                reservation_rows,
            )

    def test_adr_create_and_update_support_inline_body(self) -> None:
        with workspace_tempdir() as temp_dir:
            repo = Path(temp_dir) / "repo"
            repo.mkdir()
            init = run_cli("init", str(repo), "--repo-id", "repo:adr-inline", "--repo-name", "adr-inline", "--version", "1.0.0")
            self.assertEqual(init.returncode, 0, init.stderr)

            create = run_cli(
                "adr",
                "create",
                str(repo),
                "--title",
                "Inline ADR",
                "--slug",
                "inline-adr",
                "--body",
                "Inline ADR body.",
            )
            self.assertEqual(create.returncode, 0, create.stderr)

            update = run_cli("adr", "update", str(repo), "--id", "adr:1000", "--body", "Updated inline ADR body.")
            self.assertEqual(update.returncode, 0, update.stderr)

            get_result = run_cli("adr", "get", str(repo), "--id", "adr:1000")
            self.assertEqual(get_result.returncode, 0, get_result.stderr)
            self.assertEqual(json.loads(get_result.stdout)["title"], "Inline ADR")

    def test_adr_cli_rejects_missing_or_conflicting_body_sources(self) -> None:
        with workspace_tempdir() as temp_dir:
            repo = Path(temp_dir) / "repo"
            repo.mkdir()
            init = run_cli("init", str(repo), "--repo-id", "repo:adr-conflict", "--repo-name", "adr-conflict", "--version", "1.0.0")
            self.assertEqual(init.returncode, 0, init.stderr)

            body = repo / "adr-body.yaml"
            body.write_text('body: |-\n  Local ADR body.\n', encoding="utf-8")

            missing = run_cli("adr", "create", str(repo), "--title", "No body", "--slug", "no-body")
            self.assertEqual(missing.returncode, 1)
            self.assertIn("requires exactly one of body or body_file", missing.stdout)

            conflict = run_cli(
                "adr",
                "create",
                str(repo),
                "--title",
                "Conflicting body",
                "--slug",
                "conflicting-body",
                "--body",
                "Inline ADR body.",
                "--body-file",
                str(body),
            )
            self.assertEqual(conflict.returncode, 1)
            self.assertIn("accepts only one of body or body_file", conflict.stdout)


if __name__ == "__main__":
    unittest.main()
