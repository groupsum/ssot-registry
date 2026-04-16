from __future__ import annotations

from ssot_contracts.generated.python.enums import GRAPH_NODE_KIND


def build_graph_json(registry: dict[str, object]) -> dict[str, object]:
    nodes: list[dict[str, str]] = []
    edges: list[dict[str, str]] = []

    for section, kind in GRAPH_NODE_KIND.items():
        for row in registry.get(section, []):
            nodes.append({"id": row["id"], "kind": kind})

    for boundary in registry.get("boundaries", []):
        for feature_id in boundary.get("feature_ids", []):
            edges.append({"type": "SCOPES", "from": boundary["id"], "to": feature_id})
        for profile_id in boundary.get("profile_ids", []):
            edges.append({"type": "SCOPES_PROFILE", "from": boundary["id"], "to": profile_id})

    for profile in registry.get("profiles", []):
        for feature_id in profile.get("feature_ids", []):
            edges.append({"type": "BUNDLES", "from": profile["id"], "to": feature_id})
        for nested_profile_id in profile.get("profile_ids", []):
            edges.append({"type": "COMPOSES", "from": profile["id"], "to": nested_profile_id})

    for release in registry.get("releases", []):
        edges.append({"type": "USES_BOUNDARY", "from": release["id"], "to": release["boundary_id"]})
        for claim_id in release.get("claim_ids", []):
            edges.append({"type": "PUBLISHES", "from": release["id"], "to": claim_id})
        for evidence_id in release.get("evidence_ids", []):
            edges.append({"type": "INCLUDES", "from": release["id"], "to": evidence_id})

    for feature in registry.get("features", []):
        for required_feature_id in feature.get("requires", []):
            edges.append({"type": "REQUIRES", "from": feature["id"], "to": required_feature_id})
        for test_id in feature.get("test_ids", []):
            edges.append({"type": "COVERED_BY", "from": feature["id"], "to": test_id})

    for claim in registry.get("claims", []):
        for feature_id in claim.get("feature_ids", []):
            edges.append({"type": "ASSERTS", "from": claim["id"], "to": feature_id})
        for test_id in claim.get("test_ids", []):
            edges.append({"type": "VERIFIES", "from": test_id, "to": claim["id"]})
        for evidence_id in claim.get("evidence_ids", []):
            edges.append({"type": "SUPPORTS", "from": evidence_id, "to": claim["id"]})

    for test in registry.get("tests", []):
        for evidence_id in test.get("evidence_ids", []):
            edges.append({"type": "DERIVES_FROM", "from": evidence_id, "to": test["id"]})

    for issue in registry.get("issues", []):
        for section_key in ("feature_ids", "claim_ids", "test_ids", "evidence_ids", "risk_ids"):
            for target_id in issue.get(section_key, []):
                edges.append({"type": "AFFECTS", "from": issue["id"], "to": target_id})

    for risk in registry.get("risks", []):
        for section_key in ("feature_ids", "claim_ids", "test_ids", "evidence_ids", "issue_ids"):
            for target_id in risk.get(section_key, []):
                edges.append({"type": "AFFECTS", "from": risk["id"], "to": target_id})

    return {
        "nodes": nodes,
        "edges": edges,
    }
