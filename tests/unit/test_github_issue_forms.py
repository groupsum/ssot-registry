from __future__ import annotations

import re
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
FORM = ".github/ISSUE_TEMPLATE/bug_report.yml"
CONFIG = ".github/ISSUE_TEMPLATE/config.yml"

REQUIRED_FIELD_IDS = (
    "command",
    "expected-behavior",
    "actual-behavior",
    "ssot-versions",
    "python-version",
    "os",
    "minimal-reproduction",
)

_FIELD_ID_RE = re.compile(r"^ {4}id: (\S+)$", re.MULTILINE)


def _read(path: str) -> str:
    return (REPO_ROOT / path).read_text(encoding="utf-8")


def _field_blocks() -> dict[str, str]:
    """Map each body item's ``id`` to the raw YAML block that declares it."""
    body = _read(FORM).split("\nbody:\n", 1)[1]
    blocks: dict[str, str] = {}
    for block in body.split("\n  - ")[1:]:
        match = _FIELD_ID_RE.search(block)
        if match is not None:
            blocks[match.group(1)] = block
    return blocks


class GitHubIssueFormTests(unittest.TestCase):
    def test_bug_report_form_exists(self) -> None:
        self.assertTrue((REPO_ROOT / FORM).is_file(), FORM)

    def test_bug_report_form_has_required_top_level_keys(self) -> None:
        form = _read(FORM)
        for key in ("name", "description", "body"):
            self.assertIn(f"\n{key}:", f"\n{form}", key)

    def test_bug_report_form_declares_every_acceptance_criteria_field(self) -> None:
        declared = _field_blocks()
        for field_id in REQUIRED_FIELD_IDS:
            self.assertIn(field_id, declared, field_id)

    def test_bug_report_form_requires_every_acceptance_criteria_field(self) -> None:
        declared = _field_blocks()
        for field_id in REQUIRED_FIELD_IDS:
            self.assertIn("required: true", declared[field_id], field_id)

    def test_bug_report_form_keeps_supplementary_fields_optional(self) -> None:
        declared = _field_blocks()
        optional = set(declared) - set(REQUIRED_FIELD_IDS)
        self.assertEqual(optional, {"additional-context"})
        for field_id in optional:
            self.assertNotIn("required: true", declared[field_id], field_id)

    def test_bug_report_form_references_version_report_commands(self) -> None:
        declared = _field_blocks()
        self.assertIn("ssot --version", declared["ssot-versions"])
        self.assertIn("python --version", declared["python-version"])

    def test_issue_template_config_disables_blank_issues(self) -> None:
        self.assertTrue((REPO_ROOT / CONFIG).is_file(), CONFIG)
        self.assertIn("blank_issues_enabled: false", _read(CONFIG))


if __name__ == "__main__":
    unittest.main()
