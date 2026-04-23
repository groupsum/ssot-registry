from __future__ import annotations

from typing import Any

from ssot_registry.model.enums import (
    BOUNDARY_STATUSES,
    CLAIM_STATUSES,
    CLAIM_TIERS,
    CORE_ENTITY_SECTIONS,
    EVIDENCE_STATUSES,
    FEATURE_IMPLEMENTATION_STATUSES,
    FEATURE_LIFECYCLE_STAGES,
    ISSUE_STATUSES,
    OUT_OF_BOUNDS_DISPOSITIONS,
    PLANNING_HORIZONS,
    PROFILE_EVALUATION_MODES,
    PROFILE_KINDS,
    PROFILE_STATUSES,
    RELEASE_STATUSES,
    REQUIRED_ENTITY_FIELDS,
    REQUIRED_TOP_LEVEL_KEYS,
    RISK_STATUSES,
    SCHEMA_VERSION,
    SEVERITIES,
    TEST_STATUSES,
)
from ssot_registry.model.registry import REPO_KINDS, REPO_KIND_ALIASES, legacy_repo_kinds_allowed


def _list_of_strings(value: Any) -> bool:
    return isinstance(value, list) and all(isinstance(item, str) for item in value)


def _validate_feature(feature: dict[str, Any], failures: list[str]) -> None:
    entity_id = feature.get("id", "<missing>")
    if feature.get("implementation_status") not in FEATURE_IMPLEMENTATION_STATUSES:
        failures.append(
            f"features.{entity_id}.implementation_status must be one of {sorted(FEATURE_IMPLEMENTATION_STATUSES)}"
        )

    lifecycle = feature.get("lifecycle")
    if not isinstance(lifecycle, dict):
        failures.append(f"features.{entity_id}.lifecycle must be an object")
    else:
        if lifecycle.get("stage") not in FEATURE_LIFECYCLE_STAGES:
            failures.append(f"features.{entity_id}.lifecycle.stage must be one of {sorted(FEATURE_LIFECYCLE_STAGES)}")
        replacement_ids = lifecycle.get("replacement_feature_ids", [])
        if not _list_of_strings(replacement_ids):
            failures.append(f"features.{entity_id}.lifecycle.replacement_feature_ids must be a list of strings")
        note = lifecycle.get("note")
        if note is not None and not isinstance(note, str):
            failures.append(f"features.{entity_id}.lifecycle.note must be a string or null")

    plan = feature.get("plan")
    if not isinstance(plan, dict):
        failures.append(f"features.{entity_id}.plan must be an object")
    else:
        horizon = plan.get("horizon")
        if horizon not in PLANNING_HORIZONS:
            failures.append(f"features.{entity_id}.plan.horizon must be one of {sorted(PLANNING_HORIZONS)}")
        slot = plan.get("slot")
        if horizon == "explicit" and (not isinstance(slot, str) or not slot.strip()):
            failures.append(f"features.{entity_id}.plan.slot must be a non-empty string when horizon is explicit")
        if slot is not None and not isinstance(slot, str):
            failures.append(f"features.{entity_id}.plan.slot must be a string or null")
        target_claim_tier = plan.get("target_claim_tier")
        if horizon in {"current", "next", "future", "explicit"} and target_claim_tier not in CLAIM_TIERS:
            failures.append(
                f"features.{entity_id}.plan.target_claim_tier must be one of {sorted(CLAIM_TIERS)} for a targeted feature"
            )
        if horizon in {"backlog", "out_of_bounds"} and target_claim_tier is not None and target_claim_tier not in CLAIM_TIERS:
            failures.append(f"features.{entity_id}.plan.target_claim_tier must be null or one of {sorted(CLAIM_TIERS)}")
        if plan.get("target_lifecycle_stage") not in FEATURE_LIFECYCLE_STAGES:
            failures.append(
                f"features.{entity_id}.plan.target_lifecycle_stage must be one of {sorted(FEATURE_LIFECYCLE_STAGES)}"
            )
        out_of_bounds_disposition = plan.get("out_of_bounds_disposition")
        if out_of_bounds_disposition is not None and out_of_bounds_disposition not in OUT_OF_BOUNDS_DISPOSITIONS:
            failures.append(
                f"features.{entity_id}.plan.out_of_bounds_disposition must be null or one of {sorted(OUT_OF_BOUNDS_DISPOSITIONS)}"
            )
        if horizon != "out_of_bounds" and out_of_bounds_disposition is not None:
            failures.append(
                f"features.{entity_id}.plan.out_of_bounds_disposition may only be set when plan.horizon is out_of_bounds"
            )

    if not _list_of_strings(feature.get("spec_ids")):
        failures.append(f"features.{entity_id}.spec_ids must be a list of strings")
    if not _list_of_strings(feature.get("claim_ids")):
        failures.append(f"features.{entity_id}.claim_ids must be a list of strings")
    if not _list_of_strings(feature.get("test_ids")):
        failures.append(f"features.{entity_id}.test_ids must be a list of strings")
    requires = feature.get("requires")
    if requires is not None and not _list_of_strings(requires):
        failures.append(f"features.{entity_id}.requires must be a list of strings when present")


