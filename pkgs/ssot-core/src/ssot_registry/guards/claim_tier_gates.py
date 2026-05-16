from __future__ import annotations

from pathlib import Path
from typing import Any

from ssot_registry.model.enums import CLAIM_TIER_RANK


ROBUSTNESS_DIMENSIONS = {
    "negative_cases",
    "edge_cases",
    "property_based",
    "fuzz",
    "mutation",
    "concurrency",
    "state_transitions",
    "compatibility_matrix",
    "cross_surface",
    "regression_corpus",
    "security_abuse_cases",
    "performance_envelope",
    "failure_recovery",
    "idempotency",
}

EXTERNAL_VALIDATION_MODES = {
    "external-authored-internal-run",
    "external-run",
    "independent-review",
    "third-party-certification",
    "external-attestation",
}

INTERNAL_AUTHORSHIP_CLASSIFICATIONS = {
    "internal",
    "self",
    "self-authored",
    "project-controlled",
    "project_owned",
}


def _as_string_list(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str) and item.strip()]


def _passed_evidence(
    claim: dict[str, Any],
    index: dict[str, dict[str, dict[str, Any]]],
    *,
    minimum_tier: str,
) -> list[dict[str, Any]]:
    return [
        evidence
        for evidence_id in claim.get("evidence_ids", [])
        if (evidence := index["evidence"].get(evidence_id)) is not None
        and evidence.get("status") == "passed"
        and CLAIM_TIER_RANK.get(str(evidence.get("tier")), -1) >= CLAIM_TIER_RANK[minimum_tier]
    ]


def _linked_tests_passing(claim: dict[str, Any], index: dict[str, dict[str, dict[str, Any]]]) -> bool:
    linked_tests = [index["tests"].get(test_id) for test_id in claim.get("test_ids", [])]
    return bool(linked_tests) and all(test is not None and test.get("status") == "passing" for test in linked_tests)


def _evidence_paths_exist(evidence_rows: list[dict[str, Any]], repo_root: Path | None) -> bool:
    if repo_root is None:
        return True
    return bool(evidence_rows) and all((repo_root / str(evidence["path"])).exists() for evidence in evidence_rows)


def _highest_valid_tier(checks: dict[str, bool]) -> str:
    approved = "T0"
    for tier in ("T1", "T2", "T3", "T4"):
        if checks.get(f"{tier.lower()}_gate", False):
            approved = tier
        else:
            break
    return approved


def _t1_checks(
    claim: dict[str, Any],
    index: dict[str, dict[str, dict[str, Any]]],
    repo_root: Path | None,
) -> tuple[dict[str, bool], list[str], list[dict[str, Any]]]:
    evidence_rows = _passed_evidence(claim, index, minimum_tier="T1")
    checks = {
        "t1_linked_tests_passing": _linked_tests_passing(claim, index),
        "t1_passed_project_evidence": bool(evidence_rows),
        "t1_evidence_artifacts_exist": _evidence_paths_exist(evidence_rows, repo_root),
    }
    failures = [
        message
        for key, message in (
            ("t1_linked_tests_passing", f"Claim {claim['id']} T1 gate requires linked tests to be passing"),
            ("t1_passed_project_evidence", f"Claim {claim['id']} T1 gate requires passed linked evidence at or above T1"),
            ("t1_evidence_artifacts_exist", f"Claim {claim['id']} T1 gate requires evidence artifact paths to exist"),
        )
        if not checks[key]
    ]
    return checks, failures, evidence_rows


def _t2_checks(claim: dict[str, Any], index: dict[str, dict[str, dict[str, Any]]]) -> tuple[dict[str, bool], list[str]]:
    evidence_rows = _passed_evidence(claim, index, minimum_tier="T2")
    robustness_evidence = [
        evidence
        for evidence in evidence_rows
        if set(_as_string_list(evidence.get("robustness_dimensions"))) & ROBUSTNESS_DIMENSIONS
    ]
    source_linked = [
        evidence
        for evidence in robustness_evidence
        if _as_string_list(evidence.get("source_evidence_ids"))
    ]
    checks = {
        "t2_passed_robustness_evidence": bool(evidence_rows),
        "t2_declared_robustness_dimensions": bool(robustness_evidence),
        "t2_distinct_from_t1_evidence": bool(source_linked),
    }
    failures = [
        message
        for key, message in (
            ("t2_passed_robustness_evidence", f"Claim {claim['id']} T2 gate requires passed linked evidence at or above T2"),
            ("t2_declared_robustness_dimensions", f"Claim {claim['id']} T2 gate requires declared robustness dimensions"),
            ("t2_distinct_from_t1_evidence", f"Claim {claim['id']} T2 gate requires source T1 evidence links"),
        )
        if not checks[key]
    ]
    return checks, failures


