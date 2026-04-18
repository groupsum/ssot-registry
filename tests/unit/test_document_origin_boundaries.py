from __future__ import annotations

import json
import unittest
from pathlib import Path

from ssot_registry.api import create_document, initialize_repo, sync_documents
from ssot_registry.model.registry import build_minimal_registry, default_paths, legacy_repo_kinds_allowed
from ssot_registry.util.errors import ValidationError
from ssot_registry.util.jsonio import save_json
from tests.helpers import workspace_tempdir


class DocumentOriginBoundaryTests(unittest.TestCase):
    def test_legacy_repo_kinds_are_rejected_at_0_3_0_and_later(self) -> None:
        self.assertTrue(legacy_repo_kinds_allowed("0.2.6.dev1"))
        self.assertFalse(legacy_repo_kinds_allowed("0.3.0"))
        self.assertFalse(legacy_repo_kinds_allowed("0.3.1"))

    def _make_core_repo(self, repo: Path) -> Path:
        paths = default_paths()
        for relative in paths.values():
            (repo / relative).mkdir(parents=True, exist_ok=True)
        registry = build_minimal_registry(
            repo_id="repo:core-test",
            repo_name="core-test",
            version="1.0.0",
            repo_kind="ssot-core",
        )
        registry_path = repo / paths["ssot_root"] / "registry.json"
        save_json(registry_path, registry)
        return registry_path

    def test_operator_repo_cannot_create_ssot_origin_rows(self) -> None:
        with workspace_tempdir() as temp_dir:
            repo = Path(temp_dir) / "repo"
            initialize_repo(repo, repo_id="repo:operator-create", repo_name="operator-create", version="1.0.0")
            body = repo / "body.md"
            body.write_text("Operator body\n", encoding="utf-8")

            with self.assertRaises(ValidationError):
                create_document(
                    repo,
                    "adr",
                    title="Should fail",
                    slug="should-fail",
                    body_file=body,
                    origin="ssot-origin",
                    number=620,
                )

    def test_ssot_core_sync_is_skipped(self) -> None:
        with workspace_tempdir() as temp_dir:
            repo = Path(temp_dir) / "repo"
            self._make_core_repo(repo)

            result = sync_documents(repo, "adr")
            self.assertTrue(result["passed"])
            self.assertTrue(result.get("skipped"))
            self.assertEqual([], result["created"])
            self.assertEqual([], result["updated"])

    def test_ssot_core_can_create_ssot_origin_with_explicit_reserved_number(self) -> None:
        with workspace_tempdir() as temp_dir:
            repo = Path(temp_dir) / "repo"
            registry_path = self._make_core_repo(repo)
            body = repo / "body.md"
            body.write_text("Upstream authored body\n", encoding="utf-8")

            result = create_document(
                repo,
                "spec",
                title="Upstream Contract",
                slug="upstream-contract",
                body_file=body,
                origin="ssot-origin",
                number=601,
            )

            self.assertTrue(result["passed"])
            row = result["document"]
            self.assertEqual("ssot-origin", row["origin"])
            self.assertFalse(row["managed"])
            self.assertFalse(row["immutable"])
            self.assertEqual("governance", row["kind"])

            registry = json.loads(registry_path.read_text(encoding="utf-8"))
            self.assertEqual("ssot-core", registry["repo"]["kind"])


if __name__ == "__main__":
    unittest.main()
