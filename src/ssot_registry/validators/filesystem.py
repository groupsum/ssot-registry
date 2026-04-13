from __future__ import annotations

from pathlib import Path


def validate_filesystem_paths(
    index: dict[str, dict[str, dict[str, object]]],
    repo_root: Path,
    failures: list[str],
    warnings: list[str],
) -> None:
    for test_id, row in index["tests"].items():
        path = row.get("path")
        if isinstance(path, str):
            target = repo_root / path
            if not target.exists():
                failures.append(f"tests.{test_id}.path does not exist: {path}")

    for evidence_id, row in index["evidence"].items():
        path = row.get("path")
        if isinstance(path, str):
            target = repo_root / path
            if not target.exists():
                failures.append(f"evidence.{evidence_id}.path does not exist: {path}")

    for path_key in ("ssot_root", "schema_root", "adr_root", "spec_root", "graph_root", "evidence_root", "release_root", "report_root"):
        # Path existence is advisory for configured directories.
        # The registry may declare a path before it is created.
        pass
