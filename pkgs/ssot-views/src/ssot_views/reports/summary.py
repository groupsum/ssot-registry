from __future__ import annotations

def build_summary(registry: dict[str, object]) -> dict[str, object]:
    profile_status = {"passing": 0, "failing": 0, "draft": 0}
    profiles = registry.get("profiles", [])
    if not isinstance(profiles, list):
        profiles = []
    for profile in profiles:
        if not isinstance(profile, dict):
            continue
        if profile.get("status") == "draft":
            profile_status["draft"] += 1
        else:
            profile_status["passing"] += 1
    return {
        "counts": {
            "features": len(registry.get("features", [])),
            "profiles": len(registry.get("profiles", [])),
            "tests": len(registry.get("tests", [])),
            "claims": len(registry.get("claims", [])),
            "evidence": len(registry.get("evidence", [])),
            "issues": len(registry.get("issues", [])),
            "risks": len(registry.get("risks", [])),
            "boundaries": len(registry.get("boundaries", [])),
            "releases": len(registry.get("releases", [])),
            "adrs": len(registry.get("adrs", [])),
            "specs": len(registry.get("specs", [])),
        },
        "profile_status": profile_status,
    }
