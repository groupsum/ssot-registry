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


def _dependency_closure_contains(
    claim: dict[str, object],
    target_claim_id: str,
    index: dict[str, dict[str, dict[str, object]]],
    *,
    seen: set[str] | None = None,
) -> bool:
    seen = seen or set()
    for dependency_id in claim.get("depends_on_claim_ids", []):
        if dependency_id == target_claim_id:
            return True
        if dependency_id in seen or dependency_id not in index["claims"]:
            continue
        seen.add(str(dependency_id))
        if _dependency_closure_contains(index["claims"][dependency_id], target_claim_id, index, seen=seen):
            return True
    return False


def _has_satisfying_successor(
    claim: dict[str, object],
    satisfying_claims: list[dict[str, object]],
    index: dict[str, dict[str, dict[str, object]]],
) -> bool:
    claim_id = str(claim["id"])
    return any(_dependency_closure_contains(candidate, claim_id, index) for candidate in satisfying_claims)


def feature_claim_ceiling_failures(
    feature: dict[str, Any],
    index: dict[str, dict[str, dict[str, object]]],
    *,
    require_evidenced_status: bool = True,
) -> list[str]:
    feature_id = str(feature["id"])
    required_tier = feature.get("plan", {}).get("target_claim_tier")
    active_claims = active_required_feature_claims(feature, index)
    satisfying_claims = [
        claim
        for claim in active_claims
        if claim.get("tier") != "T0"
        and (required_tier is None or CLAIM_TIER_RANK[claim["tier"]] >= CLAIM_TIER_RANK[required_tier])
        and (
            not require_evidenced_status
            or CLAIM_STATUS_RANK.get(claim.get("status"), -999) >= CLAIM_STATUS_RANK["evidenced"]
        )
    ]
    if satisfying_claims:
        failures: list[str] = []
        for claim in active_claims:
            claim_tier = str(claim["tier"])
            if claim in satisfying_claims:
                continue
            if required_tier is None or CLAIM_TIER_RANK[claim_tier] < CLAIM_TIER_RANK[required_tier]:
                if not _has_satisfying_successor(claim, satisfying_claims, index):
                    failures.append(
                        f"features.{feature_id} is capped below implemented by claim {claim['id']} outside satisfying claim lineage"
                    )
        return failures

    failures: list[str] = []
    for claim in active_claims:
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
