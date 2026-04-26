from __future__ import annotations

import json
import unittest
from pathlib import Path

from tests.helpers import run_cli, temp_repo_from_fixture


class CliScopeFlowTests(unittest.TestCase):
    def test_pre_freeze_scope_flow_covers_adr_spec_feature_and_test(self) -> None:
        temp_dir = temp_repo_from_fixture("repo_valid")
        self.addCleanup(temp_dir.cleanup)
        repo = Path(temp_dir.name) / "repo"
        baseline_registry = json.loads((repo / ".ssot" / "registry.json").read_text(encoding="utf-8"))

        adr_body = repo / "adr-body.yaml"
        adr_body.write_text('body: |-\n  Scope the login rollout before freeze.\n', encoding="utf-8")
        spec_body = repo / "spec-body.yaml"
        spec_body.write_text('body: |-\n  Define the pre-freeze login contract.\n', encoding="utf-8")

        adr_create = run_cli(
            "adr",
            "create",
            str(repo),
            "--title",
            "Scope login rollout",
            "--slug",
            "scope-login-rollout",
            "--body-file",
            str(adr_body),
        )
        self.assertEqual(adr_create.returncode, 0, adr_create.stderr)
        self.assertEqual(json.loads(adr_create.stdout)["document"]["id"], "adr:1000")

        spec_create = run_cli(
            "spec",
            "create",
            str(repo),
            "--title",
            "Login pre-freeze contract",
            "--slug",
            "login-pre-freeze-contract",
            "--body-file",
            str(spec_body),
            "--kind",
            "operational",
            "--adr-ids",
            "adr:1000",
        )
        self.assertEqual(spec_create.returncode, 0, spec_create.stderr)
        self.assertEqual(json.loads(spec_create.stdout)["document"]["id"], "spc:1000")

        feature_create = run_cli(
            "feature",
            "create",
            str(repo),
            "--id",
            "feat:demo.login",
            "--title",
            "User login",
            "--spec-ids",
            "spc:1000",
            "--claim-ids",
            "clm:rfc.9000.connection-migration.t3",
        )
        self.assertEqual(feature_create.returncode, 0, feature_create.stderr)
        feature_payload = json.loads(feature_create.stdout)
        self.assertEqual(feature_payload["entity"]["spec_ids"], ["spc:1000"])

        test_path = repo / "tests" / "test_login.py"
        test_path.parent.mkdir(parents=True, exist_ok=True)
        test_path.write_text("def test_login():\n    assert True\n", encoding="utf-8")

        test_create = run_cli(
            "test",
            "create",
            str(repo),
            "--id",
            "tst:demo.login.unit",
            "--title",
            "Login unit",
            "--status",
            "passing",
            "--kind",
            "unit",
            "--test-path",
            "tests/test_login.py",
            "--feature-ids",
            "feat:demo.login",
            "--claim-ids",
            "clm:rfc.9000.connection-migration.t3",
            "--evidence-ids",
            "evd:t3.rfc.9000.connection-migration.bundle",
        )
        self.assertEqual(test_create.returncode, 0, test_create.stderr)

        feature_plan = run_cli(
            "feature",
            "plan",
            str(repo),
            "--ids",
            "feat:demo.login",
            "--horizon",
            "current",
            "--claim-tier",
            "T3",
            "--target-lifecycle-stage",
            "active",
        )
        self.assertEqual(feature_plan.returncode, 0, feature_plan.stderr)

        feature_link = run_cli(
            "feature",
            "link",
            str(repo),
            "--id",
            "feat:demo.login",
            "--test-ids",
            "tst:demo.login.unit",
        )
        self.assertEqual(feature_link.returncode, 0, feature_link.stderr)

        registry = json.loads((repo / ".ssot" / "registry.json").read_text(encoding="utf-8"))
        adr = next(row for row in registry["adrs"] if row["id"] == "adr:1000")
        spec = next(row for row in registry["specs"] if row["id"] == "spc:1000")
        feature = next(row for row in registry["features"] if row["id"] == "feat:demo.login")
        test_row = next(row for row in registry["tests"] if row["id"] == "tst:demo.login.unit")

        self.assertEqual(adr["title"], "Scope login rollout")
        self.assertEqual(spec["adr_ids"], ["adr:1000"])
        self.assertEqual(feature["spec_ids"], ["spc:1000"])
        self.assertEqual(feature["claim_ids"], ["clm:rfc.9000.connection-migration.t3"])
        self.assertEqual(feature["plan"]["horizon"], "current")
        self.assertEqual(feature["plan"]["target_claim_tier"], "T3")
        self.assertEqual(feature["test_ids"], ["tst:demo.login.unit"])
        self.assertEqual(test_row["feature_ids"], ["feat:demo.login"])
        self.assertEqual(test_row["claim_ids"], ["clm:rfc.9000.connection-migration.t3"])
        self.assertEqual(test_row["evidence_ids"], ["evd:t3.rfc.9000.connection-migration.bundle"])

        self.assertTrue((repo / ".ssot" / "adr" / "ADR-1000-scope-login-rollout.yaml").exists())
        self.assertTrue((repo / ".ssot" / "specs" / "SPEC-1000-login-pre-freeze-contract.yaml").exists())
        self.assertEqual(len(registry["boundaries"]), len(baseline_registry["boundaries"]))
        self.assertEqual(len(registry["releases"]), len(baseline_registry["releases"]))


if __name__ == "__main__":
    unittest.main()
