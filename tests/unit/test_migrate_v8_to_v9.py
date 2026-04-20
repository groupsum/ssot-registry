from __future__ import annotations

import json
import unittest
from pathlib import Path

from ssot_registry.api.upgrade import migrate_v8_to_v9
from ssot_registry.model.registry import build_minimal_registry, default_paths
from ssot_registry.util.document_io import load_document_yaml
from tests.helpers import workspace_tempdir


class MigrateV8ToV9Tests(unittest.TestCase):
    def test_migration_converts_markdown_documents_to_yaml(self) -> None:
        with workspace_tempdir() as temp_dir:
            repo = Path(temp_dir) / "repo"
            paths = default_paths()
            for relative in paths.values():
                (repo / relative).mkdir(parents=True, exist_ok=True)

            registry = build_minimal_registry(repo_id="repo:migrate-v9", repo_name="migrate-v9", version="1.0.0")
            registry["schema_version"] = 8
            registry["adrs"] = [
                {
                    "id": "adr:1000",
                    "number": 1000,
                    "slug": "local-decision",
                    "title": "Local decision",
                    "path": ".ssot/adr/ADR-1000-local-decision.md",
                    "origin": "repo-local",
                    "managed": False,
                    "immutable": False,
                    "package_version": "0.2.5",
                    "content_sha256": "0" * 64,
                    "status": "draft",
                    "supersedes": [],
                    "superseded_by": [],
                    "status_notes": [],
                }
            ]
            registry["specs"] = []
            source = repo / ".ssot" / "adr" / "ADR-1000-local-decision.md"
            source.write_text("# ADR-1000: Local decision\n\n## Decision\n\nUse YAML.\n", encoding="utf-8")

            migrated, summary = migrate_v8_to_v9(registry, repo, previous_version="0.2.5", target_version="0.2.5")

            self.assertEqual(9, migrated["schema_version"])
            self.assertEqual(["adr:1000"], summary["adr"]["converted"])
            self.assertFalse(source.exists())
            target = repo / ".ssot" / "adr" / "ADR-1000-local-decision.yaml"
            self.assertTrue(target.exists())
            payload = load_document_yaml(target)
            self.assertEqual("adr", payload["kind"])
            self.assertEqual("Use YAML.", payload["body"])

    def test_migration_keeps_existing_json_documents_valid(self) -> None:
        with workspace_tempdir() as temp_dir:
            repo = Path(temp_dir) / "repo"
            paths = default_paths()
            for relative in paths.values():
                (repo / relative).mkdir(parents=True, exist_ok=True)

            registry = build_minimal_registry(repo_id="repo:migrate-json", repo_name="migrate-json", version="1.0.0")
            registry["schema_version"] = 8
            registry["adrs"] = [
                {
                    "id": "adr:1000",
                    "number": 1000,
                    "slug": "local-decision",
                    "title": "Local decision",
                    "path": ".ssot/adr/ADR-1000-local-decision.json",
                    "origin": "repo-local",
                    "managed": False,
                    "immutable": False,
                    "package_version": "0.2.5",
                    "content_sha256": "0" * 64,
                    "status": "draft",
                    "supersedes": [],
                    "superseded_by": [],
                    "status_notes": [],
                }
            ]
            registry["specs"] = []
            source = repo / ".ssot" / "adr" / "ADR-1000-local-decision.json"
            source.write_text(
                json.dumps(
                    {
                        "schema_version": "0.1.0",
                        "kind": "adr",
                        "id": "adr:1000",
                        "number": 1000,
                        "slug": "local-decision",
                        "title": "Local decision",
                        "status": "draft",
                        "origin": "repo-local",
                        "decision_date": None,
                        "tags": [],
                        "summary": "Local decision",
                        "supersedes": [],
                        "superseded_by": [],
                        "status_notes": [],
                        "references": [],
                        "sections": {"decision": ["Use JSON."]},
                    },
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )

            migrated, summary = migrate_v8_to_v9(registry, repo, previous_version="0.2.5", target_version="0.2.5")

            self.assertEqual(9, migrated["schema_version"])
            self.assertEqual(["adr:1000"], summary["adr"]["converted"])
            self.assertTrue(source.exists())
            self.assertEqual(".ssot/adr/ADR-1000-local-decision.json", migrated["adrs"][0]["path"])
            payload = json.loads(source.read_text(encoding="utf-8"))
            self.assertEqual("Use JSON.", payload["body"])


if __name__ == "__main__":
    unittest.main()
