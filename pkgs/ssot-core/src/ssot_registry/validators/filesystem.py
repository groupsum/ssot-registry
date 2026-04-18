from __future__ import annotations

from pathlib import Path


MAX_SSOT_PATH_LENGTH = 240
MAX_SSOT_FILENAME_LENGTH = 120


def _is_ssot_relative_path(relative_path: str, ssot_root: str) -> bool:
    candidate = Path(relative_path.strip())
    if candidate.is_absolute():
        return False

    ssot = Path(ssot_root.strip())
    if not ssot.parts:
        return False

    try:
        candidate.relative_to(ssot)
        return True
    except ValueError:
        return False


def _validate_ssot_path_length(relative_path: str, failures: list[str], context: str) -> None:
    path = Path(relative_path)
    filename = path.name
    if len(relative_path) > MAX_SSOT_PATH_LENGTH:
        failures.append(
            f"{context} exceeds max .ssot path length {MAX_SSOT_PATH_LENGTH}: {relative_path}"
        )
    if filename and len(filename) > MAX_SSOT_FILENAME_LENGTH:
        failures.append(
            f"{context} exceeds max .ssot filename length {MAX_SSOT_FILENAME_LENGTH}: {filename}"
        )


def validate_filesystem_paths(
    registry: dict[str, object],
    index: dict[str, dict[str, dict[str, object]]],
    repo_root: Path,
    failures: list[str],
    warnings: list[str],
) -> None:
    paths = registry.get("paths")
    ssot_root = ".ssot"
    if isinstance(paths, dict) and isinstance(paths.get("ssot_root"), str):
        ssot_root = paths["ssot_root"]

    for test_id, row in index["tests"].items():
        path = row.get("path")
        if isinstance(path, str):
            target = repo_root / path
            if not target.exists():
                failures.append(f"tests.{test_id}.path does not exist: {path}")
            if _is_ssot_relative_path(path, ssot_root):
                _validate_ssot_path_length(path, failures, f"tests.{test_id}.path")

    for evidence_id, row in index["evidence"].items():
        path = row.get("path")
        if isinstance(path, str):
            target = repo_root / path
            if not target.exists():
                failures.append(f"evidence.{evidence_id}.path does not exist: {path}")
            if _is_ssot_relative_path(path, ssot_root):
                _validate_ssot_path_length(path, failures, f"evidence.{evidence_id}.path")

    for section in ("adrs", "specs"):
        for document_id, row in index.get(section, {}).items():
            path = row.get("path")
            if isinstance(path, str) and _is_ssot_relative_path(path, ssot_root):
                _validate_ssot_path_length(path, failures, f"{section}.{document_id}.path")

    for path_key in ("adr_root", "spec_root"):
        configured = paths.get(path_key) if isinstance(paths, dict) else None
        if not isinstance(configured, str):
            continue
        document_root = repo_root / configured
        if not document_root.exists() or not document_root.is_dir():
            continue
        for legacy_path in sorted(document_root.glob("*.md")):
            failures.append(f"Legacy markdown document is not allowed after migration: {legacy_path.relative_to(repo_root).as_posix()}")

    ssot_dir = repo_root / ssot_root
    if ssot_dir.exists() and ssot_dir.is_dir():
        for target in ssot_dir.rglob("*"):
            relative_path = target.relative_to(repo_root).as_posix()
            _validate_ssot_path_length(relative_path, failures, f"filesystem path")

    for path_key in ("ssot_root", "schema_root", "adr_root", "spec_root", "graph_root", "evidence_root", "release_root", "report_root"):
        # Path existence is advisory for configured directories.
        # The registry may declare a path before it is created.
        pass