def _validate_test(test: dict[str, Any], failures: list[str]) -> None:
    entity_id = test.get("id", "<missing>")
    if test.get("status") not in TEST_STATUSES:
        failures.append(f"tests.{entity_id}.status must be one of {sorted(TEST_STATUSES)}")
    if not isinstance(test.get("kind"), str) or not test["kind"].strip():
        failures.append(f"tests.{entity_id}.kind must be a non-empty string")
    if not isinstance(test.get("path"), str) or not test["path"].strip():
        failures.append(f"tests.{entity_id}.path must be a non-empty string")
    for field_name in ("feature_ids", "claim_ids", "evidence_ids"):
        if not _list_of_strings(test.get(field_name)):
            failures.append(f"tests.{entity_id}.{field_name} must be a list of strings")


def _validate_profile(profile: dict[str, Any], failures: list[str]) -> None:
    entity_id = profile.get("id", "<missing>")
    if profile.get("status") not in PROFILE_STATUSES:
        failures.append(f"profiles.{entity_id}.status must be one of {sorted(PROFILE_STATUSES)}")
    if profile.get("kind") not in PROFILE_KINDS:
        failures.append(f"profiles.{entity_id}.kind must be one of {sorted(PROFILE_KINDS)}")
    if not isinstance(profile.get("description"), str):
        failures.append(f"profiles.{entity_id}.description must be a string")
    if not _list_of_strings(profile.get("feature_ids")):
        failures.append(f"profiles.{entity_id}.feature_ids must be a list of strings")
    if not _list_of_strings(profile.get("profile_ids")):
        failures.append(f"profiles.{entity_id}.profile_ids must be a list of strings")
    claim_tier = profile.get("claim_tier")
    if claim_tier is not None and claim_tier not in CLAIM_TIERS:
        failures.append(f"profiles.{entity_id}.claim_tier must be null or one of {sorted(CLAIM_TIERS)}")
    evaluation = profile.get("evaluation")
    if not isinstance(evaluation, dict):
        failures.append(f"profiles.{entity_id}.evaluation must be an object")
    else:
        if evaluation.get("mode") not in PROFILE_EVALUATION_MODES:
            failures.append(
                f"profiles.{entity_id}.evaluation.mode must be one of {sorted(PROFILE_EVALUATION_MODES)}"
            )
        if not isinstance(evaluation.get("allow_feature_override_tier"), bool):
            failures.append(
                f"profiles.{entity_id}.evaluation.allow_feature_override_tier must be a boolean"
            )


def _validate_claim(claim: dict[str, Any], failures: list[str]) -> None:
    entity_id = claim.get("id", "<missing>")
    if claim.get("status") not in CLAIM_STATUSES:
        failures.append(f"claims.{entity_id}.status must be one of {sorted(CLAIM_STATUSES)}")
    if claim.get("tier") not in CLAIM_TIERS:
        failures.append(f"claims.{entity_id}.tier must be one of {sorted(CLAIM_TIERS)}")
    if not isinstance(claim.get("kind"), str) or not claim["kind"].strip():
        failures.append(f"claims.{entity_id}.kind must be a non-empty string")
    if not isinstance(claim.get("description"), str):
        failures.append(f"claims.{entity_id}.description must be a string")
    for field_name in ("feature_ids", "test_ids", "evidence_ids"):
        if not _list_of_strings(claim.get(field_name)):
            failures.append(f"claims.{entity_id}.{field_name} must be a list of strings")


