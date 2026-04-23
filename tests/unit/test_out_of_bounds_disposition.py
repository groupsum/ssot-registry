from __future__ import annotations

import json
import unittest
from copy import deepcopy
from pathlib import Path

from ssot_registry.api import plan_features, validate_registry
from ssot_registry.util.jsonio import save_json
from tests.helpers import temp_repo_from_fixture


def _out_of_bounds_feature(**overrides: object) -> dict[str, object]:
    row: dict[str, object] = {
        "id": "feat:out-of-bounds.partial",
        "title": "Out-of-bounds partial feature",
        "description": "Feature used to exercise out-of-bounds disposition validation.",
        "implementation_status": "partial",
        "lifecycle": {
            "stage": "active",
            "replacement_feature_ids": [],
            "note": "Partial incidental support is tracked but not release-targeted.",
        },
        "plan": {
            "horizon": "out_of_bounds",
            "slot": None,
            "target_claim_tier": None,
            "target_lifecycle_stage": "active",
            "out_of_bounds_disposition": "tolerated",
        },
        "requires": [],
        "spec_ids": [],
        "claim_ids": [],
        "test_ids": [],
    }
    row.update(overrides)
    return row


def _release_blocking_issue(feature_id: str) -> dict[str, object]:
    return {
        "id": "iss:out-of-bounds.partial-removal",
        "title": "Remove prohibited out-of-bounds partial feature",
        "status": "open",
        "severity": "high",
        "description": "Prohibited out-of-bounds implementation remains present.",
        "plan": {"horizon": "current", "slot": None},
        "feature_ids": [feature_id],
        "claim_ids": [],
        "test_ids": [],
        "evidence_ids": [],
        "risk_ids": [],
        "release_blocking": True,
    }


class OutOfBoundsDispositionTests(unittest.TestCase):
    def _repo_and_registry(self) -> tuple[object, Path, dict[str, object]]:
        temp_dir = temp_repo_from_fixture("repo_valid")
        self.addCleanup(temp_dir.cleanup)
        repo = Path(temp_dir.name) / "repo"
        registry = json.loads((repo / ".ssot" / "registry.json").read_text(encoding="utf-8"))
        return temp_dir, repo, registry

    def _write_and_validate(self, repo: Path, registry: dict[str, object]) -> dict[str, object]:
        save_json(repo / ".ssot" / "registry.json", registry)
        return validate_registry(repo)

    def test_tolerated_non_absent_out_of_bounds_feature_passes(self) -> None:
        _temp_dir, repo, registry = self._repo_and_registry()
        registry["features"].append(_out_of_bounds_feature())

        report = self._write_and_validate(repo, registry)

        self.assertTrue(report["passed"], report)

    def test_non_absent_out_of_bounds_feature_requires_disposition(self) -> None:
        _temp_dir, repo, registry = self._repo_and_registry()
        feature = _out_of_bounds_feature()
        feature["plan"] = deepcopy(feature["plan"])
        feature["plan"].pop("out_of_bounds_disposition")
        registry["features"].append(feature)

        report = self._write_and_validate(repo, registry)

        self.assertFalse(report["passed"])
        self.assertIn("plan.out_of_bounds_disposition is not set", "\n".join(report["failures"]))

    def test_prohibited_non_absent_out_of_bounds_feature_requires_removal_target_and_blocker(self) -> None:
        _temp_dir, repo, registry = self._repo_and_registry()
        feature = _out_of_bounds_feature()
        feature["plan"] = deepcopy(feature["plan"])
        feature["plan"]["out_of_bounds_disposition"] = "prohibited"
        registry["features"].append(feature)

        report = self._write_and_validate(repo, registry)

        joined = "\n".join(report["failures"])
        self.assertFalse(report["passed"])
        self.assertIn("plan.target_lifecycle_stage is not removed", joined)
        self.assertIn("has no open release-blocking issue or active release-blocking risk", joined)

    def test_prohibited_non_absent_out_of_bounds_feature_passes_with_removal_target_and_blocker(self) -> None:
        _temp_dir, repo, registry = self._repo_and_registry()
        feature = _out_of_bounds_feature()
        feature["plan"] = deepcopy(feature["plan"])
        feature["plan"]["out_of_bounds_disposition"] = "prohibited"
        feature["plan"]["target_lifecycle_stage"] = "removed"
        registry["features"].append(feature)
        registry["issues"].append(_release_blocking_issue(str(feature["id"])))

        report = self._write_and_validate(repo, registry)

        self.assertTrue(report["passed"], report)

    def test_out_of_bounds_feature_cannot_remain_in_active_boundary(self) -> None:
        _temp_dir, repo, registry = self._repo_and_registry()
        feature = _out_of_bounds_feature()
        registry["features"].append(feature)
        boundary = next(row for row in registry["boundaries"] if row["id"] == registry["program"]["active_boundary_id"])
        boundary["feature_ids"].append(feature["id"])

        report = self._write_and_validate(repo, registry)

        self.assertFalse(report["passed"])
        self.assertIn("out_of_bounds but is still present in the active boundary", "\n".join(report["failures"]))

    def test_plan_api_sets_and_clears_out_of_bounds_disposition(self) -> None:
        _temp_dir, repo, registry = self._repo_and_registry()
        feature = _out_of_bounds_feature(
            implementation_status="absent",
            lifecycle={"stage": "active", "replacement_feature_ids": [], "note": None},
            plan={
                "horizon": "backlog",
                "slot": None,
                "target_claim_tier": None,
                "target_lifecycle_stage": "active",
            },
        )
        registry["features"].append(feature)
        self._write_and_validate(repo, registry)

        plan_features(
            repo,
            [str(feature["id"])],
            "out_of_bounds",
            None,
            out_of_bounds_disposition="tolerated",
        )
        registry = json.loads((repo / ".ssot" / "registry.json").read_text(encoding="utf-8"))
        planned = next(row for row in registry["features"] if row["id"] == feature["id"])
        self.assertEqual(planned["plan"]["out_of_bounds_disposition"], "tolerated")

        plan_features(repo, [str(feature["id"])], "backlog", None)
        registry = json.loads((repo / ".ssot" / "registry.json").read_text(encoding="utf-8"))
        planned = next(row for row in registry["features"] if row["id"] == feature["id"])
        self.assertNotIn("out_of_bounds_disposition", planned["plan"])


if __name__ == "__main__":
    unittest.main()
