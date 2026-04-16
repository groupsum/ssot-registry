from __future__ import annotations


def evaluate_release_publication_guard(
    registry: dict[str, object],
    index: dict[str, dict[str, dict[str, object]]],
    release_id: str,
) -> dict[str, object]:
    failures: list[str] = []
    release = index["releases"].get(release_id)
    if release is None:
        return {
            "release_id": release_id,
            "passed": False,
            "failures": [f"Missing release {release_id}"],
            "warnings": [],
        }

    publication_policy = registry.get("guard_policies", {}).get("publication", {})
    if publication_policy.get("require_release_status_promoted", True):
        if release.get("status") != "promoted":
            failures.append(
                f"Release {release_id} must be promoted before publication; current status is {release.get('status')}"
            )

    return {
        "release_id": release_id,
        "passed": not failures,
        "failures": failures,
        "warnings": [],
    }
