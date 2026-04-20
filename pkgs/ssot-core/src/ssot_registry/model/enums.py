from __future__ import annotations

from ssot_contracts.generated.python.enums import (
    BOUNDARY_STATUSES,
    CLAIM_STATUSES,
    CLAIM_TIERS,
    DOCUMENT_STATUSES,
    ENTITY_PREFIXES,
    EVIDENCE_STATUSES,
    FEATURE_IMPLEMENTATION_STATUSES,
    FEATURE_LIFECYCLE_STAGES,
    GRAPH_NODE_KIND,
    ISSUE_STATUSES,
    PLANNING_HORIZONS,
    PROFILE_KINDS,
    PROFILE_STATUSES,
    RELEASE_STATUSES,
    RISK_STATUSES,
    SCHEMA_VERSION,
    SEVERITIES,
    SPEC_KINDS,
    TEST_STATUSES,
)

TOP_LEVEL_SECTIONS = (
    "schema_version",
    "repo",
    "tooling",
    "paths",
    "program",
    "guard_policies",
    "document_id_reservations",
    "features",
    "profiles",
    "tests",
    "claims",
    "evidence",
    "issues",
    "risks",
    "boundaries",
    "releases",
    "adrs",
    "specs",
)

CORE_ENTITY_SECTIONS = ("features", "profiles", "tests", "claims", "evidence", "issues", "risks", "boundaries", "releases")
DOCUMENT_ENTITY_SECTIONS = ("adrs", "specs")
ENTITY_SECTIONS = CORE_ENTITY_SECTIONS + DOCUMENT_ENTITY_SECTIONS

PROFILE_EVALUATION_MODES = {"all_features_must_pass"}
CLAIM_TIER_RANK = {"T0": 0, "T1": 1, "T2": 2, "T3": 3, "T4": 4}
CLAIM_STATUS_RANK = {
    "proposed": 0,
    "declared": 1,
    "implemented": 2,
    "asserted": 3,
    "evidenced": 4,
    "certified": 5,
    "promoted": 6,
    "published": 7,
    "blocked": -1,
    "retired": -2,
}

REQUIRED_TOP_LEVEL_KEYS = set(TOP_LEVEL_SECTIONS)

REQUIRED_ENTITY_FIELDS = {
    "features": {"id", "title", "description", "implementation_status", "lifecycle", "plan", "spec_ids", "claim_ids", "test_ids"},
    "profiles": {"id", "title", "description", "status", "kind", "feature_ids", "profile_ids", "claim_tier", "evaluation"},
    "tests": {"id", "title", "status", "kind", "path", "feature_ids", "claim_ids", "evidence_ids"},
    "claims": {"id", "title", "status", "tier", "kind", "description", "feature_ids", "test_ids", "evidence_ids"},
    "evidence": {"id", "title", "status", "kind", "tier", "path", "claim_ids", "test_ids"},
    "issues": {"id", "title", "status", "severity", "description", "plan", "feature_ids", "claim_ids", "test_ids", "evidence_ids", "risk_ids", "release_blocking"},
    "risks": {"id", "title", "status", "severity", "description", "feature_ids", "claim_ids", "test_ids", "evidence_ids", "issue_ids", "release_blocking"},
    "boundaries": {"id", "title", "status", "frozen", "feature_ids", "profile_ids"},
    "releases": {"id", "version", "status", "boundary_id", "claim_ids", "evidence_ids"},
}

REF_FIELD_TARGETS = {
    ("tests", "feature_ids"): "features",
    ("tests", "claim_ids"): "claims",
    ("tests", "evidence_ids"): "evidence",
    ("features", "spec_ids"): "specs",
    ("features", "claim_ids"): "claims",
    ("features", "test_ids"): "tests",
    ("features", "requires"): "features",
    ("profiles", "feature_ids"): "features",
    ("profiles", "profile_ids"): "profiles",
    ("claims", "feature_ids"): "features",
    ("claims", "test_ids"): "tests",
    ("claims", "evidence_ids"): "evidence",
    ("evidence", "claim_ids"): "claims",
    ("evidence", "test_ids"): "tests",
    ("issues", "feature_ids"): "features",
    ("issues", "claim_ids"): "claims",
    ("issues", "test_ids"): "tests",
    ("issues", "evidence_ids"): "evidence",
    ("issues", "risk_ids"): "risks",
    ("risks", "feature_ids"): "features",
    ("risks", "claim_ids"): "claims",
    ("risks", "test_ids"): "tests",
    ("risks", "evidence_ids"): "evidence",
    ("risks", "issue_ids"): "issues",
    ("boundaries", "feature_ids"): "features",
    ("boundaries", "profile_ids"): "profiles",
    ("releases", "boundary_id"): "boundaries",
    ("releases", "claim_ids"): "claims",
    ("releases", "evidence_ids"): "evidence",
}

BIDIRECTIONAL_LINKS = (
    ("features", "claim_ids", "claims", "feature_ids"),
    ("features", "test_ids", "tests", "feature_ids"),
    ("claims", "test_ids", "tests", "claim_ids"),
    ("claims", "evidence_ids", "evidence", "claim_ids"),
    ("tests", "evidence_ids", "evidence", "test_ids"),
    ("issues", "risk_ids", "risks", "issue_ids"),
)
