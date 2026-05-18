from __future__ import annotations

from typing import Any

from ssot_registry.model.enums import CLAIM_TIER_RANK


def validate_claim_lineage(index: dict[str, dict[str, dict[str, Any]]], failures: list[str]) -> None:
    for claim_id, claim in index.get("claims", {}).items():
        depends_on = claim.get("depends_on_claim_ids", [])
        if not isinstance(depends_on, list):
            continue
        claim_tier = claim.get("tier")
        claim_rank = CLAIM_TIER_RANK.get(str(claim_tier), -1)
        for dependency_id in depends_on:
            if dependency_id == claim_id:
                failures.append(f"claims.{claim_id}.depends_on_claim_ids cannot reference itself")
                continue
            dependency = index["claims"].get(dependency_id)
            if dependency is None:
                continue
            dependency_tier = dependency.get("tier")
            dependency_rank = CLAIM_TIER_RANK.get(str(dependency_tier), -1)
            if dependency_rank >= claim_rank:
                failures.append(
                    f"claims.{claim_id}.depends_on_claim_ids references {dependency_id} at tier {dependency_tier}; dependencies must be lower than {claim_tier}"
                )
