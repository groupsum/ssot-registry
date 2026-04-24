from __future__ import annotations

import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


class CertificationInventoryTests(unittest.TestCase):
    def test_every_feature_has_claims_tests_and_current_or_explicit_plan(self) -> None:
        registry = json.loads((REPO_ROOT / ".ssot" / "registry.json").read_text(encoding="utf-8"))

        features = {row["id"]: row for row in registry["features"]}
        claims = {row["id"]: row for row in registry["claims"]}
        tests = {row["id"]: row for row in registry["tests"]}
        evidence = {row["id"]: row for row in registry["evidence"]}

        targeted_feature_ids = {
            feature["id"]
            for feature in features.values()
            if feature["plan"]["horizon"] in {"current", "explicit"}
        }

        for feature in features.values():
            if feature["id"] in targeted_feature_ids:
                self.assertEqual(feature["implementation_status"], "implemented", feature["id"])
            self.assertTrue(feature["claim_ids"], feature["id"])
            self.assertTrue(feature["test_ids"], feature["id"])
            for claim_id in feature["claim_ids"]:
                self.assertIn(claim_id, claims, (feature["id"], claim_id))
            for test_id in feature["test_ids"]:
                self.assertIn(test_id, tests, (feature["id"], test_id))

        for claim in claims.values():
            self.assertTrue(claim["feature_ids"], claim["id"])
            self.assertTrue(claim["test_ids"], claim["id"])
            self.assertTrue(claim["evidence_ids"], claim["id"])
            for evidence_id in claim["evidence_ids"]:
                self.assertIn(evidence_id, evidence, (claim["id"], evidence_id))

        for test in tests.values():
            if set(test["feature_ids"]) & targeted_feature_ids:
                self.assertEqual(test["status"], "passing", test["id"])
            self.assertTrue(test["evidence_ids"], test["id"])

        for evidence_row in evidence.values():
            linked_test_ids = set(evidence_row["test_ids"])
            linked_feature_ids = {
                feature_id
                for test_id in linked_test_ids
                for feature_id in tests[test_id]["feature_ids"]
            }
            if linked_feature_ids & targeted_feature_ids:
                self.assertEqual(evidence_row["status"], "passed", evidence_row["id"])

    def test_full_certification_boundary_and_release_cover_all_features(self) -> None:
        registry = json.loads((REPO_ROOT / ".ssot" / "registry.json").read_text(encoding="utf-8"))
        features = {row["id"]: row for row in registry["features"]}
        claims = {row["id"]: row for row in registry["claims"]}
        evidence = {row["id"]: row for row in registry["evidence"]}

        boundary = next(row for row in registry["boundaries"] if row["id"] == "bnd:full-cert")
        self.assertTrue(boundary["frozen"])
        self.assertEqual(boundary["status"], "frozen")
        for feature_id in boundary["feature_ids"]:
            self.assertIn(feature_id, features)

        release = next(row for row in registry["releases"] if row["id"] == "rel:full-cert")
        self.assertEqual(release["boundary_id"], "bnd:full-cert")
        self.assertEqual(release["status"], "candidate")
        for claim_id in release["claim_ids"]:
            self.assertIn(claim_id, claims)
        for evidence_id in release["evidence_ids"]:
            self.assertIn(evidence_id, evidence)
