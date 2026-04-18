from __future__ import annotations

from pathlib import Path

from ssot_registry.model.ids import filesystem_safe_id
from ssot_registry.util.fs import sha256_path
from ssot_registry.util.time import utc_now_iso


def build_boundary_snapshot(
    repo_root: Path,
    registry_path: Path,
    boundary: dict[str, object],
    features: list[dict[str, object]],
) -> tuple[dict[str, object], Path]:
    snapshot = {
        "schema_version": 1,
        "kind": "boundary_snapshot",
        "generated_at": utc_now_iso(),
        "registry_path": registry_path.relative_to(repo_root).as_posix(),
        "registry_sha256": sha256_path(registry_path),
        "boundary": boundary,
        "features": features,
        "summary": {
            "boundary_id": boundary["id"],
            "feature_count": len(features),
            "profile_count": len(boundary.get("profile_ids", [])),
            "frozen": boundary["frozen"],
            "status": boundary["status"],
        },
    }
    output_path = repo_root / ".ssot" / "releases" / "boundaries" / f"{filesystem_safe_id(boundary['id'])}.snapshot.json"
    return snapshot, output_path
