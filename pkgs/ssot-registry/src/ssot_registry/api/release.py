from __future__ import annotations

from pathlib import Path

from ssot_registry.guards.certification import evaluate_release_certification_guard
from ssot_registry.guards.promotion import evaluate_release_promotion_guard
from ssot_registry.guards.publication import evaluate_release_publication_guard
from ssot_registry.model.enums import CLAIM_STATUS_RANK
from ssot_registry.reports.certification_report import build_certification_report
from ssot_registry.snapshots.published_snapshot import build_published_snapshot
from ssot_registry.snapshots.release_snapshot import build_release_snapshot
from ssot_registry.util.errors import GuardError, ValidationError
from ssot_registry.util.jsonio import save_json
from ssot_registry.validators.identity import build_index
from .load import load_registry
from .profile_eval import evaluate_profile
from .profile_resolution import resolve_boundary_feature_ids
from .save import save_registry
from .validate import validate_registry, validate_registry_document


def _selected_release_id(registry: dict[str, object], release_id: str | None) -> str:
    return release_id or registry["program"]["active_release_id"]


def _entity_lookup(registry: dict[str, object], section: str) -> dict[str, dict[str, object]]:
    return {row["id"]: row for row in registry[section]}


def certify_release(path: str | Path, release_id: str | None = None, write_report: bool = False) -> dict[str, object]:
    registry_path, repo_root, registry = load_registry(path)
    preflight = validate_registry(registry_path)
    if not preflight["passed"]:
        raise ValidationError("Registry validation failed; release certification refused")

    index = build_index(registry, [])
    selected_release_id = _selected_release_id(registry, release_id)
    certification = evaluate_release_certification_guard(registry, index, selected_release_id)
    report = build_certification_report(registry, registry_path.as_posix(), certification)

    if write_report:
        save_json(repo_root / ".ssot" / "reports" / "certification.report.json", report)

    if not certification["passed"]:
        raise GuardError("; ".join(certification["failures"]))

    release = _entity_lookup(registry, "releases")[selected_release_id]
    release["status"] = "certified"
    claims = _entity_lookup(registry, "claims")
    for claim_id in release.get("claim_ids", []):
        if claim_id in claims and CLAIM_STATUS_RANK[claims[claim_id]["status"]] < CLAIM_STATUS_RANK["certified"]:
            claims[claim_id]["status"] = "certified"

    postflight = validate_registry_document(registry, registry_path, repo_root)
    if not postflight["passed"]:
        raise ValidationError("Registry validation failed after certification")

    save_registry(registry_path, registry)
    return {
        "passed": True,
        "registry_path": registry_path.as_posix(),
        "release_id": selected_release_id,
        "report_path": (repo_root / ".ssot" / "reports" / "certification.report.json").as_posix() if write_report else None,
        "certification": certification,
    }


def promote_release(path: str | Path, release_id: str | None = None) -> dict[str, object]:
    registry_path, repo_root, registry = load_registry(path)
    preflight = validate_registry(registry_path)
    if not preflight["passed"]:
        raise ValidationError("Registry validation failed; release promotion refused")

    index = build_index(registry, [])
    selected_release_id = _selected_release_id(registry, release_id)
    promotion = evaluate_release_promotion_guard(registry, index, selected_release_id)
    if not promotion["passed"]:
        raise GuardError("; ".join(promotion["failures"]))

    release_lookup = _entity_lookup(registry, "releases")
    claim_lookup = _entity_lookup(registry, "claims")
    test_lookup = _entity_lookup(registry, "tests")
    evidence_lookup = _entity_lookup(registry, "evidence")
    feature_lookup = _entity_lookup(registry, "features")
    boundary_lookup = _entity_lookup(registry, "boundaries")

    release = release_lookup[selected_release_id]
    boundary = boundary_lookup[release["boundary_id"]]
    release["status"] = "promoted"
    for claim_id in release.get("claim_ids", []):
        if claim_id in claim_lookup and CLAIM_STATUS_RANK[claim_lookup[claim_id]["status"]] < CLAIM_STATUS_RANK["promoted"]:
            claim_lookup[claim_id]["status"] = "promoted"

    postflight = validate_registry_document(registry, registry_path, repo_root)
    if not postflight["passed"]:
        raise ValidationError("Registry validation failed after promotion")

    save_registry(registry_path, registry)

    release_claims = [claim_lookup[claim_id] for claim_id in release.get("claim_ids", []) if claim_id in claim_lookup]
    boundary_feature_ids = resolve_boundary_feature_ids(boundary, index)
    boundary_features = [feature_lookup[feature_id] for feature_id in boundary_feature_ids if feature_id in feature_lookup]
    boundary_profiles = [index["profiles"][profile_id] for profile_id in boundary.get("profile_ids", []) if profile_id in index["profiles"]]
    profile_evaluations = [evaluate_profile(profile, index, registry.get("guard_policies", {})) for profile in boundary_profiles]
    release_test_ids = sorted({test_id for claim in release_claims for test_id in claim.get("test_ids", []) if test_id in test_lookup})
    release_evidence_ids = sorted(
        set(release.get("evidence_ids", [])) | {evidence_id for claim in release_claims for evidence_id in claim.get("evidence_ids", [])}
    )
    release_tests = [test_lookup[test_id] for test_id in release_test_ids]
    release_evidence = [evidence_lookup[evidence_id] for evidence_id in release_evidence_ids if evidence_id in evidence_lookup]

    snapshot, output_path = build_release_snapshot(
        repo_root,
        registry_path,
        release,
        boundary,
        boundary_features,
        boundary_profiles,
        profile_evaluations,
        release_claims,
        release_tests,
        release_evidence,
    )
    save_json(output_path, snapshot)
    save_json(repo_root / ".ssot" / "reports" / "promotion.report.json", {
        "passed": True,
        "release_id": selected_release_id,
        "output_path": output_path.as_posix(),
    })

    return {
        "passed": True,
        "registry_path": registry_path.as_posix(),
        "release_id": selected_release_id,
        "output_path": output_path.as_posix(),
        "snapshot": snapshot["summary"],
    }


