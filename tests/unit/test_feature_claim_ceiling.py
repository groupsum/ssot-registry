from __future__ import annotations

import json
import unittest
from copy import deepcopy
from pathlib import Path

from ssot_registry.api.profile_eval import evaluate_feature_passing
from ssot_registry.api.validate import validate_registry_document
from ssot_registry.util.jsonio import stable_json_dumps
from ssot_registry.validators.identity import build_index
from tests.helpers import temp_repo_from_fixture


class FeatureClaimCeilingTests(unittest.TestCase):
    def _registry_with_t0_implemented_feature(self) -> tuple[Path, dict[str, object], str]:
        temp_dir = temp_repo_from_fixture("repo_valid")
        self.addCleanup(temp_dir.cleanup)
        repo = Path(temp_dir.name) / "repo"
        registry = json.loads((repo / ".ssot" / "registry.json").read_text(encoding="utf-8"))
        feature = registry["features"][0]
        claim = registry["claims"][0]
        evidence = registry["evidence"][0]
        feature["id"] = "feat:claim-ceiling.validation"
        feature["claim_ids"] = ["clm:claim-ceiling.validation.t0"]
        feature["test_ids"] = ["tst:pytest.rfc.9000.connection-migration"]
        feature["plan"]["target_claim_tier"] = None
        feature["implementation_status"] = "implemented"
        claim["id"] = "clm:claim-ceiling.validation.t0"
        claim["feature_ids"] = [feature["id"]]
        claim["tier"] = "T0"
        claim["status"] = "evidenced"
        claim["evidence_ids"] = [evidence["id"]]
        registry["tests"][0]["feature_ids"] = [feature["id"]]
        registry["tests"][0]["claim_ids"] = [claim["id"]]
        evidence["claim_ids"] = [claim["id"]]
        evidence["tier"] = "T0"
        evidence["status"] = "passed"
        (repo / ".ssot" / "registry.json").write_text(stable_json_dumps(registry), encoding="utf-8")
        return repo, registry, feature["id"]

    def _registry_with_tier_ladder_feature(self) -> tuple[Path, dict[str, object], str]:
        repo, registry, feature_id = self._registry_with_t0_implemented_feature()
        feature = registry["features"][0]
        t0_claim = registry["claims"][0]
        t0_test = registry["tests"][0]
        t0_evidence = registry["evidence"][0]

        feature["claim_ids"] = [
            "clm:claim-ceiling.validation.t0",
            "clm:claim-ceiling.validation.t1",
            "clm:claim-ceiling.validation.t2",
        ]
        feature["plan"]["target_claim_tier"] = "T2"
        feature["test_ids"] = [
            "tst:claim-ceiling.validation.t0",
            "tst:claim-ceiling.validation.t1",
            "tst:claim-ceiling.validation.t2",
        ]

        t0_test["id"] = "tst:claim-ceiling.validation.t0"
        t0_test["claim_ids"] = ["clm:claim-ceiling.validation.t0"]
        t0_test["evidence_ids"] = ["evd:claim-ceiling.validation.t0"]
        t0_evidence["id"] = "evd:claim-ceiling.validation.t0"
        t0_evidence["claim_ids"] = ["clm:claim-ceiling.validation.t0"]
        t0_evidence["test_ids"] = ["tst:claim-ceiling.validation.t0"]
        t0_claim["test_ids"] = ["tst:claim-ceiling.validation.t0"]
        t0_claim["evidence_ids"] = ["evd:claim-ceiling.validation.t0"]
        t0_claim["depends_on_claim_ids"] = []

        for tier in ("T1", "T2"):
            suffix = tier.lower()
            dependency_suffix = "t0" if tier == "T1" else "t1"
            claim_id = f"clm:claim-ceiling.validation.{suffix}"
            test_id = f"tst:claim-ceiling.validation.{suffix}"
            evidence_id = f"evd:claim-ceiling.validation.{suffix}"
            claim = deepcopy(t0_claim)
            test = deepcopy(t0_test)
            evidence = deepcopy(t0_evidence)
            claim["id"] = claim_id
            claim["tier"] = tier
            claim["test_ids"] = [test_id]
            claim["evidence_ids"] = [evidence_id]
            claim["depends_on_claim_ids"] = [f"clm:claim-ceiling.validation.{dependency_suffix}"]
            test["id"] = test_id
            test["claim_ids"] = [claim_id]
            test["evidence_ids"] = [evidence_id]
            evidence["id"] = evidence_id
            evidence["claim_ids"] = [claim_id]
            evidence["test_ids"] = [test_id]
            evidence["tier"] = tier
            registry["claims"].append(claim)
            registry["tests"].append(test)
            registry["evidence"].append(evidence)

        for boundary in registry["boundaries"]:
            boundary["feature_ids"] = [
                feature_id if value == "feat:rfc.9000.connection-migration" else value
                for value in boundary.get("feature_ids", [])
            ]
        for release in registry["releases"]:
            release["claim_ids"] = [
                "clm:claim-ceiling.validation.t2" if value == "clm:rfc.9000.connection-migration.t3" else value
                for value in release.get("claim_ids", [])
            ]
            release["evidence_ids"] = [
                "evd:claim-ceiling.validation.t2" if value == "evd:t3.rfc.9000.connection-migration.bundle" else value
                for value in release.get("evidence_ids", [])
            ]

        (repo / ".ssot" / "registry.json").write_text(stable_json_dumps(registry), encoding="utf-8")
        return repo, registry, feature_id

    def test_validation_rejects_implemented_feature_with_active_t0_claim(self) -> None:
        repo, registry, _feature_id = self._registry_with_t0_implemented_feature()

        report = validate_registry_document(registry, repo / ".ssot" / "registry.json", repo)

        self.assertFalse(report["passed"])
        self.assertTrue(
            any("active T0 claim" in failure for failure in report["failures"]),
            report["failures"],
        )

    def test_profile_feature_evaluation_rejects_t0_only_implementation_claim(self) -> None:
        _repo, registry, feature_id = self._registry_with_t0_implemented_feature()
        index = build_index(registry, [])

        result = evaluate_feature_passing(index["features"][feature_id], index, registry["guard_policies"])

        self.assertFalse(result["passed"])
        self.assertTrue(any("active T0 claim" in failure for failure in result["failures"]), result)

    def test_t0_t1_t2_claim_ladder_satisfies_implemented_feature(self) -> None:
        repo, registry, feature_id = self._registry_with_tier_ladder_feature()

        report = validate_registry_document(registry, repo / ".ssot" / "registry.json", repo)
        index = build_index(registry, [])
        result = evaluate_feature_passing(index["features"][feature_id], index, registry["guard_policies"])

        self.assertTrue(report["passed"], report["failures"])
        self.assertTrue(result["passed"], result)
        self.assertEqual(result["satisfying_claim_ids"], ["clm:claim-ceiling.validation.t2"])


if __name__ == "__main__":
    unittest.main()
