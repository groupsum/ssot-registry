from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_high_volume_renderer_generated_html_exposes_visible_edge_and_finite_zoom_contracts() -> None:
    asset = (ROOT / "pkgs/ssot-core/src/ssot_registry/assets/lineage_graph/ssot-lineage-graph.js").read_text(
        encoding="utf-8"
    )

    assert "Render Node Limit" in asset
    assert "Ego-Focus Hops Limit" in asset
    assert "Isolate Active Focus" in asset
    assert "line-flow-active" in asset
    assert "url(#arrow-incoming)" in asset
    assert "url(#arrow-outgoing)" in asset
    assert "edgeWidth" in asset
    assert "edgeOpacity" in asset
    assert "zoom" in asset
