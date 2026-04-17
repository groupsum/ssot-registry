from __future__ import annotations

import unittest
from pathlib import Path

from ssot_registry.api.upgrade import migrate_v7_to_v8
from ssot_registry.model.registry import build_minimal_registry, default_paths
from tests.helpers import workspace_tempdir


class MigrateV7ToV8Tests(unittest.TestCase):
    def test_migration_renumbers_ssot_origin_documents(self) -> None:
        with workspace_tempdir() as temp_dir:
            repo = Path(temp_dir) / "repo"
            paths = default_paths()
            for relative in paths.values():
                (repo / relative).mkdir(parents=True, exist_ok=True)

            registry = build_minimal_registry(
                repo_id="repo:migrate-v8",
                repo_name="migrate-v8",
                version="1.0.0",
            )
            registry["schema_version"] = 7
            registry["adrs"] = [
                {
                    "id": "adr:0001",
                    "number": 1,
                    "slug": "canonical-json-registry",
                    "title": "Canonical registry is a single JSON document",
                    "path": ".ssot/adr/ADR-0001-canonical-json-registry.md",
                    "origin": "ssot-origin",
                    "managed": True,
                    "immutable": True,
                    "package_version": "0.2.3",
                    "content_sha256": "0" * 64,
                    "status": "draft",
                    "supersedes": [],
                    "superseded_by": [],
                    "status_notes": [],
                }
            ]
            registry["specs"] = [
                {
                    "id": "spc:0001",
                    "number": 1,
                    "slug": "registry-core",
                    "title": "Registry core",
                    "path": ".ssot/specs/SPEC-0001-registry-core.md",
                    "origin": "ssot-origin",
                    "managed": True,
                    "immutable": True,
                    "package_version": "0.2.3",
                    "content_sha256": "0" * 64,
                    "status": "draft",
                    "supersedes": [],
                    "superseded_by": [],
                    "status_notes": [],
                    "kind": "normative",
                }
            ]

            (repo / ".ssot" / "adr" / "ADR-0001-canonical-json-registry.md").write_text("# ADR-0001: Legacy\n", encoding="utf-8")
            (repo / ".ssot" / "specs" / "SPEC-0001-registry-core.md").write_text("# SPEC-0001: Legacy\n", encoding="utf-8")

            migrated = migrate_v7_to_v8(registry, repo, previous_version="0.2.3", target_version="0.2.4")

            self.assertEqual(8, migrated["schema_version"])
            adr_ids = {row["id"] for row in migrated["adrs"]}
            spec_ids = {row["id"] for row in migrated["specs"]}
            self.assertIn("adr:0600", adr_ids)
            self.assertIn("spc:0600", spec_ids)
            self.assertFalse((repo / ".ssot" / "adr" / "ADR-0001-canonical-json-registry.md").exists())
            self.assertFalse((repo / ".ssot" / "specs" / "SPEC-0001-registry-core.md").exists())
            self.assertTrue((repo / ".ssot" / "adr" / "ADR-0600-canonical-json-registry.md").exists())
            self.assertTrue((repo / ".ssot" / "specs" / "SPEC-0600-registry-core.md").exists())


if __name__ == "__main__":
    unittest.main()
