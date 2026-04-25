from __future__ import annotations

import json
import unittest
from pathlib import Path

from tests.helpers import run_cli, temp_repo_from_fixture


class CliIssueSurfaceTests(unittest.TestCase):
    def setUp(self) -> None:
        temp_dir = temp_repo_from_fixture("repo_valid")
        self.addCleanup(temp_dir.cleanup)
        self.repo = Path(temp_dir.name) / "repo"

    def _run_ok(self, *args: str) -> dict[str, object] | list[dict[str, object]]:
        result = run_cli(*args)
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)

    def _run_error(self, *args: str) -> dict[str, object]:
        result = run_cli(*args)
        self.assertNotEqual(result.returncode, 0)
        return json.loads(result.stdout)

    def _get_issue(self, issue_id: str) -> dict[str, object]:
        payload = self._run_ok("issue", "get", str(self.repo), "--id", issue_id)
        self.assertIsInstance(payload, dict)
        return payload

    def _get_risk(self, risk_id: str) -> dict[str, object]:
        payload = self._run_ok("risk", "get", str(self.repo), "--id", risk_id)
        self.assertIsInstance(payload, dict)
        return payload

    def _assert_issue_fields(self, issue_id: str, **expected: object) -> dict[str, object]:
        issue = self._get_issue(issue_id)
        for field_name, expected_value in expected.items():
            if field_name == "plan":
                self.assertEqual(issue["plan"], expected_value)
            else:
                self.assertEqual(issue[field_name], expected_value)
        return issue

    def _create_supporting_risk(self, risk_id: str = "rsk:cli.generated") -> dict[str, object]:
        payload = self._run_ok(
            "risk",
            "create",
            str(self.repo),
            "--id",
            risk_id,
            "--title",
            "CLI supporting risk",
            "--severity",
            "high",
            "--description",
            "supporting risk for issue tests",
            "--feature-ids",
            "feat:rfc.9000.connection-migration",
        )
        self.assertIsInstance(payload, dict)
        return payload

    def test_issue_create_get_and_list_variants(self) -> None:
        create_payload = self._run_ok(
            "issue",
            "create",
            str(self.repo),
            "--id",
            "iss:cli.generated",
            "--title",
            "CLI generated issue",
            "--status",
            "blocked",
            "--severity",
            "critical",
            "--description",
            "generated issue",
            "--horizon",
            "explicit",
            "--slot",
            "2026.q3",
            "--feature-ids",
            "feat:rfc.9000.connection-migration",
            "--claim-ids",
            "clm:rfc.9000.connection-migration.t3",
            "--test-ids",
            "tst:pytest.rfc.9000.connection-migration",
            "--evidence-ids",
            "evd:t3.rfc.9000.connection-migration.bundle",
            "--release-blocking",
        )
        self.assertTrue(create_payload["passed"])
        self._assert_issue_fields(
            "iss:cli.generated",
            id="iss:cli.generated",
            title="CLI generated issue",
            status="blocked",
            severity="critical",
            description="generated issue",
            plan={"horizon": "explicit", "slot": "2026.q3"},
            feature_ids=["feat:rfc.9000.connection-migration"],
            claim_ids=["clm:rfc.9000.connection-migration.t3"],
            test_ids=["tst:pytest.rfc.9000.connection-migration"],
            evidence_ids=["evd:t3.rfc.9000.connection-migration.bundle"],
            risk_ids=[],
            release_blocking=True,
        )

        default_create_payload = self._run_ok(
            "issue",
            "create",
            str(self.repo),
            "--id",
            "iss:cli.defaults",
            "--title",
            "CLI default issue",
            "--description",
            "default issue",
            "--no-release-blocking",
        )
        self.assertTrue(default_create_payload["passed"])
        self._assert_issue_fields(
            "iss:cli.defaults",
            status="open",
            severity="medium",
            description="default issue",
            plan={"horizon": "backlog", "slot": None},
            feature_ids=[],
            claim_ids=[],
            test_ids=[],
            evidence_ids=[],
            risk_ids=[],
            release_blocking=False,
        )

        list_payload = self._run_ok("issue", "list", str(self.repo))
        self.assertIsInstance(list_payload, list)
        self.assertEqual(
            [row["id"] for row in list_payload],
            ["iss:cli.defaults", "iss:cli.generated"],
        )

        filtered_payload = self._run_ok(
            "issue",
            "list",
            str(self.repo),
            "--ids",
            "iss:cli.generated",
        )
        self.assertEqual([row["id"] for row in filtered_payload], ["iss:cli.generated"])
        self.assertEqual(filtered_payload[0]["plan"], {"horizon": "explicit", "slot": "2026.q3"})

    def test_issue_update_plan_close_reopen_and_delete_persist_state(self) -> None:
        self._run_ok(
            "issue",
            "create",
            str(self.repo),
            "--id",
            "iss:cli.lifecycle",
            "--title",
            "CLI lifecycle issue",
            "--severity",
            "high",
            "--description",
            "before update",
            "--horizon",
            "backlog",
            "--release-blocking",
        )
        self._assert_issue_fields(
            "iss:cli.lifecycle",
            title="CLI lifecycle issue",
            severity="high",
            description="before update",
            status="open",
            plan={"horizon": "backlog", "slot": None},
            release_blocking=True,
        )

        update_payload = self._run_ok(
            "issue",
            "update",
            str(self.repo),
            "--id",
            "iss:cli.lifecycle",
            "--title",
            "CLI lifecycle issue updated",
            "--severity",
            "low",
            "--description",
            "after update",
            "--no-release-blocking",
        )
        self.assertEqual(update_payload["entity"]["title"], "CLI lifecycle issue updated")
        self._assert_issue_fields(
            "iss:cli.lifecycle",
            title="CLI lifecycle issue updated",
            severity="low",
            description="after update",
            status="open",
            plan={"horizon": "backlog", "slot": None},
            release_blocking=False,
        )

        enable_blocking_payload = self._run_ok(
            "issue",
            "update",
            str(self.repo),
            "--id",
            "iss:cli.lifecycle",
            "--release-blocking",
        )
        self.assertTrue(enable_blocking_payload["entity"]["release_blocking"])
        self._assert_issue_fields("iss:cli.lifecycle", release_blocking=True)

        plan_payload = self._run_ok(
            "issue",
            "plan",
            str(self.repo),
            "--ids",
            "iss:cli.lifecycle",
            "--horizon",
            "explicit",
            "--slot",
            "sprint-42",
        )
        self.assertTrue(plan_payload["passed"])
        self._assert_issue_fields(
            "iss:cli.lifecycle",
            plan={"horizon": "explicit", "slot": "sprint-42"},
            title="CLI lifecycle issue updated",
            severity="low",
            release_blocking=True,
        )

        self._run_ok("issue", "close", str(self.repo), "--id", "iss:cli.lifecycle")
        self._assert_issue_fields("iss:cli.lifecycle", status="closed", plan={"horizon": "explicit", "slot": "sprint-42"})

        self._run_ok("issue", "reopen", str(self.repo), "--id", "iss:cli.lifecycle")
        self._assert_issue_fields("iss:cli.lifecycle", status="open", plan={"horizon": "explicit", "slot": "sprint-42"})

        delete_payload = self._run_ok("issue", "delete", str(self.repo), "--id", "iss:cli.lifecycle")
        self.assertTrue(delete_payload["passed"])
        self.assertEqual(delete_payload["deleted_id"], "iss:cli.lifecycle")

        missing_payload = self._run_error("issue", "get", str(self.repo), "--id", "iss:cli.lifecycle")
        self.assertIn("Unknown issue id: iss:cli.lifecycle", missing_payload["error"])

    def test_issue_link_and_unlink_cover_all_supported_surfaces(self) -> None:
        self._create_supporting_risk()
        self._run_ok(
            "issue",
            "create",
            str(self.repo),
            "--id",
            "iss:cli.links",
            "--title",
            "CLI linked issue",
            "--description",
            "issue for link coverage",
            "--feature-ids",
            "feat:rfc.9000.connection-migration",
        )
        self._assert_issue_fields(
            "iss:cli.links",
            feature_ids=["feat:rfc.9000.connection-migration"],
            claim_ids=[],
            test_ids=[],
            evidence_ids=[],
            risk_ids=[],
        )

        link_payload = self._run_ok(
            "issue",
            "link",
            str(self.repo),
            "--id",
            "iss:cli.links",
            "--feature-ids",
            "feat:rfc.9000.connection-migration",
            "--claim-ids",
            "clm:rfc.9000.connection-migration.t3",
            "--test-ids",
            "tst:pytest.rfc.9000.connection-migration",
            "--evidence-ids",
            "evd:t3.rfc.9000.connection-migration.bundle",
            "--risk-ids",
            "rsk:cli.generated",
        )
        self.assertEqual(link_payload["entity"]["id"], "iss:cli.links")
        self._assert_issue_fields(
            "iss:cli.links",
            feature_ids=["feat:rfc.9000.connection-migration"],
            claim_ids=["clm:rfc.9000.connection-migration.t3"],
            test_ids=["tst:pytest.rfc.9000.connection-migration"],
            evidence_ids=["evd:t3.rfc.9000.connection-migration.bundle"],
            risk_ids=["rsk:cli.generated"],
        )

        risk = self._get_risk("rsk:cli.generated")
        self.assertEqual(risk["issue_ids"], ["iss:cli.links"])

        unlink_payload = self._run_ok(
            "issue",
            "unlink",
            str(self.repo),
            "--id",
            "iss:cli.links",
            "--claim-ids",
            "clm:rfc.9000.connection-migration.t3",
            "--test-ids",
            "tst:pytest.rfc.9000.connection-migration",
            "--evidence-ids",
            "evd:t3.rfc.9000.connection-migration.bundle",
            "--risk-ids",
            "rsk:cli.generated",
        )
        self.assertEqual(unlink_payload["entity"]["id"], "iss:cli.links")
        self._assert_issue_fields(
            "iss:cli.links",
            feature_ids=["feat:rfc.9000.connection-migration"],
            claim_ids=[],
            test_ids=[],
            evidence_ids=[],
            risk_ids=[],
        )

        risk_after_unlink = self._get_risk("rsk:cli.generated")
        self.assertEqual(risk_after_unlink["issue_ids"], [])

        relink_payload = self._run_ok(
            "issue",
            "link",
            str(self.repo),
            "--id",
            "iss:cli.links",
            "--risk-ids",
            "rsk:cli.generated",
        )
        self.assertEqual(relink_payload["entity"]["risk_ids"], ["rsk:cli.generated"])
        self.assertEqual(self._get_risk("rsk:cli.generated")["issue_ids"], ["iss:cli.links"])

    def test_issue_rejects_duplicate_empty_and_missing_operations(self) -> None:
        self._run_ok(
            "issue",
            "create",
            str(self.repo),
            "--id",
            "iss:cli.invalid",
            "--title",
            "CLI invalid operations issue",
            "--description",
            "seed issue",
        )

        duplicate_payload = self._run_error(
            "issue",
            "create",
            str(self.repo),
            "--id",
            "iss:cli.invalid",
            "--title",
            "CLI duplicate issue",
        )
        self.assertIn("Issue already exists: iss:cli.invalid", duplicate_payload["error"])

        update_payload = self._run_error("issue", "update", str(self.repo), "--id", "iss:cli.invalid")
        self.assertIn("At least one update field is required", update_payload["error"])

        link_payload = self._run_error("issue", "link", str(self.repo), "--id", "iss:cli.invalid")
        self.assertIn("At least one link field is required", link_payload["error"])

        unlink_payload = self._run_error("issue", "unlink", str(self.repo), "--id", "iss:cli.invalid")
        self.assertIn("At least one link field is required", unlink_payload["error"])

        missing_get_payload = self._run_error("issue", "get", str(self.repo), "--id", "iss:cli.missing")
        self.assertIn("Unknown issue id: iss:cli.missing", missing_get_payload["error"])

        missing_delete_payload = self._run_error("issue", "delete", str(self.repo), "--id", "iss:cli.missing")
        self.assertIn("Unknown issue id: iss:cli.missing", missing_delete_payload["error"])

        missing_close_payload = self._run_error("issue", "close", str(self.repo), "--id", "iss:cli.missing")
        self.assertIn("Unknown issue id: iss:cli.missing", missing_close_payload["error"])

        missing_reopen_payload = self._run_error("issue", "reopen", str(self.repo), "--id", "iss:cli.missing")
        self.assertIn("Unknown issue id: iss:cli.missing", missing_reopen_payload["error"])

        missing_list_payload = self._run_error(
            "issue",
            "list",
            str(self.repo),
            "--ids",
            "iss:cli.invalid",
            "iss:cli.missing",
        )
        self.assertIn("Unknown issue ids: iss:cli.missing", missing_list_payload["error"])

        missing_plan_payload = self._run_error(
            "issue",
            "plan",
            str(self.repo),
            "--ids",
            "iss:cli.invalid",
            "iss:cli.missing",
            "--horizon",
            "current",
        )
        self.assertIn("Unknown issue ids: iss:cli.missing", missing_plan_payload["error"])

    def test_issue_link_rejects_unknown_target_ids(self) -> None:
        self._run_ok(
            "issue",
            "create",
            str(self.repo),
            "--id",
            "iss:cli.permissive",
            "--title",
            "CLI permissive link issue",
            "--description",
            "issue for permissive links",
        )

        link_payload = self._run_error(
            "issue",
            "link",
            str(self.repo),
            "--id",
            "iss:cli.permissive",
            "--feature-ids",
            "feat:unknown.target",
        )
        self.assertIn(
            "issues.iss:cli.permissive.feature_ids references missing feature feat:unknown.target",
            link_payload["error"],
        )
        self._assert_issue_fields("iss:cli.permissive", feature_ids=[], claim_ids=[], test_ids=[], evidence_ids=[], risk_ids=[])


if __name__ == "__main__":
    unittest.main()
