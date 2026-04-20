from __future__ import annotations

import json
import unittest
from pathlib import Path

from scripts import sync_packaged_docs
from ssot_registry.util.document_io import dump_document_yaml
from tests.helpers import workspace_tempdir


def _adr_payload(number: int, slug: str) -> dict[str, object]:
    return {
        "schema_version": "0.1.0",
        "kind": "adr",
        "id": f"adr:{number:04d}",
        "number": number,
        "slug": slug,
        "title": slug.replace("-", " ").title(),
        "status": "draft",
        "origin": "ssot-origin",
        "decision_date": None,
        "tags": [],
        "summary": slug.replace("-", " ").title(),
        "supersedes": [],
        "superseded_by": [],
        "status_notes": [],
        "references": [],
        "body": slug.replace("-", " ").title(),
    }


def _spec_payload(number: int, slug: str) -> dict[str, object]:
    return {
        "schema_version": "0.1.0",
        "kind": "spec",
        "id": f"spc:{number:04d}",
        "number": number,
        "slug": slug,
        "title": slug.replace("-", " ").title(),
        "status": "draft",
        "origin": "ssot-origin",
        "decision_date": None,
        "tags": [],
        "summary": slug.replace("-", " ").title(),
        "spec_kind": "normative",
        "adr_ids": [],
        "supersedes": [],
        "superseded_by": [],
        "status_notes": [],
        "references": [],
        "body": slug.replace("-", " ").title(),
    }


