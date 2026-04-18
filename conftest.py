from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
for path in (
    REPO_ROOT / "pkgs" / "ssot-core" / "src",
    REPO_ROOT / "pkgs" / "ssot-codegen" / "src",
    REPO_ROOT / "pkgs" / "ssot-views" / "src",
    REPO_ROOT / "pkgs" / "ssot-contracts" / "src",
    REPO_ROOT / "pkgs" / "ssot-tui" / "src",
    REPO_ROOT / "pkgs" / "ssot-cli" / "src",
):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

collect_ignore_glob = ["tests/fixtures/*/tests/*.py"]
