import json
from pathlib import Path

from ssot_registry.api import export_lineage_graph
from tests.helpers import temp_repo_from_fixture


def test_lineage_export_embeds_payload_that_matches_current_viewer_contract() -> None:
    temp_dir = temp_repo_from_fixture("repo_valid")
    try:
        repo = Path(temp_dir.name) / "repo"
        result = export_lineage_graph(repo)
        html = Path(result["output_path"]).read_text(encoding="utf-8")

        marker = "window.__SSOT_LINEAGE_PAYLOAD__="
        start = html.index(marker) + len(marker)
        end = html.index(";</script>", start)
        payload = json.loads(html[start:end])

        assert result["passed"]
        assert payload["schemaVersion"] == "2"
        assert payload["nodes"]
        assert payload["edges"]
        assert payload["summaries"]["counts"]["nodes"] == len(payload["nodes"])
        assert "graph-application-shell" in html
        assert "feat:rfc.9000.connection-migration" in html
    finally:
        temp_dir.cleanup()
