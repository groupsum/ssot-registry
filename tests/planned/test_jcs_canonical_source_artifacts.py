from __future__ import annotations

import json
from pathlib import Path

from ssot_registry.api import export_graph, export_registry
from ssot_registry.util.jcs import assert_jcs_canonical_text, dump_jcs_json
from ssot_registry.util.jsonio import save_json
from tests.helpers import run_cli, temp_repo_from_fixture, workspace_tempdir


def _assert_canonical_json(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    assert_jcs_canonical_text(text, source=path.as_posix())
    assert text == dump_jcs_json(json.loads(text))


def test_inserted_json_is_canonicalized_before_persistence():
    with workspace_tempdir() as temp_dir:
        target = Path(temp_dir) / ".ssot" / "reports" / "inserted.json"
        payload = {
            "z": [{"b": 2, "a": 1}],
            "a": {"nested": True, "label": "canonical"},
        }

        save_json(target, payload)

        _assert_canonical_json(target)
        assert target.read_text(encoding="utf-8") == (
            '{"a":{"label":"canonical","nested":true},"z":[{"a":1,"b":2}]}'
        )


def test_generated_json_artifacts_use_canonical_source_form():
    temp_dir = temp_repo_from_fixture("repo_valid")
    try:
        repo = Path(temp_dir.name) / "repo"

        registry_export = repo / ".ssot" / "exports" / "registry-export.json"
        graph_export = repo / ".ssot" / "graphs" / "registry.graph.json"

        export_registry(repo, "json", registry_export.as_posix())
        export_graph(repo, "json", graph_export.as_posix())
        validate = run_cli("validate", str(repo), "--write-report")
        assert validate.returncode == 0, validate.stderr

        _assert_canonical_json(registry_export)
        _assert_canonical_json(graph_export)
        _assert_canonical_json(repo / ".ssot" / "reports" / "validation.report.json")
    finally:
        temp_dir.cleanup()
