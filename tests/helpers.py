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


def temp_repo_from_fixture(name: str) -> tempfile.TemporaryDirectory[str]:
    temp_dir = tempfile.TemporaryDirectory()
    target = Path(temp_dir.name) / "repo"
    shutil.copytree(FIXTURES_ROOT / name, target)
    return temp_dir


def run_cli(*args: str, cwd: str | Path | None = None) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(SRC_ROOT)
    return subprocess.run(
        [sys.executable, "-m", "ssot_registry", *args],
        cwd=str(cwd) if cwd is not None else None,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )
