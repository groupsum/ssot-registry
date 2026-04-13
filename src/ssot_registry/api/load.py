from __future__ import annotations

from pathlib import Path

from ssot_registry.util.fs import repo_root_from_registry_path, resolve_registry_path
from ssot_registry.util.jsonio import load_json


def load_registry(path: str | Path) -> tuple[Path, Path, dict[str, object]]:
    registry_path = resolve_registry_path(path)
    registry = load_json(registry_path)
    repo_root = repo_root_from_registry_path(registry_path)
    return registry_path, repo_root, registry
