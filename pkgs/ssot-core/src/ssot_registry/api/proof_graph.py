from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from ssot_registry.model.enums import CLAIM_TIER_RANK
from ssot_registry.util.errors import GuardError, ValidationError
from ssot_registry.util.jsonio import save_json

from .boundary import freeze_boundary
from .load import load_registry
from .release import certify_release, promote_release, publish_release
from .save import save_registry
from .status_sync import sync_automated_statuses
from .test_execution import run_resolved_test_rows
from .validate import validate_registry, validate_registry_document


def _row_lookup(registry: dict[str, Any], section: str) -> dict[str, dict[str, Any]]:
    return {
        row["id"]: row
        for row in registry.get(section, [])
        if isinstance(row, dict) and isinstance(row.get("id"), str)
    }


def _dedupe_preserve(values: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for value in values:
        if value not in seen:
            seen.add(value)
            ordered.append(value)
    return ordered


def _ensure_list(row: dict[str, Any], field_name: str) -> list[str]:
    value = row.get(field_name)
    if not isinstance(value, list):
        value = []
        row[field_name] = value
    return value


def _safe_slug(entity_id: str) -> str:
    return entity_id.split(":", 1)[-1].replace("/", ".").replace(" ", "-").lower()


def _claims_for_feature(feature: dict[str, Any], claim_lookup: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    return [claim_lookup[claim_id] for claim_id in feature.get("claim_ids", []) if claim_id in claim_lookup]


def _claim_for_tier(feature: dict[str, Any], claim_lookup: dict[str, dict[str, Any]], tier: str) -> dict[str, Any] | None:
    for claim in _claims_for_feature(feature, claim_lookup):
        if claim.get("tier") == tier:
            return claim
    return None


def _release_claim_for_feature(feature: dict[str, Any], claim_lookup: dict[str, dict[str, Any]]) -> dict[str, Any]:
    claims = _claims_for_feature(feature, claim_lookup)
    if not claims:
        raise ValidationError(f"Feature {feature['id']} has no linked claims")
    target_tier = str(feature.get("plan", {}).get("target_claim_tier") or "T1")
    exact = [claim for claim in claims if claim.get("tier") == target_tier]
    if exact:
        return exact[0]
    ranked = sorted(claims, key=lambda claim: CLAIM_TIER_RANK.get(str(claim.get("tier")), -1), reverse=True)
    return ranked[0]


def _require_proof_graph_feature(feature: dict[str, Any], claim_lookup: dict[str, dict[str, Any]]) -> None:
    release_claim = _release_claim_for_feature(feature, claim_lookup)
    if CLAIM_TIER_RANK.get(str(release_claim.get("tier")), -1) < CLAIM_TIER_RANK["T3"]:
        raise ValidationError(
            f"Feature {feature['id']} does not have a linked T3-capable claim; proof-graph certification flow requires T3 coverage"
        )
    if _claim_for_tier(feature, claim_lookup, "T1") is None:
        raise ValidationError(f"Feature {feature['id']} is missing a linked T1 claim required for source evidence closure")


def _write_evidence_artifact(
    repo_root: Path,
    *,
    feature: dict[str, Any],
    evidence: dict[str, Any],
    linked_test_ids: list[str],
    summary: dict[str, Any],
) -> None:
    save_json(
        repo_root / str(evidence["path"]),
        {
            "schema_version": "ssot.evidence.bundle.v1",
            "feature_id": feature["id"],
            "evidence_id": evidence["id"],
            "tier": evidence["tier"],
            "status": evidence["status"],
            "claim_ids": list(evidence.get("claim_ids", [])),
            "test_ids": linked_test_ids,
            "summary": summary,
            "robustness_dimensions": list(evidence.get("robustness_dimensions", [])),
            "source_evidence_ids": list(evidence.get("source_evidence_ids", [])),
            "release_context": deepcopy(evidence.get("release_context", {})),
        },
    )


def _ensure_t1_evidence_row(
    registry: dict[str, Any],
    feature: dict[str, Any],
    claim_lookup: dict[str, dict[str, Any]],
    evidence_lookup: dict[str, dict[str, Any]],
    linked_test_ids: list[str],
) -> dict[str, Any]:
    slug = _safe_slug(str(feature["id"]))
    evidence_id = f"evd:t1.{slug}.proof-graph-source"
    row = evidence_lookup.get(evidence_id)
    if row is None:
        row = {
            "id": evidence_id,
            "title": f"{feature['title']} proof-graph source evidence",
            "status": "passed",
            "kind": "bundle",
            "tier": "T1",
            "body": f"T1 source evidence for {feature['id']}.",
            "origin": feature.get("origin", "repo-local"),
            "path": f".ssot/evidence/{slug}/proof-graph-t1.json",
            "claim_ids": [],
            "test_ids": [],
        }
        registry.setdefault("evidence", []).append(row)
        evidence_lookup[evidence_id] = row

    t1_claim = _claim_for_tier(feature, claim_lookup, "T1")
    assert t1_claim is not None
    row["status"] = "passed"
    row["kind"] = "bundle"
    row["tier"] = "T1"
    row["claim_ids"] = _dedupe_preserve([t1_claim["id"], *_ensure_list(row, "claim_ids")])
    row["test_ids"] = _dedupe_preserve([*linked_test_ids, *_ensure_list(row, "test_ids")])
    _ensure_list(t1_claim, "evidence_ids")
    t1_claim["evidence_ids"] = _dedupe_preserve([row["id"], *t1_claim["evidence_ids"]])
    for test_id in linked_test_ids:
        test = _row_lookup(registry, "tests")[test_id]
        test["evidence_ids"] = _dedupe_preserve([row["id"], *_ensure_list(test, "evidence_ids")])
    return row


def _ensure_t3_evidence_row(
    registry: dict[str, Any],
    feature: dict[str, Any],
    claim_lookup: dict[str, dict[str, Any]],
    evidence_lookup: dict[str, dict[str, Any]],
    linked_test_ids: list[str],
    *,
    release_id: str,
    boundary_id: str,
    robustness_dimensions: list[str],
    source_evidence_id: str,
) -> dict[str, Any]:
    release_claim = _release_claim_for_feature(feature, claim_lookup)
    slug = _safe_slug(str(feature["id"]))
    evidence_id = f"evd:t3.{slug}.proof-graph"
    row = evidence_lookup.get(evidence_id)
    if row is None:
        row = {
            "id": evidence_id,
            "title": f"{feature['title']} proof-graph certification evidence",
            "status": "planned",
            "kind": "bundle",
            "tier": "T3",
            "body": f"T3 proof-graph evidence for {feature['id']}.",
            "origin": feature.get("origin", "repo-local"),
            "path": f".ssot/evidence/{slug}/proof-graph-t3.json",
            "claim_ids": [],
            "test_ids": [],
        }
        registry.setdefault("evidence", []).append(row)
        evidence_lookup[evidence_id] = row

    row["status"] = "passed"
    row["kind"] = "bundle"
    row["tier"] = "T3"
    row["claim_ids"] = _dedupe_preserve([release_claim["id"], *_ensure_list(row, "claim_ids")])
    row["test_ids"] = _dedupe_preserve([*linked_test_ids, *_ensure_list(row, "test_ids")])
    row["robustness_dimensions"] = list(dict.fromkeys(robustness_dimensions))
    row["source_evidence_ids"] = _dedupe_preserve([source_evidence_id, *_ensure_list(row, "source_evidence_ids")])
    row["release_context"] = {
        "release_id": release_id,
        "boundary_id": boundary_id,
        "boundary_ids": [boundary_id],
    }
    _ensure_list(release_claim, "evidence_ids")
    release_claim["evidence_ids"] = _dedupe_preserve([row["id"], *release_claim["evidence_ids"]])
    for test_id in linked_test_ids:
        test = _row_lookup(registry, "tests")[test_id]
        test["evidence_ids"] = _dedupe_preserve([row["id"], *_ensure_list(test, "evidence_ids")])
    return row


def _ensure_boundary(
    registry: dict[str, Any],
    *,
    boundary_id: str,
    boundary_title: str,
    feature_ids: list[str],
) -> dict[str, Any]:
    boundary_lookup = _row_lookup(registry, "boundaries")
    boundary = boundary_lookup.get(boundary_id)
    if boundary is None:
        boundary = {
            "id": boundary_id,
            "title": boundary_title,
            "status": "active",
            "frozen": False,
            "feature_ids": [],
            "profile_ids": [],
        }
        registry.setdefault("boundaries", []).append(boundary)
    boundary["title"] = boundary.get("title") or boundary_title
    boundary["status"] = "active"
    boundary["frozen"] = False
    boundary["feature_ids"] = _dedupe_preserve([*feature_ids, *_ensure_list(boundary, "feature_ids")])
    return boundary


def _ensure_release(
    registry: dict[str, Any],
    *,
    release_id: str,
    release_version: str,
    boundary_id: str,
    claim_ids: list[str],
    evidence_ids: list[str],
) -> dict[str, Any]:
    release_lookup = _row_lookup(registry, "releases")
    release = release_lookup.get(release_id)
    if release is None:
        release = {
            "id": release_id,
            "version": release_version,
            "status": "candidate",
            "boundary_id": boundary_id,
            "boundary_ids": [boundary_id],
            "claim_ids": [],
            "evidence_ids": [],
        }
        registry.setdefault("releases", []).append(release)
    release["version"] = release_version
    release["status"] = "candidate"
    release["boundary_id"] = boundary_id
    release["boundary_ids"] = [boundary_id]
    release["claim_ids"] = _dedupe_preserve([*claim_ids, *_ensure_list(release, "claim_ids")])
    release["evidence_ids"] = _dedupe_preserve([*evidence_ids, *_ensure_list(release, "evidence_ids")])
    return release


def _save_checked(registry_path: Path, repo_root: Path, registry: dict[str, Any], action: str) -> None:
    report = validate_registry_document(registry, registry_path, repo_root)
    if not report["passed"]:
        detail = "; ".join(report["failures"])
        raise ValidationError(f"Registry validation failed after {action}: {detail}")
    save_registry(registry_path, registry)


def certify_feature_proof_graphs(
    path: str | Path,
    *,
    feature_ids: list[str],
    boundary_id: str,
    boundary_title: str,
    release_id: str,
    release_version: str,
    robustness_dimensions: list[str],
    write_report: bool = False,
    promote: bool = False,
    publish: bool = False,
) -> dict[str, Any]:
    registry_path, repo_root, registry = load_registry(path)
    preflight = validate_registry(registry_path)
    if not preflight["passed"]:
        raise ValidationError("Registry validation failed before proof-graph certification flow")

    feature_lookup = _row_lookup(registry, "features")
    claim_lookup = _row_lookup(registry, "claims")
    test_lookup = _row_lookup(registry, "tests")
    evidence_lookup = _row_lookup(registry, "evidence")
    selected_feature_ids = _dedupe_preserve(feature_ids)
    missing = [feature_id for feature_id in selected_feature_ids if feature_id not in feature_lookup]
    if missing:
        raise ValueError(f"Unknown feature ids: {', '.join(sorted(missing))}")

    selected_features = [feature_lookup[feature_id] for feature_id in selected_feature_ids]
    for feature in selected_features:
        _require_proof_graph_feature(feature, claim_lookup)

    selected_test_ids = _dedupe_preserve(
        [test_id for feature in selected_features for test_id in feature.get("test_ids", []) if test_id in test_lookup]
    )
    if not selected_test_ids:
        raise ValidationError("Proof-graph certification flow requires linked tests")
    selected_tests = [test_lookup[test_id] for test_id in selected_test_ids]

    test_run = run_resolved_test_rows(
        repo_root,
        target={"kind": "feature", "ids": selected_feature_ids},
        tests=selected_tests,
    )
    if not test_run["passed"]:
        failed = [case["test_id"] for case in test_run.get("cases", []) if case.get("outcome") != "passed"]
        raise GuardError(f"Proof-graph certification flow failed linked tests: {', '.join(failed)}")

    t1_evidence_ids: list[str] = []
    t3_evidence_ids: list[str] = []
    release_claim_ids: list[str] = []
    for test in selected_tests:
        test["status"] = "passing"

    for feature in selected_features:
        feature["implementation_status"] = "implemented"
        plan = feature.get("plan") if isinstance(feature.get("plan"), dict) else {}
        if plan.get("horizon") not in {"current", "explicit"}:
            plan["horizon"] = "current"
        linked_test_ids = [test_id for test_id in feature.get("test_ids", []) if test_id in test_lookup]
        t1_evidence = _ensure_t1_evidence_row(registry, feature, claim_lookup, evidence_lookup, linked_test_ids)
        t3_evidence = _ensure_t3_evidence_row(
            registry,
            feature,
            claim_lookup,
            evidence_lookup,
            linked_test_ids,
            release_id=release_id,
            boundary_id=boundary_id,
            robustness_dimensions=robustness_dimensions,
            source_evidence_id=t1_evidence["id"],
        )
        release_claim = _release_claim_for_feature(feature, claim_lookup)
        t1_evidence_ids.append(str(t1_evidence["id"]))
        t3_evidence_ids.append(str(t3_evidence["id"]))
        release_claim_ids.append(str(release_claim["id"]))

    for feature in selected_features:
        linked_test_ids = [test_id for test_id in feature.get("test_ids", []) if test_id in test_lookup]
        t1_evidence = evidence_lookup[f"evd:t1.{_safe_slug(str(feature['id']))}.proof-graph-source"]
        t3_evidence = evidence_lookup[f"evd:t3.{_safe_slug(str(feature['id']))}.proof-graph"]
        _write_evidence_artifact(repo_root, feature=feature, evidence=t1_evidence, linked_test_ids=linked_test_ids, summary=test_run["summary"])
        _write_evidence_artifact(repo_root, feature=feature, evidence=t3_evidence, linked_test_ids=linked_test_ids, summary=test_run["summary"])

    _ensure_boundary(
        registry,
        boundary_id=boundary_id,
        boundary_title=boundary_title,
        feature_ids=selected_feature_ids,
    )
    _ensure_release(
        registry,
        release_id=release_id,
        release_version=release_version,
        boundary_id=boundary_id,
        claim_ids=release_claim_ids,
        evidence_ids=t3_evidence_ids,
    )
    program = registry.setdefault("program", {})
    if isinstance(program, dict):
        program["active_boundary_id"] = boundary_id
        program["active_release_id"] = release_id

    _save_checked(registry_path, repo_root, registry, "preparing proof-graph certification flow")
    freeze_result = freeze_boundary(repo_root, boundary_id=boundary_id)
    certification_result = certify_release(repo_root, release_id=release_id, write_report=write_report)
    sync_after_certify = sync_automated_statuses(repo_root)

    if promote or publish:
        promote_release(repo_root, release_id=release_id)
    if publish:
        publish_release(repo_root, release_id=release_id)
    sync_after_publish = sync_automated_statuses(repo_root)

    _registry_path, repo_root, final_registry = load_registry(repo_root)
    final_evidence_lookup = _row_lookup(final_registry, "evidence")
    for feature in selected_features:
        slug = _safe_slug(str(feature["id"]))
        linked_test_ids = [test_id for test_id in feature.get("test_ids", []) if test_id in test_lookup]
        final_feature = _row_lookup(final_registry, "features")[str(feature["id"])]
        _write_evidence_artifact(
            repo_root,
            feature=final_feature,
            evidence=final_evidence_lookup[f"evd:t1.{slug}.proof-graph-source"],
            linked_test_ids=linked_test_ids,
            summary=test_run["summary"],
        )
        _write_evidence_artifact(
            repo_root,
            feature=final_feature,
            evidence=final_evidence_lookup[f"evd:t3.{slug}.proof-graph"],
            linked_test_ids=linked_test_ids,
            summary=test_run["summary"],
        )

    final_validation = validate_registry(repo_root)
    if not final_validation["passed"]:
        raise ValidationError("Registry validation failed after proof-graph certification flow")

    return {
        "passed": True,
        "registry_path": registry_path.as_posix(),
        "feature_ids": selected_feature_ids,
        "boundary_id": boundary_id,
        "release_id": release_id,
        "test_run": test_run,
        "freeze": freeze_result,
        "certification": certification_result,
        "sync_after_certify": sync_after_certify,
        "sync_after_publish": sync_after_publish,
        "release_claim_ids": _dedupe_preserve(release_claim_ids),
        "t1_evidence_ids": _dedupe_preserve(t1_evidence_ids),
        "t3_evidence_ids": _dedupe_preserve(t3_evidence_ids),
        "validation": final_validation,
    }
