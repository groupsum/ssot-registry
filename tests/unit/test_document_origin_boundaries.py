from __future__ import annotations

import json
import unittest
from pathlib import Path

from ssot_registry.api import create_document, initialize_repo, sync_documents
from ssot_registry.model.registry import build_minimal_registry, default_paths
from ssot_registry.util.errors import ValidationError
from ssot_registry.util.jsonio import save_json
from tests.helpers import workspace_tempdir


class DocumentOriginBoundaryTests(unittest.TestCase):
    def _make_upstream_repo(self, repo: Path) -> Path:
        paths = default_paths()
        for relative in paths.values():
            (repo / relative).mkdir(parents=True, exist_ok=True)
        registry = build_minimal_registry(
            repo_id="repo:upstream-test",
            repo_name="upstream-test",
            version="1.0.0",
            repo_kind="ssot-upstream",
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

    def test_upstream_sync_is_skipped(self) -> None:
        with workspace_tempdir() as temp_dir:
            repo = Path(temp_dir) / "repo"
            self._make_upstream_repo(repo)

            result = sync_documents(repo, "adr")
            self.assertTrue(result["passed"])
            self.assertTrue(result.get("skipped"))
            self.assertEqual([], result["created"])
            self.assertEqual([], result["updated"])

    def test_upstream_can_create_ssot_origin_with_explicit_reserved_number(self) -> None:
        with workspace_tempdir() as temp_dir:
            repo = Path(temp_dir) / "repo"
            registry_path = self._make_upstream_repo(repo)
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
            self.assertEqual("ssot-upstream", registry["repo"]["kind"])


if __name__ == "__main__":
    unittest.main()
