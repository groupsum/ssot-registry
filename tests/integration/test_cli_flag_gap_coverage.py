from __future__ import annotations

import json
import unittest
from pathlib import Path

from tests.helpers import run_cli, temp_repo_from_fixture


class CliFlagGapCoverageTests(unittest.TestCase):
    def test_manifest_includes_new_body_flags(self) -> None:
        manifest = json.loads((Path(__file__).resolve().parents[1] / "fixtures" / "cli_surface_manifest.json").read_text(encoding="utf-8"))
        self.assertIn("--body", manifest["flags_by_path"]["adr create"])
        self.assertIn("--body", manifest["flags_by_path"]["adr update"])
        self.assertIn("--body", manifest["flags_by_path"]["spec create"])
        self.assertIn("--body", manifest["flags_by_path"]["spec update"])

    def test_graph_and_registry_output_flags_write_requested_paths(self) -> None:
        temp_dir = temp_repo_from_fixture("repo_valid")
        self.addCleanup(temp_dir.cleanup)
        repo = Path(temp_dir.name) / "repo"

        registry_out = repo / ".ssot" / "exports" / "registry-output.toml"
        registry_result = run_cli("registry", "export", str(repo), "--format", "toml", f"--output={registry_out}")
        self.assertEqual(registry_result.returncode, 0, registry_result.stderr)
        self.assertTrue(registry_out.exists())

        graph_out = repo / ".ssot" / "graphs" / "registry-output.json"
        graph_result = run_cli("graph", "export", str(repo), "--format", "json", f"--output={graph_out}")
        self.assertEqual(graph_result.returncode, 0, graph_result.stderr)
        self.assertTrue(graph_out.exists())

    def test_feature_release_and_document_gap_flags_are_exercised(self) -> None:
        temp_dir = temp_repo_from_fixture("repo_valid")
        self.addCleanup(temp_dir.cleanup)
        repo = Path(temp_dir.name) / "repo"

        adr_body = repo / "adr.yaml"
        adr_body.write_text('body: |-\n  ADR body file.\n', encoding="utf-8")
        spec_body = repo / "spec.yaml"
        spec_body.write_text('body: |-\n  SPEC body file.\n', encoding="utf-8")

        reserve_adr = run_cli("adr", "reserve", "create", str(repo), "--name", "origin:adr-gap", "--start", "5300", "--end", "5399")
        self.assertEqual(reserve_adr.returncode, 0, reserve_adr.stderr)
        reserve_spec = run_cli("spec", "reserve", "create", str(repo), "--name", "origin:spec-gap", "--start", "5400", "--end", "5499")
        self.assertEqual(reserve_spec.returncode, 0, reserve_spec.stderr)

        adr_create = run_cli(
            "adr",
            "create",
            str(repo),
            "--title",
            "Gap ADR",
            "--slug",
            "gap-adr",
            "--body-file",
            str(adr_body),
            "--note",
            "gap note",
            "--origin",
            "repo-local",
            "--reserve-range",
            "origin:adr-gap",
        )
        self.assertEqual(adr_create.returncode, 0, adr_create.stderr)

        adr_update = run_cli("adr", "update", str(repo), "--id", "adr:5300", "--status", "accepted", "--note", "accepted now")
        self.assertEqual(adr_update.returncode, 0, adr_update.stderr)

        spec_create = run_cli(
            "spec",
            "create",
            str(repo),
            "--title",
            "Gap SPEC",
            "--slug",
            "gap-spec",
            "--body-file",
            str(spec_body),
            "--origin",
            "repo-local",
            "--note",
            "spec note",
            "--reserve-range",
            "origin:spec-gap",
            "--kind",
            "operational",
        )
        self.assertEqual(spec_create.returncode, 0, spec_create.stderr)

        spec_body_2 = repo / "spec-2.yaml"
        spec_body_2.write_text('body: |-\n  SPEC replacement body.\n', encoding="utf-8")
        spec_update = run_cli(
            "spec",
            "update",
            str(repo),
            "--id",
            "spc:5400",
            "--body-file",
            str(spec_body_2),
            "--kind",
            "governance",
            "--status",
            "accepted",
            "--note",
            "updated",
        )
        self.assertEqual(spec_update.returncode, 0, spec_update.stderr)

        shared_claim_id = "clm:rfc.9000.connection-migration.t3"
        shared_test_id = "tst:pytest.rfc.9000.connection-migration"
        shared_evidence_id = "evd:t3.rfc.9000.connection-migration.bundle"

        replacement_create = run_cli(
            "feature",
            "create",
            str(repo),
            "--id",
            "feat:gap.replacement",
            "--title",
            "Gap replacement feature",
            "--implementation-status",
            "implemented",
            "--horizon",
            "current",
            "--claim-tier",
            "T1",
            "--claim-ids",
            shared_claim_id,
            "--test-ids",
            shared_test_id,
        )
        self.assertEqual(replacement_create.returncode, 0, replacement_create.stderr)

        feature_create = run_cli(
            "feature",
            "create",
            str(repo),
            "--id",
            "feat:gap.demo",
            "--title",
            "Gap demo feature",
            "--description",
            "Feature gap coverage",
            "--implementation-status",
            "implemented",
            "--lifecycle-stage",
            "deprecated",
            "--replacement-feature-id",
            "feat:gap.replacement",
            "--note",
            "sunsetting",
            "--horizon",
            "explicit",
            "--claim-tier",
            "T1",
            "--target-lifecycle-stage",
            "deprecated",
            "--slot",
            "r1",
            "--claim-ids",
            shared_claim_id,
            "--test-ids",
            shared_test_id,
        )
        self.assertEqual(feature_create.returncode, 0, feature_create.stderr)

        feature_lifecycle = run_cli(
            "feature",
            "lifecycle",
            "set",
            str(repo),
            "--ids",
            "feat:gap.demo",
            "--stage",
            "deprecated",
            "--replacement-feature-id",
            "feat:gap.replacement",
            "--effective-release-id",
            "rel:1.2.0",
        )
        self.assertEqual(feature_lifecycle.returncode, 0, feature_lifecycle.stderr)

        feature_link = run_cli("feature", "link", str(repo), "--id", "feat:gap.demo", "--requires", "feat:gap.replacement")
        self.assertEqual(feature_link.returncode, 0, feature_link.stderr)

        feature_update = run_cli("feature", "update", str(repo), "--id", "feat:gap.demo", "--description", "Updated description")
        self.assertEqual(feature_update.returncode, 0, feature_update.stderr)

        release_create = run_cli(
            "release",
            "create",
            str(repo),
            "--id",
            "rel:gap.1",
            "--version",
            "1.0.1",
            "--boundary-id",
            "bnd:2026q2.core",
            "--status",
            "candidate",
            "--claim-ids",
            shared_claim_id,
            "--evidence-ids",
            shared_evidence_id,
        )
        self.assertEqual(release_create.returncode, 0, release_create.stderr)

        release_update = run_cli("release", "update", str(repo), "--id", "rel:gap.1", "--version", "1.0.2")
        self.assertEqual(release_update.returncode, 0, release_update.stderr)
