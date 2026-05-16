from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from ssot_registry.guards.claim_closure import evaluate_claim_guard
from ssot_registry.guards.claim_tier_gates import evaluate_claim_tier_gate
from ssot_registry.guards.feature_claims import (
    active_required_feature_claims,
    claim_satisfies_feature_implementation,
    feature_claim_ceiling_failures,
)
from ssot_registry.model.enums import CLAIM_STATUS_RANK, CLAIM_TIER_RANK
from ssot_registry.validators.identity import build_index

from .load import load_registry
from .profile_eval import evaluate_profile
from .save import save_registry
from .validate import validate_registry_document

AUTOMATED_SECTIONS = ("evidence", "tests", "claims", "features", "profiles")
CLAIM_TERMINAL_STATUSES = {"retired"}
CLAIM_RELEASE_STATUSES = {"promoted", "published"}


def _is_planned_path(path: object, marker: str) -> bool:
    if not isinstance(path, str):
        return False
    normalized = path.replace("\\", "/")
    return marker in normalized


def _build_current_index(registry: dict[str, Any]) -> dict[str, dict[str, dict[str, object]]]:
    failures: list[str] = []
    return build_index(registry, failures)


def _change(section: str, entity_id: str, field: str, before: object, after: object, reason: str) -> dict[str, object] | None:
    if before == after:
        return None
    return {
        "section": section,
        "id": entity_id,
        "field": field,
        "before": before,
        "after": after,
        "reason": reason,
    }


def _apply(row: dict[str, Any], field: str, value: object) -> None:
    row[field] = value


def _missing_refs(row: dict[str, Any], field: str, target: dict[str, dict[str, Any]]) -> list[str]:
    return [value for value in row.get(field, []) if value not in target]


def _collapse_changes(changes: list[dict[str, object]]) -> list[dict[str, object]]:
    collapsed: dict[tuple[object, object, object], dict[str, object]] = {}
    order: list[tuple[object, object, object]] = []
    for change in changes:
        key = (change["section"], change["id"], change["field"])
        if key not in collapsed:
            collapsed[key] = dict(change)
            order.append(key)
            continue
        collapsed[key]["after"] = change["after"]
        collapsed[key]["reason"] = change["reason"]
    return [change for key in order if (change := collapsed[key])["before"] != change["after"]]


def _sync_evidence(registry: dict[str, Any], repo_root: Path) -> list[dict[str, object]]:
    index = _build_current_index(registry)
    changes: list[dict[str, object]] = []
    for evidence in registry.get("evidence", []):
        evidence_id = evidence["id"]
        reason = "evidence artifact exists and linked claim tiers are satisfied"
        status = "passed"
        if _is_planned_path(evidence.get("path"), "/evidence/planned/"):
            status = "planned"
            reason = "evidence path is a planned placeholder"
        elif not (repo_root / evidence["path"]).exists():
            status = "planned"
            reason = "evidence artifact path does not exist"
        elif _missing_refs(evidence, "claim_ids", index["claims"]) or _missing_refs(evidence, "test_ids", index["tests"]):
            status = "collected"
            reason = "evidence artifact exists but has missing linked claims or tests"
        else:
            tier_failures = [
                claim_id
                for claim_id in evidence.get("claim_ids", [])
                if CLAIM_TIER_RANK[evidence["tier"]] < CLAIM_TIER_RANK[index["claims"][claim_id]["tier"]]
            ]
            if tier_failures:
                status = "collected"
                reason = "evidence artifact exists but is below at least one linked claim tier"

        change = _change("evidence", evidence_id, "status", evidence.get("status"), status, reason)
        if change is not None:
            changes.append(change)
            _apply(evidence, "status", status)
    return changes


def _sync_tests(registry: dict[str, Any], repo_root: Path) -> list[dict[str, object]]:
    index = _build_current_index(registry)
    changes: list[dict[str, object]] = []
    for test in registry.get("tests", []):
        test_id = test["id"]
        reason = "test path exists and linked evidence is passed"
        status = "passing"
        if _is_planned_path(test.get("path"), "tests/planned/"):
            status = "planned"
            reason = "test path is a planned placeholder"
        elif not (repo_root / test["path"]).exists():
            status = "planned"
            reason = "test path does not exist"
        elif _missing_refs(test, "feature_ids", index["features"]) or _missing_refs(test, "claim_ids", index["claims"]):
            status = "blocked"
            reason = "test has missing linked features or claims"
        else:
            linked_evidence = [index["evidence"][evidence_id] for evidence_id in test.get("evidence_ids", []) if evidence_id in index["evidence"]]
            if _missing_refs(test, "evidence_ids", index["evidence"]):
                status = "blocked"
                reason = "test has missing linked evidence"
            elif not linked_evidence:
                status = "planned"
                reason = "test has no linked evidence"
            elif any(evidence.get("status") in {"failed", "stale"} for evidence in linked_evidence):
                status = "failing"
                reason = "test has failed or stale linked evidence"
            elif not all(evidence.get("status") == "passed" for evidence in linked_evidence):
                status = "planned"
                reason = "test linked evidence is not yet passed"

        change = _change("tests", test_id, "status", test.get("status"), status, reason)
        if change is not None:
            changes.append(change)
            _apply(test, "status", status)
    return changes


