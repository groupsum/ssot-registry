from __future__ import annotations

import unittest
from pathlib import Path


class TemplateDocumentsYamlOnlyTests(unittest.TestCase):
    def test_template_document_trees_do_not_contain_markdown(self) -> None:
        root = Path(__file__).resolve().parents[2]
        template_roots = (
            root / "pkgs" / "ssot-contracts" / "src" / "ssot_contracts" / "templates",
            root / "pkgs" / "ssot-registry" / "src" / "ssot_registry" / "templates",
        )

        markdown_documents: list[str] = []
        for template_root in template_roots:
            for section in ("adr", "specs"):
                section_root = template_root / section
                markdown_documents.extend(
                    path.relative_to(root).as_posix()
                    for path in sorted(section_root.glob("*.md"))
                )

        self.assertEqual([], markdown_documents)


if __name__ == "__main__":
    unittest.main()
