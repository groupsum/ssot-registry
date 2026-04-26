from __future__ import annotations

CONFORMANCE_FAMILY = "proof-chain"


def test_proof_chain_contract(ssot_registry) -> None:
    claims = {row["id"]: row for row in ssot_registry["claims"]}
    tests = {row["id"]: row for row in ssot_registry["tests"]}
    evidence = {row["id"]: row for row in ssot_registry["evidence"]}
    for feature in ssot_registry["features"]:
        if feature.get("implementation_status") != "implemented":
            continue
        assert feature["claim_ids"], feature["id"]
        assert feature["test_ids"], feature["id"]
        for claim_id in feature["claim_ids"]:
            assert claim_id in claims, (feature["id"], claim_id)
        for test_id in feature["test_ids"]:
            assert test_id in tests, (feature["id"], test_id)
    for claim in ssot_registry["claims"]:
        for test_id in claim.get("test_ids", []):
            assert test_id in tests, (claim["id"], test_id)
        for evidence_id in claim.get("evidence_ids", []):
            assert evidence_id in evidence, (claim["id"], evidence_id)
