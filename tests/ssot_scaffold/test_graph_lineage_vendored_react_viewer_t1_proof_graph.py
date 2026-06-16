from pathlib import Path

from ssot_registry.api import export_lineage_graph
from tests.helpers import temp_repo_from_fixture


def test_vendored_react_viewer_exports_offline_html_with_payload_root() -> None:
    temp_dir = temp_repo_from_fixture("repo_valid")
    try:
        repo = Path(temp_dir.name) / "repo"
        result = export_lineage_graph(repo)
        html = Path(result["output_path"]).read_text(encoding="utf-8")

        assert "window.__SSOT_LINEAGE_PAYLOAD__=" in html
        assert 'id="ssot-lineage-root"' in html
        assert "<script src=" not in html
        assert '<link rel="stylesheet"' not in html
    finally:
        temp_dir.cleanup()
