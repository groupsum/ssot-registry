from __future__ import annotations

import json
import unittest
from pathlib import Path

from ssot_registry.util.jsonio import stable_json_dumps
from tests.helpers import run_cli, temp_repo_from_fixture


class CliStatusSyncTests(unittest.TestCase):
    def _append_feature_claim_ceiling_rows(
        self,
        repo: Path,
        registry: dict[str, object],
        *,
        feature_id: str,
        claim_tiers: list[str],
        target_tier: str = "T1",
    ) -> None:
        test_id = f"tst:{feature_id.removeprefix('feat:')}"
        evidence_id = f"evd:{feature_id.removeprefix('feat:')}"
        claim_ids = [f"clm:{feature_id.removeprefix('feat:')}.{tier.lower()}.{index}" for index, tier in enumerate(claim_tiers, start=1)]
        test_path = f"tests/{feature_id.removeprefix('feat:').replace('.', '_')}.py"
        evidence_path = f".ssot/evidence/reports/{feature_id.removeprefix('feat:').replace('.', '_')}.json"
        (repo / test_path).write_text("def test_feature_claim_ceiling():\n    assert True\n", encoding="utf-8")
        evidence_target = repo / evidence_path
        evidence_target.parent.mkdir(parents=True, exist_ok=True)
        evidence_target.write_text("{}", encoding="utf-8")

        registry["features"].append(
            {
                "id": feature_id,
                "title": "Feature claim ceiling fixture",
                "description": "Feature used to verify claim ceilings during status sync.",
                "origin": "repo-local",
                "implementation_status": "absent",
                "lifecycle": {"stage": "active", "replacement_feature_ids": [], "note": None},
                "plan": {"horizon": "current", "slot": None, "target_claim_tier": target_tier, "target_lifecycle_stage": "active"},
                "requires": [],
                "spec_ids": [],
                "claim_ids": claim_ids,
                "test_ids": [test_id],
            }
        )
        for claim_id, tier in zip(claim_ids, claim_tiers, strict=True):
            registry["claims"].append(
                {
                    "id": claim_id,
                    "title": "Feature claim ceiling claim",
                    "origin": "repo-local",
                    "status": "asserted",
                    "tier": tier,
                    "kind": "conformance",
                    "description": "Claim used to verify feature implementation ceilings.",
                    "feature_ids": [feature_id],
                    "test_ids": [test_id],
                    "evidence_ids": [evidence_id],
                }
            )
        registry["tests"].append(
            {
                "id": test_id,
            "title": "Feature claim ceiling test",
            "origin": "repo-local",
            "status": "planned",
                "kind": "conformance",
                "path": test_path,
                "feature_ids": [feature_id],
                "claim_ids": claim_ids,
                "evidence_ids": [evidence_id],
            }
        )
        evidence_row = {
            "id": evidence_id,
            "title": "Feature claim ceiling evidence",
            "origin": "repo-local",
            "status": "collected",
            "kind": "report",
            "tier": max(claim_tiers),
            "path": evidence_path,
            "claim_ids": claim_ids,
            "test_ids": [test_id],
        }
        if max(claim_tiers) >= "T2":
            evidence_row["robustness_dimensions"] = ["negative_cases"]
            evidence_row["source_evidence_ids"] = ["evd:source.t1"]
        registry["evidence"].append(evidence_row)

    def test_registry_sync_statuses_updates_all_automated_entity_sections(self) -> None:
        temp_dir = temp_repo_from_fixture("repo_valid")
        self.addCleanup(temp_dir.cleanup)
        repo = Path(temp_dir.name) / "repo"
        registry_path = repo / ".ssot" / "registry.json"
        registry = json.loads(registry_path.read_text(encoding="utf-8"))

        registry["features"][0]["implementation_status"] = "absent"
        registry["tests"][0]["status"] = "planned"
        registry["claims"][0]["status"] = "declared"
        registry["evidence"][0]["status"] = "collected"
        registry["profiles"].append(
            {
                "id": "prf:cli.status-sync",
                "title": "Status sync profile",
                "description": "Profile used by status sync integration coverage.",
                "status": "draft",
                "kind": "certification",
                "feature_ids": [registry["features"][0]["id"]],
                "profile_ids": [],
                "claim_tier": "T3",
                "evaluation": {
                    "mode": "all_features_must_pass",
                    "allow_feature_override_tier": True,
                },
            }
        )
        registry_path.write_text(stable_json_dumps(registry), encoding="utf-8")

        dry_run = run_cli("registry", "sync-statuses", str(repo), "--dry-run")
        self.assertEqual(dry_run.returncode, 0, dry_run.stderr)
        dry_payload = json.loads(dry_run.stdout)
        self.assertTrue(dry_payload["dry_run"])
        self.assertEqual(dry_payload["changed"], 5)
        unchanged = json.loads(registry_path.read_text(encoding="utf-8"))
        self.assertEqual(unchanged["features"][0]["implementation_status"], "absent")
        self.assertEqual(unchanged["profiles"][0]["status"], "draft")

        result = run_cli("registry", "sync-statuses", str(repo))
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["changed"], 5)

        updated = json.loads(registry_path.read_text(encoding="utf-8"))
        self.assertEqual(updated["evidence"][0]["status"], "passed")
        self.assertEqual(updated["tests"][0]["status"], "passing")
        self.assertEqual(updated["claims"][0]["status"], "certified")
        self.assertEqual(updated["features"][0]["implementation_status"], "implemented")
        self.assertEqual(updated["profiles"][0]["status"], "active")

    def test_registry_sync_statuses_keeps_planned_placeholders_planned(self) -> None:
        temp_dir = temp_repo_from_fixture("repo_valid")
        self.addCleanup(temp_dir.cleanup)
        repo = Path(temp_dir.name) / "repo"
        registry_path = repo / ".ssot" / "registry.json"
        registry = json.loads(registry_path.read_text(encoding="utf-8"))

        test_path = repo / "tests" / "planned" / "test_placeholder.py"
        evidence_path = repo / ".ssot" / "evidence" / "planned" / "placeholder.json"
        test_path.parent.mkdir(parents=True, exist_ok=True)
        evidence_path.parent.mkdir(parents=True, exist_ok=True)
        test_path.write_text("def test_placeholder():\n    assert True\n", encoding="utf-8")
        evidence_path.write_text("{}", encoding="utf-8")

        feature_id = "feat:planned.placeholder"
        claim_id = "clm:planned.placeholder.t1"
        test_id = "tst:planned.placeholder"
        evidence_id = "evd:planned.placeholder"
        registry["features"].append(
            {
                "id": feature_id,
                "title": "Planned placeholder feature",
                "description": "Feature with planned placeholder support.",
                "origin": "repo-local",
                "implementation_status": "absent",
                "lifecycle": {"stage": "active", "replacement_feature_ids": [], "note": None},
                "plan": {"horizon": "next", "slot": None, "target_claim_tier": "T1", "target_lifecycle_stage": "active"},
                "requires": [],
                "spec_ids": [],
                "claim_ids": [claim_id],
                "test_ids": [test_id],
            }
        )
        registry["claims"].append(
            {
                "id": claim_id,
                "title": "Planned placeholder claim",
                "origin": "repo-local",
                "status": "proposed",
                "tier": "T1",
                "kind": "conformance",
                "description": "Planned placeholder support must not certify.",
                "feature_ids": [feature_id],
                "test_ids": [test_id],
                "evidence_ids": [evidence_id],
            }
        )
        registry["tests"].append(
            {
                "id": test_id,
                "title": "Planned placeholder test",
                "origin": "repo-local",
                "status": "planned",
                "kind": "conformance",
                "path": "tests/planned/test_placeholder.py",
                "feature_ids": [feature_id],
                "claim_ids": [claim_id],
                "evidence_ids": [evidence_id],
            }
        )
        registry["evidence"].append(
            {
                "id": evidence_id,
                "title": "Planned placeholder evidence",
                "origin": "repo-local",
                "status": "planned",
                "kind": "report",
                "tier": "T1",
                "path": ".ssot/evidence/planned/placeholder.json",
                "claim_ids": [claim_id],
                "test_ids": [test_id],
            }
        )
        registry_path.write_text(stable_json_dumps(registry), encoding="utf-8")

        result = run_cli("registry", "sync-statuses", str(repo))
        self.assertEqual(result.returncode, 0, result.stderr)

        updated = json.loads(registry_path.read_text(encoding="utf-8"))
        feature = next(row for row in updated["features"] if row["id"] == feature_id)
        claim = next(row for row in updated["claims"] if row["id"] == claim_id)
        test = next(row for row in updated["tests"] if row["id"] == test_id)
        evidence = next(row for row in updated["evidence"] if row["id"] == evidence_id)
        self.assertEqual(feature["implementation_status"], "absent")
        self.assertEqual(claim["status"], "proposed")
        self.assertEqual(test["status"], "planned")
        self.assertEqual(evidence["status"], "planned")

    def test_registry_sync_statuses_caps_t0_feature_at_partial(self) -> None:
        temp_dir = temp_repo_from_fixture("repo_valid")
        self.addCleanup(temp_dir.cleanup)
        repo = Path(temp_dir.name) / "repo"
        registry_path = repo / ".ssot" / "registry.json"
        registry = json.loads(registry_path.read_text(encoding="utf-8"))

        feature_id = "feat:claim-ceiling.t0"
        self._append_feature_claim_ceiling_rows(repo, registry, feature_id=feature_id, claim_tiers=["T0"], target_tier="T0")
        registry_path.write_text(stable_json_dumps(registry), encoding="utf-8")

        dry_run = run_cli("registry", "sync-statuses", str(repo), "--dry-run")
        self.assertEqual(dry_run.returncode, 0, dry_run.stderr)
        dry_payload = json.loads(dry_run.stdout)
        feature_changes = [
            change
            for change in dry_payload["changes"]
            if change["section"] == "features" and change["id"] == feature_id
        ]
        self.assertTrue(any("active T0 claim" in change["reason"] for change in feature_changes), dry_payload)

        result = run_cli("registry", "sync-statuses", str(repo))
        self.assertEqual(result.returncode, 0, result.stderr)

        updated = json.loads(registry_path.read_text(encoding="utf-8"))
        feature = next(row for row in updated["features"] if row["id"] == feature_id)
        claim = next(row for row in updated["claims"] if row["id"] == "clm:claim-ceiling.t0.t0.1")
        self.assertEqual(claim["status"], "evidenced")
        self.assertEqual(feature["implementation_status"], "partial")

    def test_registry_sync_statuses_requires_all_active_claims_to_pass(self) -> None:
        temp_dir = temp_repo_from_fixture("repo_valid")
        self.addCleanup(temp_dir.cleanup)
        repo = Path(temp_dir.name) / "repo"
        registry_path = repo / ".ssot" / "registry.json"
        registry = json.loads(registry_path.read_text(encoding="utf-8"))

        capped_feature_id = "feat:claim-ceiling.mixed"
        passing_feature_id = "feat:claim-ceiling.all-pass"
        self._append_feature_claim_ceiling_rows(repo, registry, feature_id=capped_feature_id, claim_tiers=["T1", "T0"])
        self._append_feature_claim_ceiling_rows(repo, registry, feature_id=passing_feature_id, claim_tiers=["T1", "T2"])
        registry_path.write_text(stable_json_dumps(registry), encoding="utf-8")

        result = run_cli("registry", "sync-statuses", str(repo))
        self.assertEqual(result.returncode, 0, result.stderr)

        updated = json.loads(registry_path.read_text(encoding="utf-8"))
        capped_feature = next(row for row in updated["features"] if row["id"] == capped_feature_id)
        passing_feature = next(row for row in updated["features"] if row["id"] == passing_feature_id)
        self.assertEqual(capped_feature["implementation_status"], "partial")
        self.assertEqual(passing_feature["implementation_status"], "implemented")

    def test_registry_sync_statuses_blocks_label_only_t2_promotion(self) -> None:
        temp_dir = temp_repo_from_fixture("repo_valid")
        self.addCleanup(temp_dir.cleanup)
        repo = Path(temp_dir.name) / "repo"
        registry_path = repo / ".ssot" / "registry.json"
        registry = json.loads(registry_path.read_text(encoding="utf-8"))

        feature_id = "feat:claim-tier-gates.label-only-t2"
        self._append_feature_claim_ceiling_rows(repo, registry, feature_id=feature_id, claim_tiers=["T2"], target_tier="T2")
        evidence = next(row for row in registry["evidence"] if row["id"] == "evd:claim-tier-gates.label-only-t2")
        evidence.pop("robustness_dimensions")
        evidence.pop("source_evidence_ids")
        claim = next(row for row in registry["claims"] if row["id"] == "clm:claim-tier-gates.label-only-t2.t2.1")
        claim["status"] = "evidenced"
        registry_path.write_text(stable_json_dumps(registry), encoding="utf-8")

        result = run_cli("registry", "sync-statuses", str(repo), "--dry-run")
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        claim_change = next(
            change
            for change in payload["changes"]
            if change["section"] == "claims" and change["id"] == "clm:claim-tier-gates.label-only-t2.t2.1"
        )
        self.assertEqual(claim_change["after"], "asserted")
        self.assertEqual(claim_change["requested_tier"], "T2")
        self.assertEqual(claim_change["approved_tier"], "T1")
        self.assertTrue(any("robustness dimensions" in failure for failure in claim_change["gate_failures"]))


if __name__ == "__main__":
    unittest.main()
