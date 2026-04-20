from __future__ import annotations

import json
import unittest
from pathlib import Path

from ssot_registry.api import add_spec_adr_links, remove_spec_adr_links, validate_registry
from ssot_registry.util.document_io import validate_document_payload
from tests.helpers import run_cli, temp_repo_from_fixture, workspace_tempdir


class SpecAdrIdsValidationTests(unittest.TestCase):
    def test_validate_document_payload_accepts_spec_adr_ids(self) -> None:
        payload = {
            "schema_version": "0.2.0",
            "kind": "spec",
            "id": "spc:demo.spec-adr",
            "number": 1000,
            "slug": "demo-spec-adr",
            "title": "Demo SPEC ADR",
            "status": "draft",
            "origin": "repo-local",
            "decision_date": None,
            "tags": [],
            "summary": "Demo SPEC ADR",
            "spec_kind": "operational",
            "adr_ids": ["adr:demo.decision"],
            "supersedes": [],
            "superseded_by": [],
            "status_notes": [],
            "references": [],
            "body": "Demo SPEC body.",
        }

        validate_document_payload("spec", payload)

    def test_registry_validation_rejects_missing_spec_adr_target(self) -> None:
        temp_dir = temp_repo_from_fixture("repo_valid")
        self.addCleanup(temp_dir.cleanup)
        repo = Path(temp_dir.name) / "repo"
        registry_path = repo / ".ssot" / "registry.json"
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
        registry["specs"][0]["adr_ids"] = ["adr:missing.decision"]
        registry_path.write_text(json.dumps(registry, indent=2) + "\n", encoding="utf-8")

        report = validate_registry(repo)

        self.assertFalse(report["passed"])
        self.assertTrue(any("specs.spc:0600.adr_ids references missing ADR adr:missing.decision" in failure for failure in report["failures"]))

    def test_spec_api_link_and_unlink_rewrite_authored_payload(self) -> None:
        with workspace_tempdir() as temp_dir:
            repo = Path(temp_dir) / "repo"
            repo.mkdir()
            init = run_cli("init", str(repo), "--repo-id", "repo:api-spec-adr", "--repo-name", "api-spec-adr", "--version", "1.0.0")
            self.assertEqual(init.returncode, 0, init.stderr)

            adr_body = repo / "adr.yaml"
            adr_body.write_text('body: |-\n  ADR body.\n', encoding="utf-8")
            spec_body = repo / "spec.yaml"
            spec_body.write_text('body: |-\n  SPEC body.\n', encoding="utf-8")

            self.assertEqual(
                run_cli("adr", "create", str(repo), "--title", "ADR One", "--slug", "adr-one", "--body-file", str(adr_body)).returncode,
                0,
            )
            self.assertEqual(
                run_cli("spec", "create", str(repo), "--title", "Spec One", "--slug", "spec-one", "--body-file", str(spec_body), "--kind", "operational").returncode,
                0,
            )

            linked = add_spec_adr_links(repo, "spc:1000", ["adr:1000"])
            self.assertEqual(linked["document"]["adr_ids"], ["adr:1000"])

            payload = json.loads(run_cli("--output-format", "json", "spec", "get", str(repo), "--id", "spc:1000").stdout)
            self.assertEqual(payload["adr_ids"], ["adr:1000"])

            unlinked = remove_spec_adr_links(repo, "spc:1000", ["adr:1000"])
            self.assertEqual(unlinked["document"]["adr_ids"], [])


if __name__ == "__main__":
    unittest.main()
