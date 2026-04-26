from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
for path in (
    REPO_ROOT / "pkgs" / "ssot-core" / "src",
    REPO_ROOT / "pkgs" / "ssot-contracts" / "src",
    REPO_ROOT / "pkgs" / "ssot-conformance" / "src",
):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from ssot_conformance.evidence import build_evidence_output, write_evidence_output


class ConformanceEvidenceOutputTests(unittest.TestCase):
    def test_evidence_output_is_machine_readable_json(self) -> None:
        payload = build_evidence_output(
            repo_root="repo-root",
            selected_profiles=["registry"],
            selected_families=["registry"],
            cases=[{"nodeid": "case::one", "family": "registry", "outcome": "passed"}],
        )
        self.assertEqual(payload["summary"]["passed"], 1)
        self.assertEqual(payload["summary"]["total"], 1)

    def test_write_evidence_output_persists_json(self) -> None:
        temp_path = REPO_ROOT / ".tmp_test_runs" / "conformance-evidence.json"
        payload = build_evidence_output(
            repo_root="repo-root",
            selected_profiles=["registry"],
            selected_families=["registry"],
            cases=[{"nodeid": "case::one", "family": "registry", "outcome": "passed"}],
        )
        written = write_evidence_output(temp_path, payload)
        loaded = json.loads(Path(written).read_text(encoding="utf-8"))
        self.assertEqual(loaded["repo_root"], "repo-root")


if __name__ == "__main__":
    unittest.main()
