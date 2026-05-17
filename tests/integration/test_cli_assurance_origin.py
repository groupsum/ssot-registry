from __future__ import annotations

import json
import unittest
from pathlib import Path

from tests.helpers import run_cli, temp_repo_from_fixture


class CliAssuranceOriginTests(unittest.TestCase):
    def test_feature_origin_create_update_and_list_filter(self) -> None:
        temp_dir = temp_repo_from_fixture("repo_valid")
        self.addCleanup(temp_dir.cleanup)
        repo = Path(temp_dir.name) / "repo"

        create = run_cli(
            "feature",
            "create",
            str(repo),
            "--id",
            "feat:origin.cli",
            "--title",
            "Origin CLI feature",
            "--description",
            "created through origin-aware CLI",
            "--origin",
            "repo-local",
        )
        self.assertEqual(create.returncode, 0, create.stderr)
        self.assertEqual("repo-local", json.loads(create.stdout)["entity"]["origin"])

        listed = run_cli("feature", "list", str(repo), "--origin", "repo-local")
        self.assertEqual(listed.returncode, 0, listed.stderr)
        ids = {row["id"] for row in json.loads(listed.stdout)}
        self.assertIn("feat:origin.cli", ids)

        rejected = run_cli(
            "feature",
            "create",
            str(repo),
            "--id",
            "feat:origin.forbidden",
            "--title",
            "Forbidden origin feature",
            "--description",
            "repo-local cannot author ssot-core rows",
            "--origin",
            "ssot-core",
        )
        self.assertNotEqual(rejected.returncode, 0)
        self.assertIn("cannot use origin ssot-core", rejected.stdout + rejected.stderr)

    def test_claim_test_and_evidence_origin_create(self) -> None:
        temp_dir = temp_repo_from_fixture("repo_valid")
        self.addCleanup(temp_dir.cleanup)
        repo = Path(temp_dir.name) / "repo"
        (repo / "tests" / "test_origin_cli.py").write_text("def test_origin_cli():\n    assert True\n", encoding="utf-8")
        (repo / ".ssot" / "evidence" / "origin-cli.json").write_text("{}", encoding="utf-8")

        claim = run_cli(
            "claim",
            "create",
            str(repo),
            "--id",
            "clm:origin.cli.t1",
            "--title",
            "Origin CLI claim",
            "--kind",
            "conformance",
            "--description",
            "origin-aware claim",
            "--origin",
            "repo-local",
        )
        self.assertEqual(claim.returncode, 0, claim.stderr)

        test = run_cli(
            "test",
            "create",
            str(repo),
            "--id",
            "tst:origin.cli",
            "--title",
            "Origin CLI test",
            "--kind",
            "pytest",
            "--test-path",
            "tests/test_origin_cli.py",
            "--feature-ids",
            "feat:rfc.9000.connection-migration",
            "--claim-ids",
            "clm:rfc.9000.connection-migration.t3",
            "--evidence-ids",
            "evd:t3.rfc.9000.connection-migration.bundle",
            "--origin",
            "repo-local",
        )
        self.assertEqual(test.returncode, 0, test.stderr)

        evidence = run_cli(
            "evidence",
            "create",
            str(repo),
            "--id",
            "evd:origin.cli",
            "--title",
            "Origin CLI evidence",
            "--kind",
            "report",
            "--evidence-path",
            ".ssot/evidence/origin-cli.json",
            "--claim-ids",
            "clm:rfc.9000.connection-migration.t3",
            "--test-ids",
            "tst:pytest.rfc.9000.connection-migration",
            "--origin",
            "repo-local",
        )
        self.assertEqual(evidence.returncode, 0, evidence.stderr)

        self.assertEqual("repo-local", json.loads(claim.stdout)["entity"]["origin"])
        self.assertEqual("repo-local", json.loads(test.stdout)["entity"]["origin"])
        self.assertEqual("repo-local", json.loads(evidence.stdout)["entity"]["origin"])


if __name__ == "__main__":
    unittest.main()
