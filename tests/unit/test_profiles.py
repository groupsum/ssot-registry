from __future__ import annotations

import unittest
from pathlib import Path

from ssot_registry.api.load import load_registry
from ssot_registry.api.profile_eval import evaluate_profile
from ssot_registry.api.profile_resolution import resolve_boundary_feature_ids
from ssot_registry.validators.identity import build_index
from tests.helpers import temp_repo_from_fixture


class ProfileEvaluationTests(unittest.TestCase):
    def _load_valid(self) -> tuple[Path, dict[str, object], dict[str, dict[str, dict[str, object]]]]:
        temp_dir = temp_repo_from_fixture("repo_valid")
        self.addCleanup(temp_dir.cleanup)
        repo = Path(temp_dir.name) / "repo"
        _registry_path, _repo_root, registry = load_registry(repo)
        index = build_index(registry, [])
        return repo, registry, index

    def test_profile_passes_when_all_features_have_satisfying_claims(self) -> None:
        _repo, registry, index = self._load_valid()
        profile = {
            "id": "prf:core",
            "title": "Core profile",
            "description": "Core bundle",
            "status": "active",
            "kind": "capability",
            "feature_ids": ["feat:rfc.9000.connection-migration"],
            "profile_ids": [],
            "claim_tier": "T3",
            "evaluation": {"mode": "all_features_must_pass", "allow_feature_override_tier": True},
        }
        index["profiles"][profile["id"]] = profile
        result = evaluate_profile(profile, index, registry.get("guard_policies", {}))
        self.assertTrue(result["passed"])

    def test_profile_fails_when_feature_target_claim_tier_not_met(self) -> None:
        _repo, registry, index = self._load_valid()
        feature = index["features"]["feat:rfc.9000.connection-migration"]
        feature["plan"]["target_claim_tier"] = "T4"
        profile = {
            "id": "prf:strict",
            "title": "Strict profile",
            "description": "Strict tier",
            "status": "active",
            "kind": "certification",
            "feature_ids": [feature["id"]],
            "profile_ids": [],
            "claim_tier": None,
            "evaluation": {"mode": "all_features_must_pass", "allow_feature_override_tier": True},
        }
        index["profiles"][profile["id"]] = profile
        result = evaluate_profile(profile, index, registry.get("guard_policies", {}))
        self.assertFalse(result["passed"])

    def test_profile_claim_tier_applies_when_feature_has_no_target(self) -> None:
        _repo, registry, index = self._load_valid()
        feature = index["features"]["feat:rfc.9000.connection-migration"]
        feature["plan"]["target_claim_tier"] = None
        profile = {
            "id": "prf:tiered",
            "title": "Tiered",
            "description": "Tier floor",
            "status": "active",
            "kind": "capability",
            "feature_ids": [feature["id"]],
            "profile_ids": [],
            "claim_tier": "T4",
            "evaluation": {"mode": "all_features_must_pass", "allow_feature_override_tier": True},
        }
        index["profiles"][profile["id"]] = profile
        result = evaluate_profile(profile, index, registry.get("guard_policies", {}))
        self.assertFalse(result["passed"])

    def test_nested_profile_cycle_is_reported(self) -> None:
        _repo, registry, index = self._load_valid()
        a = {
            "id": "prf:a",
            "title": "A",
            "description": "A",
            "status": "active",
            "kind": "capability",
            "feature_ids": [],
            "profile_ids": ["prf:b"],
            "claim_tier": None,
            "evaluation": {"mode": "all_features_must_pass", "allow_feature_override_tier": True},
        }
        b = {
            "id": "prf:b",
            "title": "B",
            "description": "B",
            "status": "active",
            "kind": "capability",
            "feature_ids": [],
            "profile_ids": ["prf:a"],
            "claim_tier": None,
            "evaluation": {"mode": "all_features_must_pass", "allow_feature_override_tier": True},
        }
        index["profiles"]["prf:a"] = a
        index["profiles"]["prf:b"] = b
        result = evaluate_profile(a, index, registry.get("guard_policies", {}))
        self.assertTrue(any("cycle detected" in failure.lower() for failure in result["failures"]))

    def test_boundary_profile_resolution_includes_transitive_features(self) -> None:
        _repo, _registry, index = self._load_valid()
        index["profiles"]["prf:leaf"] = {
            "id": "prf:leaf",
            "title": "Leaf",
            "description": "Leaf",
            "status": "active",
            "kind": "capability",
            "feature_ids": ["feat:rfc.9000.connection-migration"],
            "profile_ids": [],
            "claim_tier": "T3",
            "evaluation": {"mode": "all_features_must_pass", "allow_feature_override_tier": True},
        }
        index["profiles"]["prf:root"] = {
            "id": "prf:root",
            "title": "Root",
            "description": "Root",
            "status": "active",
            "kind": "capability",
            "feature_ids": [],
            "profile_ids": ["prf:leaf"],
            "claim_tier": "T3",
            "evaluation": {"mode": "all_features_must_pass", "allow_feature_override_tier": True},
        }
        resolved = resolve_boundary_feature_ids(
            {"feature_ids": [], "profile_ids": ["prf:root"]},
            index,
        )
        self.assertIn("feat:rfc.9000.connection-migration", resolved)


if __name__ == "__main__":
    unittest.main()
