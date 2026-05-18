from __future__ import annotations

import fnmatch
import hashlib
from pathlib import Path
from typing import Any

from ssot_registry.util.fs import sha256_path
from ssot_registry.util.jsonio import save_json
from ssot_registry.util.jcs import dump_jcs_json

from .load import load_registry
from .validate import validate_registry

DEFAULT_EXCLUDES = {
    ".git/**",
    ".pytest_cache/**",
    ".tmp/**",
    ".tmp_test_runs/**",
    ".uv-cache/**",
    ".venv/**",
    "__pycache__/**",
    "dist/**",
    "node_modules/**",
}


def _lookup(registry: dict[str, Any], section: str) -> dict[str, dict[str, Any]]:
    return {row["id"]: row for row in registry.get(section, []) if isinstance(row, dict) and isinstance(row.get("id"), str)}


def _safe_release_id(release_id: str) -> str:
    return release_id.replace(":", "__").replace("/", "_").replace("\\", "_")


def _is_excluded(relative_path: str, excludes: set[str]) -> bool:
    return any(fnmatch.fnmatch(relative_path, pattern) for pattern in excludes)


def resolve_snapshot_paths(
    repo_root: Path,
    registry: dict[str, Any],
    *,
    path_policy: str = "ssot-only",
    extra_paths: list[str] | None = None,
) -> list[str]:
    if path_policy not in {"ssot-only", "declared", "full-repo"}:
        raise ValueError("path_policy must be one of ssot-only, declared, or full-repo")
    paths: set[str] = set(extra_paths or [])
    if path_policy in {"ssot-only", "declared"}:
        paths.add(".ssot/registry.json")
        for section in ("adrs", "specs", "evidence", "tests"):
            for row in registry.get(section, []):
                row_path = row.get("path")
                if isinstance(row_path, str) and row_path:
                    paths.add(row_path)
    if path_policy == "full-repo":
        for child in repo_root.rglob("*"):
            if child.is_file():
                relative_path = child.relative_to(repo_root).as_posix()
                if not _is_excluded(relative_path, DEFAULT_EXCLUDES):
                    paths.add(relative_path)
    existing = []
    for relative_path in sorted(paths):
        if (repo_root / relative_path).is_file():
            existing.append(relative_path)
    return existing


def deterministic_root_hash(file_hashes: dict[str, str]) -> str:
    return hashlib.sha256(dump_jcs_json(file_hashes).encode("utf-8")).hexdigest()


def build_source_snapshot(
    path: str | Path,
    *,
    release_id: str | None = None,
    path_policy: str = "ssot-only",
    extra_paths: list[str] | None = None,
    output: str | Path | None = None,
) -> dict[str, Any]:
    registry_path, repo_root, registry = load_registry(path)
    selected_release_id = release_id or registry.get("program", {}).get("active_release_id")
    file_paths = resolve_snapshot_paths(repo_root, registry, path_policy=path_policy, extra_paths=extra_paths)
    file_hashes = {relative_path: sha256_path(repo_root / relative_path) for relative_path in file_paths}
    snapshot = {
        "kind": "governed_source_snapshot",
        "registry_path": registry_path.as_posix(),
        "release_id": selected_release_id,
        "path_policy": path_policy,
        "file_count": len(file_hashes),
        "file_hashes": file_hashes,
        "root_hash": deterministic_root_hash(file_hashes),
    }
    output_path = Path(output) if output is not None else repo_root / ".ssot" / "releases" / _safe_release_id(str(selected_release_id)) / "source.snapshot.json"
    save_json(output_path, snapshot)
    return {"passed": True, "output_path": output_path.as_posix(), "snapshot": snapshot}


def build_artifact_manifest(
    path: str | Path,
    *,
    release_id: str | None = None,
    artifacts: list[dict[str, Any]],
    output: str | Path | None = None,
) -> dict[str, Any]:
    _registry_path, repo_root, registry = load_registry(path)
    selected_release_id = release_id or registry.get("program", {}).get("active_release_id")
    seen_ids: set[str] = set()
    failures: list[str] = []
    rows: list[dict[str, Any]] = []
    for artifact in artifacts:
        artifact_id = str(artifact.get("id", "")).strip()
        relative_path = str(artifact.get("path", "")).strip()
        if not artifact_id:
            failures.append("artifact id is required")
            continue
        if artifact_id in seen_ids:
            failures.append(f"duplicate artifact id {artifact_id}")
            continue
        seen_ids.add(artifact_id)
        target = repo_root / relative_path
        if not target.is_file():
            failures.append(f"artifact {artifact_id} path does not exist: {relative_path}")
            continue
        expected_sha = artifact.get("sha256")
        actual_sha = sha256_path(target)
        if expected_sha is not None and expected_sha != actual_sha:
            failures.append(f"artifact {artifact_id} sha256 mismatch")
        rows.append(
            {
                "id": artifact_id,
                "path": relative_path,
                "kind": artifact.get("kind", "artifact"),
                "media_type": artifact.get("media_type", "application/octet-stream"),
                "size": target.stat().st_size,
                "sha256": actual_sha,
            }
        )
    manifest = {"kind": "output_artifact_manifest", "release_id": selected_release_id, "artifacts": rows}
    output_path = Path(output) if output is not None else repo_root / ".ssot" / "releases" / _safe_release_id(str(selected_release_id)) / "artifact.manifest.json"
    if not failures:
        save_json(output_path, manifest)
    return {"passed": not failures, "failures": failures, "output_path": output_path.as_posix(), "manifest": manifest}