def publish_release(path: str | Path, release_id: str | None = None) -> dict[str, object]:
    registry_path, repo_root, registry = load_registry(path)
    preflight = validate_registry(registry_path)
    if not preflight["passed"]:
        raise ValidationError("Registry validation failed; release publication refused")

    index = build_index(registry, [])
    selected_release_id = _selected_release_id(registry, release_id)
    publication = evaluate_release_publication_guard(registry, index, selected_release_id)
    if not publication["passed"]:
        raise GuardError("; ".join(publication["failures"]))

    release_lookup = _entity_lookup(registry, "releases")
    claim_lookup = _entity_lookup(registry, "claims")
    evidence_lookup = _entity_lookup(registry, "evidence")
    boundary_lookup = _entity_lookup(registry, "boundaries")

    release = release_lookup[selected_release_id]
    boundary = boundary_lookup[release["boundary_id"]]
    release["status"] = "published"
    for claim_id in release.get("claim_ids", []):
        if claim_id in claim_lookup and CLAIM_STATUS_RANK[claim_lookup[claim_id]["status"]] < CLAIM_STATUS_RANK["published"]:
            claim_lookup[claim_id]["status"] = "published"

    postflight = validate_registry_document(registry, registry_path, repo_root)
    if not postflight["passed"]:
        raise ValidationError("Registry validation failed after publication")

    save_registry(registry_path, registry)

    claims = [claim_lookup[claim_id] for claim_id in release.get("claim_ids", []) if claim_id in claim_lookup]
    evidence_ids = sorted(set(release.get("evidence_ids", [])) | {evidence_id for claim in claims for evidence_id in claim.get("evidence_ids", [])})
    evidence = [evidence_lookup[evidence_id] for evidence_id in evidence_ids if evidence_id in evidence_lookup]
    snapshot, output_path = build_published_snapshot(
        repo_root,
        registry_path,
        release,
        boundary,
        claims,
        evidence,
    )
    save_json(output_path, snapshot)
    save_json(repo_root / ".ssot" / "reports" / "publication.report.json", {
        "passed": True,
        "release_id": selected_release_id,
        "output_path": output_path.as_posix(),
    })
    return {
        "passed": True,
        "registry_path": registry_path.as_posix(),
        "release_id": selected_release_id,
        "output_path": output_path.as_posix(),
        "snapshot": snapshot["summary"],
    }


def revoke_release(path: str | Path, release_id: str, reason: str) -> dict[str, object]:
    registry_path, repo_root, registry = load_registry(path)
    release_lookup = _entity_lookup(registry, "releases")
    if release_id not in release_lookup:
        raise ValueError(f"Unknown release id: {release_id}")

    release_lookup[release_id]["status"] = "revoked"
    postflight = validate_registry_document(registry, registry_path, repo_root)
    if not postflight["passed"]:
        raise ValidationError("Registry validation failed after revocation")

    save_registry(registry_path, registry)
    output_path = repo_root / ".ssot" / "releases" / release_id.replace(":", "__") / "revoked.snapshot.json"
    save_json(output_path, {
        "kind": "revoked_snapshot",
        "release_id": release_id,
        "reason": reason,
    })
    return {
        "passed": True,
        "registry_path": registry_path.as_posix(),
        "release_id": release_id,
        "output_path": output_path.as_posix(),
    }
