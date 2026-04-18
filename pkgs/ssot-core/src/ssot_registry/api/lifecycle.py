from __future__ import annotations

from pathlib import Path

from ssot_registry.guards.lifecycle import evaluate_feature_lifecycle_transition_guard
from ssot_registry.util.errors import GuardError, ValidationError
from ssot_registry.validators.identity import build_index
from .load import load_registry
from .save import save_registry
from .validate import validate_registry_document


def set_feature_lifecycle(
    path: str | Path,
    ids: list[str],
    stage: str,
    replacement_feature_ids: list[str] | None = None,
    note: str | None = None,
    effective_release_id: str | None = None,
) -> dict[str, object]:
    registry_path, repo_root, registry = load_registry(path)
    failures: list[str] = []
    index = build_index(registry, failures)
    if failures:
        raise ValidationError("Registry identity validation failed before lifecycle transition")

    feature_rows = {row["id"]: row for row in registry["features"]}
    missing = [feature_id for feature_id in ids if feature_id not in feature_rows]
    if missing:
        raise ValueError(f"Unknown feature ids: {', '.join(sorted(missing))}")

    guard_reports = [
        evaluate_feature_lifecycle_transition_guard(
            registry,
            index,
            feature_id=feature_id,
            target_stage=stage,
            replacement_feature_ids=replacement_feature_ids,
            note=note,
        )
        for feature_id in ids
    ]
    guard_failures = [failure for report in guard_reports for failure in report["failures"]]
    if guard_failures:
        raise GuardError("; ".join(guard_failures))

    for feature_id in ids:
        lifecycle = feature_rows[feature_id]["lifecycle"]
        lifecycle["stage"] = stage
        lifecycle["replacement_feature_ids"] = replacement_feature_ids or []
        lifecycle["note"] = note
        if effective_release_id is not None:
            lifecycle["effective_release_id"] = effective_release_id

    report = validate_registry_document(registry, registry_path, repo_root)
    if not report["passed"]:
        raise ValidationError("Registry validation failed after lifecycle transition")

    save_registry(registry_path, registry)
    return {
        "passed": True,
        "registry_path": registry_path.as_posix(),
        "updated_ids": ids,
        "guard_reports": guard_reports,
        "validation": report,
    }
