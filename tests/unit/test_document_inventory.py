from __future__ import annotations

import re
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
PATTERNS = {
    "adr": re.compile(r"^ADR-(?P<number>\d{4})-(?P<slug>[a-z0-9-]+)\.yaml$"),
    "specs": re.compile(r"^SPEC-(?P<number>\d{4})-(?P<slug>[a-z0-9-]+)\.yaml$"),
}
ORIGIN_ROOTS = {
    "adr": REPO_ROOT / "pkgs" / "ssot-contracts" / "src" / "ssot_contracts" / "templates" / "adr",
    "specs": REPO_ROOT / "pkgs" / "ssot-contracts" / "src" / "ssot_contracts" / "templates" / "specs",
}
CORE_ROOTS = {
    "adr": REPO_ROOT / ".ssot" / "adr",
    "specs": REPO_ROOT / ".ssot" / "specs",
}


def _numbers(root: Path, kind: str) -> set[int]:
    numbers: set[int] = set()
    for path in sorted(root.glob("*.yaml")):
        match = PATTERNS[kind].match(path.name)
        if match is None:
            raise AssertionError(f"Unexpected {kind} filename: {path.relative_to(REPO_ROOT).as_posix()}")
        numbers.add(int(match.group("number")))
    return numbers


class DocumentInventoryTests(unittest.TestCase):
    def test_ssot_origin_templates_use_reserved_range(self) -> None:
        for kind, root in ORIGIN_ROOTS.items():
            for number in _numbers(root, kind):
                self.assertGreaterEqual(number, 600)
                self.assertLessEqual(number, 999)

    def test_ssot_core_docs_use_reserved_range(self) -> None:
        for kind, root in CORE_ROOTS.items():
            for number in _numbers(root, kind):
                self.assertGreaterEqual(number, 1)
                self.assertLessEqual(number, 599)

    def test_ssot_core_and_ssot_origin_do_not_collide(self) -> None:
        for kind in ("adr", "specs"):
            self.assertEqual(set(), _numbers(ORIGIN_ROOTS[kind], kind) & _numbers(CORE_ROOTS[kind], kind))


if __name__ == "__main__":
    unittest.main()
