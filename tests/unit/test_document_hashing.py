from __future__ import annotations

import unittest
from pathlib import Path

from ssot_registry.util.fs import sha256_normalized_text_path
from tests.helpers import workspace_tempdir


class DocumentHashingTests(unittest.TestCase):
    def test_normalized_hash_ignores_line_ending_style(self) -> None:
        temp_dir = workspace_tempdir()
        self.addCleanup(temp_dir.cleanup)
        root = Path(temp_dir.name)
        lf_path = root / "lf.md"
        crlf_path = root / "crlf.md"

        lf_path.write_text("# Example\n\nBody\n", encoding="utf-8", newline="\n")
        crlf_path.write_text("# Example\n\nBody\n", encoding="utf-8", newline="\r\n")

        self.assertEqual(sha256_normalized_text_path(lf_path), sha256_normalized_text_path(crlf_path))


if __name__ == "__main__":
    unittest.main()
