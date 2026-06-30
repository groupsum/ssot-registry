from ssot_registry.api.graph import _lineage_payload


def test_lineage_payload_uses_current_viewer_schema() -> None:
    registry = {
        "repo": {
            "id": "repo:demo",
            "name": "Demo",
            "version": "1.2.3",
            "repository_url": "https://example.invalid/repo",
        },
        "schema_version": "1.0",
        "features": [
            {
                "id": "feat:demo",
                "title": "Demo feature",
                "description": "Feature description",
                "origin": "repo-local",
                "path": "src/demo.py",
                "tags": ["lineage"],
                "plan": {"target_claim_tier": "T2"},
                "spec_ids": ["spc:demo"],
            }
        ],
        "specs": [{"id": "spc:demo", "title": "Demo spec"}],
        "adrs": [],
        "tests": [],
        "claims": [],
        "evidence": [],
        "issues": [],
        "risks": [],
        "boundaries": [],
        "releases": [],
        "profiles": [],
    }

    payload = _lineage_payload(registry)
    feature = next(node for node in payload["nodes"] if node["id"] == "feat:demo")

    assert payload["schemaVersion"] == "2"
    assert payload["package"]["repositoryUrl"] == "https://example.invalid/repo"
    assert feature["title"] == "Demo feature"
    assert feature["source"]["path"] == "src/demo.py"
    assert feature["proof"]["claimTier"] == "T2"
    assert any(edge["from"] == "feat:demo" and edge["to"] == "spc:demo" for edge in payload["edges"])
