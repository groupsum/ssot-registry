from __future__ import annotations

import hashlib
from pathlib import Path


def ensure_directory(path: str | Path) -> Path:
    target = Path(path)
    target.mkdir(parents=True, exist_ok=True)
    return target


def resolve_registry_path(path: str | Path) -> Path:
    candidate = Path(path)
    if candidate.is_dir():
        return candidate / ".ssot" / "registry.json"
    return candidate


def repo_root_from_registry_path(registry_path: str | Path) -> Path:
    registry = Path(registry_path)
    if registry.name != "registry.json" or registry.parent.name != ".ssot":
        raise ValueError(f"Expected a .ssot/registry.json path, got: {registry}")
    return registry.parent.parent


def sha256_normalized_text_path(path: str | Path) -> str:
    target = Path(path)
    return hashlib.sha256(target.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def sha256_path(path: str | Path) -> str:
    target = Path(path)
    digest = hashlib.sha256()
    if target.is_dir():
        for child in sorted(p for p in target.rglob("*") if p.is_file()):
            digest.update(child.relative_to(target).as_posix().encode("utf-8"))
            digest.update(child.read_bytes())
        return digest.hexdigest()
    digest.update(target.read_bytes())
    return digest.hexdigest()
