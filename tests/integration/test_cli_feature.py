from __future__ import annotations

import json
import unittest
from pathlib import Path

from tests.helpers import run_cli, temp_repo_from_fixture


class CliFeatureTests(unittest.TestCase):
    def test_feature_create_auto_scaffolds_proof_graph_by_default(self) -> None:
        temp_dir = temp_repo_from_fixture("repo_valid")
        self.addCleanup(temp_dir.cleanup)
        repo = Path(temp_dir.name) / "repo"

        create = run_cli(
            "feature",
            "create",
            str(repo),
            "--id",
            "feat:cli.scaffolded",
            "--title",
            "CLI scaffolded feature",
            "--description",
            "generated scaffold graph",
            "--implementation-status",
            "partial",
            "--horizon",
            "current",
            "--claim-tier",
            "T2",
        )
        self.assertEqual(create.returncode, 0, create.stderr)
        payload = json.loads(create.stdout)
        self.assertTrue(payload["passed"])
        self.assertEqual(payload["entity"]["id"], "feat:cli.scaffolded")
        self.assertEqual(
            payload["scaffolded"]["claim_ids"],
            ["clm:cli.scaffolded.t0", "clm:cli.scaffolded.t1", "clm:cli.scaffolded.t2"],
        )
        self.assertEqual(payload["scaffolded"]["test_id"], "tst:pytest.cli.scaffolded.t2.proof-graph")
        self.assertEqual(
            payload["scaffolded"]["test_ids"],
            [
                "tst:pytest.cli.scaffolded.t0.proof-graph",
                "tst:pytest.cli.scaffolded.t1.proof-graph",
                "tst:pytest.cli.scaffolded.t2.proof-graph",
            ],
        )
        self.assertEqual(payload["scaffolded"]["evidence_id"], "evd:t2.cli.scaffolded.proof-graph")
        self.assertTrue((repo / payload["scaffolded"]["test_path"]).exists())
        for test_path in payload["scaffolded"]["test_paths"]:
            self.assertTrue((repo / test_path).exists())
        self.assertTrue((repo / payload["scaffolded"]["evidence_path"]).exists())

        feature_payload = json.loads(run_cli("feature", "get", str(repo), "--id", "feat:cli.scaffolded").stdout)
        self.assertEqual(
            feature_payload["claim_ids"],
            ["clm:cli.scaffolded.t0", "clm:cli.scaffolded.t1", "clm:cli.scaffolded.t2"],
        )
        self.assertEqual(
            feature_payload["test_ids"],
            [
                "tst:pytest.cli.scaffolded.t0.proof-graph",
                "tst:pytest.cli.scaffolded.t1.proof-graph",
                "tst:pytest.cli.scaffolded.t2.proof-graph",
            ],
        )

    def test_feature_create_cli_override_can_disable_default_scaffold(self) -> None:
        temp_dir = temp_repo_from_fixture("repo_valid")
        self.addCleanup(temp_dir.cleanup)
        repo = Path(temp_dir.name) / "repo"

        create = run_cli(
            "feature",
            "create",
            str(repo),
            "--id",
            "feat:cli.no-scaffold",
            "--title",
            "CLI no scaffold feature",
            "--description",
            "current feature without scaffold should fail closed",
            "--implementation-status",
            "partial",
            "--horizon",
            "current",
            "--claim-tier",
            "T2",
            "--no-auto-scaffold-proof-graph",
        )
        self.assertNotEqual(create.returncode, 0)
        self.assertIn("has no linked claims", create.stdout)
        self.assertIn("has no linked tests", create.stdout)

    def test_non_targeted_inventory_feature_can_explicitly_opt_out_of_scaffold(self) -> None:
        temp_dir = temp_repo_from_fixture("repo_valid")
        self.addCleanup(temp_dir.cleanup)
        repo = Path(temp_dir.name) / "repo"

        create = run_cli(
            "feature",
            "create",
            str(repo),
            "--id",
            "feat:cli.inventory-parent",
            "--title",
            "CLI inventory parent",
            "--description",
            "inventory-only umbrella parent",
            "--parent-feature-ids",
            "feat:rfc.9000.connection-migration",
            "--no-auto-scaffold-proof-graph",
        )
        self.assertEqual(create.returncode, 0, create.stderr)
        payload = json.loads(create.stdout)
        self.assertEqual(payload["entity"]["claim_ids"], [])
        self.assertEqual(payload["entity"]["test_ids"], [])

    def test_feature_surface(self) -> None:
        temp_dir = temp_repo_from_fixture("repo_valid")
        self.addCleanup(temp_dir.cleanup)
        repo = Path(temp_dir.name) / "repo"
        create_body = repo / "feature-body.txt"
        create_body.write_text("generated feature body from file", encoding="utf-8")
        update_body = repo / "feature-body-update.txt"
        update_body.write_text("updated feature body from file", encoding="utf-8")

        create = run_cli(
            "feature",
            "create",
            str(repo),
            "--id",
            "feat:cli.generated",
            "--title",
            "CLI generated feature",
            "--description",
            "generated from cli test",
            "--body-file",
            str(create_body),
            "--implementation-status",
            "partial",
            "--requires",
            "feat:rfc.9000.connection-migration",
            "--parent-feature-ids",
            "feat:rfc.9000.connection-migration",
            "--no-auto-scaffold-proof-graph",
        )
        self.assertEqual(create.returncode, 0, create.stderr)
        self.assertTrue(json.loads(create.stdout)["passed"])
        self.assertFalse((repo / ".ssot" / "registry.json.lock").exists())

        get_result = run_cli("feature", "get", str(repo), "--id", "feat:cli.generated")
        self.assertEqual(get_result.returncode, 0, get_result.stderr)
        get_payload = json.loads(get_result.stdout)
        self.assertEqual(get_payload["id"], "feat:cli.generated")
        self.assertEqual(get_payload["body"], "generated feature body from file")
        self.assertEqual(get_payload["parent_feature_ids"], ["feat:rfc.9000.connection-migration"])

        list_result = run_cli("feature", "list", str(repo))
        self.assertEqual(list_result.returncode, 0, list_result.stderr)
        list_payload = json.loads(list_result.stdout)
        self.assertIsInstance(list_payload, list)
        ids = {row["id"] for row in list_payload}
        self.assertIn("feat:cli.generated", ids)
        list_by_ids = run_cli("feature", "list", str(repo), "--ids", "feat:cli.generated")
        self.assertEqual(list_by_ids.returncode, 0, list_by_ids.stderr)
        list_by_ids_payload = json.loads(list_by_ids.stdout)
        self.assertEqual([row["id"] for row in list_by_ids_payload], ["feat:cli.generated"])

        update = run_cli(
            "feature",
            "update",
            str(repo),
            "--id",
            "feat:cli.generated",
            "--title",
            "CLI generated feature updated",
            "--body-file",
            str(update_body),
        )
        self.assertEqual(update.returncode, 0, update.stderr)
        self.assertEqual(json.loads(update.stdout)["entity"]["title"], "CLI generated feature updated")
        self.assertEqual(json.loads(update.stdout)["entity"]["body"], "updated feature body from file")

        link = run_cli(
            "feature",
            "link",
            str(repo),
            "--id",
            "feat:cli.generated",
            "--claim-ids",
            "clm:rfc.9000.connection-migration.t3",
            "--test-ids",
            "tst:pytest.rfc.9000.connection-migration",
        )
        self.assertEqual(link.returncode, 0, link.stderr)

        implement = run_cli(
            "feature",
            "update",
            str(repo),
            "--id",
            "feat:cli.generated",
            "--implementation-status",
            "implemented",
        )
        self.assertEqual(implement.returncode, 0, implement.stderr)

        parent_set = run_cli(
            "feature",
            "parent",
            "set",
            str(repo),
            "--ids",
            "feat:cli.generated",
            "--parent-ids",
            "feat:rfc.9000.connection-migration",
        )
        self.assertEqual(parent_set.returncode, 0, parent_set.stderr)
        self.assertEqual(json.loads(parent_set.stdout)["entities"][0]["parent_feature_ids"], ["feat:rfc.9000.connection-migration"])

        parent_remove = run_cli(
            "feature",
            "parent",
            "remove",
            str(repo),
            "--ids",
            "feat:cli.generated",
            "--parent-ids",
            "feat:rfc.9000.connection-migration",
        )
        self.assertEqual(parent_remove.returncode, 0, parent_remove.stderr)
        self.assertEqual(json.loads(parent_remove.stdout)["entities"][0]["parent_feature_ids"], [])

        children_add = run_cli(
            "feature",
            "children",
            "add",
            str(repo),
            "--id",
            "feat:rfc.9000.connection-migration",
            "--child-ids",
            "feat:cli.generated",
        )
        self.assertEqual(children_add.returncode, 0, children_add.stderr)

        children_list = run_cli(
            "feature",
            "children",
            "list",
            str(repo),
            "--id",
            "feat:rfc.9000.connection-migration",
        )
        self.assertEqual(children_list.returncode, 0, children_list.stderr)
        self.assertEqual([row["id"] for row in json.loads(children_list.stdout)], ["feat:cli.generated"])

        failed_parent = run_cli(
            "feature",
            "parent",
            "add",
            str(repo),
            "--ids",
            "feat:cli.generated",
            "--parent-ids",
            "feat:missing.parent",
        )
        self.assertNotEqual(failed_parent.returncode, 0)
        after_failed_parent = run_cli("feature", "get", str(repo), "--id", "feat:cli.generated")
        self.assertEqual(after_failed_parent.returncode, 0, after_failed_parent.stderr)
        self.assertEqual(json.loads(after_failed_parent.stdout)["parent_feature_ids"], ["feat:rfc.9000.connection-migration"])

        children_remove = run_cli(
            "feature",
            "children",
            "remove",
            str(repo),
            "--id",
            "feat:rfc.9000.connection-migration",
            "--child-ids",
            "feat:cli.generated",
        )
        self.assertEqual(children_remove.returncode, 0, children_remove.stderr)
        self.assertEqual(json.loads(children_remove.stdout)["entities"][0]["parent_feature_ids"], [])

        parent_clear = run_cli(
            "feature",
            "parent",
            "clear",
            str(repo),
            "--ids",
            "feat:cli.generated",
        )
        self.assertEqual(parent_clear.returncode, 0, parent_clear.stderr)
        self.assertEqual(json.loads(parent_clear.stdout)["entities"][0]["parent_feature_ids"], [])

        plan = run_cli(
            "feature",
            "plan",
            str(repo),
            "--ids",
            "feat:cli.generated",
            "--horizon",
            "current",
            "--claim-tier",
            "T3",
            "--target-lifecycle-stage",
            "active",
        )
        self.assertEqual(plan.returncode, 0, plan.stderr)

        lifecycle = run_cli(
            "feature",
            "lifecycle",
            "set",
            str(repo),
            "--ids",
            "feat:cli.generated",
            "--stage",
            "deprecated",
            "--note",
            "sunsetting test feature",
        )
        self.assertEqual(lifecycle.returncode, 0, lifecycle.stderr)

        backlog = run_cli(
            "feature",
            "plan",
            str(repo),
            "--ids",
            "feat:cli.generated",
            "--horizon",
            "backlog",
            "--target-lifecycle-stage",
            "deprecated",
        )
        self.assertEqual(backlog.returncode, 0, backlog.stderr)

        out_of_bounds = run_cli(
            "feature",
            "create",
            str(repo),
            "--id",
            "feat:cli.out-of-bounds",
            "--title",
            "CLI out-of-bounds feature",
            "--description",
            "generated from cli out-of-bounds test",
            "--implementation-status",
            "partial",
            "--horizon",
            "out_of_bounds",
            "--out-of-bounds-disposition",
            "tolerated",
            "--note",
            "Partial incidental support is tracked but not release-targeted.",
            "--no-auto-scaffold-proof-graph",
        )
        self.assertEqual(out_of_bounds.returncode, 0, out_of_bounds.stderr)
        out_of_bounds_payload = json.loads(out_of_bounds.stdout)
        self.assertEqual(
            out_of_bounds_payload["entity"]["plan"]["out_of_bounds_disposition"],
            "tolerated",
        )

        deimplement = run_cli(
            "feature",
            "update",
            str(repo),
            "--id",
            "feat:cli.generated",
            "--implementation-status",
            "partial",
        )
        self.assertEqual(deimplement.returncode, 0, deimplement.stderr)

        unlink = run_cli(
            "feature",
            "unlink",
            str(repo),
            "--id",
            "feat:cli.generated",
            "--claim-ids",
            "clm:rfc.9000.connection-migration.t3",
            "--test-ids",
            "tst:pytest.rfc.9000.connection-migration",
            "--requires",
            "feat:rfc.9000.connection-migration",
        )
        self.assertEqual(unlink.returncode, 0, unlink.stderr)

        delete = run_cli("feature", "delete", str(repo), "--id", "feat:cli.generated")
        self.assertEqual(delete.returncode, 0, delete.stderr)
        self.assertTrue(json.loads(delete.stdout)["passed"])

    def test_feature_certify_proof_graph_flow(self) -> None:
        temp_dir = temp_repo_from_fixture("repo_valid")
        self.addCleanup(temp_dir.cleanup)
        repo = Path(temp_dir.name) / "repo"

        for feature_id, title in (
            ("feat:cli.proof-graph-one", "CLI proof graph one"),
            ("feat:cli.proof-graph-two", "CLI proof graph two"),
        ):
            create = run_cli(
                "feature",
                "create",
                str(repo),
                "--id",
                feature_id,
                "--title",
                title,
                "--description",
                "scaffold for certification flow",
                "--implementation-status",
                "absent",
                "--horizon",
                "next",
                "--claim-tier",
                "T3",
                "--auto-scaffold-proof-graph",
            )
            self.assertEqual(create.returncode, 0, create.stderr)
            payload = json.loads(create.stdout)
            test_path = repo / payload["scaffolded"]["test_path"]
            test_path.write_text(
                "def test_ssot_scaffold_placeholder():\n    assert True\n",
                encoding="utf-8",
            )

        certify = run_cli(
            "feature",
            "certify-proof-graph",
            str(repo),
            "--ids",
            "feat:cli.proof-graph-one",
            "feat:cli.proof-graph-two",
            "--boundary-id",
            "bnd:cli.proof-graph",
            "--boundary-title",
            "CLI proof graph boundary",
            "--release-id",
            "rel:cli.proof-graph",
            "--release-version",
            "9.9.9",
            "--robustness-dimensions",
            "negative_cases",
            "state_transitions",
            "--write-report",
            "--promote",
            "--publish",
        )
        self.assertEqual(certify.returncode, 0, certify.stderr)
        payload = json.loads(certify.stdout)
        self.assertTrue(payload["passed"], payload)
        self.assertEqual(payload["boundary_id"], "bnd:cli.proof-graph")
        self.assertEqual(payload["release_id"], "rel:cli.proof-graph")
        self.assertEqual(payload["test_run"]["summary"]["failed"], 0)
        self.assertTrue((repo / ".ssot" / "reports" / "certification.report.json").exists())
        self.assertTrue((repo / ".ssot" / "releases" / "rel__cli.proof-graph" / "release.snapshot.json").exists())
        self.assertTrue((repo / ".ssot" / "releases" / "rel__cli.proof-graph" / "published.snapshot.json").exists())

        registry = json.loads((repo / ".ssot" / "registry.json").read_text(encoding="utf-8"))
        features = {row["id"]: row for row in registry["features"]}
        claims = {row["id"]: row for row in registry["claims"]}
        evidence = {row["id"]: row for row in registry["evidence"]}
        releases = {row["id"]: row for row in registry["releases"]}
        boundaries = {row["id"]: row for row in registry["boundaries"]}

        self.assertTrue(boundaries["bnd:cli.proof-graph"]["frozen"])
        self.assertEqual(releases["rel:cli.proof-graph"]["status"], "published")
        self.assertEqual(registry["program"]["active_boundary_id"], "bnd:cli.proof-graph")
        self.assertEqual(registry["program"]["active_release_id"], "rel:cli.proof-graph")

        for feature_id in ("feat:cli.proof-graph-one", "feat:cli.proof-graph-two"):
            self.assertEqual(features[feature_id]["implementation_status"], "implemented")
            self.assertEqual(features[feature_id]["plan"]["horizon"], "current")
            slug = feature_id.split(":", 1)[-1]
            t0_claim = claims[f"clm:{slug}.t0"]
            t1_claim = claims[f"clm:{slug}.t1"]
            t3_claim = claims[f"clm:{slug}.t3"]
            self.assertEqual(t0_claim["status"], "certified")
            self.assertEqual(t1_claim["status"], "certified")
            self.assertEqual(t3_claim["status"], "published")

            t1_evidence = evidence[f"evd:t1.{slug}.proof-graph-source"]
            t3_evidence = evidence[f"evd:t3.{slug}.proof-graph"]
            self.assertEqual(t1_evidence["status"], "passed")
            self.assertEqual(t3_evidence["status"], "passed")
            self.assertEqual(t3_evidence["source_evidence_ids"], [t1_evidence["id"]])
            self.assertEqual(t3_evidence["release_context"]["release_id"], "rel:cli.proof-graph")
            self.assertEqual(t3_evidence["release_context"]["boundary_ids"], ["bnd:cli.proof-graph"])
            self.assertEqual(t3_evidence["release_context"]["verification_report_result"], "certified")
            self.assertEqual(t3_evidence["release_context"]["blocking_issue_result"], "clear")
            self.assertEqual(t3_evidence["release_context"]["blocking_risk_result"], "clear")
            self.assertTrue((repo / t1_evidence["path"]).exists())
            self.assertTrue((repo / t3_evidence["path"]).exists())


if __name__ == "__main__":
    unittest.main()
