from __future__ import annotations

import json
from pathlib import Path

from tests.helpers import run_cli, temp_repo_from_fixture


def test_ssot_cli_proof_graph_certification_flow_proof_graph() -> None:
    temp_dir = temp_repo_from_fixture("repo_valid")
    try:
        repo = Path(temp_dir.name) / "repo"
        create = run_cli(
            "feature",
            "create",
            str(repo),
            "--id",
            "feat:ssot-scaffold.proof-graph",
            "--title",
            "SSOT scaffold proof graph",
            "--description",
            "scaffolded feature used by the governed proof test",
            "--implementation-status",
            "absent",
            "--horizon",
            "next",
            "--claim-tier",
            "T3",
            "--auto-scaffold-proof-graph",
        )
        assert create.returncode == 0, create.stderr
        create_payload = json.loads(create.stdout)
        test_path = repo / create_payload["scaffolded"]["test_path"]
        test_path.write_text("def test_ssot_scaffold_placeholder():\n    assert True\n", encoding="utf-8")

        certify = run_cli(
            "feature",
            "certify-proof-graph",
            str(repo),
            "--ids",
            "feat:ssot-scaffold.proof-graph",
            "--boundary-id",
            "bnd:ssot-scaffold.proof-graph",
            "--boundary-title",
            "SSOT scaffold proof graph boundary",
            "--release-id",
            "rel:ssot-scaffold.proof-graph",
            "--release-version",
            "1.0.0",
            "--robustness-dimensions",
            "negative_cases",
            "state_transitions",
            "--write-report",
            "--promote",
            "--publish",
        )
        assert certify.returncode == 0, certify.stderr
        payload = json.loads(certify.stdout)
        assert payload["passed"] is True

        registry = json.loads((repo / ".ssot" / "registry.json").read_text(encoding="utf-8"))
        feature = next(row for row in registry["features"] if row["id"] == "feat:ssot-scaffold.proof-graph")
        release = next(row for row in registry["releases"] if row["id"] == "rel:ssot-scaffold.proof-graph")
        t3_evidence = next(row for row in registry["evidence"] if row["id"] == "evd:t3.ssot-scaffold.proof-graph.proof-graph")

        assert feature["implementation_status"] == "implemented"
        assert feature["plan"]["horizon"] == "current"
        assert release["status"] == "published"
        assert t3_evidence["release_context"]["verification_report_result"] == "certified"
        assert (repo / ".ssot" / "reports" / "certification.report.json").exists()
        assert (repo / ".ssot" / "releases" / "rel__ssot-scaffold.proof-graph" / "published.snapshot.json").exists()
    finally:
        temp_dir.cleanup()