def _release_context(evidence: dict[str, Any]) -> dict[str, Any]:
    value = evidence.get("release_context")
    return value if isinstance(value, dict) else {}


def _t3_checks(
    registry: dict[str, Any],
    claim: dict[str, Any],
    index: dict[str, dict[str, dict[str, Any]]],
) -> tuple[dict[str, bool], list[str]]:
    from ssot_registry.guards.certification import evaluate_release_certification_guard

    evidence_rows = _passed_evidence(claim, index, minimum_tier="T3")
    contexts = [_release_context(evidence) for evidence in evidence_rows]
    release_ids = [context.get("release_id") for context in contexts if isinstance(context.get("release_id"), str)]
    boundary_context = [
        context
        for context in contexts
        if _as_string_list(context.get("boundary_ids")) or isinstance(context.get("boundary_id"), str)
    ]
    report_context_passes = any(
        context.get("verification_report_result") in {"passed", "accepted", "certified"}
        and context.get("blocking_issue_result") in {None, "none", "passed", "clear"}
        and context.get("blocking_risk_result") in {None, "none", "passed", "clear"}
        for context in contexts
    )
    certification_reports = [
        evaluate_release_certification_guard(registry, index, release_id)
        for release_id in release_ids
        if release_id in index["releases"]
    ]
    checks = {
        "t3_passed_release_evidence": bool(evidence_rows),
        "t3_release_context": bool(release_ids),
        "t3_boundary_context": bool(boundary_context),
        "t3_release_certification_guard": report_context_passes or (bool(certification_reports) and any(report["passed"] for report in certification_reports)),
    }
    failures = [
        message
        for key, message in (
            ("t3_passed_release_evidence", f"Claim {claim['id']} T3 gate requires passed linked evidence at or above T3"),
            ("t3_release_context", f"Claim {claim['id']} T3 gate requires release context"),
            ("t3_boundary_context", f"Claim {claim['id']} T3 gate requires boundary context"),
            ("t3_release_certification_guard", f"Claim {claim['id']} T3 gate requires a passing release certification guard"),
        )
        if not checks[key]
    ]
    return checks, failures


def _external_source(value: object) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _has_external_source_identity(source: dict[str, Any]) -> bool:
    return bool(source.get("name")) and bool(source.get("version") or source.get("artifact_id") or source.get("report_id") or source.get("commit"))


def _has_external_authority(source: dict[str, Any]) -> bool:
    classification = str(source.get("authorship_control", "")).strip().lower()
    return bool(classification) and classification not in INTERNAL_AUTHORSHIP_CLASSIFICATIONS


def _t4_checks(claim: dict[str, Any], index: dict[str, dict[str, dict[str, Any]]]) -> tuple[dict[str, bool], list[str]]:
    evidence_rows = _passed_evidence(claim, index, minimum_tier="T4")
    externally_validated = []
    for evidence in evidence_rows:
        source = _external_source(evidence.get("external_source"))
        if (
            _has_external_source_identity(source)
            and _has_external_authority(source)
            and evidence.get("validation_mode") in EXTERNAL_VALIDATION_MODES
            and bool(evidence.get("validation_scope"))
            and evidence.get("result") in {"passed", "accepted", "attested", "certified"}
        ):
            externally_validated.append(evidence)
    checks = {
        "t4_passed_external_evidence": bool(evidence_rows),
        "t4_external_source_identity": any(_has_external_source_identity(_external_source(evidence.get("external_source"))) for evidence in evidence_rows),
        "t4_external_validation_authority": any(_has_external_authority(_external_source(evidence.get("external_source"))) for evidence in evidence_rows),
        "t4_validation_mode": any(evidence.get("validation_mode") in EXTERNAL_VALIDATION_MODES for evidence in evidence_rows),
        "t4_validation_scope": any(bool(evidence.get("validation_scope")) for evidence in evidence_rows),
        "t4_validation_result": bool(externally_validated),
    }
    failures = [
        message
        for key, message in (
            ("t4_passed_external_evidence", f"Claim {claim['id']} T4 gate requires passed linked evidence at or above T4"),
            ("t4_external_source_identity", f"Claim {claim['id']} T4 gate requires external source identity and version/artifact/report"),
            ("t4_external_validation_authority", f"Claim {claim['id']} T4 gate requires external validation authority"),
            ("t4_validation_mode", f"Claim {claim['id']} T4 gate requires an accepted external validation mode"),
            ("t4_validation_scope", f"Claim {claim['id']} T4 gate requires validation scope"),
            ("t4_validation_result", f"Claim {claim['id']} T4 gate requires an accepted external validation result"),
        )
        if not checks[key]
    ]
    return checks, failures


