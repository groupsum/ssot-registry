from __future__ import annotations

def build_summary(registry: dict[str, object]) -> dict[str, object]:
    from ssot_views.reports import build_summary as _build_summary

    return _build_summary(registry)
