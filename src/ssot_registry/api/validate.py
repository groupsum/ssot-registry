from __future__ import annotations

from pathlib import Path

from ssot_registry.reports.validation_report import build_validation_report
from ssot_registry.validators import (
    validate_identity,
    validate_structure,
    validate_references,
    validate_bidirectional_links,
    validate_coverage,
    validate_tiers,
    validate_lifecycle_semantics,
    validate_filesystem_paths,
)
from .load import load_registry


def validate_registry_document(
    registry: dict[str, object],
    registry_path: str | Path,
    repo_root: str | Path,
) -> dict[str, object]:
    failures: list[str] = []
    warnings: list[str] = []

    index = validate_identity(registry, failures)
    validate_structure(registry, index, failures)
    validate_references(registry, index, failures)
    validate_bidirectional_links(index, failures)
    validate_coverage(index, failures, warnings)
    validate_tiers(index, failures)
    validate_lifecycle_semantics(registry, index, failures, warnings)
    validate_filesystem_paths(index, Path(repo_root), failures, warnings)

    return build_validation_report(registry, Path(registry_path).as_posix(), sorted(set(failures)), sorted(set(warnings)))


def validate_registry(path: str | Path) -> dict[str, object]:
    registry_path, repo_root, registry = load_registry(path)
    return validate_registry_document(registry, registry_path, repo_root)
