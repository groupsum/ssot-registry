from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import re
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
ORIGIN_MIRRORS = (
    (
        PROJECT_ROOT / "pkgs" / "ssot-contracts" / "src" / "ssot_contracts" / "templates" / "adr",
        PROJECT_ROOT / "pkgs" / "ssot-registry" / "src" / "ssot_registry" / "templates" / "adr",
    ),
    (
        PROJECT_ROOT / "pkgs" / "ssot-contracts" / "src" / "ssot_contracts" / "templates" / "specs",
        PROJECT_ROOT / "pkgs" / "ssot-registry" / "src" / "ssot_registry" / "templates" / "specs",
    ),
)
FILENAME_PATTERNS = {
    "adr": re.compile(r"^ADR-(?P<number>\d{4})-(?P<slug>[a-z0-9-]+)\.yaml$"),
    "specs": re.compile(r"^SPEC-(?P<number>\d{4})-(?P<slug>[a-z0-9-]+)\.yaml$"),
}
EXPECTED_RANGES = {
    "ssot-core": {"adr": (1, 599), "specs": (1, 599)},
    "ssot-origin": {"adr": (600, 999), "specs": (600, 999)},
}
ORIGIN_ROOTS = {
    "adr": PROJECT_ROOT / "pkgs" / "ssot-contracts" / "src" / "ssot_contracts" / "templates" / "adr",
    "specs": PROJECT_ROOT / "pkgs" / "ssot-contracts" / "src" / "ssot_contracts" / "templates" / "specs",
}
CORE_ROOTS = {
    "adr": PROJECT_ROOT / ".ssot" / "adr",
    "specs": PROJECT_ROOT / ".ssot" / "specs",
}


def _iter_documents(directory: Path) -> list[Path]:
    return sorted(path for path in directory.glob("*.yaml") if path.is_file())


def _iter_mirror_files(directory: Path) -> list[Path]:
    paths = list(_iter_documents(directory))
    paths.extend(path for path in directory.glob("*.json") if path.is_file())
    return sorted(paths)


