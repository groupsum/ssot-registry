from __future__ import annotations

from copy import deepcopy

from ssot_registry.guards.certification import evaluate_release_certification_guard


def evaluate_release_promotion_guard(
    registry: dict[str, object],
    index: dict[str, dict[str, dict[str, object]]],
    release_id: str,
) -> dict[str, object]:
    certification_registry = deepcopy(registry)
    certification_registry.setdefault("guard_policies", {}).setdefault("certification", {})[
        "require_release_status_draft_or_candidate"
    ] = False
    certification = evaluate_release_certification_guard(certification_registry, index, release_id)
    failures = list(certification["failures"])

    release = index["releases"].get(release_id)
    if release is None:
        return {
            "release_id": release_id,
            "passed": False,
            "failures": [f"Missing release {release_id}"],
            "warnings": [],
        }

    promotion_policy = registry.get("guard_policies", {}).get("promotion", {})
    if promotion_policy.get("require_release_status_certified", True):
        if release.get("status") != "certified":
            failures.append(
                f"Release {release_id} must be certified before promotion; current status is {release.get('status')}"
            )

    return {
        "release_id": release_id,
        "passed": not failures,
        "failures": sorted(set(failures)),
        "warnings": certification["warnings"],
    }
