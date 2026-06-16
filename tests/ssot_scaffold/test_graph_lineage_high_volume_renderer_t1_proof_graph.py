from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_high_volume_renderer_force_step_uses_all_visible_families_and_edges() -> None:
    layout = (ROOT / "packages/ssot-lineage-graph/src/layout.ts").read_text(encoding="utf-8")
    test = (ROOT / "packages/ssot-lineage-graph/src/lineageGraph.test.ts").read_text(encoding="utf-8")

    assert "applyBarnesHutRepulsion" in layout
    assert "applyForceLayoutStep" in layout
    assert "for (const node of nodes)" in layout
    assert "updates every visible SSOT family" in test
