from __future__ import annotations

from ssot_registry.model.ids import is_normalized_id

CONFORMANCE_FAMILY = "id"


def test_id_contract(ssot_registry) -> None:
    for section in ("features", "tests", "claims", "evidence", "issues", "risks", "boundaries", "releases", "adrs", "specs"):
        for row in ssot_registry.get(section, []):
            assert is_normalized_id(row["id"]), f"{section}.{row['id']}"
