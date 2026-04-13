from __future__ import annotations

from ssot_registry.reports.summary import build_summary


def build_certification_report(
    registry: dict[str, object],
    registry_path: str,
    release_report: dict[str, object],
) -> dict[str, object]:
    return {
        "passed": bool(release_report.get("passed")),
        "registry_path": registry_path,
        "release": release_report,
        "summary": build_summary(registry),
    }
