from __future__ import annotations

import json
from pathlib import Path

from tests.helpers import run_cli, temp_repo_from_fixture


def test_ssot_evidence_release_certification_feedback_proof_graph() -> None:
    temp_dir = temp_repo_from_fixture("repo_valid")
    try:
        repo = Path(temp_dir.name) / "repo"
        certify = run_cli("release", "certify", str(repo), "--release-id", "rel:1.2.0", "--write-report")
        assert certify.returncode == 0, certify.stderr

        registry = json.loads((repo / ".ssot" / "registry.json").read_text(encoding="utf-8"))
        evidence = next(row for row in registry["evidence"] if row["id"] == "evd:t3.rfc.9000.connection-migration.bundle")
        assert evidence["release_context"]["release_id"] == "rel:1.2.0"
        assert evidence["release_context"]["boundary_ids"] == ["bnd:2026q2.core"]
        assert evidence["release_context"]["verification_report_result"] == "certified"
        assert evidence["release_context"]["blocking_issue_result"] == "clear"
        assert evidence["release_context"]["blocking_risk_result"] == "clear"
        assert (repo / ".ssot" / "reports" / "certification.report.json").exists()
    finally:
        temp_dir.cleanup()
