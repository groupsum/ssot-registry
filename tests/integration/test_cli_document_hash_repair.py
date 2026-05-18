from __future__ import annotations

import json
import unittest
from pathlib import Path

from tests.helpers import run_cli, workspace_tempdir


def _write_body(path: Path, body: str) -> None:
    path.write_text(f"body: |-\n  {body}\n", encoding="utf-8")


def _replace_document_body(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    updated = text.replace(old, new)
    if updated == text:
        raise AssertionError(f"{old!r} was not found in {path}")
    path.write_text(updated, encoding="utf-8", newline="\n")


class CliDocumentHashRepairTests(unittest.TestCase):
    def test_registry_repair_doc_hashes_fixes_multiple_stale_repo_local_documents(self) -> None:
        with workspace_tempdir() as temp_dir:
            repo = Path(temp_dir) / "repo"
            repo.mkdir()
            init = run_cli("init", str(repo), "--repo-id", "repo:doc-hash-repair", "--repo-name", "doc-hash-repair", "--version", "1.0.0")
            self.assertEqual(init.returncode, 0, init.stderr)

            adr_body = repo / "adr-body.yaml"
            spec_body = repo / "spec-body.yaml"
            _write_body(adr_body, "Original ADR body.")
            _write_body(spec_body, "Original SPEC body.")

            adr = run_cli("adr", "create", str(repo), "--title", "Repair ADR", "--slug", "repair-adr", "--body-file", str(adr_body))
            self.assertEqual(adr.returncode, 0, adr.stderr)
            spec_one = run_cli(
                "spec",
                "create",
                str(repo),
                "--title",
                "Repair SPEC one",
                "--slug",
                "repair-spec-one",
                "--body-file",
                str(spec_body),
                "--kind",
                "operational",
                "--adr-ids",
                "adr:1000",
            )
            self.assertEqual(spec_one.returncode, 0, spec_one.stderr)
            spec_two = run_cli(
                "spec",
                "create",
                str(repo),
                "--title",
                "Repair SPEC two",
                "--slug",
                "repair-spec-two",
                "--body-file",
                str(spec_body),
                "--kind",
                "operational",
                "--adr-ids",
                "adr:1000",
            )
            self.assertEqual(spec_two.returncode, 0, spec_two.stderr)

            adr_path = repo / ".ssot" / "adr" / "ADR-1000-repair-adr.yaml"
            spec_one_path = repo / ".ssot" / "specs" / "SPEC-1000-repair-spec-one.yaml"
            spec_two_path = repo / ".ssot" / "specs" / "SPEC-1001-repair-spec-two.yaml"
            _replace_document_body(adr_path, "Original ADR body.", "Current ADR body.")
            _replace_document_body(spec_one_path, "Original SPEC body.", "Current SPEC one body.")
            _replace_document_body(spec_two_path, "Original SPEC body.", "Current SPEC two body.")

            validate = run_cli("validate", str(repo))
            self.assertEqual(validate.returncode, 1)
            failures = "\n".join(json.loads(validate.stdout)["failures"])
            self.assertIn("adrs.adr:1000 content hash does not match file content", failures)
            self.assertIn("specs.spc:1000 content hash does not match file content", failures)
            self.assertIn("specs.spc:1001 content hash does not match file content", failures)

            blocked_feature = run_cli(
                "feature",
                "create",
                str(repo),
                "--id",
                "feat:blocked-by-stale-doc-hashes",
                "--title",
                "Blocked by stale document hashes",
            )
            self.assertEqual(blocked_feature.returncode, 1)
            self.assertIn("content hash does not match file content", blocked_feature.stdout)

            repair = run_cli(
                "registry",
                "repair-doc-hashes",
                str(repo),
                "--ids",
                "adr:1000",
                "spc:1000",
                "spc:1001",
            )
            self.assertEqual(repair.returncode, 0, repair.stderr)
            repair_payload = json.loads(repair.stdout)
            self.assertTrue(repair_payload["passed"], repair_payload)
            self.assertEqual([row["id"] for row in repair_payload["repaired"]], ["adr:1000", "spc:1000", "spc:1001"])

            validate_after = run_cli("validate", str(repo))
            self.assertEqual(validate_after.returncode, 0, validate_after.stderr)
            self.assertTrue(json.loads(validate_after.stdout)["passed"])

            unblocked_feature = run_cli(
                "feature",
                "create",
                str(repo),
                "--id",
                "feat:blocked-by-stale-doc-hashes",
                "--title",
                "Blocked by stale document hashes",
            )
            self.assertEqual(unblocked_feature.returncode, 0, unblocked_feature.stderr)

    def test_registry_repair_doc_hashes_rejects_mismatched_document_kind_without_saving_partial_repairs(self) -> None:
        with workspace_tempdir() as temp_dir:
            repo = Path(temp_dir) / "repo"
            repo.mkdir()
            init = run_cli("init", str(repo), "--repo-id", "repo:doc-hash-repair-negative", "--repo-name", "doc-hash-repair-negative", "--version", "1.0.0")
            self.assertEqual(init.returncode, 0, init.stderr)

            adr_body = repo / "adr-body.yaml"
            spec_body = repo / "spec-body.yaml"
            _write_body(adr_body, "Original ADR body.")
            _write_body(spec_body, "Original SPEC body.")
            adr = run_cli("adr", "create", str(repo), "--title", "Repair ADR", "--slug", "repair-adr", "--body-file", str(adr_body))
            self.assertEqual(adr.returncode, 0, adr.stderr)
            spec = run_cli(
                "spec",
                "create",
                str(repo),
                "--title",
                "Repair SPEC",
                "--slug",
                "repair-spec",
                "--body-file",
                str(spec_body),
                "--kind",
                "operational",
            )
            self.assertEqual(spec.returncode, 0, spec.stderr)

            adr_path = repo / ".ssot" / "adr" / "ADR-1000-repair-adr.yaml"
            spec_path = repo / ".ssot" / "specs" / "SPEC-1000-repair-spec.yaml"
            _replace_document_body(adr_path, "Original ADR body.", "Current ADR body.")
            _replace_document_body(spec_path, 'kind: "spec"', 'kind: "adr"')

            repair = run_cli("registry", "repair-doc-hashes", str(repo), "--ids", "adr:1000", "spc:1000")
            self.assertEqual(repair.returncode, 1)
            self.assertIn("kind", repair.stdout)
            self.assertIn("spec", repair.stdout)

            validate = run_cli("validate", str(repo))
            self.assertEqual(validate.returncode, 1)
            failures = "\n".join(json.loads(validate.stdout)["failures"])
            self.assertIn("adrs.adr:1000 content hash does not match file content", failures)
            self.assertIn("specs.spc:1000 content hash does not match file content", failures)

    def test_registry_repair_doc_hashes_rejects_packaged_documents(self) -> None:
        with workspace_tempdir() as temp_dir:
            repo = Path(temp_dir) / "repo"
            repo.mkdir()
            init = run_cli("init", str(repo), "--repo-id", "repo:doc-hash-repair-packaged", "--repo-name", "doc-hash-repair-packaged", "--version", "1.0.0")
            self.assertEqual(init.returncode, 0, init.stderr)

            repair = run_cli("registry", "repair-doc-hashes", str(repo), "--ids", "adr:0600")
            self.assertEqual(repair.returncode, 1)
            self.assertIn("hash repair only supports mutable repo-local documents", repair.stdout)


if __name__ == "__main__":
    unittest.main()
