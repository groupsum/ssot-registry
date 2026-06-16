from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_release_workflows_build_test_pack_and_publish_lineage_graph_npm_package() -> None:
    release = (ROOT / ".github/workflows/release.yml").read_text(encoding="utf-8")
    prepare = (ROOT / ".github/workflows/prepare-release.yml").read_text(encoding="utf-8")

    assert "build-npm-distributions" in release
    assert "publish-ssot-lineage-graph" in release
    assert "npm publish --access public --provenance" in release
    assert "publish_to_npm" in release
    assert "ssot-lineage-graph" in prepare
