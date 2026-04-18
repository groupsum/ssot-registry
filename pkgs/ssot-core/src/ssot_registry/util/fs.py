from __future__ import annotations

import hashlib
from pathlib import Path


def ensure_directory(path: str | Path) -> Path:
    target = Path(path)
    target.mkdir(parents=True, exist_ok=True)
    return target


def _registry_candidate(path: Path) -> Path:
    return path / ".ssot" / "registry.json"


def resolve_registry_path(path: str | Path) -> Path:
    candidate = Path(path).expanduser()
    if candidate.name == "registry.json" and candidate.parent.name == ".ssot":
        return candidate
    if candidate.name == ".ssot":
        registry_path = candidate / "registry.json"
        if registry_path.is_file():
            return registry_path
    search_roots = [candidate]
    search_roots.extend(candidate.parents)
    for root in search_roots:
        registry_path = _registry_candidate(root)
        if registry_path.is_file():
            return registry_path
    raise FileNotFoundError(
        "Unable to locate .ssot/registry.json from "
        f"{candidate}. Provide the repository root, the .ssot directory, "
        "the registry.json file, or any path inside a repository that contains .ssot/registry.json."
    )


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
