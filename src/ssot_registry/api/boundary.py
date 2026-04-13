from __future__ import annotations

from pathlib import Path

from ssot_registry.snapshots.boundary_snapshot import build_boundary_snapshot
from ssot_registry.util.errors import ValidationError
from ssot_registry.util.jsonio import save_json
from .load import load_registry
from .save import save_registry
from .validate import validate_registry, validate_registry_document


def freeze_boundary(path: str | Path, boundary_id: str | None = None) -> dict[str, object]:
    registry_path, repo_root, registry = load_registry(path)

    preflight = validate_registry(registry_path)
    if not preflight["passed"]:
        raise ValidationError("Registry validation failed; boundary freeze refused")

    boundary_lookup = {row["id"]: row for row in registry["boundaries"]}
    selected_boundary_id = boundary_id or registry["program"]["active_boundary_id"]
    boundary = boundary_lookup.get(selected_boundary_id)
    if boundary is None:
        raise ValueError(f"Unknown boundary id: {selected_boundary_id}")

    boundary["frozen"] = True
    boundary["status"] = "frozen"

    postflight = validate_registry_document(registry, registry_path, repo_root)
    if not postflight["passed"]:
        raise ValidationError("Registry validation failed after boundary freeze")

    save_registry(registry_path, registry)

    features = {row["id"]: row for row in registry["features"]}
    snapshot, output_path = build_boundary_snapshot(
        repo_root,
        registry_path,
        boundary,
        [features[feature_id] for feature_id in boundary.get("feature_ids", []) if feature_id in features],
    )
    save_json(output_path, snapshot)

    return {
        "passed": True,
        "registry_path": registry_path.as_posix(),
        "boundary_id": selected_boundary_id,
        "output_path": output_path.as_posix(),
        "snapshot": snapshot["summary"],
    }