def _sha256_normalized_text(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def _load_document_payload(path: Path) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Document payload must be an object: {path}")
    return payload


def _extract_title(path: Path, kind: str, slug: str) -> str:
    payload = _load_document_payload(path)
    title = payload.get("title")
    return str(title) if isinstance(title, str) and title.strip() else slug.replace("-", " ").title()


def _extract_status(path: Path) -> str:
    payload = _load_document_payload(path)
    status = payload.get("status")
    return str(status).lower() if isinstance(status, str) and status.strip() else "draft"


def _load_existing_manifest(manifest_path: Path) -> dict[str, dict[str, object]]:
    if not manifest_path.exists():
        return {}
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError(f"Manifest must be a list: {manifest_path}")
    existing: dict[str, dict[str, object]] = {}
    for entry in payload:
        if isinstance(entry, dict):
            slug = entry.get("slug")
            if isinstance(slug, str):
                existing[slug] = entry
    return existing


def _build_manifest_entry(path: Path, kind: str, existing: dict[str, object]) -> dict[str, object]:
    match = FILENAME_PATTERNS[kind].match(path.name)
    if match is None:
        raise ValueError(f"Invalid {kind} filename: {path}")
    number = int(match.group("number"))
    slug = match.group("slug")
    target_dir = "adr" if kind == "adr" else "specs"
    entity_prefix = "adr" if kind == "adr" else "spc"
    entry = {
        "id": f"{entity_prefix}:{number:04d}",
        "number": number,
        "slug": slug,
        "title": _extract_title(path, kind, slug),
        "filename": path.name,
        "target_path": f".ssot/{target_dir}/{path.name}",
        "sha256": _sha256_normalized_text(path),
        "origin": "ssot-origin",
        "reservation_owner": "ssot-origin",
        "immutable": True,
        "minimum_schema_version": int(existing.get("minimum_schema_version", 4)),
        "introduced_in": str(existing.get("introduced_in", "0.2.1")),
        "status": _extract_status(path),
        "supersedes": list(existing.get("supersedes", [])),
        "superseded_by": list(existing.get("superseded_by", [])),
        "status_notes": list(existing.get("status_notes", [])),
    }
    if kind == "specs":
        entry["kind"] = str(existing.get("kind", "normative"))
    return entry


def sync_manifest(source: Path, kind: str, *, check: bool) -> list[str]:
    manifest_path = source / "manifest.json"
    existing_manifest = _load_existing_manifest(manifest_path)
    manifest = [
        _build_manifest_entry(path, kind, existing_manifest.get(FILENAME_PATTERNS[kind].match(path.name).group("slug"), {}))
        for path in _iter_documents(source)
    ]
    expected_text = json.dumps(manifest, indent=2) + "\n"
    if manifest_path.exists() and manifest_path.read_text(encoding="utf-8") == expected_text:
        return []
    if check:
        return [f"Manifest drift: {manifest_path.relative_to(PROJECT_ROOT).as_posix()}"]
    manifest_path.write_text(expected_text, encoding="utf-8")
    return []


def sync_mirror(source: Path, destination: Path, *, check: bool, prune: bool = False) -> list[str]:
    destination.mkdir(parents=True, exist_ok=True)
    failures: list[str] = []

    source_files = {path.name: path for path in _iter_mirror_files(source)}
    destination_files = {path.name: path for path in _iter_mirror_files(destination)}

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

    if prune:
        for name, destination_path in destination_files.items():
            if name in source_files:
                continue
            if check:
                failures.append(f"Unexpected mirrored doc: {destination_path.relative_to(PROJECT_ROOT).as_posix()}")
            else:
                destination_path.unlink()

    return failures


def _collect_numbers(directory: Path, kind: str) -> tuple[set[int], list[str]]:
    failures: list[str] = []
    numbers: set[int] = set()
    pattern = FILENAME_PATTERNS[kind]
    for path in _iter_documents(directory):
        match = pattern.match(path.name)
        if match is None:
            failures.append(f"Invalid {kind} filename: {path.relative_to(PROJECT_ROOT).as_posix()}")
            continue
        numbers.add(int(match.group("number")))
    return numbers, failures


def validate_number_ranges() -> list[str]:
    failures: list[str] = []
    inventory_numbers: dict[str, dict[str, set[int]]] = {"ssot-core": {}, "ssot-origin": {}}

    for owner, roots in (("ssot-core", CORE_ROOTS), ("ssot-origin", ORIGIN_ROOTS)):
        for kind, root in roots.items():
            numbers, parse_failures = _collect_numbers(root, kind)
            failures.extend(parse_failures)
            inventory_numbers[owner][kind] = numbers
            start, end = EXPECTED_RANGES[owner][kind]
            for number in sorted(numbers):
                if number < start or number > end:
                    failures.append(
                        f"{owner} {kind} id {number:04d} is outside reserved range {start:04d}..{end:04d}"
                    )

    for kind in ("adr", "specs"):
        conflicts = sorted(inventory_numbers["ssot-origin"][kind] & inventory_numbers["ssot-core"][kind])
        for number in conflicts:
            failures.append(
                f"Conflicting {kind} id {number:04d} is present in both ssot-origin templates and ssot-core docs"
            )
    return failures


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Sync packaged ssot-origin docs/manifests and verify ADR/SPEC inventory boundaries."
    )
    parser.add_argument("--check", action="store_true", help="Fail if mirrors or inventory boundaries drift.")
    args = parser.parse_args()

    failures: list[str] = []
    for kind, source in ORIGIN_ROOTS.items():
        failures.extend(sync_manifest(source, kind, check=args.check))
    for source, destination in ORIGIN_MIRRORS:
        failures.extend(sync_mirror(source, destination, check=args.check, prune=True))
    failures.extend(validate_number_ranges())

    if failures:
        for failure in failures:
            print(failure)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
