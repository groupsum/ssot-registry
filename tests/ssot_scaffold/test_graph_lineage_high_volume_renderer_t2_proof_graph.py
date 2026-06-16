from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_high_volume_renderer_generated_html_exposes_visible_edge_and_finite_zoom_contracts() -> None:
    asset = (ROOT / "pkgs/ssot-core/src/ssot_registry/assets/lineage_graph/ssot-lineage-graph.js").read_text(
        encoding="utf-8"
    )

    assert "visible nodes" in asset
    assert "visible edges" in asset
    assert "Number.isFinite" in asset
    assert "rgba(8,145,178" in asset
