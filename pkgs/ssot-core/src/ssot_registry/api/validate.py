from __future__ import annotations

from pathlib import Path

from ssot_contracts.generated.python.enums import SCHEMA_VERSION
from ssot_registry.model.schema_version import is_known_schema_version, schema_version_is_older
from ssot_registry.reports.validation_report import build_validation_report
from ssot_registry.validators import (
    validate_identity,
    validate_structure,
    validate_references,
    validate_bidirectional_links,
    validate_coverage,
    validate_document_rows,
    validate_document_reservations,
    validate_tiers,
    validate_lifecycle_semantics,
    validate_out_of_bounds_disposition,
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
    validate_document_reservations(registry, failures)
    validate_document_rows(registry, index, Path(repo_root), failures)
    validate_references(registry, index, failures)
    validate_bidirectional_links(index, failures)
    validate_coverage(index, failures, warnings)
    validate_tiers(index, failures)
    validate_lifecycle_semantics(registry, index, failures, warnings)
    validate_out_of_bounds_disposition(registry, index, failures, warnings)
    validate_filesystem_paths(registry, index, Path(repo_root), failures, warnings)

    return build_validation_report(registry, Path(registry_path).as_posix(), sorted(set(failures)), sorted(set(warnings)))


def validate_registry(path: str | Path) -> dict[str, object]:
    registry_path, repo_root, registry = load_registry(path)
    schema_version = registry.get("schema_version")
    if schema_version != SCHEMA_VERSION:
        if schema_version_is_older(schema_version, SCHEMA_VERSION):
            failures = [
                f"Registry schema_version {schema_version} is older than supported schema_version {SCHEMA_VERSION}; run `ssot upgrade {repo_root.as_posix()}`"
            ]
        elif not is_known_schema_version(schema_version, SCHEMA_VERSION):
            failures = [f"Registry schema_version is unsupported: {schema_version!r}"]
        else:
            failures = [f"Registry schema_version must be {SCHEMA_VERSION}"]
        return build_validation_report(registry, registry_path.as_posix(), failures, [])
    return validate_registry_document(registry, registry_path, repo_root)
