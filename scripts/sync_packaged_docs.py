from __future__ import annotations

import argparse
import shutil
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MIRRORS = (
    (PROJECT_ROOT / "pkgs" / "ssot-contracts" / "src" / "ssot_contracts" / "templates" / "adr", PROJECT_ROOT / "docs" / "adr"),
    (PROJECT_ROOT / "pkgs" / "ssot-contracts" / "src" / "ssot_contracts" / "templates" / "specs", PROJECT_ROOT / "docs" / "specs"),
)


def _iter_markdown(directory: Path) -> list[Path]:
    return sorted(path for path in directory.glob("*.md") if path.is_file())


def sync_mirror(source: Path, destination: Path, *, check: bool) -> list[str]:
    destination.mkdir(parents=True, exist_ok=True)
    failures: list[str] = []

    source_files = {path.name: path for path in _iter_markdown(source)}
    destination_files = {path.name: path for path in _iter_markdown(destination)}

    for name, source_path in source_files.items():
        destination_path = destination / name
        source_text = source_path.read_text(encoding="utf-8")
        if not destination_path.exists():
            if check:
                failures.append(f"Missing mirrored doc: {destination_path.relative_to(PROJECT_ROOT).as_posix()}")
            else:
                shutil.copyfile(source_path, destination_path)
            continue

        destination_text = destination_path.read_text(encoding="utf-8")
        if destination_text != source_text:
            if check:
                failures.append(f"Doc mirror drift: {destination_path.relative_to(PROJECT_ROOT).as_posix()}")
            else:
                destination_path.write_text(source_text, encoding="utf-8")

    for name, destination_path in destination_files.items():
        if name in source_files:
            continue
        if check:
            failures.append(f"Unexpected mirrored doc: {destination_path.relative_to(PROJECT_ROOT).as_posix()}")
        else:
            destination_path.unlink()

    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description="Sync or verify docs/ mirrors for packaged ADRs and specs.")
    parser.add_argument("--check", action="store_true", help="Fail if docs/ differs from packaged templates.")
    args = parser.parse_args()

    failures: list[str] = []
    for source, destination in MIRRORS:
        failures.extend(sync_mirror(source, destination, check=args.check))

    if failures:
        for failure in failures:
            print(failure)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