def _claim_support_status(
    registry: dict[str, Any],
    claim: dict[str, Any],
    index: dict[str, dict[str, dict[str, object]]],
    repo_root: Path,
) -> tuple[str, str, dict[str, Any] | None]:
    if claim.get("status") in CLAIM_TERMINAL_STATUSES:
        return str(claim["status"]), "terminal claim status is preserved", None
    if _missing_refs(claim, "feature_ids", index["features"]) or _missing_refs(claim, "test_ids", index["tests"]) or _missing_refs(claim, "evidence_ids", index["evidence"]):
        return "blocked", "claim has missing linked features, tests, or evidence", None
    linked_features = [index["features"][feature_id] for feature_id in claim.get("feature_ids", []) if feature_id in index["features"]]
    linked_tests = [index["tests"][test_id] for test_id in claim.get("test_ids", []) if test_id in index["tests"]]
    linked_evidence = [index["evidence"][evidence_id] for evidence_id in claim.get("evidence_ids", []) if evidence_id in index["evidence"]]
    if linked_evidence and any(evidence.get("status") in {"failed", "stale"} for evidence in linked_evidence):
        return "blocked", "claim has failed or stale linked evidence", None
    if (linked_tests or linked_evidence) and not any(test.get("status") != "planned" for test in linked_tests) and not any(
        evidence.get("status") != "planned" for evidence in linked_evidence
    ):
        return "proposed", "claim has only planned verification support", None
    tier_gate = evaluate_claim_tier_gate(
        registry,
        claim,
        index,
        str(claim.get("tier", "T0")),
        repo_root=repo_root,
        policy=registry.get("guard_policies", {}).get("claim_tier_gates", {}),
    )
    if linked_tests and all(test.get("status") == "passing" for test in linked_tests) and linked_evidence:
        tier_met = any(
            evidence.get("status") == "passed" and CLAIM_TIER_RANK[evidence["tier"]] >= CLAIM_TIER_RANK[claim["tier"]]
            for evidence in linked_evidence
        )
        if tier_met:
            if not tier_gate["passed"]:
                failures = "; ".join(tier_gate["failures"])
                return "asserted", f"claim closure support exists but tier gate failed: {failures}", tier_gate
            if linked_features and all(feature.get("implementation_status") == "implemented" for feature in linked_features):
                return "certified", "claim support passes closure guards and tier gate passes", tier_gate
            return "evidenced", "claim has passing tests, sufficient evidence, and tier gate passes", tier_gate
    if linked_tests or linked_evidence:
        return "asserted", "claim has linked verification support that is not yet passing", tier_gate
    if linked_features:
        return "declared", "claim is linked to features but has no verification support", tier_gate
    return "proposed", "claim has no linked support", tier_gate


def _sync_claims(registry: dict[str, Any], repo_root: Path) -> list[dict[str, object]]:
    index = _build_current_index(registry)
    changes: list[dict[str, object]] = []
    for claim in registry.get("claims", []):
        status, reason, tier_gate = _claim_support_status(registry, claim, index, repo_root)
        guard = evaluate_claim_guard(claim, index, registry.get("guard_policies", {}))
        if guard["passed"] and (tier_gate is None or tier_gate["passed"]):
            current = str(claim.get("status"))
            status = current if current in CLAIM_RELEASE_STATUSES else "certified"
            reason = "claim support passes closure guards and tier gate passes"
        elif guard["passed"] and tier_gate is not None and not tier_gate["passed"]:
            status = "asserted"
            reason = f"claim closure passes but tier gate failed: {'; '.join(tier_gate['failures'])}"
        change = _change("claims", claim["id"], "status", claim.get("status"), status, reason)
        if change is not None:
            if tier_gate is not None and not tier_gate["passed"]:
                change["gate_failures"] = tier_gate["failures"]
                change["requested_tier"] = tier_gate["requested_tier"]
                change["approved_tier"] = tier_gate["approved_tier"]
            changes.append(change)
            _apply(claim, "status", status)
    return changes


