from __future__ import annotations

CONFORMANCE_FAMILY = "spec-adr"


def test_spec_adr_contract(ssot_registry) -> None:
    adr_ids = {row["id"] for row in ssot_registry["adrs"]}
    for row in ssot_registry["specs"]:
        assert isinstance(row.get("adr_ids", []), list), row["id"]
        for adr_id in row.get("adr_ids", []):
            assert adr_id in adr_ids, (row["id"], adr_id)
