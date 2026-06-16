from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_react_lineage_graph_package_emits_declarations_and_standalone_assets() -> None:
    package = (ROOT / "packages/ssot-lineage-graph/package.json").read_text(encoding="utf-8")
    build_tsconfig = (ROOT / "packages/ssot-lineage-graph/tsconfig.build.json").read_text(encoding="utf-8")
    copy_script = (ROOT / "packages/ssot-lineage-graph/scripts/copy-vendored.mjs").read_text(encoding="utf-8")

    assert "tsc -p tsconfig.build.json" in package
    assert '"emitDeclarationOnly": true' in build_tsconfig
    assert "ssot-lineage-graph.js" in copy_script
    assert "ssot-lineage-graph.css" in copy_script
