from __future__ import annotations

import subprocess
from pathlib import Path


def parse_porcelain_v2_z(output: bytes) -> list[str]:
    paths: list[str] = []
    for entry in output.split(b"\0"):
        if not entry:
            continue
        text = entry.decode("utf-8", errors="replace")
        if text.startswith("? "):
            paths.append(text[2:])
            continue
        parts = text.split(" ")
        if len(parts) >= 9 and parts[0] in {"1", "2", "u"}:
            paths.append(parts[-1])
    return sorted(dict.fromkeys(path.replace("\\", "/") for path in paths))


def git_changed_paths(repo_root: str | Path) -> list[str]:
    result = subprocess.run(
        ["git", "status", "--porcelain=v2", "-z", "--untracked-files=all"],
        cwd=str(repo_root),
        capture_output=True,
        check=True,
    )
    return parse_porcelain_v2_z(result.stdout)