def evaluate_claim_tier_gate(
    registry: dict[str, Any],
    claim: dict[str, Any],
    index: dict[str, dict[str, dict[str, Any]]],
    requested_tier: str | None = None,
    *,
    repo_root: str | Path | None = None,
    policy: dict[str, Any] | None = None,
) -> dict[str, Any]:
    requested = requested_tier or str(claim.get("tier", "T0"))
    root = Path(repo_root) if repo_root is not None else None
    checks: dict[str, bool] = {}
    failures: list[str] = []
    warnings: list[str] = []

    if requested not in CLAIM_TIER_RANK:
        return {
            "claim_id": claim.get("id"),
            "passed": False,
            "requested_tier": requested,
            "approved_tier": "T0",
            "failures": [f"Unknown requested claim tier {requested}"],
            "warnings": [],
            "checks": {},
        }

    checks["t0_gate"] = True
    if requested == "T0":
        return {
            "claim_id": claim["id"],
            "passed": True,
            "requested_tier": requested,
            "approved_tier": "T0",
            "failures": [],
            "warnings": warnings,
            "checks": checks,
        }

    t1, t1_failures, _ = _t1_checks(claim, index, root)
    checks.update(t1)
    checks["t1_gate"] = all(t1.values())
    if CLAIM_TIER_RANK[requested] >= CLAIM_TIER_RANK["T1"] and not checks["t1_gate"]:
        failures.extend(t1_failures)

    if CLAIM_TIER_RANK[requested] >= CLAIM_TIER_RANK["T2"]:
        t2, t2_failures = _t2_checks(claim, index)
        checks.update(t2)
        checks["t2_gate"] = checks["t1_gate"] and all(t2.values())
        if not checks["t2_gate"]:
            failures.extend(t2_failures)

    t4_policy = (policy or {}).get("t4", {}) if isinstance(policy, dict) else {}
    require_t3_for_t4 = bool(t4_policy.get("require_t3", True))
    should_evaluate_t3 = CLAIM_TIER_RANK[requested] >= CLAIM_TIER_RANK["T3"] and not (
        requested == "T4" and not require_t3_for_t4
    )
    if should_evaluate_t3:
        t3, t3_failures = _t3_checks(registry, claim, index)
        checks.update(t3)
        checks["t3_gate"] = checks.get("t2_gate", False) and all(t3.values())
        if not checks["t3_gate"]:
            failures.extend(t3_failures)
    elif requested == "T4" and not require_t3_for_t4:
        checks["t3_gate"] = True

    if CLAIM_TIER_RANK[requested] >= CLAIM_TIER_RANK["T4"]:
        t4, t4_failures = _t4_checks(claim, index)
        checks.update(t4)
        checks["t4_gate"] = checks.get("t3_gate", False) and all(t4.values())
        if not checks["t4_gate"]:
            failures.extend(t4_failures)

    approved_tier = _highest_valid_tier(checks)
    return {
        "claim_id": claim["id"],
        "passed": CLAIM_TIER_RANK[approved_tier] >= CLAIM_TIER_RANK[requested],
        "requested_tier": requested,
        "approved_tier": approved_tier,
        "failures": sorted(set(failures)),
        "warnings": warnings,
        "checks": checks,
    }
