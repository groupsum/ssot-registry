from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_react_lineage_graph_package_exports_component_app_html_and_types() -> None:
    index = (ROOT / "packages/ssot-lineage-graph/src/index.ts").read_text(encoding="utf-8")
    types = (ROOT / "packages/ssot-lineage-graph/src/types.ts").read_text(encoding="utf-8")

    for expected in ("LineageGraph", "LineageGraphApp", "createStandaloneHtml"):
        assert expected in index
    for expected in ("LineagePayload", "LineageNode", "LineageEdge", "RendererOptions", "SelectionState", "LayoutMode"):
        assert expected in types
