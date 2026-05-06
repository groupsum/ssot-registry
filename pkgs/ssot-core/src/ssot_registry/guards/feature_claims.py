from __future__ import annotations

from typing import Any

from ssot_registry.model.enums import CLAIM_STATUS_RANK, CLAIM_TIER_RANK

INACTIVE_CLAIM_STATUSES = {"retired"}


def active_required_feature_claims(
    feature: dict[str, Any],
    index: dict[str, dict[str, dict[str, object]]],
) -> list[dict[str, object]]:
    return [
        index["claims"][claim_id]
        for claim_id in feature.get("claim_ids", [])
        if claim_id in index["claims"] and index["claims"][claim_id].get("status") not in INACTIVE_CLAIM_STATUSES
    ]


def claim_satisfies_feature_implementation(
    claim: dict[str, object],
    required_tier: str | None,
) -> bool:
    if claim.get("tier") == "T0":
        return False
    if required_tier is not None and CLAIM_TIER_RANK[claim["tier"]] < CLAIM_TIER_RANK[required_tier]:
        return False
    return CLAIM_STATUS_RANK.get(claim.get("status"), -999) >= CLAIM_STATUS_RANK["evidenced"]


def feature_claim_ceiling_failures(
    feature: dict[str, Any],
    index: dict[str, dict[str, dict[str, object]]],
    *,
    require_evidenced_status: bool = True,
) -> list[str]:
    feature_id = str(feature["id"])
    required_tier = feature.get("plan", {}).get("target_claim_tier")
    failures: list[str] = []
    for claim in active_required_feature_claims(feature, index):
        claim_id = str(claim["id"])
        claim_tier = str(claim["tier"])
        claim_status = str(claim.get("status"))
        if claim_tier == "T0":
            failures.append(f"features.{feature_id} is capped below implemented by active T0 claim {claim_id}")
            continue
        if required_tier is not None and CLAIM_TIER_RANK[claim_tier] < CLAIM_TIER_RANK[required_tier]:
            failures.append(
                f"features.{feature_id} is capped below implemented by claim {claim_id} tier {claim_tier} below target {required_tier}"
            )
            continue
        if require_evidenced_status and CLAIM_STATUS_RANK.get(claim_status, -999) < CLAIM_STATUS_RANK["evidenced"]:
            failures.append(
                f"features.{feature_id} is capped below implemented by claim {claim_id} status {claim_status} below evidenced"
            )
    return failures
