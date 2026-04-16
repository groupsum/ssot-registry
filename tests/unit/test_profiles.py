from __future__ import annotations

import unittest
from pathlib import Path

from ssot_registry.api.profile_eval import evaluate_profile
from ssot_registry.api.profile_resolution import resolve_boundary_feature_ids
from ssot_registry.api.validate import validate_registry_document
from ssot_registry.validators.identity import build_index
from tests.helpers import temp_repo_from_fixture


class ProfileEvaluationTests(unittest.TestCase):
    def _load_registry(self) -> tuple[Path, dict[str, object]]:
        temp_dir = temp_repo_from_fixture("repo_valid")
        self.addCleanup(temp_dir.cleanup)
        repo = Path(temp_dir.name) / "repo"
        import json

        registry = json.loads((repo / ".ssot" / "registry.json").read_text(encoding="utf-8"))
        return repo, registry

    def test_profile_passes_when_all_features_have_satisfying_claims(self) -> None:
        repo, registry = self._load_registry()
        registry["profiles"].append(
            {
                "id": "prf:http3-core",
                "title": "HTTP3 core",
                "description": "bundle",
                "status": "active",
                "kind": "capability",
                "feature_ids": ["feat:rfc.9000.connection-migration"],
                "profile_ids": [],
                "claim_tier": "T3",
                "evaluation": {"mode": "all_features_must_pass", "allow_feature_override_tier": True},
            }
        )
        index = build_index(registry, [])
        result = evaluate_profile(index["profiles"]["prf:http3-core"], index, registry["guard_policies"])
        self.assertTrue(result["passed"], result)
        self.assertIn("feat:rfc.9000.connection-migration", result["resolved_feature_ids"])
        self.assertTrue(validate_registry_document(registry, repo / ".ssot" / "registry.json", repo)["passed"])

    def test_profile_fails_when_feature_target_claim_tier_not_met(self) -> None:
        _repo, registry = self._load_registry()
        registry["claims"][0]["tier"] = "T1"
        profile = {
            "id": "prf:targeted",
            "title": "Targeted",
            "description": "targeted",
            "status": "active",
            "kind": "capability",
            "feature_ids": ["feat:rfc.9000.connection-migration"],
            "profile_ids": [],
            "claim_tier": "T3",
            "evaluation": {"mode": "all_features_must_pass", "allow_feature_override_tier": True},
        }
        registry["profiles"].append(profile)
        index = build_index(registry, [])
        result = evaluate_profile(profile, index, registry["guard_policies"])
        self.assertFalse(result["passed"])
        self.assertTrue(any("tier" in failure.lower() for failure in result["failures"]))

    def test_profile_claim_tier_applies_when_feature_has_no_target(self) -> None:
        _repo, registry = self._load_registry()
        registry["features"][0]["plan"]["target_claim_tier"] = None
        registry["claims"][0]["tier"] = "T1"
        profile = {
            "id": "prf:fallback-tier",
            "title": "Fallback",
            "description": "fallback",
            "status": "active",
            "kind": "capability",
            "feature_ids": ["feat:rfc.9000.connection-migration"],
            "profile_ids": [],
            "claim_tier": "T2",
            "evaluation": {"mode": "all_features_must_pass", "allow_feature_override_tier": True},
        }
        registry["profiles"].append(profile)
        index = build_index(registry, [])
        result = evaluate_profile(profile, index, registry["guard_policies"])
        self.assertFalse(result["passed"])
        self.assertTrue(any("T2" in failure for failure in result["failures"]))

    def test_nested_profile_cycle_is_reported(self) -> None:
        _repo, registry = self._load_registry()
        registry["profiles"].extend(
            [
                {
                    "id": "prf:a",
                    "title": "A",
                    "description": "A",
                    "status": "active",
                    "kind": "capability",
                    "feature_ids": [],
                    "profile_ids": ["prf:b"],
                    "claim_tier": None,
                    "evaluation": {"mode": "all_features_must_pass", "allow_feature_override_tier": True},
                },
                {
                    "id": "prf:b",
                    "title": "B",
                    "description": "B",
                    "status": "active",
                    "kind": "capability",
                    "feature_ids": [],
                    "profile_ids": ["prf:a"],
                    "claim_tier": None,
                    "evaluation": {"mode": "all_features_must_pass", "allow_feature_override_tier": True},
                },
            ]
        )
        index = build_index(registry, [])
        result = evaluate_profile(index["profiles"]["prf:a"], index, registry["guard_policies"])
        self.assertFalse(result["passed"])
        self.assertTrue(any("cycle" in failure.lower() for failure in result["failures"]))

    def test_boundary_profile_resolution_includes_transitive_features(self) -> None:
        _repo, registry = self._load_registry()
        registry["features"].append(
            {
                "id": "feat:extra",
                "title": "extra",
                "description": "extra",
                "implementation_status": "implemented",
                "lifecycle": {"stage": "active", "replacement_feature_ids": [], "note": None},
                "plan": {"horizon": "current", "slot": None, "target_claim_tier": "T3", "target_lifecycle_stage": "active"},
                "claim_ids": ["clm:rfc.9000.connection-migration.t3"],
                "test_ids": ["tst:pytest.rfc.9000.connection-migration"],
                "requires": [],
            }
        )
        registry["profiles"].extend(
            [
                {
                    "id": "prf:child",
                    "title": "Child",
                    "description": "child",
                    "status": "active",
                    "kind": "capability",
                    "feature_ids": ["feat:extra"],
                    "profile_ids": [],
                    "claim_tier": "T3",
                    "evaluation": {"mode": "all_features_must_pass", "allow_feature_override_tier": True},
                },
                {
                    "id": "prf:parent",
                    "title": "Parent",
                    "description": "parent",
                    "status": "active",
                    "kind": "capability",
                    "feature_ids": ["feat:rfc.9000.connection-migration"],
                    "profile_ids": ["prf:child"],
                    "claim_tier": "T3",
                    "evaluation": {"mode": "all_features_must_pass", "allow_feature_override_tier": True},
                },
            ]
        )
        boundary = {"id": "bnd:x", "feature_ids": [], "profile_ids": ["prf:parent"]}
        index = build_index(registry, [])
        resolved = resolve_boundary_feature_ids(boundary, index)
        self.assertEqual(resolved, ["feat:rfc.9000.connection-migration", "feat:extra"])


if __name__ == "__main__":
    unittest.main()
