from __future__ import annotations

from ssot_registry.model.registry import count_entities


def build_summary(registry: dict[str, object]) -> dict[str, object]:
    return {
        "counts": count_entities(registry),
    }
