from pathlib import Path

from ssot_registry.api import export_lineage_graph
from tests.helpers import temp_repo_from_fixture


def test_lineage_html_uses_vendored_current_react_viewer() -> None:
    temp_dir = temp_repo_from_fixture("repo_valid")
    try:
        repo = Path(temp_dir.name) / "repo"
        result = export_lineage_graph(repo)
        html = Path(result["output_path"]).read_text(encoding="utf-8")

        assert result["passed"]
        assert "window.__SSOT_LINEAGE_PAYLOAD__=" in html
        assert 'id="ssot-lineage-root"' in html
        assert "graph-application-shell" in html
        assert "Interactive Viewer" in html
        assert "__PAYLOAD__" not in html
        assert "const DATA =" not in html
        assert "<script src=" not in html
        assert '<link rel="stylesheet"' not in html
    finally:
        temp_dir.cleanup()