class SyncPackagedDocsTests(unittest.TestCase):
    def _with_project_root(self, root: Path) -> tuple[Path, Path]:
        upstream = root / ".ssot"
        packaged = root / "pkgs" / "ssot-contracts" / "src" / "ssot_contracts" / "templates"
        for path in (upstream / "adr", upstream / "specs", packaged / "adr", packaged / "specs"):
            path.mkdir(parents=True, exist_ok=True)
        return upstream, packaged

    def _patch_project_root(self, root: Path) -> tuple[Path, Path]:
        original_root = sync_packaged_docs.PROJECT_ROOT
        original_registry = sync_packaged_docs.UPSTREAM_REGISTRY_PATH
        sync_packaged_docs.PROJECT_ROOT = root
        sync_packaged_docs.UPSTREAM_REGISTRY_PATH = root / ".ssot" / "registry.json"
        self.addCleanup(setattr, sync_packaged_docs, "PROJECT_ROOT", original_root)
        self.addCleanup(setattr, sync_packaged_docs, "UPSTREAM_REGISTRY_PATH", original_registry)
        return original_root, original_registry

    def test_check_detects_missing_packaged_doc(self) -> None:
        temp_dir = workspace_tempdir()
        self.addCleanup(temp_dir.cleanup)
        root = Path(temp_dir.name)
        upstream, packaged = self._with_project_root(root)
        self._patch_project_root(root)

        source_path = upstream / "adr" / "ADR-0600-example.yaml"
        source_path.write_text(dump_document_yaml(_adr_payload(600, "example")), encoding="utf-8")
        registry = {
            "schema_version": "0.1.0",
            "tooling": {"ssot_registry_version": "0.2.6.dev1"},
            "adrs": [
                {
                    "id": "adr:0600",
                    "number": 600,
                    "slug": "example",
                    "title": "Example",
                    "path": ".ssot/adr/ADR-0600-example.yaml",
                    "origin": "ssot-origin",
                    "status": "draft",
                    "supersedes": [],
                    "superseded_by": [],
                    "status_notes": [],
                }
            ],
            "specs": [],
        }

        failures = sync_packaged_docs.sync_packaged_files(registry, "adr", packaged / "adr", check=True)

        self.assertEqual(
            [f"Missing packaged doc: {(packaged / 'adr' / 'ADR-0600-example.yaml').relative_to(root).as_posix()}"],
            failures,
        )

    def test_prune_removes_stale_packaged_doc(self) -> None:
        temp_dir = workspace_tempdir()
        self.addCleanup(temp_dir.cleanup)
        root = Path(temp_dir.name)
        upstream, packaged = self._with_project_root(root)
        self._patch_project_root(root)

        source_path = upstream / "adr" / "ADR-0600-example.yaml"
        source_path.write_text(dump_document_yaml(_adr_payload(600, "example")), encoding="utf-8")
        stale = packaged / "adr" / "ADR-0601-stale.yaml"
        stale.write_text(dump_document_yaml(_adr_payload(601, "stale")), encoding="utf-8")
        registry = {
            "schema_version": "0.1.0",
            "tooling": {"ssot_registry_version": "0.2.6.dev1"},
            "adrs": [
                {
                    "id": "adr:0600",
                    "number": 600,
                    "slug": "example",
                    "title": "Example",
                    "path": ".ssot/adr/ADR-0600-example.yaml",
                    "origin": "ssot-origin",
                    "status": "draft",
                    "supersedes": [],
                    "superseded_by": [],
                    "status_notes": [],
                }
            ],
            "specs": [],
        }

        failures = sync_packaged_docs.sync_packaged_files(registry, "adr", packaged / "adr", check=False, prune=True)

        self.assertEqual([], failures)
        self.assertTrue((packaged / "adr" / "ADR-0600-example.yaml").exists())
        self.assertFalse(stale.exists())

    def test_sync_manifest_rewrites_stale_hashes_from_upstream_registry(self) -> None:
        temp_dir = workspace_tempdir()
        self.addCleanup(temp_dir.cleanup)
        root = Path(temp_dir.name)
        upstream, packaged = self._with_project_root(root)
        self._patch_project_root(root)

        source_path = upstream / "specs" / "SPEC-0607-repo-policy.yaml"
        source_path.write_text(dump_document_yaml(_spec_payload(607, "repo-policy")), encoding="utf-8")
        registry = {
            "schema_version": "0.1.0",
            "tooling": {"ssot_registry_version": "0.2.6.dev1"},
            "adrs": [],
            "specs": [
                {
                    "id": "spc:0607",
                    "number": 607,
                    "slug": "repo-policy",
                    "title": "Repository policy",
                    "path": ".ssot/specs/SPEC-0607-repo-policy.yaml",
                    "origin": "ssot-origin",
                    "status": "draft",
                    "kind": "normative",
                    "adr_ids": [],
                    "supersedes": [],
                    "superseded_by": [],
                    "status_notes": [],
                }
            ],
        }
        (packaged / "specs" / "manifest.json").write_text(
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
                        "adr_ids": [],
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

        failures = sync_packaged_docs.sync_manifest(registry, "specs", packaged / "specs", check=False)

        self.assertEqual([], failures)
        manifest = json.loads((packaged / "specs" / "manifest.json").read_text(encoding="utf-8"))
        self.assertNotEqual(manifest[0]["sha256"], "0" * 64)
        self.assertEqual(manifest[0]["filename"], "SPEC-0607-repo-policy.yaml")
        self.assertEqual(manifest[0]["kind"], "normative")

    def test_range_validation_detects_cross_origin_collision(self) -> None:
        temp_dir = workspace_tempdir()
        self.addCleanup(temp_dir.cleanup)
        root = Path(temp_dir.name)
        upstream, _packaged = self._with_project_root(root)
        self._patch_project_root(root)

        (upstream / "adr" / "ADR-0010-origin.yaml").write_text(dump_document_yaml(_adr_payload(10, "origin")), encoding="utf-8")
        (upstream / "specs" / "SPEC-0008-origin.yaml").write_text(
            dump_document_yaml(_spec_payload(8, "origin")),
            encoding="utf-8",
        )
        registry = {
            "schema_version": "0.1.0",
            "tooling": {"ssot_registry_version": "0.2.6.dev1"},
            "adrs": [
                {
                    "id": "adr:0010",
                    "number": 10,
                    "slug": "origin",
                    "title": "Origin",
                    "path": ".ssot/adr/ADR-0010-origin.yaml",
                    "origin": "ssot-origin",
                    "status": "draft",
                    "supersedes": [],
                    "superseded_by": [],
                    "status_notes": [],
                },
                {
                    "id": "adr:0010",
                    "number": 10,
                    "slug": "core-collision",
                    "title": "Core collision",
                    "path": ".ssot/adr/ADR-0010-core-collision.yaml",
                    "origin": "ssot-core",
                    "status": "draft",
                    "supersedes": [],
                    "superseded_by": [],
                    "status_notes": [],
                },
            ],
            "specs": [
                {
                    "id": "spc:0008",
                    "number": 8,
                    "slug": "origin",
                    "title": "Origin",
                    "path": ".ssot/specs/SPEC-0008-origin.yaml",
                    "origin": "ssot-origin",
                    "status": "draft",
                    "kind": "normative",
                    "adr_ids": [],
                    "supersedes": [],
                    "superseded_by": [],
                    "status_notes": [],
                }
            ],
        }

        failures = sync_packaged_docs.validate_number_ranges(registry)

        self.assertIn("ssot-origin adr id 0010 is outside reserved range 0600..0999", failures)
        self.assertIn("ssot-origin specs id 0008 is outside reserved range 0600..0999", failures)
        self.assertIn("Conflicting adr id 0010 is present in both ssot-origin and ssot-core upstream docs", failures)


if __name__ == "__main__":
    unittest.main()
