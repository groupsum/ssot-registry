from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent
for path in (
    REPO_ROOT / "pkgs" / "ssot-core" / "src",
    REPO_ROOT / "pkgs" / "ssot-codegen" / "src",
    REPO_ROOT / "pkgs" / "ssot-views" / "src",
    REPO_ROOT / "pkgs" / "ssot-contracts" / "src",
    REPO_ROOT / "pkgs" / "ssot-conformance" / "src",
    REPO_ROOT / "pkgs" / "ssot-tui" / "src",
    REPO_ROOT / "pkgs" / "ssot-cli" / "src",
):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

collect_ignore_glob = ["tests/fixtures/*/tests/*.py"]


@pytest.fixture(scope="session")
def ssot_repo_root(pytestconfig: pytest.Config) -> Path:
    return Path(pytestconfig.getoption("ssot_repo_root", default=".")).resolve()


@pytest.fixture(scope="session")
def ssot_registry(ssot_repo_root: Path) -> dict[str, object]:
    import json

    return json.loads((ssot_repo_root / ".ssot" / "registry.json").read_text(encoding="utf-8"))
