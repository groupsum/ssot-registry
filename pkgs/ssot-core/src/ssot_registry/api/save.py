from __future__ import annotations

from pathlib import Path

from ssot_registry.util.registry_lock import save_registry_json_locked


def save_registry(registry_path: str | Path, registry: dict[str, object]) -> None:
    save_registry_json_locked(registry_path, registry)
