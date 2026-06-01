from __future__ import annotations

import hashlib
import importlib
import json
import sys
import unittest
from pathlib import Path

from ssot_pack_contracts import (
    InvalidPackManifestError,
    InvalidPackMetadataError,
    UnsupportedDocumentKindError,
    bind_pack_contract,
    get_packaged_document_entry,
    list_packaged_document_ids,
    load_document_manifest,
    load_pack_manifest,
    load_pack_metadata,
    load_pack_schema_version,
    normalize_document_kind,
    read_packaged_document_text,
)
from tests.helpers import workspace_tempdir


def _write_dist_info(root: Path, *, dist_name: str, version: str, top_level: str) -> None:
    dist_info = root / f"{dist_name.replace('-', '_')}-{version}.dist-info"
    dist_info.mkdir()
    (dist_info / "METADATA").write_text(
        f"Metadata-Version: 2.1\nName: {dist_name}\nVersion: {version}\n",
        encoding="utf-8",
    )
    (dist_info / "top_level.txt").write_text(f"{top_level}\n", encoding="utf-8")


def _write_pack(root: Path, package_name: str = "example_governance_pack", dist_name: str = "example-governance-pack") -> str:
    package_root = root / package_name
    docs_root = package_root / "templates" / "adr"
    docs_root.mkdir(parents=True)
    (package_root / "__init__.py").write_text("", encoding="utf-8")
    _write_dist_info(root, dist_name=dist_name, version="1.2.3", top_level=package_name)
    document = (
        'schema_version: "0.4.0"\n'
        'kind: "adr"\n'
        'id: "adr:5000"\n'
        "number: 5000\n"
        'slug: "example-pack-adr"\n'
        'title: "Example Pack ADR"\n'
        'status: "draft"\n'
        'origin: "extension-pack"\n'
        "decision_date: null\n"
        "tags: []\n"
        'summary: "Example Pack ADR"\n'
        "supersedes: []\n"
        "superseded_by: []\n"
        "status_notes: []\n"
        "references: []\n"
        "body: |-\n"
        "  Example packaged ADR.\n"
    )
    document_path = docs_root / "ADR-5000-example-pack-adr.yaml"
    document_path.write_text(document, encoding="utf-8", newline="\n")
    sha256 = hashlib.sha256(document_path.read_bytes()).hexdigest()
    (docs_root / "manifest.json").write_text(
        json.dumps(
            [
                {
                    "id": "adr:5000",
                    "number": 5000,
                    "slug": "example-pack-adr",
                    "title": "Example Pack ADR",
                    "filename": "ADR-5000-example-pack-adr.yaml",
                    "target_path": ".ssot/adr/ADR-5000-example-pack-adr.yaml",
                    "sha256": sha256,
                    "origin": "extension-pack",
                    "reservation_owner": "extension-pack:example-governance-pack",
                    "immutable": True,
                    "minimum_schema_version": "0.4.0",
                    "introduced_in": "1.2.3",
                    "status": "draft",
                    "supersedes": [],
                    "superseded_by": [],
                    "status_notes": [],
                }
            ]
        ),
        encoding="utf-8",
    )
    (package_root / "metadata.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0.0",
                "ssot_package_name": dist_name,
                "origin": {
                    "id": "pack:example-governance",
                    "package_name": dist_name,
                    "import_name": package_name,
                    "kind": "governance-pack",
                    "title": "Example Governance Pack",
                    "description": "Installable SSOT governance pack.",
                },
                "compatibility": {
                    "python": ">=3.10,<3.15",
                    "ssot_registry_schema": ">=0.4.0",
                    "ssot_pack_contract": ">=1.0.0",
                },
                "trust": {
                    "trusted_by_default": True,
                    "origin": "extension-pack",
                    "reservation_owner": "extension-pack:example-governance-pack",
                },
                "documents": {"adr": {"manifest_path": "templates/adr/manifest.json"}},
            }
        ),
        encoding="utf-8",
    )
    return package_name


