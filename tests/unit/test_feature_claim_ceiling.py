from __future__ import annotations

import json
import unittest
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

    def test_validation_rejects_implemented_feature_with_active_t0_claim(self) -> None:
        repo, registry, _feature_id = self._registry_with_t0_implemented_feature()

        report = validate_registry_document(registry, repo / ".ssot" / "registry.json", repo)

        self.assertFalse(report["passed"])
        self.assertTrue(
            any("active T0 claim" in failure for failure in report["failures"]),
            report["failures"],
        )

    def test_profile_feature_evaluation_requires_all_active_claims(self) -> None:
        _repo, registry, feature_id = self._registry_with_t0_implemented_feature()
        index = build_index(registry, [])

        result = evaluate_feature_passing(index["features"][feature_id], index, registry["guard_policies"])

        self.assertFalse(result["passed"])
        self.assertTrue(any("active T0 claim" in failure for failure in result["failures"]), result)


if __name__ == "__main__":
    unittest.main()
