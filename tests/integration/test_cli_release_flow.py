from __future__ import annotations

import json
import unittest
from pathlib import Path

from tests.helpers import run_cli, temp_repo_from_fixture


class CliReleaseFlowTests(unittest.TestCase):
    def test_full_release_flow(self) -> None:
        temp_dir = temp_repo_from_fixture("repo_valid")
        self.addCleanup(temp_dir.cleanup)
        repo = Path(temp_dir.name) / "repo"

        certify = run_cli("release", "certify", str(repo), "--release-id", "rel:1.2.0", "--write-report")
        self.assertEqual(certify.returncode, 0, certify.stderr)
        certify_payload = json.loads(certify.stdout)
        self.assertTrue(certify_payload["passed"], certify_payload)

        promote = run_cli("release", "promote", str(repo), "--release-id", "rel:1.2.0")
        self.assertEqual(promote.returncode, 0, promote.stderr)
        promote_payload = json.loads(promote.stdout)
        self.assertTrue(promote_payload["passed"], promote_payload)
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