class PackContractTests(unittest.TestCase):
    def test_pack_metadata_manifest_and_document_loading(self) -> None:
        temp_dir = workspace_tempdir()
        self.addCleanup(temp_dir.cleanup)
        root = Path(temp_dir.name)
        package_name = _write_pack(root, "example_governance_pack_a")
        sys.path.insert(0, str(root))
        self.addCleanup(sys.path.remove, str(root))
        importlib.invalidate_caches()

        metadata = load_pack_metadata(package_name)

        self.assertEqual(metadata["schema_version"], "1.0.0")
        self.assertEqual(metadata["ssot_package_name"], "example-governance-pack")
        self.assertEqual(metadata["pypi_package_name"], "example-governance-pack")
        self.assertEqual(metadata["origin"]["package_name"], "example-governance-pack")
        self.assertEqual(metadata["version"], "1.2.3")
        self.assertEqual(load_pack_schema_version(package_name), "1.0.0")
        self.assertEqual(normalize_document_kind("adrs"), "adr")
        manifest = load_document_manifest(package_name, "adr")
        self.assertEqual(manifest[0]["id"], "adr:5000")
        self.assertEqual(load_pack_manifest(package_name)["documents"]["adr"][0]["id"], "adr:5000")
        self.assertEqual(list_packaged_document_ids(package_name), ["adr:5000"])
        self.assertEqual(get_packaged_document_entry(package_name, "adr:5000")["filename"], "ADR-5000-example-pack-adr.yaml")
        self.assertIn("Example packaged ADR.", read_packaged_document_text(package_name, "adr", "ADR-5000-example-pack-adr.yaml"))

    def test_bound_pack_contract_exports_zero_argument_pack_api(self) -> None:
        temp_dir = workspace_tempdir()
        self.addCleanup(temp_dir.cleanup)
        root = Path(temp_dir.name)
        package_name = _write_pack(root, "example_governance_pack_exports")
        sys.path.insert(0, str(root))
        self.addCleanup(sys.path.remove, str(root))
        importlib.invalidate_caches()

        exports = bind_pack_contract(package_name)

        self.assertEqual(exports["__version__"], "1.2.3")
        self.assertEqual(exports["__ssot_package_name__"], "example-governance-pack")
        self.assertEqual(exports["__pypi_package_name__"], "example-governance-pack")
        self.assertIn("load_pack_metadata", exports["__all__"])
        self.assertEqual(exports["load_pack_metadata"]()["ssot_package_name"], "example-governance-pack")
        self.assertEqual(exports["load_pack_schema_version"](), "1.0.0")
        self.assertEqual(exports["load_document_manifest"]("adr")[0]["id"], "adr:5000")
        self.assertEqual(exports["list_packaged_document_ids"](), ["adr:5000"])
        self.assertEqual(exports["get_packaged_document_entry"]("adr:5000")["filename"], "ADR-5000-example-pack-adr.yaml")

    def test_invalid_kind_and_hash_fail_closed(self) -> None:
        temp_dir = workspace_tempdir()
        self.addCleanup(temp_dir.cleanup)
        root = Path(temp_dir.name)
        package_name = _write_pack(root, "example_governance_pack_b")
        sys.path.insert(0, str(root))
        self.addCleanup(sys.path.remove, str(root))
        importlib.invalidate_caches()

        with self.assertRaises(UnsupportedDocumentKindError):
            normalize_document_kind("claim")

        manifest_path = root / package_name / "templates" / "adr" / "manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest[0]["sha256"] = "0" * 64
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

        with self.assertRaises(InvalidPackManifestError):
            read_packaged_document_text(package_name, "adr", "ADR-5000-example-pack-adr.yaml")

    def test_manifest_minimum_schema_version_must_be_semver_string(self) -> None:
        invalid_values = [
            4,
            "",
            "4",
            "0.4",
            "0.4.0-alpha",
            " 0.4.0",
        ]
        for index, value in enumerate(invalid_values):
            with self.subTest(value=value):
                temp_dir = workspace_tempdir()
                self.addCleanup(temp_dir.cleanup)
                root = Path(temp_dir.name)
                package_name = _write_pack(
                    root,
                    f"example_governance_pack_schema_{index}",
                    dist_name=f"example-governance-pack-schema-{index}",
                )
                sys.path.insert(0, str(root))
                self.addCleanup(sys.path.remove, str(root))
                importlib.invalidate_caches()

                manifest_path = root / package_name / "templates" / "adr" / "manifest.json"
                manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                manifest[0]["minimum_schema_version"] = value
                manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

                with self.assertRaisesRegex(InvalidPackManifestError, "minimum_schema_version"):
                    load_document_manifest(package_name, "adr")

    def test_manifest_minimum_schema_version_is_required(self) -> None:
        temp_dir = workspace_tempdir()
        self.addCleanup(temp_dir.cleanup)
        root = Path(temp_dir.name)
        package_name = _write_pack(root, "example_governance_pack_missing_schema")
        sys.path.insert(0, str(root))
        self.addCleanup(sys.path.remove, str(root))
        importlib.invalidate_caches()

        manifest_path = root / package_name / "templates" / "adr" / "manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        del manifest[0]["minimum_schema_version"]
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

        with self.assertRaisesRegex(InvalidPackManifestError, "minimum_schema_version"):
            load_document_manifest(package_name, "adr")

    def test_ambiguous_import_package_distribution_mapping_fails_closed(self) -> None:
        temp_dir = workspace_tempdir()
        self.addCleanup(temp_dir.cleanup)
        root = Path(temp_dir.name)
        package_name = _write_pack(root, "example_governance_pack_ambiguous", dist_name="expected-governance-pack")
        _write_dist_info(root, dist_name="other-governance-pack", version="9.9.9", top_level=package_name)
        metadata_path = root / package_name / "metadata.json"
        payload = json.loads(metadata_path.read_text(encoding="utf-8"))
        payload["ssot_package_name"] = "missing-governance-pack"
        payload["origin"]["package_name"] = "missing-governance-pack"
        metadata_path.write_text(json.dumps(payload), encoding="utf-8")
        sys.path.insert(0, str(root))
        self.addCleanup(sys.path.remove, str(root))
        importlib.invalidate_caches()

        with self.assertRaises(InvalidPackMetadataError):
            load_pack_metadata(package_name)


if __name__ == "__main__":
    unittest.main()
