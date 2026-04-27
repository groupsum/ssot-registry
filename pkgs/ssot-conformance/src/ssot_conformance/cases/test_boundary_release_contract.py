from __future__ import annotations

CONFORMANCE_FAMILY = "boundary-release"


def test_boundary_release_contract(ssot_registry) -> None:
    features = {row["id"] for row in ssot_registry["features"]}
    claims = {row["id"] for row in ssot_registry["claims"]}
    evidence = {row["id"] for row in ssot_registry["evidence"]}
    boundaries = {row["id"]: row for row in ssot_registry["boundaries"]}
    for boundary in boundaries.values():
        for feature_id in boundary.get("feature_ids", []):
            assert feature_id in features, (boundary["id"], feature_id)
    for release in ssot_registry["releases"]:
        assert release["boundary_id"] in boundaries, release["id"]
        for boundary_id in release.get("boundary_ids", [release["boundary_id"]]):
            assert boundary_id in boundaries, (release["id"], boundary_id)
        for claim_id in release.get("claim_ids", []):
            assert claim_id in claims, (release["id"], claim_id)
        for evidence_id in release.get("evidence_ids", []):
            assert evidence_id in evidence, (release["id"], evidence_id)
