from __future__ import annotations

import json
from pathlib import Path

from tests.helpers import run_cli, temp_repo_from_fixture


def test_lineage_html_large_graph_controls_are_exported() -> None:
    temp_dir = temp_repo_from_fixture("repo_valid")
    try:
        repo = Path(temp_dir.name) / "repo"
        result = run_cli("graph", "lineage", str(repo))
        assert result.returncode == 0, result.stderr
        payload = json.loads(result.stdout)
        html = Path(payload["output_path"]).read_text(encoding="utf-8")
        for expected in (
            "Barnes-Hut Force",
            "Force Cutoff",
            'max="10000"',
            "Ribbon Culling",
            "barnesRepulsion",
            "cullRibbons",
            "Exact O(n^2) force",
        ):
            assert expected in html
    finally:
        temp_dir.cleanup()
