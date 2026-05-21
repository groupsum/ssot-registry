from __future__ import annotations

import json
from pathlib import Path

from tests.helpers import run_cli, temp_repo_from_fixture


def test_feature_create_can_scaffold_a_valid_proof_graph() -> None:
    temp_dir = temp_repo_from_fixture("repo_valid")
    try:
        repo = Path(temp_dir.name) / "repo"
        create = run_cli(
            "feature",
            "create",
            str(repo),
            "--id",
            "feat:cli.proof-graph-smoke",
            "--title",
            "CLI proof graph smoke",
            "--description",
            "prove CLI can author a linked proof graph in one transaction",
            "--implementation-status",
            "partial",
            "--horizon",
            "current",
            "--claim-tier",
            "T2",
            "--auto-scaffold-proof-graph",
        )
        assert create.returncode == 0, create.stderr
        payload = json.loads(create.stdout)
        assert payload["passed"] is True
        assert payload["scaffolded"]["test_id"] == "tst:pytest.cli.proof-graph-smoke.proof-graph"
        assert (repo / payload["scaffolded"]["test_path"]).exists()
        assert (repo / payload["scaffolded"]["evidence_path"]).exists()
    finally:
        temp_dir.cleanup()
