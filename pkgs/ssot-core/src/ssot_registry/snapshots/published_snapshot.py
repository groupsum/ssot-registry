from __future__ import annotations

from pathlib import Path

from ssot_registry.model.ids import filesystem_safe_id
from ssot_registry.util.fs import sha256_path
from ssot_registry.util.time import utc_now_iso


def build_published_snapshot(
    repo_root: Path,
    registry_path: Path,
    release: dict[str, object],
    boundaries: list[dict[str, object]],
    claims: list[dict[str, object]],
    evidence: list[dict[str, object]],
) -> tuple[dict[str, object], Path]:
    snapshot = {
        "schema_version": 1,
        "kind": "published_snapshot",
        "generated_at": utc_now_iso(),
        "registry_path": registry_path.relative_to(repo_root).as_posix(),
        "registry_sha256": sha256_path(registry_path),
        "release": release,
        "boundary": boundaries[0] if boundaries else None,
        "boundaries": boundaries,
        "claims": claims,
        "evidence": evidence,
        "summary": {
            "release_id": release["id"],
            "version": release["version"],
            "status": release["status"],
            "boundary_ids": [boundary["id"] for boundary in boundaries],
            "boundary_count": len(boundaries),
            "claim_count": len(claims),
            "evidence_count": len(evidence),
        },
    }
    output_path = repo_root / ".ssot" / "releases" / filesystem_safe_id(release["id"]) / "published.snapshot.json"
    return snapshot, output_path
