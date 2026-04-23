from __future__ import annotations

NON_ABSENT_IMPLEMENTATION_STATUSES = {"partial", "implemented"}
OPEN_ISSUE_STATUSES = {"open", "in_progress", "blocked"}


def _has_lifecycle_note(feature: dict[str, object]) -> bool:
    note = feature.get("lifecycle", {}).get("note") if isinstance(feature.get("lifecycle"), dict) else None
    return isinstance(note, str) and bool(note.strip())


def _has_release_blocking_open_issue(feature_id: str, index: dict[str, dict[str, dict[str, object]]]) -> bool:
    for issue in index["issues"].values():
        if feature_id not in issue.get("feature_ids", []):
            continue
        if issue.get("release_blocking") and issue.get("status") in OPEN_ISSUE_STATUSES:
            return True
    return False


def _has_release_blocking_active_risk(feature_id: str, index: dict[str, dict[str, dict[str, object]]]) -> bool:
    for risk in index["risks"].values():
        if feature_id not in risk.get("feature_ids", []):
            continue
        if risk.get("release_blocking") and risk.get("status") == "active":
            return True
    return False


def _active_boundary_feature_ids(
    registry: dict[str, object],
    index: dict[str, dict[str, dict[str, object]]],
) -> set[str]:
    program = registry.get("program", {})
    active_boundary_id = program.get("active_boundary_id") if isinstance(program, dict) else None
    active_boundary = index["boundaries"].get(active_boundary_id) if isinstance(active_boundary_id, str) else None
    if not active_boundary:
        return set()
    return set(active_boundary.get("feature_ids", []))


def validate_out_of_bounds_disposition(
    registry: dict[str, object],
    index: dict[str, dict[str, dict[str, object]]],
    failures: list[str],
    warnings: list[str],
) -> None:
    _ = warnings
    active_boundary_features = _active_boundary_feature_ids(registry, index)

    for feature_id, feature in index["features"].items():
        plan = feature.get("plan", {})
        if not isinstance(plan, dict) or plan.get("horizon") != "out_of_bounds":
            continue

        if feature_id in active_boundary_features:
            failures.append(f"features.{feature_id} is out_of_bounds but is still present in the active boundary")

        implementation_status = feature.get("implementation_status")
        if implementation_status not in NON_ABSENT_IMPLEMENTATION_STATUSES:
            continue

        disposition = plan.get("out_of_bounds_disposition")
        if disposition is None:
            failures.append(
                f"features.{feature_id} is out_of_bounds and {implementation_status} but plan.out_of_bounds_disposition is not set"
            )
            continue

        if not _has_lifecycle_note(feature):
            failures.append(
                f"features.{feature_id} has out_of_bounds_disposition {disposition!r} but lifecycle.note is empty"
            )

        if disposition == "tolerated":
            if plan.get("target_lifecycle_stage") == "removed":
                failures.append(
                    f"features.{feature_id} is tolerated out_of_bounds but targets removed; use prohibited for removal targets"
                )
            continue

        if disposition != "prohibited":
            continue

        if plan.get("target_lifecycle_stage") != "removed":
            failures.append(
                f"features.{feature_id} is prohibited out_of_bounds but plan.target_lifecycle_stage is not removed"
            )
        if not (
            _has_release_blocking_open_issue(feature_id, index)
            or _has_release_blocking_active_risk(feature_id, index)
        ):
            failures.append(
                f"features.{feature_id} is prohibited out_of_bounds and {implementation_status} but has no open release-blocking issue or active release-blocking risk"
            )
