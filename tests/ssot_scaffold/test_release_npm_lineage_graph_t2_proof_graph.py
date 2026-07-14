from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_release_workflows_build_test_pack_and_publish_lineage_graph_npm_package() -> None:
    release = (ROOT / ".github/workflows/release.yml").read_text(encoding="utf-8")
    prepare = (ROOT / ".github/workflows/prepare-release.yml").read_text(encoding="utf-8")

    assert "build-npm-distributions" in release
    assert "publish-ssot-lineage-graph" in release
    assert "npm publish --access public --provenance" in release
    assert "uses: actions/setup-node@v6" in release
    assert 'node-version: "24"' in release
    assert "package-manager-cache: false" in release
    assert "NODE_AUTH_TOKEN: ${{ secrets.NPM_API_TOKEN }}" not in release
    assert "id-token: write" in release
    assert "id-token: write" in prepare
    assert "publish_to_npm" in release
    assert "ssot-lineage-graph" in prepare
