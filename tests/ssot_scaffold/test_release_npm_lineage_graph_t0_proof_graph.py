from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_release_metadata_declares_lineage_graph_npm_target() -> None:
    metadata = (ROOT / "scripts/release_metadata.py").read_text(encoding="utf-8")

    assert "NPM_PACKAGE_INFOS" in metadata
    assert "ssot-lineage-graph" in metadata
    assert "@ssot-registry/lineage-graph" in metadata
    assert "resolve_npm_targets" in metadata
