from ssot_cli.adr_cmd import register_adr
from ssot_cli.boundary_cmd import register_boundary
from ssot_cli.claim_cmd import register_claim
from ssot_cli.evidence_cmd import register_evidence
from ssot_cli.feature_cmd import register_feature
from ssot_cli.graph_cmd import register_graph
from ssot_cli.init_cmd import register_init
from ssot_cli.issue_cmd import register_issue
from ssot_cli.main import build_parser, main
from ssot_cli.profile_cmd import register_profile
from ssot_cli.registry_cmd import register_registry
from ssot_cli.release_cmd import register_release
from ssot_cli.risk_cmd import register_risk
from ssot_cli.spec_cmd import register_spec
from ssot_cli.test_cmd import register_test
from ssot_cli.upgrade_cmd import register_upgrade
from ssot_cli.validate_cmd import register_validate

__all__ = [
    "build_parser",
    "main",
    "register_adr",
    "register_boundary",
    "register_claim",
    "register_evidence",
    "register_feature",
    "register_graph",
    "register_init",
    "register_issue",
    "register_profile",
    "register_registry",
    "register_release",
    "register_risk",
    "register_spec",
    "register_test",
    "register_upgrade",
    "register_validate",
]
