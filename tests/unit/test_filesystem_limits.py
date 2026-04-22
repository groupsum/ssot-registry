from __future__ import annotations

import json
import unittest
from pathlib import Path

from ssot_registry.api import validate_registry
from ssot_registry.util.jsonio import stable_json_dumps
from tests.helpers import temp_repo_from_fixture


class FilesystemLimitsTests(unittest.TestCase):
    def test_rejects_ssot_path_longer_than_max(self) -> None:
        temp_dir = temp_repo_from_fixture("repo_valid")
        self.addCleanup(temp_dir.cleanup)
        repo = Path(temp_dir.name) / "repo"
        registry_path = repo / ".ssot" / "registry.json"
        registry = json.loads(registry_path.read_text(encoding="utf-8"))

        long_path = ".ssot/evidence/" + "/".join(["segment1234567890"] * 14) + "/ok.txt"
        target = repo / long_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("ok", encoding="utf-8")

        registry["evidence"][0]["path"] = long_path
        registry_path.write_text(stable_json_dumps(registry), encoding="utf-8")

        report = validate_registry(repo)
        self.assertFalse(report["passed"])
        self.assertIn("exceeds max .ssot path length 240", "\n".join(report["failures"]))

    def test_rejects_ssot_filename_longer_than_max(self) -> None:
        temp_dir = temp_repo_from_fixture("repo_valid")
        self.addCleanup(temp_dir.cleanup)
        repo = Path(temp_dir.name) / "repo"
        registry_path = repo / ".ssot" / "registry.json"
        registry = json.loads(registry_path.read_text(encoding="utf-8"))

        long_name = "b" * 121
        filename = f"{long_name}.txt"
        long_filename_path = f".ssot/evidence/{filename}"
        target = repo / long_filename_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("ok", encoding="utf-8")

        registry["evidence"][0]["path"] = long_filename_path
        registry_path.write_text(stable_json_dumps(registry), encoding="utf-8")

        report = validate_registry(repo)
        self.assertFalse(report["passed"])
        self.assertIn("exceeds max .ssot filename length 120", "\n".join(report["failures"]))


if __name__ == "__main__":
    unittest.main()
