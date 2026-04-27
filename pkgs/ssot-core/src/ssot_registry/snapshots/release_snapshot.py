from __future__ import annotations

from pathlib import Path

from ssot_registry.model.ids import filesystem_safe_id
from ssot_registry.snapshots.hashing import hash_paths
from ssot_registry.util.fs import sha256_path
from ssot_registry.util.time import utc_now_iso


def build_release_snapshot(
    repo_root: Path,
    registry_path: Path,
    release: dict[str, object],
    boundaries: list[dict[str, object]],
    features: list[dict[str, object]],
    profiles: list[dict[str, object]],
    profile_evaluations: list[dict[str, object]],
    claims: list[dict[str, object]],
    tests: list[dict[str, object]],
    evidence: list[dict[str, object]],
) -> tuple[dict[str, object], Path]:
    relative_paths = [test["path"] for test in tests] + [row["path"] for row in evidence]
    snapshot = {
        "schema_version": 1,
        "kind": "release_snapshot",
        "generated_at": utc_now_iso(),
        "registry_path": registry_path.relative_to(repo_root).as_posix(),
        "registry_sha256": sha256_path(registry_path),
        "release": release,
        "boundary": boundaries[0] if boundaries else None,
        "boundaries": boundaries,
        "features": features,
        "profiles": profiles,
        "profile_evaluations": profile_evaluations,
        "claims": claims,
        "tests": tests,
        "evidence": evidence,
        "file_hashes": hash_paths(repo_root, relative_paths),
        "summary": {
            "release_id": release["id"],
            "version": release["version"],
            "boundary_id": boundaries[0]["id"] if boundaries else None,
            "boundary_ids": [boundary["id"] for boundary in boundaries],
            "boundary_count": len(boundaries),
            "feature_count": len(features),
            "profile_count": len(profiles),
            "claim_count": len(claims),
            "test_count": len(tests),
            "evidence_count": len(evidence),
            "status": release["status"],
        },
    }
    output_path = repo_root / ".ssot" / "releases" / filesystem_safe_id(release["id"]) / "release.snapshot.json"
    return snapshot, output_path
