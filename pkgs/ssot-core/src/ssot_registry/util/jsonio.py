from __future__ import annotations

from pathlib import Path
from typing import Any

from ssot_registry.util.jcs import dump_jcs_json, load_jcs_json

def stable_json_dumps(data: Any) -> str:
    return dump_jcs_json(data)


def load_json(path: str | Path) -> Any:
    target = Path(path)
    return load_jcs_json(target.read_text(encoding="utf-8"), source=target.as_posix())


def save_json(path: str | Path, data: Any) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(stable_json_dumps(data), encoding="utf-8")
