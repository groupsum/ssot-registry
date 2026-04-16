from __future__ import annotations

import json
import unittest
from pathlib import Path

from tests.helpers import run_cli, temp_repo_from_fixture, workspace_tempdir


class CliFlagCoverageMatrixTests(unittest.TestCase):
    def test_cli_flag_coverage_matrix(self) -> None:
        manifest = self._load_manifest()
        matrix = self._build_coverage_matrix()

        self.assertEqual(set(manifest), set(matrix), "Coverage matrix command paths must match manifest command paths.")

        for command_path, declared in manifest.items():
            declared_flags = set(declared["flags"])
            tested_flags = set(matrix[command_path]["tested_flags"])
            missing = sorted(declared_flags - tested_flags)
            self.assertFalse(missing, f"Missing tested flags for '{command_path}': {missing}")

        for command_path, coverage in matrix.items():
            for case in coverage["cases"]:
                self._run_case(command_path, case)

    def _load_manifest(self) -> dict[str, dict[str, list[str]]]:
        manifest_path = Path(__file__).resolve().parents[1] / "fixtures" / "cli_surface_manifest.json"
        return json.loads(manifest_path.read_text(encoding="utf-8"))

    def _build_coverage_matrix(self) -> dict[str, dict[str, object]]:
        return {
            "issue create": {
                "tested_flags": [
                    "--id",
                    "--title",
                    "--status",
                    "--severity",
                    "--description",
                    "--horizon",
                    "--slot",
                    "--feature-ids",
                    "--claim-ids",
                    "--test-ids",
                    "--evidence-ids",
                    "--risk-ids",
                    "--release-blocking",
                    "--no-release-blocking",
                ],
                "cases": [
                    {
                        "builder": self._build_repo_valid_with_issue_dependencies,
                        "args": [
                            "issue",
                            "create",
                            "{repo}",
                            "--id",
                            "iss:matrix.flags",
                            "--title",
                            "Issue coverage",
                            "--status",
                            "in_progress",
                            "--severity",
                            "high",
                            "--description",
                            "matrix",
                            "--horizon",
                            "explicit",
                            "--slot",
                            "sprint-42",
                            "--feature-ids",
                            "feat:rfc.9000.connection-migration",
                            "--claim-ids",
                            "clm:rfc.9000.connection-migration.t3",
                            "--test-ids",
                            "tst:pytest.rfc.9000.connection-migration",
                            "--evidence-ids",
                            "evd:t3.rfc.9000.connection-migration.bundle",
                            "--risk-ids",
                            "rsk:rfc.9000.black-hole",
                            "--release-blocking",
                        ],
                    },
                    {
                        "builder": self._build_repo_valid,
                        "args": [
                            "issue",
                            "create",
                            "{repo}",
                            "--id",
                            "iss:matrix.no_release_blocking",
                            "--title",
                            "Issue coverage no release blocking",
                            "--no-release-blocking",
                        ],
                    },
                ],
            },
            "risk update": {
                "tested_flags": [
                    "--id",
                    "--title",
                    "--severity",
                    "--description",
                    "--release-blocking",
                    "--no-release-blocking",
                ],
                "cases": [
                    {
                        "builder": self._build_repo_valid_with_risk,
                        "args": [
                            "risk",
                            "update",
                            "{repo}",
                            "--id",
                            "rsk:matrix.flags",
                            "--title",
                            "Risk coverage updated",
                            "--severity",
                            "critical",
                            "--description",
                            "risk matrix",
                            "--release-blocking",
                        ],
                    },
                    {
                        "builder": self._build_repo_valid_with_risk,
                        "args": [
                            "risk",
                            "update",
                            "{repo}",
                            "--id",
                            "rsk:matrix.flags",
                            "--no-release-blocking",
                        ],
                    },
                ],
            },
            "spec reserve create": {
                "tested_flags": ["--name", "--start", "--end"],
                "cases": [
                    {
                        "builder": self._build_initialized_repo,
                        "args": ["spec", "reserve", "create", "{repo}", "--name", "local-spec", "--start", "5000", "--end", "5099"],
                    }
                ],
            },
            "spec create": {
                "tested_flags": ["--title", "--slug", "--body-file", "--number", "--origin", "--kind", "--status", "--note", "--reserve-range"],
                "cases": [
                    {
                        "builder": self._build_repo_with_spec_reservation,
                        "args": [
                            "spec",
                            "create",
                            "{repo}",
                            "--title",
                            "Matrix spec",
                            "--slug",
                            "matrix-spec",
                            "--body-file",
                            "{spec_body}",
                            "--number",
                            "5000",
                            "--origin",
                            "repo-local",
                            "--kind",
                            "operational",
                            "--status",
                            "in_review",
                            "--note",
                            "matrix",
                            "--reserve-range",
                            "local-spec",
                        ],
                    }
                ],
            },
            "adr reserve create": {
                "tested_flags": ["--name", "--start", "--end"],
                "cases": [
                    {
                        "builder": self._build_initialized_repo,
                        "args": ["adr", "reserve", "create", "{repo}", "--name", "local-adr", "--start", "5000", "--end", "5099"],
                    }
                ],
            },
            "adr create": {
                "tested_flags": ["--title", "--slug", "--body-file", "--number", "--status", "--note", "--origin", "--reserve-range"],
                "cases": [
                    {
                        "builder": self._build_repo_with_adr_reservation,
                        "args": [
                            "adr",
                            "create",
                            "{repo}",
                            "--title",
                            "Matrix ADR",
                            "--slug",
                            "matrix-adr",
                            "--body-file",
                            "{adr_body}",
                            "--number",
                            "5000",
                            "--status",
                            "in_review",
                            "--note",
                            "matrix",
                            "--origin",
                            "repo-local",
                            "--reserve-range",
                            "local-adr",
                        ],
                    }
                ],
            },
            "feature lifecycle set": {
                "tested_flags": ["--ids", "--stage", "--replacement-feature-id", "--effective-release-id", "--note"],
                "cases": [
                    {
                        "builder": self._build_repo_with_replacement_feature,
                        "args": [
                            "feature",
                            "lifecycle",
                            "set",
                            "{repo}",
                            "--ids",
                            "feat:matrix.primary",
                            "--stage",
                            "deprecated",
                            "--replacement-feature-id",
                            "feat:matrix.replacement",
                            "--effective-release-id",
                            "rel:rfc.9000.v3",
                            "--note",
                            "matrix",
                        ],
                    }
                ],
            },
        }

    def _run_case(self, command_path: str, case: dict[str, object]) -> None:
        builder = case["builder"]
        assert callable(builder)
        temp_dir, substitutions = builder()  # type: ignore[misc]
        self.addCleanup(temp_dir.cleanup)

        argv = [arg.format(**substitutions) for arg in case["args"]]  # type: ignore[index]
        result = run_cli(*argv)
        self.assertEqual(result.returncode, 0, f"{command_path} failed:\nSTDOUT: {result.stdout}\nSTDERR: {result.stderr}")

    def _build_repo_valid(self) -> tuple[object, dict[str, str]]:
        temp_dir = temp_repo_from_fixture("repo_valid")
        repo = Path(temp_dir.name) / "repo"
        return temp_dir, {"repo": str(repo)}


    def _build_repo_valid_with_issue_dependencies(self) -> tuple[object, dict[str, str]]:
        temp_dir = temp_repo_from_fixture("repo_valid")
        repo = Path(temp_dir.name) / "repo"

        risk = run_cli(
            "risk",
            "create",
            str(repo),
            "--id",
            "rsk:rfc.9000.black-hole",
            "--title",
            "Risk for issue matrix",
        )
        self.assertEqual(risk.returncode, 0, risk.stderr)

        return temp_dir, {"repo": str(repo)}
    def _build_repo_valid_with_risk(self) -> tuple[object, dict[str, str]]:
        temp_dir = temp_repo_from_fixture("repo_valid")
        repo = Path(temp_dir.name) / "repo"

        create = run_cli("risk", "create", str(repo), "--id", "rsk:matrix.flags", "--title", "Risk coverage seed")
        self.assertEqual(create.returncode, 0, create.stderr)
        return temp_dir, {"repo": str(repo)}

    def _build_initialized_repo(self) -> tuple[object, dict[str, str]]:
        temp_dir = workspace_tempdir()
        repo = Path(temp_dir.name) / "repo"
        repo.mkdir(parents=True, exist_ok=True)
        init = run_cli("init", str(repo), "--repo-id", "repo:matrix", "--repo-name", "matrix", "--version", "1.0.0")
        self.assertEqual(init.returncode, 0, init.stderr)
        return temp_dir, {"repo": str(repo)}

    def _build_repo_with_spec_reservation(self) -> tuple[object, dict[str, str]]:
        temp_dir, substitutions = self._build_initialized_repo()
        repo = Path(substitutions["repo"])
        spec_body = repo / "spec-body.md"
        spec_body.write_text("matrix spec body\n", encoding="utf-8")

        reserve = run_cli("spec", "reserve", "create", str(repo), "--name", "local-spec", "--start", "5000", "--end", "5099")
        self.assertEqual(reserve.returncode, 0, reserve.stderr)

        return temp_dir, {"repo": str(repo), "spec_body": str(spec_body)}

    def _build_repo_with_adr_reservation(self) -> tuple[object, dict[str, str]]:
        temp_dir, substitutions = self._build_initialized_repo()
        repo = Path(substitutions["repo"])
        adr_body = repo / "adr-body.md"
        adr_body.write_text("matrix adr body\n", encoding="utf-8")

        reserve = run_cli("adr", "reserve", "create", str(repo), "--name", "local-adr", "--start", "5000", "--end", "5099")
        self.assertEqual(reserve.returncode, 0, reserve.stderr)

        return temp_dir, {"repo": str(repo), "adr_body": str(adr_body)}

    def _build_repo_with_replacement_feature(self) -> tuple[object, dict[str, str]]:
        temp_dir = temp_repo_from_fixture("repo_valid")
        repo = Path(temp_dir.name) / "repo"

        primary = run_cli("feature", "create", str(repo), "--id", "feat:matrix.primary", "--title", "Primary feature")
        self.assertEqual(primary.returncode, 0, primary.stderr)

        replacement = run_cli("feature", "create", str(repo), "--id", "feat:matrix.replacement", "--title", "Replacement feature")
        self.assertEqual(replacement.returncode, 0, replacement.stderr)

        return temp_dir, {"repo": str(repo)}


if __name__ == "__main__":
    unittest.main()
