from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_release_workflow_rejects_stale_vendored_lineage_assets() -> None:
    release = (ROOT / ".github/workflows/release.yml").read_text(encoding="utf-8")

    assert "Verify vendored lineage graph assets are current" in release
    assert "git diff --exit-code -- pkgs/ssot-core/src/ssot_registry/assets/lineage_graph" in release


def test_graph_api_does_not_ship_stale_inline_lineage_template() -> None:
    graph_api = (ROOT / "pkgs/ssot-core/src/ssot_registry/api/graph.py").read_text(encoding="utf-8")

    assert "_LINEAGE_HTML_TEMPLATE" not in graph_api
    assert "_render_lineage_html(payload)" in graph_api
