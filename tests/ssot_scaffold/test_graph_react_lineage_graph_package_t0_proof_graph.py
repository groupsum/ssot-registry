import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_react_lineage_graph_package_exists_and_declares_public_api() -> None:
    package = json.loads((ROOT / "packages/ssot-lineage-graph/package.json").read_text(encoding="utf-8"))

    assert package["name"] == "@ssot-registry/lineage-graph"
    assert package["repository"]["url"] == "https://github.com/groupsum/ssot-registry"
    assert package["repository"]["directory"] == "packages/ssot-lineage-graph"
    assert package["types"] == "./dist/index.d.ts"
    assert "." in package["exports"]
    assert package["exports"]["."]["import"] == "./dist/lineage-graph.js"
    assert package["exports"]["."]["require"] == "./dist/lineage-graph.cjs"