def _validate_evidence(evidence: dict[str, Any], failures: list[str]) -> None:
    entity_id = evidence.get("id", "<missing>")
    if evidence.get("status") not in EVIDENCE_STATUSES:
        failures.append(f"evidence.{entity_id}.status must be one of {sorted(EVIDENCE_STATUSES)}")
    if evidence.get("tier") not in CLAIM_TIERS:
        failures.append(f"evidence.{entity_id}.tier must be one of {sorted(CLAIM_TIERS)}")
    if not isinstance(evidence.get("kind"), str) or not evidence["kind"].strip():
        failures.append(f"evidence.{entity_id}.kind must be a non-empty string")
    if not isinstance(evidence.get("path"), str) or not evidence["path"].strip():
        failures.append(f"evidence.{entity_id}.path must be a non-empty string")
    for field_name in ("claim_ids", "test_ids"):
        if not _list_of_strings(evidence.get(field_name)):
            failures.append(f"evidence.{entity_id}.{field_name} must be a list of strings")


def _validate_issue(issue: dict[str, Any], failures: list[str]) -> None:
    entity_id = issue.get("id", "<missing>")
    if issue.get("status") not in ISSUE_STATUSES:
        failures.append(f"issues.{entity_id}.status must be one of {sorted(ISSUE_STATUSES)}")
    if issue.get("severity") not in SEVERITIES:
        failures.append(f"issues.{entity_id}.severity must be one of {sorted(SEVERITIES)}")
    if not isinstance(issue.get("description"), str):
        failures.append(f"issues.{entity_id}.description must be a string")
    if not isinstance(issue.get("release_blocking"), bool):
        failures.append(f"issues.{entity_id}.release_blocking must be a boolean")
    plan = issue.get("plan")
    if not isinstance(plan, dict):
        failures.append(f"issues.{entity_id}.plan must be an object")
    else:
        horizon = plan.get("horizon")
        if horizon not in PLANNING_HORIZONS:
            failures.append(f"issues.{entity_id}.plan.horizon must be one of {sorted(PLANNING_HORIZONS)}")
        slot = plan.get("slot")
        if horizon == "explicit" and (not isinstance(slot, str) or not slot.strip()):
            failures.append(f"issues.{entity_id}.plan.slot must be a non-empty string when horizon is explicit")
        if slot is not None and not isinstance(slot, str):
            failures.append(f"issues.{entity_id}.plan.slot must be a string or null")
    for field_name in ("feature_ids", "claim_ids", "test_ids", "evidence_ids", "risk_ids"):
        if not _list_of_strings(issue.get(field_name)):
            failures.append(f"issues.{entity_id}.{field_name} must be a list of strings")


def _validate_risk(risk: dict[str, Any], failures: list[str]) -> None:
    entity_id = risk.get("id", "<missing>")
    if risk.get("status") not in RISK_STATUSES:
        failures.append(f"risks.{entity_id}.status must be one of {sorted(RISK_STATUSES)}")
    if risk.get("severity") not in SEVERITIES:
        failures.append(f"risks.{entity_id}.severity must be one of {sorted(SEVERITIES)}")
    if not isinstance(risk.get("description"), str):
        failures.append(f"risks.{entity_id}.description must be a string")
    if not isinstance(risk.get("release_blocking"), bool):
        failures.append(f"risks.{entity_id}.release_blocking must be a boolean")
    for field_name in ("feature_ids", "claim_ids", "test_ids", "evidence_ids", "issue_ids"):
        if not _list_of_strings(risk.get(field_name)):
            failures.append(f"risks.{entity_id}.{field_name} must be a list of strings")


def _validate_boundary(boundary: dict[str, Any], failures: list[str]) -> None:
    entity_id = boundary.get("id", "<missing>")
    if boundary.get("status") not in BOUNDARY_STATUSES:
        failures.append(f"boundaries.{entity_id}.status must be one of {sorted(BOUNDARY_STATUSES)}")
    if not isinstance(boundary.get("frozen"), bool):
        failures.append(f"boundaries.{entity_id}.frozen must be a boolean")
    if not _list_of_strings(boundary.get("feature_ids")):
        failures.append(f"boundaries.{entity_id}.feature_ids must be a list of strings")
    if not _list_of_strings(boundary.get("profile_ids", [])):
        failures.append(f"boundaries.{entity_id}.profile_ids must be a list of strings")


