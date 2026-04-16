from __future__ import annotations

from ssot_views.reports import build_validation_report as _build_validation_report


def build_validation_report(
    registry: dict[str, object],
    registry_path: str,
    failures: list[str],
    warnings: list[str],
) -> dict[str, object]:
    return _build_validation_report(registry, registry_path, failures, warnings)
