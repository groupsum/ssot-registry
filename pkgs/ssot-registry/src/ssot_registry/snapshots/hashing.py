from __future__ import annotations

from pathlib import Path

from ssot_registry.util.fs import sha256_path


def hash_paths(repo_root: Path, relative_paths: list[str]) -> dict[str, str]:
    return {relative_path: sha256_path(repo_root / relative_path) for relative_path in sorted(set(relative_paths))}
