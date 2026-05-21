from __future__ import annotations

import json
import unittest
from pathlib import Path

from tests.helpers import run_cli, temp_repo_from_fixture


class CliReleaseFlowTests(unittest.TestCase):
    def test_release_certify_propagates_release_context_feedback(self) -> None:
        temp_dir = temp_repo_from_fixture("repo_valid")
        self.addCleanup(temp_dir.cleanup)
        repo = Path(temp_dir.name) / "repo"

        certify = run_cli("release", "certify", str(repo), "--release-id", "rel:1.2.0", "--write-report")
        self.assertEqual(certify.returncode, 0, certify.stderr)
        payload = json.loads(certify.stdout)
        self.assertTrue(payload["passed"], payload)

        registry = json.loads((repo / ".ssot" / "registry.json").read_text(encoding="utf-8"))
        evidence = {row["id"]: row for row in registry["evidence"]}
        bundle = evidence["evd:t3.rfc.9000.connection-migration.bundle"]
        self.assertEqual(bundle["release_context"]["release_id"], "rel:1.2.0")
        self.assertEqual(bundle["release_context"]["boundary_id"], "bnd:2026q2.core")
        self.assertEqual(bundle["release_context"]["boundary_ids"], ["bnd:2026q2.core"])
        self.assertEqual(bundle["release_context"]["verification_report_result"], "certified")
        self.assertEqual(bundle["release_context"]["blocking_issue_result"], "clear")
        self.assertEqual(bundle["release_context"]["blocking_risk_result"], "clear")

    def test_full_release_flow(self) -> None:
        temp_dir = temp_repo_from_fixture("repo_valid")
        self.addCleanup(temp_dir.cleanup)
        repo = Path(temp_dir.name) / "repo"
        create_extra_boundary = run_cli(
            "boundary",
            "create",
            str(repo),
            "--id",
            "bnd:2026q2.addon",
            "--title",
            "2026 Q2 add-on boundary",
            "--status",
            "frozen",
            "--frozen",
            "--feature-ids",
            "feat:rfc.9000.connection-migration",
        )
        self.assertEqual(create_extra_boundary.returncode, 0, create_extra_boundary.stderr)

        attach_extra_boundary = run_cli(
            "release",
            "add-boundary",
            str(repo),
            "--id",
            "rel:1.2.0",
            "--boundary-ids",
            "bnd:2026q2.addon",
        )
        self.assertEqual(attach_extra_boundary.returncode, 0, attach_extra_boundary.stderr)

        certify = run_cli("release", "certify", str(repo), "--release-id", "rel:1.2.0", "--write-report")
        self.assertEqual(certify.returncode, 0, certify.stderr)
        certify_payload = json.loads(certify.stdout)
        self.assertTrue(certify_payload["passed"], certify_payload)
        self.assertEqual(certify_payload["certification"]["summary"]["boundary_ids"], ["bnd:2026q2.core", "bnd:2026q2.addon"])

        promote = run_cli("release", "promote", str(repo), "--release-id", "rel:1.2.0")
        self.assertEqual(promote.returncode, 0, promote.stderr)
        promote_payload = json.loads(promote.stdout)
        self.assertTrue(promote_payload["passed"], promote_payload)
        self.assertEqual(promote_payload["snapshot"]["boundary_count"], 2)
        self.assertTrue((repo / ".ssot" / "releases" / "rel__1.2.0" / "release.snapshot.json").exists())

        publish = run_cli("release", "publish", str(repo), "--release-id", "rel:1.2.0")
        self.assertEqual(publish.returncode, 0, publish.stderr)
        publish_payload = json.loads(publish.stdout)
        self.assertTrue(publish_payload["passed"], publish_payload)
        self.assertTrue((repo / ".ssot" / "releases" / "rel__1.2.0" / "published.snapshot.json").exists())

        graph = run_cli("graph", "export", str(repo), "--format", "json")
        self.assertEqual(graph.returncode, 0, graph.stderr)
        graph_payload = json.loads(graph.stdout)
        self.assertTrue(graph_payload["passed"], graph_payload)
        self.assertTrue((repo / ".ssot" / "graphs" / "registry.graph.json").exists())


if __name__ == "__main__":
    unittest.main()
