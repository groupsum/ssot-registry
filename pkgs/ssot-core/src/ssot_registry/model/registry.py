from __future__ import annotations

import json
from copy import deepcopy
from typing import Any

from ssot_contracts import load_template_text
from ssot_registry.model.document import default_document_id_reservations
from ssot_registry.version import __version__

from .enums import SCHEMA_VERSION


REPO_KINDS = {"ssot-core", "ssot-origin", "repo-local"}
REPO_KIND_ALIASES = {
    "ssot-upstream": "ssot-core",
    "operator-repo": "repo-local",
}
LEGACY_REPO_KIND_CUTOFF = (0, 3, 0)


def _parse_version_triplet(version: str) -> tuple[int, int, int]:
    numbers: list[int] = []
    current = []
    for char in version:
        if char.isdigit():
            current.append(char)
            continue
        if current:
            numbers.append(int("".join(current)))
            current = []
        if len(numbers) >= 3:
            break
    if current and len(numbers) < 3:
        numbers.append(int("".join(current)))
    while len(numbers) < 3:
        numbers.append(0)
    return tuple(numbers[:3])


def legacy_repo_kinds_allowed(version: str | None = None) -> bool:
    current_version = version or __version__
    return _parse_version_triplet(current_version) < LEGACY_REPO_KIND_CUTOFF


def normalize_repo_kind(kind: str | None) -> str:
    if kind in REPO_KIND_ALIASES:
        return REPO_KIND_ALIASES[kind]
    if kind in REPO_KINDS:
        return kind
    return "repo-local"


def default_paths() -> dict[str, str]:
    return {
        "ssot_root": ".ssot",
        "schema_root": ".ssot/schemas",
        "adr_root": ".ssot/adr",
        "spec_root": ".ssot/specs",
        "graph_root": ".ssot/graphs",
        "evidence_root": ".ssot/evidence",
        "release_root": ".ssot/releases",
        "report_root": ".ssot/reports",
        "cache_root": ".ssot/cache",
    }


def default_guard_policies() -> dict[str, Any]:
    return {
        "claim_closure": {
            "require_implemented_features": True,
            "require_linked_tests_passing": True,
            "require_linked_evidence_passing": True,
            "require_claim_evidence_tier_alignment": True,
            "forbid_failed_or_stale_evidence": True,
        },
        "certification": {
            "require_release_status_draft_or_candidate": True,
            "require_frozen_boundary": True,
            "require_release_claim_coverage_for_boundary_features": True,
            "require_boundary_features_current_or_explicit": True,
            "require_feature_target_tiers_met": True,
            "forbid_open_release_blocking_issues": True,
            "forbid_active_release_blocking_risks": True,
        },
        "promotion": {
            "require_release_status_certified": True,
            "require_release_snapshot_hashes": True,
        },
        "publication": {
            "require_release_status_promoted": True,
        },
        "lifecycle": {
            "require_replacement_or_note_for_deprecation": True,
            "forbid_obsolete_or_removed_in_active_boundary": True,
            "require_feature_absent_for_removed": True,
        },
    }


def build_minimal_registry(
    repo_id: str,
    repo_name: str,
    version: str,
    *,
    repo_kind: str = "repo-local",
) -> dict[str, Any]:
    registry = json.loads(load_template_text("registry.minimal.json"))
    registry["schema_version"] = SCHEMA_VERSION
    registry["repo"] = {
        "id": repo_id,
        "name": repo_name,
        "version": version,
        "kind": repo_kind,
    }
    registry["tooling"] = {
        "ssot_registry_version": __version__,
        "initialized_with_version": __version__,
        "last_upgraded_from_version": __version__,
    }
    registry["paths"] = default_paths()
    registry["program"] = {
        "active_boundary_id": "bnd:default",
        "active_release_id": f"rel:{version}",
    }
    registry["guard_policies"] = default_guard_policies()
    registry["document_id_reservations"] = default_document_id_reservations()
    registry["boundaries"] = [
        {
            "id": "bnd:default",
            "title": "Default boundary",
            "status": "draft",
            "frozen": False,
            "feature_ids": [],
            "profile_ids": [],
        }
    ]
    registry["releases"] = [
        {
            "id": f"rel:{version}",
            "version": version,
            "status": "draft",
            "boundary_id": "bnd:default",
            "boundary_ids": ["bnd:default"],
            "claim_ids": [],
            "evidence_ids": [],
        }
    ]
    registry["adrs"] = []
    registry["specs"] = []
    registry.setdefault("profiles", [])
    return registry


def count_entities(registry: dict[str, Any]) -> dict[str, int]:
    return {
        "features": len(registry.get("features", [])),
        "profiles": len(registry.get("profiles", [])),
        "tests": len(registry.get("tests", [])),
        "claims": len(registry.get("claims", [])),
        "evidence": len(registry.get("evidence", [])),
        "issues": len(registry.get("issues", [])),
        "risks": len(registry.get("risks", [])),
        "boundaries": len(registry.get("boundaries", [])),
        "releases": len(registry.get("releases", [])),
        "adrs": len(registry.get("adrs", [])),
        "specs": len(registry.get("specs", [])),
    }


def deep_copy_registry(registry: dict[str, Any]) -> dict[str, Any]:
    return deepcopy(registry)
