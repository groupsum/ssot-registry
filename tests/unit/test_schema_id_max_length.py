from __future__ import annotations

import json
import unittest
from pathlib import Path

from ssot_contracts.generated.python.ids import MAX_NORMALIZED_ID_LENGTH
from ssot_registry.api import validate_registry
from ssot_registry.model.ids import is_normalized_id
from ssot_registry.util.document_io import validate_document_payload
from ssot_registry.util.errors import ValidationError
from ssot_registry.util.jsonio import stable_json_dumps
from tests.helpers import temp_repo_from_fixture


class SchemaIdMaxLengthTests(unittest.TestCase):
    def test_is_normalized_id_rejects_values_longer_than_contract_limit(self) -> None:
        overlong_id = "feat:" + ("a" * (MAX_NORMALIZED_ID_LENGTH - len("feat:") + 1))
        self.assertFalse(is_normalized_id(overlong_id))

    def test_validate_registry_reports_overlong_entity_ids(self) -> None:
        temp_dir = temp_repo_from_fixture("repo_valid")
        self.addCleanup(temp_dir.cleanup)
        repo = Path(temp_dir.name) / "repo"
        registry_path = repo / ".ssot" / "registry.json"
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
        registry["features"].append(
            {
                "id": "feat:" + ("a" * (MAX_NORMALIZED_ID_LENGTH - len("feat:") + 1)),
                "title": "Overlong id feature",
                "description": "exercise max-length validation",
                "implementation_status": "absent",
                "lifecycle": {"stage": "active", "replacement_feature_ids": [], "note": None},
                "plan": {
                    "horizon": "backlog",
                    "slot": None,
                    "target_claim_tier": None,
                    "target_lifecycle_stage": "active",
                },
                "spec_ids": [],
                "claim_ids": [],
                "test_ids": [],
                "requires": [],
            }
        )
        registry_path.write_text(stable_json_dumps(registry), encoding="utf-8")

        report = validate_registry(repo)

        self.assertFalse(report["passed"])
        self.assertIn("not a normalized id", "\n".join(report["failures"]))

    def test_validate_registry_reports_overlong_reference_ids(self) -> None:
        temp_dir = temp_repo_from_fixture("repo_valid")
        self.addCleanup(temp_dir.cleanup)
        repo = Path(temp_dir.name) / "repo"
        registry_path = repo / ".ssot" / "registry.json"
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
        registry["features"][0]["spec_ids"] = ["spc:" + ("9" * (MAX_NORMALIZED_ID_LENGTH - len("spc:") + 1))]
        registry_path.write_text(stable_json_dumps(registry), encoding="utf-8")

        report = validate_registry(repo)

        self.assertFalse(report["passed"])
        self.assertIn("contains a non-normalized id", "\n".join(report["failures"]))

    def test_document_schema_rejects_overlong_document_ids(self) -> None:
        payload = {
            "schema_version": "0.1.0",
            "kind": "adr",
            "id": "adr:" + ("0" * (MAX_NORMALIZED_ID_LENGTH - len("adr:") + 1)),
            "number": 507,
            "slug": "schema-owned-id-max-lengths",
            "title": "Schema-owned id max lengths",
            "status": "draft",
            "origin": "ssot-core",
            "decision_date": None,
            "tags": [],
            "summary": "Schema-owned ID max-lengths.",
            "supersedes": [],
            "superseded_by": [],
            "status_notes": [],
            "references": [],
            "body": "Decision body.",
        }

        with self.assertRaises(ValidationError):
            validate_document_payload("adr", payload)


if __name__ == "__main__":
    unittest.main()
