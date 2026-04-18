from __future__ import annotations


def evaluate_feature_lifecycle_transition_guard(
    registry: dict[str, object],
    index: dict[str, dict[str, dict[str, object]]],
    feature_id: str,
    target_stage: str,
    replacement_feature_ids: list[str] | None,
    note: str | None,
) -> dict[str, object]:
    failures: list[str] = []
    warnings: list[str] = []

    feature = index["features"].get(feature_id)
    if feature is None:
        return {
            "feature_id": feature_id,
            "passed": False,
            "failures": [f"Missing feature {feature_id}"],
            "warnings": [],
        }

    lifecycle_policy = registry.get("guard_policies", {}).get("lifecycle", {})
    replacement_feature_ids = replacement_feature_ids or []

    if target_stage in {"deprecated", "obsolete"} and lifecycle_policy.get("require_replacement_or_note_for_deprecation", True):
        if not replacement_feature_ids and not note:
            failures.append(
                f"Feature {feature_id} transition to {target_stage} requires replacement_feature_ids or a note"
            )

    active_boundary_id = registry.get("program", {}).get("active_boundary_id")
    active_boundary = index["boundaries"].get(active_boundary_id)
    active_feature_ids = set(active_boundary.get("feature_ids", [])) if active_boundary else set()

    if lifecycle_policy.get("forbid_obsolete_or_removed_in_active_boundary", True):
        if target_stage in {"obsolete", "removed"} and feature_id in active_feature_ids:
            failures.append(
                f"Feature {feature_id} cannot transition to {target_stage} while it remains in the active boundary"
            )

    if target_stage == "removed" and lifecycle_policy.get("require_feature_absent_for_removed", True):
        if feature.get("implementation_status") != "absent":
            failures.append(
                f"Feature {feature_id} cannot transition to removed unless implementation_status is absent"
            )

    return {
        "feature_id": feature_id,
        "passed": not failures,
        "failures": failures,
        "warnings": warnings,
    }
