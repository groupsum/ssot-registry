from __future__ import annotations

import json
from pathlib import Path

from tests.helpers import run_cli, temp_repo_from_fixture


def test_lineage_html_cli_exposes_interactive_lineage_controls() -> None:
    temp_dir = temp_repo_from_fixture("repo_valid")
    try:
        repo = Path(temp_dir.name) / "repo"
        result = run_cli("graph", "lineage", str(repo))
        assert result.returncode == 0, result.stderr
        payload = json.loads(result.stdout)
        assert payload["format"] == "html"
        assert payload["node_count"] > 0
        assert payload["edge_count"] > 0
        html = Path(payload["output_path"]).read_text(encoding="utf-8")
        for expected in (
            "SSOT Lineage",
            "Interactive Viewer",
            "Connection Labels",
            "Render Node Limit",
            "Ego-Focus Hops Limit",
            "Isolate Active Focus",
            "Focus Node",
            "Deselect Node",
            "Export Payload JSON",
        ):
            assert expected in html
    finally:
        temp_dir.cleanup()
