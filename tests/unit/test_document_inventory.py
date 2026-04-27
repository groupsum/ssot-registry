from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

from ssot_registry.util.fs import sha256_normalized_text_path


REPO_ROOT = Path(__file__).resolve().parents[2]
PATTERNS = {
    "adr": re.compile(r"^ADR-(?P<number>\d{4})-(?P<slug>[a-z0-9-]+)\.yaml$"),
    "specs": re.compile(r"^SPEC-(?P<number>\d{4})-(?P<slug>[a-z0-9-]+)\.yaml$"),
}
PACKAGED_ROOTS = {
    "adr": REPO_ROOT / "pkgs" / "ssot-contracts" / "src" / "ssot_contracts" / "templates" / "adr",
    "specs": REPO_ROOT / "pkgs" / "ssot-contracts" / "src" / "ssot_contracts" / "templates" / "specs",
}
UPSTREAM_REGISTRY = json.loads((REPO_ROOT / ".ssot" / "registry.json").read_text(encoding="utf-8"))


def _packaged_numbers(root: Path, kind: str) -> set[int]:
    numbers: set[int] = set()
    for path in sorted(root.glob("*.yaml")):
        if path.name == "manifest.json":
            continue
        match = PATTERNS[kind].match(path.name)
        if match is None:
            raise AssertionError(f"Unexpected {kind} filename: {path.relative_to(REPO_ROOT).as_posix()}")
        numbers.add(int(match.group("number")))
    return numbers


def _manifest_rows(root: Path) -> list[dict[str, object]]:
    return json.loads((root / "manifest.json").read_text(encoding="utf-8"))


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

    def test_packaged_manifest_entries_match_files_and_checksums(self) -> None:
        for kind, root in PACKAGED_ROOTS.items():
            prefix = "adr" if kind == "adr" else "spc"
            seen_ids: set[str] = set()
            seen_numbers: set[int] = set()
            for row in _manifest_rows(root):
                document_id = row["id"]
                number = row["number"]
                filename = row["filename"]
                target_path = row["target_path"]

                self.assertNotIn(document_id, seen_ids)
                self.assertNotIn(number, seen_numbers)
                seen_ids.add(document_id)
                seen_numbers.add(number)

                self.assertEqual(document_id, f"{prefix}:{number:04d}")
                self.assertEqual(row["origin"], "ssot-origin")
                self.assertEqual(Path(target_path).name, filename)

                path = root / str(filename)
                self.assertTrue(path.exists(), path)
                self.assertEqual(row["sha256"], sha256_normalized_text_path(path))


if __name__ == "__main__":
    unittest.main()
