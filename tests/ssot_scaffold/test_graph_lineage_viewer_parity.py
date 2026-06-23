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
    for expected in ("No Element Selected", "Click any circular node", "Upstream Ancestors", "Downstream Relations"):
        assert expected in html
    assert "JSON.stringify(n,null,2)" not in html
    assert "<pre id=\"summary\">" not in html


def test_lineage_legend_context_contract() -> None:
    html = _lineage_html()
    for expected in ("SSOT Registry Scope", "Registry Index", "Lineage View Modes", "Interactive Viewer"):
        assert expected in html
    assert "Canonical Core Registry" not in html


def test_lineage_ego_focus_depth_contract() -> None:
    html = _lineage_html()
    for expected in ("Network Force", "Lineage Flow", "Proof Chain", "Origins Mode", "Packs Lineage", "Release Board", "Validation"):
        assert expected in html


def test_lineage_layout_scaling_contract() -> None:
    html = _lineage_html()
    for expected in ("ADR Setup", "Specification", "Core Features", "Claims", "Verifications", "Certificates", "Releases"):
        assert expected in html


def test_lineage_viewport_controls_contract() -> None:
    html = _lineage_html()
    for expected in ("Zoom Out", "Zoom In", "Fit Viewport on Nodes", "Reset Zoom to 100%", "Toggle canvas color scheme"):
        assert expected in html


def test_lineage_node_dragging_contract() -> None:
    html = _lineage_html()
    for expected in ("Drag to place - Double-click to unpin", "Drag to reposition", "Unpin All Anchors", "Hide this node from view", "Show All"):
        assert expected in html


def test_lineage_snapshot_export_contract() -> None:
    html = _lineage_html()
    for expected in ("Export Payload JSON", "Download the current lineage payload JSON", "_lineage_payload.json"):
        assert expected in html
    assert "https://cdn.tailwindcss.com" not in html
    assert "fonts.googleapis" not in html


def test_lineage_edges_are_visible_and_navigable_contract() -> None:
    html = _lineage_html()
    for expected in ("Upstream Ancestors", "Downstream Relations", "No incoming connections.", "No outgoing connections."):
        assert expected in html


def test_lineage_summary_uses_key_value_rows_contract() -> None:
    html = _lineage_html()
    for expected in ("Origin Provenance", "Compliance status", "Schema: v", "Edges:"):
        assert expected in html
    assert '<pre id="summary">' not in html
    assert "JSON.stringify(DATA.summary" not in html
