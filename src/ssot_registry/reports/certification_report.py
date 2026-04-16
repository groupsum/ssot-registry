from __future__ import annotations

from ssot_registry.reports.summary import build_summary


def build_certification_report(
    registry: dict[str, object],
    registry_path: str,
    release_report: dict[str, object],
) -> dict[str, object]:
    boundary = release_report.get("boundary", {})
    return {
        "passed": bool(release_report.get("passed")),
        "registry_path": registry_path,
        "release": release_report,
        "boundary_scope": {
            "boundary_id": boundary.get("id"),
            "profile_ids": boundary.get("profile_ids", []),
            "feature_ids": boundary.get("feature_ids", []),
        },
        "summary": build_summary(registry),
    }
