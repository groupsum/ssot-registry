from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import patch

from tests.helpers import PROJECT_ROOT, workspace_tempdir

sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

import update_readme_schema_badges


class UpdateReadmeSchemaBadgesTests(unittest.TestCase):
    def test_update_readme_rewrites_managed_badges_and_version_reference(self) -> None:
        with workspace_tempdir() as temp_dir:
            readme_path = Path(temp_dir) / "README.md"
            readme_path.write_text(
                "\n".join(
                    [
                        "<div>",
                        update_readme_schema_badges.BADGES_START,
                        "old badges",
                        update_readme_schema_badges.BADGES_END,
                        "</div>",
                        update_readme_schema_badges.VERSION_START,
                        "old version",
                        update_readme_schema_badges.VERSION_END,
                        "",
                    ]
                ),
                encoding="utf-8",
            )

            with patch.object(update_readme_schema_badges, "SCHEMA_VERSION", "9.9.9"):
                changed = update_readme_schema_badges.update_readme(readme_path)

            updated = readme_path.read_text(encoding="utf-8")
            self.assertTrue(changed)
            self.assertIn("schema_version-9.9.9-blue", updated)
            self.assertIn("migration%20coverage-9%2F9-brightgreen", updated)
            self.assertIn("Current registry `schema_version`: `9.9.9`.", updated)

    def test_update_readme_reports_no_change_when_current(self) -> None:
        with workspace_tempdir() as temp_dir:
            readme_path = Path(temp_dir) / "README.md"
            readme_path.write_text(
                "\n".join(
                    [
                        update_readme_schema_badges.render_badges(),
                        update_readme_schema_badges.render_version_reference(),
                        "",
                    ]
                ),
                encoding="utf-8",
            )

            self.assertFalse(update_readme_schema_badges.update_readme(readme_path))


if __name__ == "__main__":
    unittest.main()