def build_local_evidence_bundle(
    path: str | Path,
    *,
    release_id: str | None = None,
    source_snapshot: dict[str, Any] | None = None,
    artifact_manifest: dict[str, Any] | None = None,
    output: str | Path | None = None,
) -> dict[str, Any]:
    _registry_path, repo_root, registry = load_registry(path)
    selected_release_id = str(release_id or registry.get("program", {}).get("active_release_id"))
    releases = _lookup(registry, "releases")
    claims = _lookup(registry, "claims")
    tests = _lookup(registry, "tests")
    evidence = _lookup(registry, "evidence")
    release = releases[selected_release_id]
    claim_ids = list(release.get("claim_ids", []))
    evidence_ids = sorted(set(release.get("evidence_ids", [])) | {eid for cid in claim_ids for eid in claims.get(cid, {}).get("evidence_ids", [])})
    test_ids = sorted({tid for cid in claim_ids for tid in claims.get(cid, {}).get("test_ids", [])})
    bundle = {
        "kind": "local_release_evidence_bundle",
        "release": release,
        "boundary_ids": list(release.get("boundary_ids", [release.get("boundary_id")])),
        "claims": [claims[claim_id] for claim_id in claim_ids if claim_id in claims],
        "tests": [tests[test_id] for test_id in test_ids if test_id in tests],
        "evidence": [evidence[evidence_id] for evidence_id in evidence_ids if evidence_id in evidence],
        "source_snapshot_root_hash": (source_snapshot or {}).get("root_hash"),
        "artifact_manifest_hash": hashlib.sha256(dump_jcs_json(artifact_manifest or {}).encode("utf-8")).hexdigest()
        if artifact_manifest is not None
        else None,
        "verification": {"mode": "local", "schema": "ssot-local-assurance-v1"},
    }
    bundle["bundle_hash"] = hashlib.sha256(dump_jcs_json(bundle).encode("utf-8")).hexdigest()
    output_path = Path(output) if output is not None else repo_root / ".ssot" / "releases" / _safe_release_id(selected_release_id) / "evidence.bundle.json"
    save_json(output_path, bundle)
    return {"passed": True, "output_path": output_path.as_posix(), "bundle_hash": bundle["bundle_hash"], "bundle": bundle}


def verify_local_release(
    path: str | Path,
    *,
    release_id: str | None = None,
    path_policy: str = "ssot-only",
    write_artifacts: bool = True,
    blocking: bool = False,
) -> dict[str, Any]:
    registry_path, repo_root, registry = load_registry(path)
    selected_release_id = str(release_id or registry.get("program", {}).get("active_release_id"))
    failures: list[str] = []
    validation = validate_registry(registry_path)
    if not validation["passed"]:
        failures.extend(str(item) for item in validation.get("failures", []))

    snapshot_result = build_source_snapshot(path, release_id=selected_release_id, path_policy=path_policy)
    artifact_result = build_artifact_manifest(
        path,
        release_id=selected_release_id,
        artifacts=[{"id": "registry", "path": ".ssot/registry.json", "kind": "registry", "media_type": "application/json"}],
    )
    if not artifact_result["passed"]:
        failures.extend(artifact_result["failures"])
    bundle_result = build_local_evidence_bundle(
        path,
        release_id=selected_release_id,
        source_snapshot=snapshot_result["snapshot"],
        artifact_manifest=artifact_result["manifest"],
    )
    report = {
        "passed": not failures,
        "blocking": blocking,
        "registry_path": registry_path.as_posix(),
        "release_id": selected_release_id,
        "path_policy": path_policy,
        "failures": failures,
        "source_snapshot": snapshot_result["snapshot"],
        "artifact_manifest": artifact_result["manifest"],
        "bundle_hash": bundle_result["bundle_hash"],
        "artifact_paths": {
            "source_snapshot": snapshot_result["output_path"],
            "artifact_manifest": artifact_result["output_path"],
            "evidence_bundle": bundle_result["output_path"],
        },
    }
    report_path = repo_root / ".ssot" / "reports" / "local-release-verification.report.json"
    if write_artifacts:
        save_json(report_path, report)
    if blocking and failures:
        return {**report, "report_path": report_path.as_posix()}
    return {**report, "report_path": report_path.as_posix()}
