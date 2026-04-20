from __future__ import annotations

import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


class SpecAdrDeliveryInventoryTests(unittest.TestCase):
    def test_delta_boundary_and_release_cover_spec_adr_delivery(self) -> None:
        registry = json.loads((REPO_ROOT / ".ssot" / "registry.json").read_text(encoding="utf-8"))

        feature_ids = sorted(
            [
                "feat:schema.spec-adr-ids",
                "feat:api.spec-adr-linking",
                "feat:cli.flag.adr-ids",
                "feat:migration.spec-adr-ids-rollout",
                "feat:graph.spec-adr-visibility",
            ]
        )
        claim_ids = sorted(
            [
                "clm:schema.spec-adr-ids.t1",
                "clm:api.spec-adr-linking.t1",
                "clm:cli.flag.adr-ids.t1",
                "clm:migration.spec-adr-ids-rollout.t1",
                "clm:graph.spec-adr-visibility.t1",
            ]
        )
        evidence_ids = sorted(
            [
                "evd:t1.spec-adr-ids.validation",
                "evd:t1.spec-adr-linking.api",
                "evd:t1.cli.flag.adr-ids",
                "evd:t1.migration.spec-adr-ids-rollout",
                "evd:t1.graph.spec-adr-visibility",
            ]
        )

        boundary = next(row for row in registry["boundaries"] if row["id"] == "bnd:spec-adr-linking")
        self.assertTrue(boundary["frozen"])
        self.assertEqual(boundary["status"], "frozen")
        self.assertEqual(sorted(boundary["feature_ids"]), feature_ids)

        release = next(row for row in registry["releases"] if row["id"] == "rel:spec-adr-linking")
        self.assertEqual(release["status"], "certified")
        self.assertEqual(release["boundary_id"], "bnd:spec-adr-linking")
        self.assertEqual(sorted(release["claim_ids"]), claim_ids)
        self.assertEqual(sorted(release["evidence_ids"]), evidence_ids)


if __name__ == "__main__":
    unittest.main()
