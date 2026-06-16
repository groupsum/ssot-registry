from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_high_volume_renderer_declares_force_cutoff_and_ribbon_controls() -> None:
    app = (ROOT / "packages/ssot-lineage-graph/src/views/LineageGraphAppView.tsx").read_text(encoding="utf-8")
    controls = (ROOT / "packages/ssot-lineage-graph/src/components/ViewControls.tsx").read_text(encoding="utf-8")

    assert "forceCutoff" in app
    assert "10000" in app
    assert "Ribbon Culling" in controls
    assert "Edge Opacity" in controls
    assert "Edge Width" in controls
