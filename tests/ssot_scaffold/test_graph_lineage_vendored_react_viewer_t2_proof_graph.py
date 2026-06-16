from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_vendored_react_viewer_ci_checks_asset_freshness_and_wheel_contents() -> None:
    ci = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")

    assert "Verify vendored lineage graph assets are current" in ci
    assert "Verify ssot-core wheel includes lineage graph assets" in ci
    assert "pkgs/ssot-core/src/ssot_registry/assets/lineage_graph" in ci
