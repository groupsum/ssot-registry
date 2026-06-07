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
    for expected in ("Selected Node", "Connected Edges", "renderConnectedEdges", "toggleSelected", "deselectNode"):
        assert expected in html


def test_lineage_legend_context_contract() -> None:
    html = _lineage_html()
    for expected in ("packageInfo", "DATA.package", "Package context unavailable", "Legend", "renderLegend"):
        assert expected in html


def test_lineage_ego_focus_depth_contract() -> None:
    html = _lineage_html()
    for expected in ("Maximum", "centerId=selectedId", "neighbors(seeds()", "1 hop", "2 hops", "3 hops"):
        assert expected in html


def test_lineage_layout_scaling_contract() -> None:
    html = _lineage_html()
    for expected in ("X Scale", "Y Scale", "210 * scale", "90 * scale", "update(!(el===els.xScale"):
        assert expected in html


def test_lineage_viewport_controls_contract() -> None:
    html = _lineage_html()
    for expected in ("zoomIn", "zoomOut", "zoomReset", "zoomAt", "Fit"):
        assert expected in html


def test_lineage_node_dragging_contract() -> None:
    html = _lineage_html()
    for expected in ("dragNodeId", "downWasSelected", "n.x += dx/zoom", "n.y += dy/zoom"):
        assert expected in html


def test_lineage_snapshot_export_contract() -> None:
    html = _lineage_html()
    for expected in ("exportPng", "exportSvg", "toDataURL(\"image/png\")", "ssot-lineage-graph.svg"):
        assert expected in html
