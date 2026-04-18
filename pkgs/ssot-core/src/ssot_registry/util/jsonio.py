from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def stable_json_dumps(data: Any) -> str:
    return json.dumps(data, indent=2, sort_keys=False) + "\n"


def load_json(path: str | Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def save_json(path: str | Path, data: Any) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(stable_json_dumps(data), encoding="utf-8")
