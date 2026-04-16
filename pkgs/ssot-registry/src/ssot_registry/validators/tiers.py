from __future__ import annotations

from ssot_registry.model.enums import CLAIM_STATUS_RANK, CLAIM_TIER_RANK


def validate_tiers(index: dict[str, dict[str, dict[str, object]]], failures: list[str]) -> None:
    for feature_id, feature in index["features"].items():
        target_tier = feature.get("plan", {}).get("target_claim_tier")
        if target_tier is None:
            continue
        linked_claims = [index["claims"][claim_id] for claim_id in feature.get("claim_ids", []) if claim_id in index["claims"]]
        if not linked_claims:
            continue
        if not any(CLAIM_TIER_RANK[claim["tier"]] >= CLAIM_TIER_RANK[target_tier] for claim in linked_claims):
            failures.append(
                f"features.{feature_id} targets {target_tier} but has no linked claim at or above that tier"
            )

    for claim_id, claim in index["claims"].items():
        linked_evidence = [index["evidence"][evidence_id] for evidence_id in claim.get("evidence_ids", []) if evidence_id in index["evidence"]]
        if CLAIM_STATUS_RANK.get(claim.get("status"), -999) >= CLAIM_STATUS_RANK["evidenced"]:
            if not linked_evidence:
                failures.append(f"claims.{claim_id} is evidenced or higher but has no linked evidence")
            if not any(
                evidence.get("status") == "passed" and CLAIM_TIER_RANK[evidence["tier"]] >= CLAIM_TIER_RANK[claim["tier"]]
                for evidence in linked_evidence
            ):
                failures.append(
                    f"claims.{claim_id} is evidenced or higher but lacks passed evidence at or above claim tier {claim['tier']}"
                )
