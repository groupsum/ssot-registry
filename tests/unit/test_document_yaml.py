from __future__ import annotations

import json
import unittest
from pathlib import Path

from ssot_contracts.schema import list_schema_names
from ssot_registry.api import create_document, initialize_repo, load_registry, update_document, validate_registry
from ssot_registry.util.document_io import dump_document_yaml, load_document_yaml
from tests.helpers import workspace_tempdir


class DocumentJsonCanonicalTests(unittest.TestCase):
    def test_document_schemas_are_packaged(self) -> None:
        names = set(list_schema_names())
        self.assertIn("adr.schema.json", names)
        self.assertIn("spec.schema.json", names)

    def test_invalid_document_payload_fails_validation(self) -> None:
        with workspace_tempdir() as temp_dir:
            repo = Path(temp_dir) / "repo"
            initialize_repo(repo, repo_id="repo:yaml-doc", repo_name="yaml-doc", version="1.0.0")
            target = repo / ".ssot" / "adr" / "ADR-0600-canonical-json-registry.json"
            payload = load_document_yaml(target)
            del payload["body"]
            target.write_text(dump_document_yaml(payload), encoding="utf-8")

            report = validate_registry(repo)
            self.assertFalse(report["passed"])
            self.assertIn("document content is invalid", "\n".join(report["failures"]))

    def test_repo_local_json_document_validates_and_updates(self) -> None:
        with workspace_tempdir() as temp_dir:
            repo = Path(temp_dir) / "repo"
            repo.mkdir()
            initialize_repo(repo, repo_id="repo:json-doc", repo_name="json-doc", version="1.0.0")

            body = repo / "adr-body.yaml"
            body.write_text('body: |-\n  Local ADR body.\n', encoding="utf-8")
            create_result = create_document(
                repo,
                "adr",
                title="Local decision",
                slug="local-decision",
                body_file=body,
            )
            self.assertTrue(create_result["passed"])

            _registry_path, repo_root, registry = load_registry(repo)
            row = next(row for row in registry["adrs"] if row["id"] == "adr:1000")
            json_path = repo_root / row["path"]
            payload = load_document_yaml(json_path)
            self.assertTrue(json_path.exists())
            self.assertTrue(json_path.read_text(encoding="utf-8").lstrip().startswith("{"))

            report = validate_registry(repo)
            self.assertTrue(report["passed"], report)

            update_result = update_document(repo, "adr", "adr:1000", title="Local decision updated")
            self.assertTrue(update_result["passed"])
            self.assertTrue(json_path.exists())
            updated_payload = json.loads(json_path.read_text(encoding="utf-8"))
            self.assertEqual("Local decision updated", updated_payload["title"])

    def test_markdown_body_file_is_rejected(self) -> None:
        with workspace_tempdir() as temp_dir:
            repo = Path(temp_dir) / "repo"
            repo.mkdir()
            initialize_repo(repo, repo_id="repo:md-doc", repo_name="md-doc", version="1.0.0")

            body = repo / "adr-body.md"
            body.write_text("Local ADR body.\n", encoding="utf-8")

            with self.assertRaisesRegex(Exception, r"body-file must be \.json or \.yaml"):
                create_document(
                    repo,
                    "adr",
                    title="Markdown body",
                    slug="markdown-body",
                    body_file=body,
                )

    def test_inline_body_create_and_update_round_trip(self) -> None:
        with workspace_tempdir() as temp_dir:
            repo = Path(temp_dir) / "repo"
            repo.mkdir()
            initialize_repo(repo, repo_id="repo:inline-doc", repo_name="inline-doc", version="1.0.0")

            create_result = create_document(
                repo,
                "adr",
                title="Inline decision",
                slug="inline-decision",
                body="Inline ADR body.",
            )
            self.assertTrue(create_result["passed"])

            _registry_path, repo_root, registry = load_registry(repo)
            row = next(row for row in registry["adrs"] if row["id"] == "adr:1000")
            payload = load_document_yaml(repo_root / row["path"])
            self.assertEqual("Inline ADR body.", payload["body"])

            update_result = update_document(repo, "adr", "adr:1000", body="Updated inline ADR body.")
            self.assertTrue(update_result["passed"])
            updated_payload = load_document_yaml(repo_root / row["path"])
            self.assertEqual("Updated inline ADR body.", updated_payload["body"])

    def test_create_document_requires_exactly_one_body_source(self) -> None:
        with workspace_tempdir() as temp_dir:
            repo = Path(temp_dir) / "repo"
            repo.mkdir()
            initialize_repo(repo, repo_id="repo:body-source", repo_name="body-source", version="1.0.0")

            body_file = repo / "adr-body.yaml"
            body_file.write_text('body: |-\n  Local ADR body.\n', encoding="utf-8")

            with self.assertRaisesRegex(Exception, r"requires exactly one of body or body_file"):
                create_document(repo, "adr", title="Missing body", slug="missing-body")

            with self.assertRaisesRegex(Exception, r"accepts only one of body or body_file"):
                create_document(
                    repo,
                    "adr",
                    title="Conflicting body",
                    slug="conflicting-body",
                    body="Inline body",
                    body_file=body_file,
                )

    def test_update_document_rejects_conflicting_body_sources_and_preserves_existing_body(self) -> None:
        with workspace_tempdir() as temp_dir:
            repo = Path(temp_dir) / "repo"
            repo.mkdir()
            initialize_repo(repo, repo_id="repo:update-body", repo_name="update-body", version="1.0.0")

            create_result = create_document(
                repo,
                "spec",
                title="Inline spec",
                slug="inline-spec",
                body="Initial spec body.",
                spec_kind="operational",
            )
            self.assertTrue(create_result["passed"])

            body_file = repo / "spec-body.yaml"
            body_file.write_text('body: |-\n  Replacement SPEC body.\n', encoding="utf-8")

            with self.assertRaisesRegex(Exception, r"accepts only one of body or body_file"):
                update_document(repo, "spec", "spc:1000", body="Inline", body_file=body_file)

            update_result = update_document(repo, "spec", "spc:1000", title="Inline spec updated")
            self.assertTrue(update_result["passed"])

            _registry_path, repo_root, registry = load_registry(repo)
            row = next(row for row in registry["specs"] if row["id"] == "spc:1000")
            payload = load_document_yaml(repo_root / row["path"])
            self.assertEqual("Inline spec updated", payload["title"])
            self.assertEqual("Initial spec body.", payload["body"])


if __name__ == "__main__":
    unittest.main()

