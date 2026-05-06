from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

from ssot_registry.api import sync_documents, validate_registry
from ssot_registry.model import document as document_model
from ssot_registry.model.document import extension_pack_reservation_owner
from ssot_registry.util.errors import ValidationError
from ssot_registry.util.jsonio import save_json
from ssot_registry.version import __version__
from tests.helpers import temp_repo_from_fixture


class DocumentSyncTests(unittest.TestCase):
    def test_sync_restores_modified_ssot_document(self) -> None:
        temp_dir = temp_repo_from_fixture("repo_valid")
        self.addCleanup(temp_dir.cleanup)
        repo = Path(temp_dir.name) / "repo"

        target = repo / ".ssot" / "adr" / "ADR-0600-canonical-json-registry.yaml"
        target.write_text(target.read_text(encoding="utf-8") + "\nlocal edit\n", encoding="utf-8")

        report = validate_registry(repo)
        self.assertFalse(report["passed"])
        self.assertIn("content hash does not match file content", "\n".join(report["failures"]))

        sync_result = sync_documents(repo, "adr")
        self.assertIn("adr:0600", sync_result["updated"])

        report_after = validate_registry(repo)
        self.assertTrue(report_after["passed"], report_after)

    def test_sync_accepts_trusted_extension_pack_manifest(self) -> None:
        temp_dir = temp_repo_from_fixture("repo_valid")
        self.addCleanup(temp_dir.cleanup)
        repo = Path(temp_dir.name) / "repo"
        registry_path = repo / ".ssot" / "registry.json"
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
        registry["document_id_reservations"]["adr"].append(
            {
                "owner": extension_pack_reservation_owner("demo"),
                "start": 5000,
                "end": 5099,
                "immutable": True,
                "deletable": False,
                "assignable_by_repo": False,
            }
        )
        save_json(registry_path, registry)

        payload = (
            'schema_version: "0.1.0"\n'
            'kind: "adr"\n'
            'id: "adr:5000"\n'
            "number: 5000\n"
            'slug: "extension-pack-contract"\n'
            'title: "Extension Pack Contract"\n'
            'status: "draft"\n'
            'origin: "extension-pack"\n'
            'summary: "Trusted extension catalog row."\n'
            "references: []\n"
            "tags: []\n"
            "supersedes: []\n"
            "superseded_by: []\n"
            "status_notes: []\n"
            "decision_date: null\n"
            "body: |-\n"
            "  Trusted extension catalog row.\n"
        )
        payload_bytes = payload.encode("utf-8")
        payload_hash = hashlib.sha256(payload_bytes.replace(b"\r\n", b"\n")).hexdigest()
        provider = {
            "catalog_id": "demo",
            "trusted_by_default": True,
            "load_manifest": lambda kind: [
                {
                    "id": "adr:5000",
                    "number": 5000,
                    "slug": "extension-pack-contract",
                    "title": "Extension Pack Contract",
                    "filename": "ADR-5000-extension-pack-contract.yaml",
                    "target_path": ".ssot/adr/ADR-5000-extension-pack-contract.yaml",
                    "origin": "extension-pack",
                    "immutable": True,
                    "sha256": payload_hash,
                    "minimum_schema_version": "0.3.0",
                    "status": "draft",
                    "supersedes": [],
                    "superseded_by": [],
                    "status_notes": [],
                    "catalog_id": "demo",
                    "trusted": True,
                }
            ]
            if kind == "adr"
            else [],
            "read_text": lambda kind, filename: payload,
            "read_bytes": lambda kind, filename: payload_bytes,
        }
        original_providers = list(document_model._DOCUMENT_CATALOG_PROVIDERS)
        self.addCleanup(lambda: setattr(document_model, "_DOCUMENT_CATALOG_PROVIDERS", original_providers))
        document_model._DOCUMENT_CATALOG_PROVIDERS = [*original_providers, provider]

        sync_result = sync_documents(repo, "adr")
        self.assertIn("adr:5000", sync_result["created"])

        report_after = validate_registry(repo)
        self.assertTrue(report_after["passed"], report_after)

        updated_registry = json.loads(registry_path.read_text(encoding="utf-8"))
        row = next(row for row in updated_registry["adrs"] if row["id"] == "adr:5000")
        self.assertEqual("extension-pack", row["origin"])
        self.assertTrue(row["managed"])
        self.assertTrue(row["immutable"])
        self.assertEqual(__version__, row["package_version"])

    def test_sync_rejects_untrusted_extension_pack_manifest(self) -> None:
        temp_dir = temp_repo_from_fixture("repo_valid")
        self.addCleanup(temp_dir.cleanup)
        repo = Path(temp_dir.name) / "repo"

        provider = {
            "catalog_id": "demo-untrusted",
            "trusted_by_default": False,
            "load_manifest": lambda kind: [
                {
                    "id": "adr:5001",
                    "number": 5001,
                    "slug": "untrusted-extension-pack-contract",
                    "title": "Untrusted Extension Pack Contract",
                    "filename": "ADR-5001-untrusted-extension-pack-contract.yaml",
                    "target_path": ".ssot/adr/ADR-5001-untrusted-extension-pack-contract.yaml",
                    "origin": "extension-pack",
                    "immutable": True,
                    "sha256": "0" * 64,
                    "minimum_schema_version": "0.3.0",
                    "status": "draft",
                    "supersedes": [],
                    "superseded_by": [],
                    "status_notes": [],
                    "catalog_id": "demo-untrusted",
                    "trusted": False,
                }
            ]
            if kind == "adr"
            else [],
            "read_text": lambda kind, filename: "",
            "read_bytes": lambda kind, filename: b"",
        }
        original_providers = list(document_model._DOCUMENT_CATALOG_PROVIDERS)
        self.addCleanup(lambda: setattr(document_model, "_DOCUMENT_CATALOG_PROVIDERS", original_providers))
        document_model._DOCUMENT_CATALOG_PROVIDERS = [*original_providers, provider]

        with self.assertRaisesRegex(ValidationError, "Untrusted extension-pack catalogs are available but not allowed for sync"):
            sync_documents(repo, "adr")


if __name__ == "__main__":
    unittest.main()
