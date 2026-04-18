from __future__ import annotations

from pathlib import Path

from ssot_registry.util.jsonio import save_json


def save_registry(registry_path: str | Path, registry: dict[str, object]) -> None:
    save_json(registry_path, registry)
