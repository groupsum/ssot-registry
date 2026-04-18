from __future__ import annotations

from ssot_views.reports import build_certification_report as _build_certification_report


def build_certification_report(
    registry: dict[str, object],
    registry_path: str,
    release_report: dict[str, object],
) -> dict[str, object]:
    return _build_certification_report(registry, registry_path, release_report)
