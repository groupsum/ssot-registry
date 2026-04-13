from __future__ import annotations

from pathlib import Path

from ssot_registry.util.errors import ValidationError
from .load import load_registry
from .save import save_registry
from .validate import validate_registry_document


def _validate_candidate(registry: dict[str, object], registry_path: Path, repo_root: Path) -> dict[str, object]:
    report = validate_registry_document(registry, registry_path, repo_root)
    if not report["passed"]:
        raise ValidationError("Registry validation failed after attempted mutation")
    return report


def plan_features(
    path: str | Path,
    ids: list[str],
    horizon: str,
    claim_tier: str | None,
    slot: str | None = None,
    target_lifecycle_stage: str | None = None,
) -> dict[str, object]:
    registry_path, repo_root, registry = load_registry(path)
    features = {row["id"]: row for row in registry["features"]}

    missing = [feature_id for feature_id in ids if feature_id not in features]
    if missing:
        raise ValueError(f"Unknown feature ids: {', '.join(sorted(missing))}")

    for feature_id in ids:
        plan = features[feature_id]["plan"]
        plan["horizon"] = horizon
        plan["slot"] = slot
        if claim_tier is not None:
            plan["target_claim_tier"] = claim_tier
        if target_lifecycle_stage is not None:
            plan["target_lifecycle_stage"] = target_lifecycle_stage

    report = _validate_candidate(registry, registry_path, repo_root)
    save_registry(registry_path, registry)
    return {
        "passed": True,
        "registry_path": registry_path.as_posix(),
        "updated_ids": ids,
        "validation": report,
    }


def plan_issues(path: str | Path, ids: list[str], horizon: str, slot: str | None = None) -> dict[str, object]:
    registry_path, repo_root, registry = load_registry(path)
    issues = {row["id"]: row for row in registry["issues"]}

    missing = [issue_id for issue_id in ids if issue_id not in issues]
    if missing:
        raise ValueError(f"Unknown issue ids: {', '.join(sorted(missing))}")

    for issue_id in ids:
        plan = issues[issue_id]["plan"]
        plan["horizon"] = horizon
        plan["slot"] = slot

    report = _validate_candidate(registry, registry_path, repo_root)
    save_registry(registry_path, registry)
    return {
        "passed": True,
        "registry_path": registry_path.as_posix(),
        "updated_ids": ids,
        "validation": report,
    }