def _validate_release(release: dict[str, Any], failures: list[str]) -> None:
    entity_id = release.get("id", "<missing>")
    if release.get("status") not in RELEASE_STATUSES:
        failures.append(f"releases.{entity_id}.status must be one of {sorted(RELEASE_STATUSES)}")
    if not isinstance(release.get("version"), str) or not release["version"].strip():
        failures.append(f"releases.{entity_id}.version must be a non-empty string")
    if not isinstance(release.get("boundary_id"), str) or not release["boundary_id"].strip():
        failures.append(f"releases.{entity_id}.boundary_id must be a non-empty string")
    for field_name in ("claim_ids", "evidence_ids"):
        if not _list_of_strings(release.get(field_name)):
            failures.append(f"releases.{entity_id}.{field_name} must be a list of strings")


def validate_structure(registry: dict[str, Any], index: dict[str, dict[str, dict[str, Any]]], failures: list[str]) -> None:
    for key in REQUIRED_TOP_LEVEL_KEYS:
        if key not in registry:
            failures.append(f"Missing top-level section: {key}")

    if registry.get("schema_version") != SCHEMA_VERSION:
        failures.append(f"schema_version must be {SCHEMA_VERSION}")

    repo = registry.get("repo")
    if not isinstance(repo, dict):
        failures.append("repo must be an object")
    else:
        for field_name in ("id", "name", "version", "kind"):
            if not isinstance(repo.get(field_name), str) or not repo[field_name].strip():
                failures.append(f"repo.{field_name} must be a non-empty string")
        allowed_repo_kinds = set(REPO_KINDS)
        if legacy_repo_kinds_allowed():
            allowed_repo_kinds |= set(REPO_KIND_ALIASES)
        if repo.get("kind") not in allowed_repo_kinds:
            failures.append(f"repo.kind must be one of {sorted(REPO_KINDS)}")

    tooling = registry.get("tooling")
    if not isinstance(tooling, dict):
        failures.append("tooling must be an object")
    else:
        for field_name in ("ssot_registry_version", "initialized_with_version", "last_upgraded_from_version"):
            if not isinstance(tooling.get(field_name), str) or not tooling[field_name].strip():
                failures.append(f"tooling.{field_name} must be a non-empty string")

    paths = registry.get("paths")
    if not isinstance(paths, dict):
        failures.append("paths must be an object")
    else:
        for field_name in (
            "ssot_root",
            "schema_root",
            "adr_root",
            "spec_root",
            "graph_root",
            "evidence_root",
            "release_root",
            "report_root",
            "cache_root",
        ):
            if not isinstance(paths.get(field_name), str) or not paths[field_name].strip():
                failures.append(f"paths.{field_name} must be a non-empty string")

    program = registry.get("program")
    if not isinstance(program, dict):
        failures.append("program must be an object")
    else:
        for field_name in ("active_boundary_id", "active_release_id"):
            if not isinstance(program.get(field_name), str) or not program[field_name].strip():
                failures.append(f"program.{field_name} must be a non-empty string")

    guard_policies = registry.get("guard_policies")
    if not isinstance(guard_policies, dict):
        failures.append("guard_policies must be an object")

    validators = {
        "features": _validate_feature,
        "profiles": _validate_profile,
        "tests": _validate_test,
        "claims": _validate_claim,
        "evidence": _validate_evidence,
        "issues": _validate_issue,
        "risks": _validate_risk,
        "boundaries": _validate_boundary,
        "releases": _validate_release,
    }

    for section in CORE_ENTITY_SECTIONS:
        rows = index.get(section, {})
        required_fields = REQUIRED_ENTITY_FIELDS[section]
        validator = validators[section]
        for entity_id, row in rows.items():
            missing = required_fields - set(row)
            if missing:
                failures.append(f"{section}.{entity_id} is missing required fields: {', '.join(sorted(missing))}")
            title = row.get("title")
            if section != "releases" and (not isinstance(title, str) or not title.strip()):
                failures.append(f"{section}.{entity_id}.title must be a non-empty string")
            validator(row, failures)
