from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CORE_SRC_ROOT = ROOT / "pkgs" / "ssot-core" / "src"
CONTRACTS_SRC_ROOT = ROOT / "pkgs" / "ssot-contracts" / "src"
for path in (CORE_SRC_ROOT, CONTRACTS_SRC_ROOT):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from ssot_registry.util.document_io import load_document_yaml


class TemplateDocumentsYamlCanonicalTests(unittest.TestCase):
    def test_contract_packaged_document_tree_does_not_contain_markdown(self) -> None:
        root = ROOT
        template_root = root / "pkgs" / "ssot-contracts" / "src" / "ssot_contracts" / "templates"

        markdown_documents: list[str] = []
        for section in ("adr", "specs"):
            section_root = template_root / section
            markdown_documents.extend(
                path.relative_to(root).as_posix()
                for path in sorted(section_root.glob("*.md"))
            )

        self.assertEqual([], markdown_documents)

    def test_contract_packaged_documents_parse_as_yaml(self) -> None:
        root = ROOT
        template_root = root / "pkgs" / "ssot-contracts" / "src" / "ssot_contracts" / "templates"

        for section in ("adr", "specs"):
            for path in sorted((template_root / section).glob("*.yaml")):
                payload = load_document_yaml(path)
                self.assertIsInstance(payload, dict, path.as_posix())

    def test_registry_runtime_does_not_duplicate_contract_document_trees(self) -> None:
        root = ROOT
        runtime_root = root / "pkgs" / "ssot-core" / "src" / "ssot_registry" / "templates"
        facade_root = root / "pkgs" / "ssot-registry" / "src"

        self.assertFalse((runtime_root / "adr").exists())
        self.assertFalse((runtime_root / "specs").exists())
        self.assertFalse(facade_root.exists())


if __name__ == "__main__":
    unittest.main()
