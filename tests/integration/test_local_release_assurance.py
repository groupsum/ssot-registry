from __future__ import annotations

import json
import unittest
from pathlib import Path

from ssot_registry.api import (
    build_artifact_manifest,
    build_local_evidence_bundle,
    build_source_snapshot,
    deterministic_root_hash,
    verify_local_release,
)
from ssot_registry.util.fs import sha256_path
from tests.helpers import run_cli, workspace_tempdir


class LocalReleaseAssuranceTests(unittest.TestCase):
    def test_source_snapshot_path_policy_and_deterministic_root_hash_detect_file_drift(self) -> None:
        with workspace_tempdir() as temp_dir:
            repo = Path(temp_dir) / "repo"
            repo.mkdir()
            init = run_cli("init", str(repo), "--repo-id", "repo:local-assurance-source", "--repo-name", "local-assurance-source", "--version", "1.0.0")
            self.assertEqual(init.returncode, 0, init.stderr)
            governed = repo / "governed.txt"
            governed.write_text("first\n", encoding="utf-8")

            snapshot = build_source_snapshot(str(repo), path_policy="declared", extra_paths=["governed.txt"])["snapshot"]
            self.assertIn("governed.txt", snapshot["file_hashes"])
            self.assertEqual(snapshot["root_hash"], deterministic_root_hash(snapshot["file_hashes"]))
            first_hash = snapshot["root_hash"]

            governed.write_text("second\n", encoding="utf-8")
            changed = build_source_snapshot(str(repo), path_policy="declared", extra_paths=["governed.txt"])["snapshot"]
            self.assertNotEqual(first_hash, changed["root_hash"])

            full_repo = build_source_snapshot(str(repo), path_policy="full-repo")["snapshot"]
            self.assertIn("governed.txt", full_repo["file_hashes"])

    def test_artifact_manifest_validates_paths_hashes_required_fields_and_duplicates(self) -> None:
        with workspace_tempdir() as temp_dir:
            repo = Path(temp_dir) / "repo"
            repo.mkdir()
            init = run_cli("init", str(repo), "--repo-id", "repo:local-assurance-artifacts", "--repo-name", "local-assurance-artifacts", "--version", "1.0.0")
            self.assertEqual(init.returncode, 0, init.stderr)
            artifact = repo / "dist" / "artifact.txt"
            artifact.parent.mkdir()
            artifact.write_text("artifact\n", encoding="utf-8")

            manifest = build_artifact_manifest(
                str(repo),
                artifacts=[{"id": "artifact", "path": "dist/artifact.txt", "kind": "text", "media_type": "text/plain"}],
            )
            self.assertTrue(manifest["passed"], manifest)
            self.assertEqual(manifest["manifest"]["artifacts"][0]["sha256"], sha256_path(artifact))

            duplicate = build_artifact_manifest(
                str(repo),
                artifacts=[
                    {"id": "artifact", "path": "dist/artifact.txt"},
                    {"id": "artifact", "path": "dist/artifact.txt"},
                    {"id": "missing", "path": "dist/missing.txt"},
                    {"id": "bad-hash", "path": "dist/artifact.txt", "sha256": "0" * 64},
                ],
            )
            self.assertFalse(duplicate["passed"])
            self.assertIn("duplicate artifact id artifact", duplicate["failures"])
            self.assertTrue(any("path does not exist" in failure for failure in duplicate["failures"]))
            self.assertIn("artifact bad-hash sha256 mismatch", duplicate["failures"])

    def test_local_release_evidence_bundle_and_verification_report_are_canonical_outputs(self) -> None:
        with workspace_tempdir() as temp_dir:
            repo = Path(temp_dir) / "repo"
            repo.mkdir()
            init = run_cli("init", str(repo), "--repo-id", "repo:local-assurance-bundle", "--repo-name", "local-assurance-bundle", "--version", "1.0.0")
            self.assertEqual(init.returncode, 0, init.stderr)

            source = build_source_snapshot(str(repo), path_policy="ssot-only")["snapshot"]
            artifact_manifest = build_artifact_manifest(
                str(repo),
                artifacts=[{"id": "registry", "path": ".ssot/registry.json", "kind": "registry", "media_type": "application/json"}],
            )["manifest"]
            bundle = build_local_evidence_bundle(str(repo), source_snapshot=source, artifact_manifest=artifact_manifest)
            self.assertTrue(bundle["passed"])
            self.assertEqual(bundle["bundle"]["source_snapshot_root_hash"], source["root_hash"])
            bundle_path = Path(bundle["output_path"])
            self.assertTrue(bundle_path.exists())

            report = verify_local_release(str(repo), path_policy="ssot-only", blocking=True)
            self.assertTrue(report["passed"], report)
            self.assertTrue(report["blocking"])
            self.assertEqual(report["bundle_hash"], json.loads(Path(report["artifact_paths"]["evidence_bundle"]).read_text(encoding="utf-8"))["bundle_hash"])
            self.assertTrue((repo / ".ssot" / "reports" / "local-release-verification.report.json").exists())

    def test_release_verify_local_cli_emits_report_and_artifact_paths(self) -> None:
        with workspace_tempdir() as temp_dir:
            repo = Path(temp_dir) / "repo"
            repo.mkdir()
            init = run_cli("init", str(repo), "--repo-id", "repo:local-assurance-cli", "--repo-name", "local-assurance-cli", "--version", "1.0.0")
            self.assertEqual(init.returncode, 0, init.stderr)

            result = run_cli("release", "verify-local", str(repo), "--path-policy", "ssot-only", "--blocking")
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertTrue(payload["passed"], payload)
            self.assertEqual(payload["path_policy"], "ssot-only")
            self.assertIn("source_snapshot", payload["artifact_paths"])
            self.assertTrue((repo / ".ssot" / "reports" / "local-release-verification.report.json").exists())


if __name__ == "__main__":
    unittest.main()
