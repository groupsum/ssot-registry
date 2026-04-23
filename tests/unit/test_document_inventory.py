from __future__ import annotations

import json
import re
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
PATTERNS = {
    "adr": re.compile(r"^ADR-(?P<number>\d{4})-(?P<slug>[a-z0-9-]+)\.json$"),
    "specs": re.compile(r"^SPEC-(?P<number>\d{4})-(?P<slug>[a-z0-9-]+)\.json$"),
}
PACKAGED_ROOTS = {
    "adr": REPO_ROOT / "pkgs" / "ssot-contracts" / "src" / "ssot_contracts" / "templates" / "adr",
    "specs": REPO_ROOT / "pkgs" / "ssot-contracts" / "src" / "ssot_contracts" / "templates" / "specs",
}
UPSTREAM_REGISTRY = json.loads((REPO_ROOT / ".ssot" / "registry.json").read_text(encoding="utf-8"))


def _packaged_numbers(root: Path, kind: str) -> set[int]:
    numbers: set[int] = set()
    for path in sorted(root.glob("*.json")):
        if path.name == "manifest.json":
            continue
        match = PATTERNS[kind].match(path.name)
        if match is None:
            raise AssertionError(f"Unexpected {kind} filename: {path.relative_to(REPO_ROOT).as_posix()}")
        numbers.add(int(match.group("number")))
    return numbers


def _upstream_numbers(origin: str, kind: str) -> set[int]:
    section = "adrs" if kind == "adr" else "specs"
    rows = UPSTREAM_REGISTRY.get(section, [])
    if not isinstance(rows, list):
        raise AssertionError(f"Expected {section} to be a list in upstream registry")
    return {
        row["number"]
        for row in rows
        if isinstance(row, dict) and row.get("origin") == origin and isinstance(row.get("number"), int)
    }


class DocumentInventoryTests(unittest.TestCase):
    def test_packaged_ssot_origin_templates_use_reserved_range(self) -> None:
        for kind, root in PACKAGED_ROOTS.items():
            for number in _packaged_numbers(root, kind):
                self.assertGreaterEqual(number, 600)
                self.assertLessEqual(number, 999)

    def test_upstream_ssot_core_docs_use_reserved_range(self) -> None:
        for kind in ("adr", "specs"):
            for number in _upstream_numbers("ssot-core", kind):
                self.assertGreaterEqual(number, 1)
                self.assertLessEqual(number, 599)

    def test_packaged_ssot_origin_inventory_matches_upstream_filter(self) -> None:
        for kind in ("adr", "specs"):
            self.assertEqual(_upstream_numbers("ssot-origin", kind), _packaged_numbers(PACKAGED_ROOTS[kind], kind))

    def test_packaged_ssot_origin_and_upstream_ssot_core_do_not_collide(self) -> None:
        for kind in ("adr", "specs"):
            self.assertEqual(set(), _packaged_numbers(PACKAGED_ROOTS[kind], kind) & _upstream_numbers("ssot-core", kind))


if __name__ == "__main__":
    unittest.main()
