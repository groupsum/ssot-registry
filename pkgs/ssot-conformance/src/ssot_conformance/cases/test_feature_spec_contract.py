from __future__ import annotations

CONFORMANCE_FAMILY = "feature-spec"


def test_feature_spec_contract(ssot_registry) -> None:
    spec_ids = {row["id"] for row in ssot_registry["specs"]}
    for feature in ssot_registry["features"]:
        assert isinstance(feature.get("spec_ids", []), list), feature["id"]
        for spec_id in feature.get("spec_ids", []):
            assert spec_id in spec_ids, (feature["id"], spec_id)
    for spec in ssot_registry["specs"]:
        assert "feature_ids" not in spec, spec["id"]
