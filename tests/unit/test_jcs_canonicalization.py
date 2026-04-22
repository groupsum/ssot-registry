from __future__ import annotations

import json
import unittest
from pathlib import Path

from ssot_registry.api import validate_registry
from ssot_registry.util.jcs import dump_jcs_json
from ssot_registry.util.jsonio import save_json
from tests.helpers import temp_repo_from_fixture, workspace_tempdir


class JcsCanonicalizationTests(unittest.TestCase):
    def test_validate_registry_rejects_non_canonical_ssot_json(self) -> None:
        temp_dir = temp_repo_from_fixture("repo_valid")
        self.addCleanup(temp_dir.cleanup)
        repo = Path(temp_dir.name) / "repo"

        registry_path = repo / ".ssot" / "registry.json"
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
        registry_path.write_text(json.dumps(registry, indent=2) + "\n", encoding="utf-8")

        report = validate_registry(repo)
        self.assertFalse(report["passed"])
        self.assertIn(
            "JSON under .ssot must be RFC 8785 JCS canonical: .ssot/registry.json",
            "\n".join(report["failures"]),
        )

    def test_save_json_writes_jcs_canonical_output(self) -> None:
        with workspace_tempdir() as temp_dir:
            target = Path(temp_dir) / "sample.json"
            payload = {"b": 1, "a": {"z": True, "x": "ok"}}

            save_json(target, payload)

            text = target.read_text(encoding="utf-8")
            self.assertEqual(text, dump_jcs_json(payload))
            self.assertEqual(text, '{"a":{"x":"ok","z":true},"b":1}')


if __name__ == "__main__":
    unittest.main()
