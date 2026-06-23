from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_high_volume_renderer_declares_force_cutoff_and_ribbon_controls() -> None:
    app = (ROOT / "packages/ssot-lineage-graph/src/workspace/components/LineageGraphApp.tsx").read_text(encoding="utf-8")
    sidebar = (ROOT / "packages/ssot-lineage-graph/src/workspace/components/LeftSidebar.tsx").read_text(encoding="utf-8")
    canvas = (ROOT / "packages/ssot-lineage-graph/src/workspace/components/LineageGraphCanvas.tsx").read_text(encoding="utf-8")

    assert "const [nodeLimit, setNodeLimit] = useState<number>(300)" in app
    assert "const [egoHops, setEgoHops] = useState<number>(1)" in app
    assert "const [isolateEgo, setIsolateEgo] = useState<boolean>(false)" in app
    assert "Render Node Limit" in sidebar
    assert "Ego-Focus Hops Limit" in sidebar
    assert "Isolate Active Focus" in sidebar
    assert "999999" in sidebar
    assert "line-flow-active" in canvas
    assert "url(#arrow-incoming)" in canvas
    assert "url(#arrow-outgoing)" in canvas
    assert "Math.max(0.05, zoom)" in canvas
    assert "viewSettings.edgeWidth" in canvas
    assert "viewSettings.edgeOpacity" in canvas
