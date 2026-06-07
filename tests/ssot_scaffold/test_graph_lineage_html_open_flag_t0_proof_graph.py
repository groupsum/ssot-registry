from __future__ import annotations

from tests.helpers import run_cli


def test_graph_lineage_html_open_flag_is_exposed():
    result = run_cli("graph", "lineage", "--help")

    assert result.returncode == 0, result.stderr
    assert "--open" in result.stdout
