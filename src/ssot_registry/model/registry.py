from __future__ import annotations

from copy import deepcopy
from typing import Any

from ssot_registry.model.document import default_document_id_reservations
from ssot_registry.version import __version__

from .enums import SCHEMA_VERSION


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


def build_minimal_registry(repo_id: str, repo_name: str, version: str) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "repo": {
            "id": repo_id,
            "name": repo_name,
            "version": version,
        },
        "tooling": {
            "ssot_registry_version": __version__,
            "initialized_with_version": __version__,
            "last_upgraded_from_version": __version__,
        },
        "paths": default_paths(),
        "program": {
            "active_boundary_id": "bnd:default",
            "active_release_id": f"rel:{version}",
        },
        "guard_policies": default_guard_policies(),
        "document_id_reservations": default_document_id_reservations(),
        "features": [],
        "tests": [],
        "claims": [],
        "evidence": [],
        "issues": [],
        "risks": [],
        "boundaries": [
            {
                "id": "bnd:default",
                "title": "Default boundary",
                "status": "draft",
                "frozen": False,
                "feature_ids": [],
            }
        ],
        "releases": [
            {
                "id": f"rel:{version}",
                "version": version,
                "status": "draft",
                "boundary_id": "bnd:default",
                "claim_ids": [],
                "evidence_ids": [],
            }
        ],
        "adrs": [],
        "specs": [],
    }


def count_entities(registry: dict[str, Any]) -> dict[str, int]:
    return {
        "features": len(registry.get("features", [])),
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
