from __future__ import annotations

from .summary import build_summary


def build_validation_report(
    registry: dict[str, object],
    registry_path: str,
    failures: list[str],
    warnings: list[str],
) -> dict[str, object]:
    return {
        "passed": not failures,
        "registry_path": registry_path,
        "failures": failures,
        "warnings": warnings,
        "summary": build_summary(registry),
    }
