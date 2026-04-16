from __future__ import annotations


def validate_lifecycle_semantics(
    registry: dict[str, object],
    index: dict[str, dict[str, dict[str, object]]],
    failures: list[str],
    warnings: list[str],
) -> None:
    active_boundary_id = registry.get("program", {}).get("active_boundary_id")
    active_boundary = index["boundaries"].get(active_boundary_id) if isinstance(active_boundary_id, str) else None
    active_boundary_features = set(active_boundary.get("feature_ids", [])) if active_boundary else set()

    for feature_id, feature in index["features"].items():
        stage = feature.get("lifecycle", {}).get("stage")
        implementation_status = feature.get("implementation_status")
        replacement_ids = feature.get("lifecycle", {}).get("replacement_feature_ids", [])
        note = feature.get("lifecycle", {}).get("note")

        if stage == "removed" and implementation_status != "absent":
            failures.append(f"features.{feature_id} is removed but implementation_status is not absent")
        if stage in {"deprecated", "obsolete"} and not replacement_ids and not note:
            warnings.append(
                f"features.{feature_id} is {stage} but has neither replacement_feature_ids nor a lifecycle note"
            )
        if stage in {"obsolete", "removed"} and feature_id in active_boundary_features:
            failures.append(f"features.{feature_id} is {stage} but is still present in the active boundary")
