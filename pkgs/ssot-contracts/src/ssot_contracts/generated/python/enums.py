from __future__ import annotations

from ssot_contracts.contract_data import CONTRACT_DATA

SCHEMA_VERSION = CONTRACT_DATA["schema_version"]
ENTITY_PREFIXES = CONTRACT_DATA["entity_prefixes"]
GRAPH_NODE_KIND = CONTRACT_DATA["graph_node_kind"]

FEATURE_IMPLEMENTATION_STATUSES = set(CONTRACT_DATA["choice_sets"]["feature_implementation_statuses"])
FEATURE_LIFECYCLE_STAGES = set(CONTRACT_DATA["choice_sets"]["feature_lifecycle_stages"])
PLANNING_HORIZONS = set(CONTRACT_DATA["choice_sets"]["planning_horizons"])
TEST_STATUSES = set(CONTRACT_DATA["choice_sets"]["test_statuses"])
PROFILE_STATUSES = set(CONTRACT_DATA["choice_sets"]["profile_statuses"])
PROFILE_KINDS = set(CONTRACT_DATA["choice_sets"]["profile_kinds"])
CLAIM_TIERS = set(CONTRACT_DATA["choice_sets"]["claim_tiers"])
CLAIM_STATUSES = set(CONTRACT_DATA["choice_sets"]["claim_statuses"])
EVIDENCE_STATUSES = set(CONTRACT_DATA["choice_sets"]["evidence_statuses"])
ISSUE_STATUSES = set(CONTRACT_DATA["choice_sets"]["issue_statuses"])
RISK_STATUSES = set(CONTRACT_DATA["choice_sets"]["risk_statuses"])
BOUNDARY_STATUSES = set(CONTRACT_DATA["choice_sets"]["boundary_statuses"])
RELEASE_STATUSES = set(CONTRACT_DATA["choice_sets"]["release_statuses"])
SEVERITIES = set(CONTRACT_DATA["choice_sets"]["severities"])
DOCUMENT_STATUSES = tuple(CONTRACT_DATA["choice_sets"]["document_statuses"])
SPEC_KINDS = set(CONTRACT_DATA["choice_sets"]["spec_kinds"])
