from __future__ import annotations

import json
import unittest
from pathlib import Path

from ssot_contracts.schema import list_schema_names
from ssot_registry.api import create_document, initialize_repo, load_registry, save_registry, update_document, validate_registry
from ssot_registry.util.document_io import dump_document_yaml, load_document_yaml
from ssot_registry.util.fs import sha256_normalized_text_path
from ssot_registry.util.jsonio import stable_json_dumps
from tests.helpers import workspace_tempdir


class DocumentYamlTests(unittest.TestCase):
    def test_document_schemas_are_packaged(self) -> None:
        names = set(list_schema_names())
        self.assertIn("adr.schema.json", names)
        self.assertIn("spec.schema.json", names)

    def test_invalid_yaml_document_fails_validation(self) -> None:
        with workspace_tempdir() as temp_dir:
            repo = Path(temp_dir) / "repo"
            initialize_repo(repo, repo_id="repo:yaml-doc", repo_name="yaml-doc", version="1.0.0")
            target = repo / ".ssot" / "adr" / "ADR-0600-canonical-json-registry.yaml"
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

            body = repo / "adr-body.md"
            body.write_text("Local ADR body.\n", encoding="utf-8")
            create_result = create_document(
                repo,
                "adr",
                title="Local decision",
                slug="local-decision",
                body_file=body,
            )
            self.assertTrue(create_result["passed"])

            registry_path, repo_root, registry = load_registry(repo)
            row = next(row for row in registry["adrs"] if row["id"] == "adr:1000")
            yaml_path = repo_root / row["path"]
            payload = load_document_yaml(yaml_path)
            json_path = yaml_path.with_suffix(".json")
            json_path.write_text(stable_json_dumps(payload), encoding="utf-8")
            yaml_path.unlink()
            row["path"] = json_path.relative_to(repo_root).as_posix()
            row["content_sha256"] = sha256_normalized_text_path(json_path)
            save_registry(registry_path, registry)

            report = validate_registry(repo)
            self.assertTrue(report["passed"], report)

            update_result = update_document(repo, "adr", "adr:1000", title="Local decision updated")
            self.assertTrue(update_result["passed"])
            self.assertTrue(json_path.exists())
            updated_payload = json.loads(json_path.read_text(encoding="utf-8"))
            self.assertEqual("Local decision updated", updated_payload["title"])


if __name__ == "__main__":
    unittest.main()
