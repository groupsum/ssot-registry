from __future__ import annotations

from ssot_registry.guards.claim_closure import evaluate_claim_guard
from ssot_registry.model.enums import CLAIM_TIER_RANK


def evaluate_release_certification_guard(
    registry: dict[str, object],
    index: dict[str, dict[str, dict[str, object]]],
    release_id: str,
) -> dict[str, object]:
    failures: list[str] = []
    warnings: list[str] = []

    release = index["releases"].get(release_id)
    if release is None:
        return {
            "release_id": release_id,
            "passed": False,
            "failures": [f"Missing release {release_id}"],
            "warnings": [],
            "claims": [],
            "evidence": [],
        }

    boundary = index["boundaries"].get(release["boundary_id"])
    if boundary is None:
        failures.append(f"Release {release_id} references missing boundary {release['boundary_id']}")
        return {
            "release_id": release_id,
            "passed": False,
            "failures": failures,
            "warnings": warnings,
            "claims": [],
            "evidence": [],
        }

    certification_policy = registry.get("guard_policies", {}).get("certification", {})
    require_frozen_boundary = bool(certification_policy.get("require_frozen_boundary", True))
    if require_frozen_boundary and not boundary.get("frozen", False):
        failures.append(f"Boundary {boundary['id']} is not frozen")

    boundary_feature_ids = boundary.get("feature_ids", [])
    if certification_policy.get("require_boundary_features_current_or_explicit", True):
        for feature_id in boundary_feature_ids:
            feature = index["features"].get(feature_id)
            if feature is None:
                continue
            if feature.get("plan", {}).get("horizon") not in {"current", "explicit"}:
                failures.append(
                    f"Boundary {boundary['id']} contains feature {feature_id} that is not current or explicit"
                )

    release_claims = [index["claims"][claim_id] for claim_id in release.get("claim_ids", []) if claim_id in index["claims"]]
    claim_reports = [evaluate_claim_guard(claim, index, registry.get("guard_policies", {})) for claim in release_claims]
    for report in claim_reports:
        failures.extend(report["failures"])

    if certification_policy.get("require_release_claim_coverage_for_boundary_features", True):
        for feature_id in boundary_feature_ids:
            covering_claims = [claim for claim in release_claims if feature_id in claim.get("feature_ids", [])]
            if not covering_claims:
                failures.append(f"Release {release_id} has no claim coverage for boundary feature {feature_id}")

    if certification_policy.get("require_feature_target_tiers_met", True):
        for feature_id in boundary_feature_ids:
            feature = index["features"].get(feature_id)
            if feature is None:
                continue
            target_tier = feature.get("plan", {}).get("target_claim_tier")
            if target_tier is None:
                continue
            covering_claims = [claim for claim in release_claims if feature_id in claim.get("feature_ids", [])]
            if not covering_claims:
                continue
            if not any(CLAIM_TIER_RANK[claim["tier"]] >= CLAIM_TIER_RANK[target_tier] for claim in covering_claims):
                failures.append(
                    f"Feature {feature_id} targets {target_tier}, but release {release_id} has no covering claim at or above that tier"
                )

    evidence_reports: list[dict[str, object]] = []
    seen_evidence_ids: set[str] = set(release.get("evidence_ids", []))
    for claim in release_claims:
        seen_evidence_ids.update(claim.get("evidence_ids", []))
    for evidence_id in sorted(seen_evidence_ids):
        evidence = index["evidence"].get(evidence_id)
        if evidence is None:
            failures.append(f"Release {release_id} references missing evidence {evidence_id}")
            continue
        linked_tests = [index["tests"][test_id] for test_id in evidence.get("test_ids", []) if test_id in index["tests"]]
        evidence_failures: list[str] = []
        if evidence.get("status") != "passed":
            evidence_failures.append(f"Evidence {evidence_id} status is {evidence.get('status')}, expected passed")
        if not all(test.get("status") == "passing" for test in linked_tests):
            evidence_failures.append(f"Evidence {evidence_id} has non-passing linked tests")
        evidence_reports.append(
            {
                "evidence_id": evidence_id,
                "passed": not evidence_failures,
                "failures": evidence_failures,
            }
        )
        failures.extend(evidence_failures)

    if certification_policy.get("forbid_open_release_blocking_issues", True):
        for issue in index["issues"].values():
            if not issue.get("release_blocking"):
                continue
            if issue.get("status") in {"open", "in_progress", "blocked"} and (
                set(issue.get("feature_ids", [])) & set(boundary_feature_ids)
            ):
                failures.append(f"Release-blocking issue remains open for boundary scope: {issue['id']}")

    if certification_policy.get("forbid_active_release_blocking_risks", True):
        for risk in index["risks"].values():
            if not risk.get("release_blocking"):
                continue
            if risk.get("status") == "active" and (set(risk.get("feature_ids", [])) & set(boundary_feature_ids)):
                failures.append(f"Release-blocking risk remains active for boundary scope: {risk['id']}")

    return {
        "release_id": release_id,
        "passed": not failures,
        "failures": sorted(set(failures)),
        "warnings": warnings,
        "claims": claim_reports,
        "evidence": evidence_reports,
        "summary": {
            "boundary_id": boundary["id"],
            "boundary_feature_count": len(boundary_feature_ids),
            "release_claim_count": len(release_claims),
            "release_evidence_count": len(evidence_reports),
        },
    }
