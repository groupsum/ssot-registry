from __future__ import annotations

from importlib import resources
from pathlib import Path

from ssot_registry.api.documents import sync_all_documents
from ssot_registry.model.registry import build_minimal_registry, default_paths
from ssot_registry.util.errors import RegistryError
from ssot_registry.util.jsonio import save_json
from .validate import validate_registry


def _copy_resource_tree(package: str, destination: Path, suffix: str) -> None:
    destination.mkdir(parents=True, exist_ok=True)
    root = resources.files(package)
    for entry in root.iterdir():
        if entry.is_file() and entry.name.endswith(suffix):
            target = destination / entry.name
            target.write_text(entry.read_text(encoding="utf-8"), encoding="utf-8")


def initialize_repo(
    path: str | Path,
    repo_id: str,
    repo_name: str,
    version: str,
    force: bool = False,
) -> dict[str, object]:
    repo_root = Path(path)
    repo_root.mkdir(parents=True, exist_ok=True)

    paths = default_paths()
    registry_path = repo_root / paths["ssot_root"] / "registry.json"
    if registry_path.exists() and not force:
        raise RegistryError(f"Registry already exists: {registry_path}")

    for key, relative_path in paths.items():
        (repo_root / relative_path).mkdir(parents=True, exist_ok=True)

    registry = build_minimal_registry(repo_id, repo_name, version)
    save_json(registry_path, registry)

    _copy_resource_tree("ssot_registry.schema", repo_root / paths["schema_root"], ".json")
    sync_all_documents(registry_path)

    report = validate_registry(registry_path)
    if not report["passed"]:
        raise RegistryError("Newly initialized registry did not validate")

    return {
        "passed": True,
        "registry_path": registry_path.as_posix(),
        "repo_root": repo_root.as_posix(),
    }
