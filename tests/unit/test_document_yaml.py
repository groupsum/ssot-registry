from __future__ import annotations

import json
import unittest
from pathlib import Path

from ssot_contracts.schema import list_schema_names
from ssot_registry.api import initialize_repo, validate_registry
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
            payload = json.loads(target.read_text(encoding="utf-8"))
            del payload["sections"]["decision"]
            target.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

            report = validate_registry(repo)
            self.assertFalse(report["passed"])
            self.assertIn("document content is invalid", "\n".join(report["failures"]))


if __name__ == "__main__":
    unittest.main()
