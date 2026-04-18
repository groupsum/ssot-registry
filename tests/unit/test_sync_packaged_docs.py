from __future__ import annotations

import json
import unittest
from pathlib import Path

from scripts.sync_packaged_docs import sync_manifest, sync_mirror
from tests.helpers import workspace_tempdir


class SyncPackagedDocsTests(unittest.TestCase):
    def test_check_ignores_non_packaged_docs_in_destination(self) -> None:
        temp_dir = workspace_tempdir()
        self.addCleanup(temp_dir.cleanup)
        root = Path(temp_dir.name)
        source = root / "source"
        destination = root / "destination"
        source.mkdir()
        destination.mkdir()

        doc_text = json.dumps(
            {
                "schema_version": 9,
                "kind": "adr",
                "id": "adr:0001",
                "number": 1,
                "slug": "example",
                "title": "Example",
                "status": "draft",
                "origin": "ssot-origin",
                "summary": "Example",
                "sections": {"decision": ["Example"]},
            },
            indent=2,
        ) + "\n"
        (source / "ADR-0001-example.yaml").write_text(doc_text, encoding="utf-8")
        (destination / "ADR-0001-example.yaml").write_text(doc_text, encoding="utf-8")
        (destination / "ADR-0500-core.yaml").write_text(doc_text, encoding="utf-8")

        failures = sync_mirror(source, destination, check=True)

        self.assertEqual(failures, [])

    def test_prune_removes_stale_mirrored_yaml(self) -> None:
        temp_dir = workspace_tempdir()
        self.addCleanup(temp_dir.cleanup)
        root = Path(temp_dir.name)
        source = root / "source"
        destination = root / "destination"
        source.mkdir()
        destination.mkdir()

        doc_text = json.dumps(
            {
                "schema_version": 9,
                "kind": "adr",
                "id": "adr:0600",
                "number": 600,
                "slug": "example",
                "title": "Example",
                "status": "draft",
                "origin": "ssot-origin",
                "summary": "Example",
                "sections": {"decision": ["Example"]},
            },
            indent=2,
        ) + "\n"
        (source / "ADR-0600-example.yaml").write_text(doc_text, encoding="utf-8")
        stale = destination / "ADR-0001-stale.yaml"
        stale.write_text(doc_text, encoding="utf-8")

        failures = sync_mirror(source, destination, check=False, prune=True)

        self.assertEqual(failures, [])
        self.assertFalse(stale.exists())
        self.assertTrue((destination / "ADR-0600-example.yaml").exists())

    def test_sync_manifest_rewrites_stale_hashes(self) -> None:
        temp_dir = workspace_tempdir()
        self.addCleanup(temp_dir.cleanup)
        root = Path(temp_dir.name)
        specs = root / "specs"
        specs.mkdir()
        (specs / "SPEC-0607-repo-policy.yaml").write_text(
            json.dumps(
                {
                    "schema_version": 9,
                    "kind": "spec",
                    "id": "spc:0607",
                    "number": 607,
                    "slug": "repo-policy",
                    "title": "Repository policy",
                    "status": "draft",
                    "origin": "ssot-origin",
                    "summary": "Repository policy",
                    "spec_kind": "normative",
                    "sections": {"rules": ["Repository policy"]},
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        (specs / "manifest.json").write_text(
            json.dumps(
                [
                    {
                        "id": "spc:0607",
                        "number": 607,
                        "slug": "repo-policy",
                        "title": "Repository policy",
                        "filename": "SPEC-0607-repo-policy.yaml",
                        "target_path": ".ssot/specs/SPEC-0607-repo-policy.yaml",
                        "sha256": "0" * 64,
                        "origin": "ssot-origin",
                        "reservation_owner": "ssot-origin",
                        "immutable": True,
                        "minimum_schema_version": 4,
                        "introduced_in": "0.2.1",
                        "kind": "normative",
                        "status": "draft",
                        "supersedes": [],
                        "superseded_by": [],
                        "status_notes": [],
                    }
                ],
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )

        failures = sync_manifest(specs, "specs", check=False)

        self.assertEqual(failures, [])
        manifest = json.loads((specs / "manifest.json").read_text(encoding="utf-8"))
        self.assertNotEqual(manifest[0]["sha256"], "0" * 64)
        self.assertEqual(manifest[0]["filename"], "SPEC-0607-repo-policy.yaml")

    def test_range_validation_detects_cross_origin_collision(self) -> None:
        temp_dir = workspace_tempdir()
        self.addCleanup(temp_dir.cleanup)
        root = Path(temp_dir.name)
        origin_adr = root / "origin-adr"
        origin_specs = root / "origin-specs"
        core_adr = root / "core-adr"
        core_specs = root / "core-specs"
        for path in (origin_adr, origin_specs, core_adr, core_specs):
            path.mkdir()

        doc_text = json.dumps(
            {
                "schema_version": 9,
                "kind": "adr",
                "id": "adr:0010",
                "number": 10,
                "slug": "origin",
                "title": "Origin",
                "status": "draft",
                "origin": "ssot-origin",
                "summary": "Origin",
                "sections": {"decision": ["Origin"]},
            },
            indent=2,
        ) + "\n"
        spec_text = json.dumps(
            {
                "schema_version": 9,
                "kind": "spec",
                "id": "spc:0008",
                "number": 8,
                "slug": "origin",
                "title": "Origin",
                "status": "draft",
                "origin": "ssot-origin",
                "summary": "Origin",
                "spec_kind": "normative",
                "sections": {"content": ["Origin"]},
            },
            indent=2,
        ) + "\n"
        (origin_adr / "ADR-0010-origin.yaml").write_text(doc_text, encoding="utf-8")
        (origin_specs / "SPEC-0008-origin.yaml").write_text(spec_text, encoding="utf-8")
        (core_adr / "ADR-0010-core-collision.yaml").write_text(doc_text, encoding="utf-8")
        (core_specs / "SPEC-0508-core.yaml").write_text(spec_text.replace('0008', '0508'), encoding="utf-8")

        from scripts import sync_packaged_docs

        original_origin_roots = sync_packaged_docs.ORIGIN_ROOTS
        original_core_roots = sync_packaged_docs.CORE_ROOTS
        try:
            sync_packaged_docs.ORIGIN_ROOTS = {"adr": origin_adr, "specs": origin_specs}
            sync_packaged_docs.CORE_ROOTS = {"adr": core_adr, "specs": core_specs}
            failures = sync_packaged_docs.validate_number_ranges()
        finally:
            sync_packaged_docs.ORIGIN_ROOTS = original_origin_roots
            sync_packaged_docs.CORE_ROOTS = original_core_roots

        self.assertIn("ssot-origin adr id 0010 is outside reserved range 0600..0999", failures)
        self.assertIn("ssot-origin specs id 0008 is outside reserved range 0600..0999", failures)
        self.assertIn(
            "Conflicting adr id 0010 is present in both ssot-origin templates and ssot-core docs",
            failures,
        )


if __name__ == "__main__":
    unittest.main()
