from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_release_bump_script_updates_lineage_graph_npm_version() -> None:
    script = (ROOT / "scripts/bump_release_train.py").read_text(encoding="utf-8")

    assert "_python_to_npm_version" in script
    assert "resolve_npm_targets" in script
    assert "NPM_PACKAGE_INFOS" in script
    assert "ssot-lineage-graph" in script