def _claim_satisfies_feature(claim: dict[str, Any], required_tier: str | None) -> bool:
    return claim_satisfies_feature_implementation(claim, required_tier)


def _sync_features_once(registry: dict[str, Any]) -> list[dict[str, object]]:
    index = _build_current_index(registry)
    changes: list[dict[str, object]] = []
    for feature in registry.get("features", []):
        feature_id = feature["id"]
        if feature.get("lifecycle", {}).get("stage") == "removed":
            status = "absent"
            reason = "removed features must have absent implementation status"
        elif _missing_refs(feature, "claim_ids", index["claims"]) or _missing_refs(feature, "test_ids", index["tests"]) or _missing_refs(feature, "requires", index["features"]):
            status = "partial"
            reason = "feature has missing linked claims, tests, or required features"
        else:
            linked_tests = [index["tests"][test_id] for test_id in feature.get("test_ids", []) if test_id in index["tests"]]
            linked_claims = [index["claims"][claim_id] for claim_id in feature.get("claim_ids", []) if claim_id in index["claims"]]
            active_claims = active_required_feature_claims(feature, index)
            required_features = [index["features"][required_id] for required_id in feature.get("requires", []) if required_id in index["features"]]
            required_tier = feature.get("plan", {}).get("target_claim_tier")
            tests_pass = bool(linked_tests) and all(test.get("status") == "passing" for test in linked_tests)
            claims_pass = bool(active_claims) and all(_claim_satisfies_feature(claim, required_tier) for claim in active_claims)
            requirements_pass = all(required.get("implementation_status") == "implemented" for required in required_features)
            only_planned_support = (
                bool(linked_tests or linked_claims)
                and all(test.get("status") == "planned" for test in linked_tests)
                and all(CLAIM_STATUS_RANK.get(claim.get("status"), -999) <= CLAIM_STATUS_RANK["proposed"] for claim in active_claims)
            )
            if tests_pass and claims_pass and requirements_pass:
                status = "implemented"
                reason = "feature has passing tests, all active required claims satisfy implementation, and implemented requirements"
            elif only_planned_support:
                status = "absent"
                reason = "feature has only planned verification support"
            elif linked_tests or linked_claims or required_features:
                status = "partial"
                ceiling_failures = feature_claim_ceiling_failures(feature, index)
                reason = "; ".join(ceiling_failures) if ceiling_failures else "feature has linked support but does not yet satisfy implementation criteria"
            else:
                status = "absent"
                reason = "feature has no linked implementation support"

        change = _change("features", feature_id, "implementation_status", feature.get("implementation_status"), status, reason)
        if change is not None:
            changes.append(change)
            _apply(feature, "implementation_status", status)
    return changes


def _sync_features(registry: dict[str, Any]) -> list[dict[str, object]]:
    changes: list[dict[str, object]] = []
    max_passes = max(1, len(registry.get("features", [])))
    for _ in range(max_passes):
        pass_changes = _sync_features_once(registry)
        if not pass_changes:
            break
        changes.extend(pass_changes)
    return changes


def _sync_profiles(registry: dict[str, Any]) -> list[dict[str, object]]:
    index = _build_current_index(registry)
    changes: list[dict[str, object]] = []
    for profile in registry.get("profiles", []):
        if profile.get("status") == "retired":
            continue
        result = evaluate_profile(profile, index, registry.get("guard_policies", {}))
        status = "active" if result["passed"] else "draft"
        reason = "profile evaluation passes" if result["passed"] else "profile evaluation does not pass"
        change = _change("profiles", profile["id"], "status", profile.get("status"), status, reason)
        if change is not None:
            changes.append(change)
            _apply(profile, "status", status)
    return changes


def sync_automated_statuses(path: str | Path, *, dry_run: bool = False) -> dict[str, object]:
    registry_path, repo_root, registry = load_registry(path)
    working = deepcopy(registry)
    changes: list[dict[str, object]] = []
    changes.extend(_sync_evidence(working, repo_root))
    changes.extend(_sync_tests(working, repo_root))
    changes.extend(_sync_claims(working, repo_root))
    changes.extend(_sync_features(working))
    changes.extend(_sync_claims(working, repo_root))
    changes.extend(_sync_profiles(working))
    changes = _collapse_changes(changes)
    report = validate_registry_document(working, registry_path, repo_root)
    if not dry_run and report["passed"]:
        save_registry(registry_path, working)
    return {
        "passed": bool(report["passed"]),
        "registry_path": registry_path.as_posix(),
        "dry_run": dry_run,
        "changed": len(changes),
        "changes": changes,
        "validation": report,
        "sections": list(AUTOMATED_SECTIONS),
    }
