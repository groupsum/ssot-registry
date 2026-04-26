from __future__ import annotations

from ssot_contracts.generated.python.enums import SCHEMA_VERSION
from ssot_registry.api import validate_registry

CONFORMANCE_FAMILY = "registry"


def test_registry_contract(ssot_repo_root, ssot_registry) -> None:
    report = validate_registry(ssot_repo_root)
    assert report["passed"], report
    assert ssot_registry["schema_version"] == SCHEMA_VERSION
    for section in ("repo", "paths", "guard_policies", "features", "tests", "claims", "evidence", "adrs", "specs"):
        assert section in ssot_registry
