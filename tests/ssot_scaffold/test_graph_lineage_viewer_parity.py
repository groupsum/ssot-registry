from __future__ import annotations

import json
from pathlib import Path

from tests.helpers import run_cli, temp_repo_from_fixture


def _lineage_html() -> str:
    temp_dir = temp_repo_from_fixture("repo_valid")
    try:
        repo = Path(temp_dir.name) / "repo"
        result = run_cli("graph", "lineage", str(repo))
        assert result.returncode == 0, result.stderr
        payload = json.loads(result.stdout)
        return Path(payload["output_path"]).read_text(encoding="utf-8")
    finally:
        temp_dir.cleanup()


def test_lineage_selection_detail_contract() -> None:
    html = _lineage_html()
    for expected in ("Selected Node", "Connected Edges", "Select a node for details", "Deselect", "ssot-kv-row"):
        assert expected in html
    assert "JSON.stringify(n,null,2)" not in html
    assert "<pre id=\"summary\">" not in html


def test_lineage_legend_context_contract() -> None:
    html = _lineage_html()
    for expected in ("Package context unavailable", "Legend", "ssot-legend", "ssot-lineage-app"):
        assert expected in html
    assert html.index("SSOT Lineage Graph") < html.index("Legend")


def test_lineage_ego_focus_depth_contract() -> None:
    html = _lineage_html()
    for expected in ("Maximum", "centerId", "1 hop", "2 hops", "3 hops", "Focus other"):
        assert expected in html


def test_lineage_layout_scaling_contract() -> None:
    html = _lineage_html()
    for expected in ("X Scale", "Y Scale", "210", "90", "Math.pow(10", "Number.isFinite"):
        assert expected in html


def test_lineage_viewport_controls_contract() -> None:
    html = _lineage_html()
    for expected in ("Fit", "100%", "zoom", "Number.isFinite", "PNG", "SVG"):
        assert expected in html


def test_lineage_node_dragging_contract() -> None:
    html = _lineage_html()
    for expected in ("nodeId", "moved", "pinned", "onMouseMove"):
        assert expected in html


def test_lineage_snapshot_export_contract() -> None:
    html = _lineage_html()
    for expected in ("toDataURL", "image/png", "ssot-lineage-graph.svg", "image/svg+xml"):
        assert expected in html


def test_lineage_edges_are_visible_and_navigable_contract() -> None:
    html = _lineage_html()
    for expected in ("rgba(8,145,178", "Connected Edges", "Focus other", "From", "To"):
        assert expected in html


def test_lineage_summary_uses_key_value_rows_contract() -> None:
    html = _lineage_html()
    for expected in ("Summary", "ssot-kv-row", "nodeCount", "edgeTypes"):
        assert expected in html
    assert '<pre id="summary">' not in html
    assert "JSON.stringify(DATA.summary" not in html
