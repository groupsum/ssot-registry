from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
for path in (
    REPO_ROOT / "pkgs" / "ssot-core" / "src",
    REPO_ROOT / "pkgs" / "ssot-conformance" / "src",
):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from ssot_conformance.catalog import build_catalog_slice

EXTRA_CONFORMANCE_FEATURE_IDS = {"feat:conformance.release-multiple-boundaries"}


class ConformanceBoundaryGovernanceTests(unittest.TestCase):
    def test_live_conformance_boundary_is_frozen_and_complete(self) -> None:
        registry = json.loads((REPO_ROOT / ".ssot" / "registry.json").read_text(encoding="utf-8"))
        boundaries = {row["id"]: row for row in registry["boundaries"]}
        features = {row["id"]: row for row in registry["features"]}
        tests = {row["id"]: row for row in registry["tests"]}
        expected_feature_ids = {row["id"] for row in build_catalog_slice(["all"])["features"]} | EXTRA_CONFORMANCE_FEATURE_IDS

        boundary = boundaries["bnd:conformance.v1"]
        self.assertTrue(boundary["frozen"])
        self.assertEqual(boundary["status"], "frozen")
        self.assertEqual(set(boundary["feature_ids"]), expected_feature_ids)

        for feature_id in sorted(expected_feature_ids):
            with self.subTest(feature_id=feature_id):
                feature = features[feature_id]
                self.assertEqual(feature["implementation_status"], "implemented")
                self.assertEqual(feature["plan"]["horizon"], "current")
                self.assertTrue(feature["test_ids"])
                for test_id in feature["test_ids"]:
                    self.assertIn(test_id, tests)
                    self.assertEqual(tests[test_id]["status"], "passing")
                    self.assertTrue((REPO_ROOT / tests[test_id]["path"]).exists(), tests[test_id]["path"])
                    self.assertIn("execution", tests[test_id])

    def test_live_conformance_boundary_snapshot_matches_registry(self) -> None:
        snapshot_path = REPO_ROOT / ".ssot" / "releases" / "boundaries" / "bnd__conformance.v1.snapshot.json"
        snapshot = json.loads(snapshot_path.read_text(encoding="utf-8"))
        expected_feature_ids = {row["id"] for row in build_catalog_slice(["all"])["features"]} | EXTRA_CONFORMANCE_FEATURE_IDS

        self.assertEqual(snapshot["summary"]["boundary_id"], "bnd:conformance.v1")
        self.assertTrue(snapshot["summary"]["frozen"])
        self.assertEqual(snapshot["summary"]["feature_count"], len(expected_feature_ids))
        self.assertEqual(set(snapshot["boundary"]["feature_ids"]), expected_feature_ids)

        snapshot_features = {row["id"]: row for row in snapshot["features"]}
        self.assertEqual(set(snapshot_features), expected_feature_ids)
        for feature_id in sorted(expected_feature_ids):
            with self.subTest(feature_id=feature_id):
                self.assertEqual(snapshot_features[feature_id]["plan"]["horizon"], "current")


if __name__ == "__main__":
    unittest.main()
