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

        for feature in features.values():
            self.assertEqual(feature["implementation_status"], "implemented", feature["id"])
            self.assertIn(feature["plan"]["horizon"], {"current", "explicit"}, feature["id"])
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
            self.assertEqual(test["status"], "passing", test["id"])
            self.assertTrue(test["evidence_ids"], test["id"])

        for evidence_row in evidence.values():
            self.assertEqual(evidence_row["status"], "passed", evidence_row["id"])

    def test_full_certification_boundary_and_release_cover_all_features(self) -> None:
        registry = json.loads((REPO_ROOT / ".ssot" / "registry.json").read_text(encoding="utf-8"))
        feature_ids = sorted(row["id"] for row in registry["features"])

        boundary = next(row for row in registry["boundaries"] if row["id"] == "bnd:full-cert")
        self.assertTrue(boundary["frozen"])
        self.assertEqual(boundary["status"], "frozen")
        self.assertEqual(sorted(boundary["feature_ids"]), feature_ids)

        release = next(row for row in registry["releases"] if row["id"] == "rel:full-cert")
        self.assertEqual(release["boundary_id"], "bnd:full-cert")
        self.assertEqual(release["status"], "candidate")

        claim_ids = sorted(row["id"] for row in registry["claims"])
        evidence_ids = sorted(row["id"] for row in registry["evidence"])
        self.assertEqual(sorted(release["claim_ids"]), claim_ids)
        self.assertEqual(sorted(release["evidence_ids"]), evidence_ids)
