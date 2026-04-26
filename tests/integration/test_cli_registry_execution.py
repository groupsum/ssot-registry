from __future__ import annotations

import json
import unittest
from pathlib import Path

from tests.helpers import run_cli, temp_repo_from_fixture, workspace_tempdir


def _execution_json(test_path: str) -> str:
    return json.dumps(
        {
            "mode": "command",
            "argv": ["python", "-m", "pytest", test_path, "-q"],
            "cwd": ".",
            "env": {},
            "timeout_seconds": 600,
            "success": {"type": "exit_code", "expected": 0},
        }
    )


class RegistryExecutionCliTests(unittest.TestCase):
    def test_test_run_executes_registry_owned_command_and_emits_evidence(self) -> None:
        temp_dir = temp_repo_from_fixture("repo_valid")
        self.addCleanup(temp_dir.cleanup)
        repo = Path(temp_dir.name) / "repo"
        evidence_path = repo / ".ssot" / "evidence" / "runs" / "test-run.json"

        result = run_cli(
            "test",
            "run",
            str(repo),
            "--id",
            "tst:pytest.rfc.9000.connection-migration",
            "--evidence-output",
            str(evidence_path),
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["passed"], payload)
        self.assertEqual(payload["target"]["kind"], "test")
        self.assertEqual(payload["summary"]["passed"], 1)

        evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
        self.assertEqual(evidence["target"]["kind"], "test")
        self.assertEqual(evidence["resolved_test_ids"], ["tst:pytest.rfc.9000.connection-migration"])
        self.assertEqual(evidence["cases"][0]["command"][1:3], ["-m", "pytest"])

    def test_test_run_dry_run_resolves_without_execution(self) -> None:
        temp_dir = temp_repo_from_fixture("repo_valid")
        self.addCleanup(temp_dir.cleanup)
        repo = Path(temp_dir.name) / "repo"

        result = run_cli(
            "test",
            "run",
            str(repo),
            "--id",
            "tst:pytest.rfc.9000.connection-migration",
            "--dry-run",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["dry_run"], payload)
        self.assertEqual(payload["resolved_tests"][0]["id"], "tst:pytest.rfc.9000.connection-migration")

    def test_test_run_fails_closed_without_execution_metadata(self) -> None:
        temp_dir = temp_repo_from_fixture("repo_valid")
        self.addCleanup(temp_dir.cleanup)
        repo = Path(temp_dir.name) / "repo"

        generated_path = repo / "tests" / "test_no_execution_metadata.py"
        generated_path.write_text("def test_no_execution_metadata():\n    assert True\n", encoding="utf-8")

        create = run_cli(
            "test",
            "create",
            str(repo),
            "--id",
            "tst:pytest.cli.no-execution",
            "--title",
            "No execution metadata test",
            "--status",
            "planned",
            "--kind",
            "pytest",
            "--test-path",
            "tests/test_no_execution_metadata.py",
            "--feature-ids",
            "feat:rfc.9000.connection-migration",
            "--claim-ids",
            "clm:rfc.9000.connection-migration.t3",
            "--evidence-ids",
            "evd:t3.rfc.9000.connection-migration.bundle",
        )
        self.assertEqual(create.returncode, 0, create.stderr)

        result = run_cli("test", "run", str(repo), "--id", "tst:pytest.cli.no-execution")
        self.assertEqual(result.returncode, 1)
        self.assertIn("missing execution metadata", result.stdout)

    def test_spec_run_tests_resolves_via_feature_spec_ids(self) -> None:
        with workspace_tempdir() as temp_dir:
            repo = Path(temp_dir) / "repo"
            repo.mkdir()
            init = run_cli("init", str(repo), "--repo-id", "repo:spec-run", "--repo-name", "spec-run", "--version", "1.0.0")
            self.assertEqual(init.returncode, 0, init.stderr)

            spec_body = repo / "spec-body.yaml"
            spec_body.write_text('body: |-\n  SPEC body.\n', encoding="utf-8")
            create_spec = run_cli(
                "spec",
                "create",
                str(repo),
                "--title",
                "Spec run target",
                "--slug",
                "spec-run-target",
                "--body-file",
                str(spec_body),
                "--kind",
                "operational",
            )
            self.assertEqual(create_spec.returncode, 0, create_spec.stderr)

            test_path = repo / "tests" / "test_spec_run_target.py"
            test_path.parent.mkdir(parents=True, exist_ok=True)
            test_path.write_text("def test_spec_run_target():\n    assert True\n", encoding="utf-8")

            feature = run_cli(
                "feature",
                "create",
                str(repo),
                "--id",
                "feat:spec.run-target",
                "--title",
                "Spec run target feature",
                "--spec-ids",
                "spc:1000",
            )
            self.assertEqual(feature.returncode, 0, feature.stderr)

            evidence_artifact = repo / ".ssot" / "evidence" / "spec-run-target.json"
            evidence_artifact.parent.mkdir(parents=True, exist_ok=True)
            evidence_artifact.write_text("{}", encoding="utf-8")

            evidence = run_cli(
                "evidence",
                "create",
                str(repo),
                "--id",
                "evd:t1.spec.run-target",
                "--title",
                "Spec run target evidence",
                "--status",
                "passed",
                "--kind",
                "report",
                "--tier",
                "T1",
                "--evidence-path",
                ".ssot/evidence/spec-run-target.json",
            )
            self.assertEqual(evidence.returncode, 0, evidence.stderr)

            claim = run_cli(
                "claim",
                "create",
                str(repo),
                "--id",
                "clm:spec.run-target.t1",
                "--title",
                "Spec run target claim",
                "--status",
                "asserted",
                "--tier",
                "T1",
                "--kind",
                "conformance",
                "--description",
                "Spec-linked execution claim.",
                "--feature-ids",
                "feat:spec.run-target",
                "--evidence-ids",
                "evd:t1.spec.run-target",
            )
            self.assertEqual(claim.returncode, 0, claim.stderr)

            test_create = run_cli(
                "test",
                "create",
                str(repo),
                "--id",
                "tst:pytest.spec.run-target",
                "--title",
                "Spec run target test",
                "--status",
                "passing",
                "--kind",
                "pytest",
                "--test-path",
                "tests/test_spec_run_target.py",
                "--feature-ids",
                "feat:spec.run-target",
                "--claim-ids",
                "clm:spec.run-target.t1",
                "--evidence-ids",
                "evd:t1.spec.run-target",
                "--execution-json",
                _execution_json("tests/test_spec_run_target.py"),
            )
            self.assertEqual(test_create.returncode, 0, test_create.stderr)

            feature_link = run_cli(
                "feature",
                "link",
                str(repo),
                "--id",
                "feat:spec.run-target",
                "--claim-ids",
                "clm:spec.run-target.t1",
                "--test-ids",
                "tst:pytest.spec.run-target",
            )
            self.assertEqual(feature_link.returncode, 0, feature_link.stderr)

            test_link = run_cli(
                "test",
                "link",
                str(repo),
                "--id",
                "tst:pytest.spec.run-target",
                "--claim-ids",
                "clm:spec.run-target.t1",
            )
            self.assertEqual(test_link.returncode, 0, test_link.stderr)

            claim_link = run_cli(
                "claim",
                "link",
                str(repo),
                "--id",
                "clm:spec.run-target.t1",
                "--test-ids",
                "tst:pytest.spec.run-target",
            )
            self.assertEqual(claim_link.returncode, 0, claim_link.stderr)

            evidence_link = run_cli(
                "evidence",
                "link",
                str(repo),
                "--id",
                "evd:t1.spec.run-target",
                "--claim-ids",
                "clm:spec.run-target.t1",
                "--test-ids",
                "tst:pytest.spec.run-target",
            )
            self.assertEqual(evidence_link.returncode, 0, evidence_link.stderr)

            evidence_path = repo / ".ssot" / "evidence" / "runs" / "spec-run.json"
            result = run_cli(
                "spec",
                "run-tests",
                str(repo),
                "--id",
                "spc:1000",
                "--evidence-output",
                str(evidence_path),
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["target"]["kind"], "spec")
            self.assertEqual(payload["target"]["id"], "spc:1000")
            self.assertEqual(payload["summary"]["passed"], 1)
            self.assertEqual(json.loads(evidence_path.read_text(encoding="utf-8"))["resolved_test_ids"], ["tst:pytest.spec.run-target"])

    def test_boundary_run_tests_resolves_direct_and_profile_features(self) -> None:
        temp_dir = temp_repo_from_fixture("repo_valid")
        self.addCleanup(temp_dir.cleanup)
        repo = Path(temp_dir.name) / "repo"

        extra_test_path = repo / "tests" / "test_boundary_direct.py"
        extra_test_path.write_text("def test_boundary_direct():\n    assert True\n", encoding="utf-8")

        feature = run_cli(
            "feature",
            "create",
            str(repo),
            "--id",
            "feat:boundary.direct",
            "--title",
            "Boundary direct feature",
        )
        self.assertEqual(feature.returncode, 0, feature.stderr)

        evidence_artifact = repo / ".ssot" / "evidence" / "boundary-direct.json"
        evidence_artifact.parent.mkdir(parents=True, exist_ok=True)
        evidence_artifact.write_text("{}", encoding="utf-8")

        evidence = run_cli(
            "evidence",
            "create",
            str(repo),
            "--id",
            "evd:t1.boundary.direct",
            "--title",
            "Boundary direct evidence",
            "--status",
            "passed",
            "--kind",
            "report",
            "--tier",
            "T1",
            "--evidence-path",
            ".ssot/evidence/boundary-direct.json",
        )
        self.assertEqual(evidence.returncode, 0, evidence.stderr)

        claim = run_cli(
            "claim",
            "create",
            str(repo),
            "--id",
            "clm:boundary.direct.t1",
            "--title",
            "Boundary direct claim",
            "--status",
            "asserted",
            "--tier",
            "T1",
            "--kind",
            "conformance",
            "--description",
            "Boundary direct feature claim.",
            "--feature-ids",
            "feat:boundary.direct",
            "--evidence-ids",
            "evd:t1.boundary.direct",
        )
        self.assertEqual(claim.returncode, 0, claim.stderr)

        test_create = run_cli(
            "test",
            "create",
            str(repo),
            "--id",
            "tst:pytest.boundary.direct",
            "--title",
            "Boundary direct test",
            "--status",
            "passing",
            "--kind",
            "pytest",
            "--test-path",
            "tests/test_boundary_direct.py",
            "--feature-ids",
            "feat:boundary.direct",
            "--claim-ids",
            "clm:boundary.direct.t1",
            "--evidence-ids",
            "evd:t1.boundary.direct",
            "--execution-json",
            _execution_json("tests/test_boundary_direct.py"),
        )
        self.assertEqual(test_create.returncode, 0, test_create.stderr)

        feature_link = run_cli(
            "feature",
            "link",
            str(repo),
            "--id",
            "feat:boundary.direct",
            "--claim-ids",
            "clm:boundary.direct.t1",
            "--test-ids",
            "tst:pytest.boundary.direct",
        )
        self.assertEqual(feature_link.returncode, 0, feature_link.stderr)

        test_link = run_cli(
            "test",
            "link",
            str(repo),
            "--id",
            "tst:pytest.boundary.direct",
            "--claim-ids",
            "clm:boundary.direct.t1",
        )
        self.assertEqual(test_link.returncode, 0, test_link.stderr)

        claim_link = run_cli(
            "claim",
            "link",
            str(repo),
            "--id",
            "clm:boundary.direct.t1",
            "--test-ids",
            "tst:pytest.boundary.direct",
        )
        self.assertEqual(claim_link.returncode, 0, claim_link.stderr)

        evidence_link = run_cli(
            "evidence",
            "link",
            str(repo),
            "--id",
            "evd:t1.boundary.direct",
            "--claim-ids",
            "clm:boundary.direct.t1",
            "--test-ids",
            "tst:pytest.boundary.direct",
        )
        self.assertEqual(evidence_link.returncode, 0, evidence_link.stderr)

        profile = run_cli(
            "profile",
            "create",
            str(repo),
            "--id",
            "prf:boundary.profile",
            "--title",
            "Boundary profile",
            "--status",
            "active",
            "--feature-ids",
            "feat:rfc.9000.connection-migration",
        )
        self.assertEqual(profile.returncode, 0, profile.stderr)

        boundary = run_cli(
            "boundary",
            "create",
            str(repo),
            "--id",
            "bnd:registry-run",
            "--title",
            "Registry execution boundary",
            "--status",
            "active",
            "--feature-ids",
            "feat:boundary.direct",
            "--profile-ids",
            "prf:boundary.profile",
        )
        self.assertEqual(boundary.returncode, 0, boundary.stderr)

        evidence_path = repo / ".ssot" / "evidence" / "runs" / "boundary-run.json"
        result = run_cli(
            "boundary",
            "run-tests",
            str(repo),
            "--id",
            "bnd:registry-run",
            "--evidence-output",
            str(evidence_path),
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["target"]["kind"], "boundary")
        self.assertEqual(set(payload["target"]["feature_ids"]), {"feat:boundary.direct", "feat:rfc.9000.connection-migration"})
        self.assertEqual(payload["summary"]["passed"], 2)
        evidence_payload = json.loads(evidence_path.read_text(encoding="utf-8"))
        self.assertEqual(set(evidence_payload["resolved_test_ids"]), {"tst:pytest.boundary.direct", "tst:pytest.rfc.9000.connection-migration"})


if __name__ == "__main__":
    unittest.main()
