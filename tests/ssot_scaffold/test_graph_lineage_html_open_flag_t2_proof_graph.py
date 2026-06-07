from __future__ import annotations

import json
from pathlib import Path

from tests.helpers import run_cli, temp_repo_from_fixture


def test_graph_lineage_html_open_flag_rejects_directory_output():
    temp_dir = temp_repo_from_fixture("repo_valid")
    repo = Path(temp_dir.name) / "repo"
    try:
        result = run_cli("graph", "lineage", str(repo), "--output", str(repo))

        assert result.returncode != 0
        payload = json.loads(result.stdout)
        assert payload["passed"] is False
        assert "must be a file, not a directory" in payload["error"]
    finally:
        temp_dir.cleanup()
