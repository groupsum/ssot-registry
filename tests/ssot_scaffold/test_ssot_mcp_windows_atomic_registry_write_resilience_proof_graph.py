from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import patch

from ssot_registry.util.jsonio import load_json, stable_json_dumps
from ssot_registry.util.registry_lock import save_registry_json_locked


def test_windows_transient_replace_failure_is_retried(tmp_path: Path) -> None:
    registry_path = tmp_path / ".ssot" / "registry.json"
    registry_path.parent.mkdir(parents=True, exist_ok=True)
    registry_path.write_text(stable_json_dumps({"schema_version": "0.3.0", "repo": {"id": "repo:old"}}), encoding="utf-8")
    original_replace = os.replace
    attempts = {"count": 0}

    def flaky_replace(source: str, target: Path) -> None:
        attempts["count"] += 1
        if attempts["count"] == 1:
            error = PermissionError("access denied")
            error.winerror = 5  # type: ignore[attr-defined]
            raise error
        original_replace(source, target)

    with patch("ssot_registry.util.registry_lock.os.replace", side_effect=flaky_replace):
        save_registry_json_locked(registry_path, {"schema_version": "0.3.0", "repo": {"id": "repo:new"}})

    assert attempts["count"] == 2
    assert load_json(registry_path)["repo"]["id"] == "repo:new"
