from __future__ import annotations

import unittest
from pathlib import Path

from scripts.sync_packaged_docs import sync_mirror
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

        (source / "ADR-0001-example.md").write_text("# Example\n", encoding="utf-8")
        (destination / "ADR-0001-example.md").write_text("# Example\n", encoding="utf-8")
        (destination / "ADR-0500-repo-local.md").write_text("# Repo Local\n", encoding="utf-8")

        failures = sync_mirror(source, destination, check=True)

        self.assertEqual(failures, [])


if __name__ == "__main__":
    unittest.main()
