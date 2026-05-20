from __future__ import annotations

from pathlib import Path

from .models import FORBIDDEN_EXACT_PATHS, FORBIDDEN_PATH_PREFIXES


def normalize_repo_path(path: str | Path) -> str:
    raw = str(path).replace("\\", "/").strip()
    while raw.startswith("./"):
        raw = raw[2:]
    raw = raw.lstrip("/")
    parts: list[str] = []
    for part in raw.split("/"):
        if part in {"", "."}:
            continue
        if part == "..":
            if not parts:
                raise ValueError(f"path escapes repository: {path}")
            parts.pop()
            continue
        if part == "**":
            continue
        parts.append(part)
    return "/".join(parts)


def repo_relative_path(repo_root: Path, path: str | Path) -> str:
    candidate = Path(path)
    if not candidate.is_absolute():
        return normalize_repo_path(candidate)
    resolved_repo = repo_root.resolve()
    resolved_path = candidate.resolve()
    try:
        relative = resolved_path.relative_to(resolved_repo)
    except ValueError as exc:
        raise ValueError(f"path escapes repository: {path}") from exc
    return normalize_repo_path(relative)


def is_forbidden_path(path: str | Path) -> bool:
    rel = normalize_repo_path(path)
    return rel in FORBIDDEN_EXACT_PATHS or any(rel.startswith(prefix) for prefix in FORBIDDEN_PATH_PREFIXES)


def ensure_allowed_path(path: str | Path) -> str:
    rel = normalize_repo_path(path)
    if not rel:
        raise ValueError("lease path cannot be repository root")
    if is_forbidden_path(rel):
        raise ValueError(f"forbidden path: {rel}")
    return rel


def path_overlaps(left: str | Path, right: str | Path) -> bool:
    a = normalize_repo_path(left).rstrip("/")
    b = normalize_repo_path(right).rstrip("/")
    if not a or not b:
        return True
    return a == b or a.startswith(f"{b}/") or b.startswith(f"{a}/")


def path_is_under(path: str | Path, root: str | Path) -> bool:
    rel = normalize_repo_path(path).rstrip("/")
    base = normalize_repo_path(root).rstrip("/")
    return rel == base or rel.startswith(f"{base}/")
