from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import quote


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CORE_SRC_ROOT = PROJECT_ROOT / "pkgs" / "ssot-core" / "src"
CONTRACTS_SRC_ROOT = PROJECT_ROOT / "pkgs" / "ssot-contracts" / "src"

for source_root in (CORE_SRC_ROOT, CONTRACTS_SRC_ROOT):
    source_path = str(source_root)
    if source_path not in sys.path:
        sys.path.insert(0, source_path)

from ssot_registry.api.upgrade import MIGRATION_PATHS
from ssot_registry.model.enums import SCHEMA_VERSION


BADGES_START = "<!-- ssot-schema-badges:start -->"
BADGES_END = "<!-- ssot-schema-badges:end -->"
VERSION_START = "<!-- ssot-schema-version:start -->"
VERSION_END = "<!-- ssot-schema-version:end -->"


def migration_coverage_label() -> str:
    implemented = len({name for _source, _target, name in MIGRATION_PATHS})
    expected = len(MIGRATION_PATHS)
    return f"{implemented}/{expected}"


def _badge_url(label: str, message: str, color: str) -> str:
    return f"https://img.shields.io/badge/{quote(label, safe='')}-{quote(message, safe='')}-{color}"


def render_badges() -> str:
    coverage = migration_coverage_label()
    coverage_color = "brightgreen" if coverage.split("/", 1)[0] == coverage.split("/", 1)[1] else "yellow"
    schema_url = _badge_url("schema_version", SCHEMA_VERSION, "blue")
    coverage_url = _badge_url("migration coverage", coverage, coverage_color)
    return "\n".join(
        [
            BADGES_START,
            f'  <img src="{schema_url}" alt="schema_version {SCHEMA_VERSION}" />',
            f'  <img src="{coverage_url}" alt="Migration coverage {coverage}" />',
            BADGES_END,
        ]
    )


def render_version_reference() -> str:
    return "\n".join(
        [
            VERSION_START,
            f"Current registry `schema_version`: `{SCHEMA_VERSION}`.",
            VERSION_END,
        ]
    )


def replace_managed_block(text: str, start: str, end: str, replacement: str) -> str:
    pattern = re.compile(rf"{re.escape(start)}.*?{re.escape(end)}", re.DOTALL)
    if not pattern.search(text):
        raise ValueError(f"Missing managed README block: {start} ... {end}")
    return pattern.sub(replacement, text, count=1)


def update_readme(readme_path: Path = PROJECT_ROOT / "README.md") -> bool:
    original = readme_path.read_text(encoding="utf-8")
    updated = replace_managed_block(original, BADGES_START, BADGES_END, render_badges())
    updated = replace_managed_block(updated, VERSION_START, VERSION_END, render_version_reference())
    if updated == original:
        return False
    readme_path.write_text(updated, encoding="utf-8", newline="\n")
    return True


def main() -> int:
    changed = update_readme()
    print(f"README.md {'updated' if changed else 'already current'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
