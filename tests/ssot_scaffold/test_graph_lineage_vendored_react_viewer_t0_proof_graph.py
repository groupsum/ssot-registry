from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_vendored_react_viewer_assets_are_packaged_in_ssot_core() -> None:
    asset_dir = ROOT / "pkgs/ssot-core/src/ssot_registry/assets/lineage_graph"

    for name in ("__init__.py", "manifest.json", "ssot-lineage-graph.js", "ssot-lineage-graph.css"):
        assert (asset_dir / name).is_file()

    pyproject = (ROOT / "pkgs/ssot-core/pyproject.toml").read_text(encoding="utf-8")
    assert '"ssot_registry.assets.lineage_graph" = ["*.js", "*.css", "*.json"]' in pyproject
