from __future__ import annotations

from pathlib import Path

from ssot_registry.util.errors import ValidationError
from ssot_registry.util.registry_lock import save_registry_json_locked


def _repo_root_for_registry_path(registry_path: str | Path) -> Path:
    path = Path(registry_path)
    if path.name == "registry.json" and path.parent.name == ".ssot":
        return path.parent.parent
    if path.parent.name == ".ssot":
        return path.parent.parent
    return path.parent


def save_registry_unchecked(registry_path: str | Path, registry: dict[str, object]) -> None:
    save_registry_json_locked(registry_path, registry)


def save_registry(
    registry_path: str | Path,
    registry: dict[str, object],
    *,
    repo_root: str | Path | None = None,
    action: str = "saving registry",
) -> dict[str, object]:
    from .validate import validate_registry_document

    resolved_repo_root = Path(repo_root) if repo_root is not None else _repo_root_for_registry_path(registry_path)
    report = validate_registry_document(registry, registry_path, resolved_repo_root)
    if not report["passed"]:
        detail = "; ".join(report["failures"])
        raise ValidationError(f"Registry validation failed before {action}: {detail}")
    save_registry_unchecked(registry_path, registry)
    return report
