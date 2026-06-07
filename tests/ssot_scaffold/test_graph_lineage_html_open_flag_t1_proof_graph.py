from __future__ import annotations

import json
from pathlib import Path

from tests.helpers import run_cli, temp_repo_from_fixture


def test_graph_lineage_html_open_flag_is_opt_in():
    temp_dir = temp_repo_from_fixture("repo_valid")
    repo = Path(temp_dir.name) / "repo"
    try:
        result = run_cli("graph", "lineage", str(repo))

        assert result.returncode == 0, result.stderr
        payload = json.loads(result.stdout)
        assert payload["format"] == "html"
        assert payload["opened"] is False
        assert Path(payload["output_path"]).exists()
    finally:
        temp_dir.cleanup()
