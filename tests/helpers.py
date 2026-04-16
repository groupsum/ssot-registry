from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
FIXTURES_ROOT = PROJECT_ROOT / "tests" / "fixtures"
SRC_ROOT = PROJECT_ROOT / "src"
CLI_SRC_ROOT = PROJECT_ROOT / "pkgs" / "ssot-cli" / "src"
TUI_SRC_ROOT = PROJECT_ROOT / "pkgs" / "ssot-tui" / "src"
TEMP_ROOT = PROJECT_ROOT / ".tmp_test_runs"


def workspace_tempdir() -> tempfile.TemporaryDirectory[str]:
    TEMP_ROOT.mkdir(parents=True, exist_ok=True)
    return tempfile.TemporaryDirectory(dir=TEMP_ROOT)


def temp_repo_from_fixture(name: str) -> tempfile.TemporaryDirectory[str]:
    temp_dir = workspace_tempdir()
    target = Path(temp_dir.name) / "repo"
    shutil.copytree(FIXTURES_ROOT / name, target)
    return temp_dir


def run_cli(*args: str, cwd: str | Path | None = None) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    pythonpath_parts = [str(CLI_SRC_ROOT), str(TUI_SRC_ROOT), str(SRC_ROOT)]
    existing = env.get("PYTHONPATH")
    if existing:
        pythonpath_parts.append(existing)
    env["PYTHONPATH"] = os.pathsep.join(pythonpath_parts)
    return subprocess.run(
        [sys.executable, "-m", "ssot_registry", *args],
        cwd=str(cwd) if cwd is not None else None,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )
