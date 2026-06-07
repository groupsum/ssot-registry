from __future__ import annotations

from pathlib import Path

from ssot_registry.api import export_lineage_graph
from tests.helpers import temp_repo_from_fixture


def test_lineage_html_api_exports_self_contained_viewer() -> None:
    temp_dir = temp_repo_from_fixture("repo_valid")
    try:
        repo = Path(temp_dir.name) / "repo"
        result = export_lineage_graph(repo)
        assert result["passed"] is True
        assert result["format"] == "html"
        html = Path(result["output_path"]).read_text(encoding="utf-8")
        assert "const DATA =" in html
        assert "SSOT Lineage Graph" in html
        assert "feat:rfc.9000.connection-migration" in html
    finally:
        temp_dir.cleanup()
