from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import re
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
UPSTREAM_REGISTRY_PATH = PROJECT_ROOT / ".ssot" / "registry.json"
PACKAGED_ROOTS = {
    "adr": PROJECT_ROOT / "pkgs" / "ssot-contracts" / "src" / "ssot_contracts" / "templates" / "adr",
    "specs": PROJECT_ROOT / "pkgs" / "ssot-contracts" / "src" / "ssot_contracts" / "templates" / "specs",
}
EXPECTED_RANGES = {
    "ssot-core": {"adr": (1, 599), "specs": (1, 599)},
    "ssot-origin": {"adr": (600, 999), "specs": (600, 999)},
}
SEMVER_PATTERN = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")


def _sha256_normalized_text(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def _load_registry(path: Path) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Registry payload must be an object: {path}")
    return payload


def _normalize_schema_version(value: object, fallback: int | str = 4) -> int | str:
    if isinstance(value, int):
        return value
    if isinstance(value, str) and SEMVER_PATTERN.match(value):
        return value
    return fallback


def _section_for_kind(kind: str) -> str:
    return "adrs" if kind == "adr" else "specs"


def _iter_packaged_files(directory: Path) -> list[Path]:
    files = [
        path
        for path in directory.iterdir()
        if path.is_file() and path.name != "manifest.json" and path.suffix.lower() in {".yaml", ".json"}
    ]
    return sorted(files)


def _load_existing_manifest(manifest_path: Path) -> dict[str, dict[str, object]]:
    if not manifest_path.exists():
        return {}
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError(f"Manifest must be a list: {manifest_path}")
    existing: dict[str, dict[str, object]] = {}
    for entry in payload:
        if isinstance(entry, dict) and isinstance(entry.get("id"), str):
            existing[str(entry["id"])] = entry
    return existing


def _origin_rows(registry: dict[str, object], kind: str) -> list[dict[str, object]]:
    rows = registry.get(_section_for_kind(kind), [])
    if not isinstance(rows, list):
        raise ValueError(f"{_section_for_kind(kind)} must be a list in {UPSTREAM_REGISTRY_PATH}")
    origin_rows = [row for row in rows if isinstance(row, dict) and row.get("origin") == "ssot-origin"]
    return sorted(origin_rows, key=lambda row: (int(row.get("number", 0)), str(row.get("id", ""))))


def _source_path(row: dict[str, object]) -> Path:
    relative_path = row.get("path")
    if not isinstance(relative_path, str) or not relative_path.strip():
        raise ValueError(f"Document row is missing path: {row.get('id', '<unknown>')}")
    return PROJECT_ROOT / relative_path


def _validate_source_rows(registry: dict[str, object], kind: str) -> list[str]:
    failures: list[str] = []
    start, end = EXPECTED_RANGES["ssot-origin"][kind]
    for row in _origin_rows(registry, kind):
        document_id = str(row.get("id", "<unknown>"))
        number = row.get("number")
        source_path = _source_path(row)
        if not isinstance(number, int):
            failures.append(f"{document_id} is missing integer number in upstream registry")
            continue
        if number < start or number > end:
            failures.append(f"ssot-origin {kind} id {number:04d} is outside reserved range {start:04d}..{end:04d}")
        if source_path.suffix.lower() != ".yaml":
            failures.append(f"{document_id} must use canonical .yaml source path in upstream registry")
        if not source_path.exists():
            failures.append(f"{document_id} source file is missing: {source_path.relative_to(PROJECT_ROOT).as_posix()}")
    return failures


def sync_packaged_files(
    registry: dict[str, object],
    kind: str,
    destination: Path,
    *,
    check: bool,
    prune: bool = True,
) -> list[str]:
    destination.mkdir(parents=True, exist_ok=True)
    failures: list[str] = []

    expected_files = {
        _source_path(row).name: _source_path(row)
        for row in _origin_rows(registry, kind)
    }
    existing_files = {path.name: path for path in _iter_packaged_files(destination)}

    for name, source_path in expected_files.items():
        destination_path = destination / name
        source_text = source_path.read_text(encoding="utf-8")
        if not destination_path.exists():
            if check:
                failures.append(f"Missing packaged doc: {destination_path.relative_to(PROJECT_ROOT).as_posix()}")
            else:
                shutil.copyfile(source_path, destination_path)
            continue
        destination_text = destination_path.read_text(encoding="utf-8")
        if destination_text != source_text:
            if check:
                failures.append(f"Packaged doc drift: {destination_path.relative_to(PROJECT_ROOT).as_posix()}")
            else:
                destination_path.write_text(source_text, encoding="utf-8", newline="\n")

    if prune:
        for name, destination_path in existing_files.items():
            if name in expected_files:
                continue
            if check:
                failures.append(f"Unexpected packaged doc: {destination_path.relative_to(PROJECT_ROOT).as_posix()}")
            else:
                destination_path.unlink()

    return failures


def _build_manifest_entry(
    row: dict[str, object],
    source_path: Path,
    kind: str,
    existing: dict[str, object],
    *,
    fallback_schema_version: int | str,
    fallback_version: str,
) -> dict[str, object]:
    entry = {
        "id": row["id"],
        "number": row["number"],
        "slug": row["slug"],
        "title": row["title"],
        "filename": source_path.name,
        "target_path": row["path"],
        "sha256": _sha256_normalized_text(source_path),
        "origin": "ssot-origin",
        "reservation_owner": "ssot-origin",
        "immutable": True,
        "minimum_schema_version": _normalize_schema_version(
            existing.get("minimum_schema_version", fallback_schema_version),
            fallback_schema_version,
        ),
        "introduced_in": str(existing.get("introduced_in", fallback_version)),
        "status": row.get("status", "draft"),
        "supersedes": list(row.get("supersedes", [])),
        "superseded_by": list(row.get("superseded_by", [])),
        "status_notes": list(row.get("status_notes", [])),
    }
    if kind == "specs":
        entry["kind"] = row.get("kind", "normative")
        adr_ids = list(row.get("adr_ids", []))
        if adr_ids:
            entry["adr_ids"] = adr_ids
    return entry


def sync_manifest(registry: dict[str, object], kind: str, destination: Path, *, check: bool) -> list[str]:
    manifest_path = destination / "manifest.json"
    existing_manifest = _load_existing_manifest(manifest_path)
    fallback_schema_version = _normalize_schema_version(registry.get("schema_version", 4))
    tooling = registry.get("tooling", {})
    fallback_version = str(tooling.get("ssot_registry_version", "0.2.1")) if isinstance(tooling, dict) else "0.2.1"

    manifest = [
        _build_manifest_entry(
            row,
            _source_path(row),
            kind,
            existing_manifest.get(str(row["id"]), {}),
            fallback_schema_version=fallback_schema_version,
            fallback_version=fallback_version,
        )
        for row in _origin_rows(registry, "adr" if kind == "adr" else "spec")
    ]

    expected_text = json.dumps(manifest, indent=2) + "\n"
    if manifest_path.exists() and manifest_path.read_text(encoding="utf-8") == expected_text:
        return []
    if check:
        return [f"Manifest drift: {manifest_path.relative_to(PROJECT_ROOT).as_posix()}"]
    manifest_path.write_text(expected_text, encoding="utf-8")
    return []


def validate_number_ranges(registry: dict[str, object]) -> list[str]:
    failures: list[str] = []
    inventory_numbers: dict[str, dict[str, set[int]]] = {"ssot-core": {"adr": set(), "specs": set()}, "ssot-origin": {"adr": set(), "specs": set()}}

    for kind in ("adr", "specs"):
        rows = registry.get(_section_for_kind(kind if kind == "adr" else "spec"), [])
        if not isinstance(rows, list):
            failures.append(f"{_section_for_kind(kind if kind == 'adr' else 'spec')} must be a list in upstream registry")
            continue
        for row in rows:
            if not isinstance(row, dict):
                continue
            origin = row.get("origin")
            if origin not in {"ssot-core", "ssot-origin"}:
                continue
            number = row.get("number")
            if not isinstance(number, int):
                failures.append(f"{row.get('id', '<unknown>')} is missing integer number in upstream registry")
                continue
            inventory_numbers[origin][kind].add(number)
            start, end = EXPECTED_RANGES[origin][kind]
            if number < start or number > end:
                failures.append(f"{origin} {kind} id {number:04d} is outside reserved range {start:04d}..{end:04d}")

    for kind in ("adr", "specs"):
        conflicts = sorted(inventory_numbers["ssot-origin"][kind] & inventory_numbers["ssot-core"][kind])
        for number in conflicts:
            failures.append(f"Conflicting {kind} id {number:04d} is present in both ssot-origin and ssot-core upstream docs")
    failures.extend(_validate_source_rows(registry, "adr"))
    failures.extend(_validate_source_rows(registry, "specs"))
    return failures


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Regenerate packaged ssot-origin docs/manifests from upstream .ssot inventory."
    )
    parser.add_argument("--check", action="store_true", help="Fail if packaged docs/manifests drift from upstream .ssot.")
    args = parser.parse_args()

    registry = _load_registry(UPSTREAM_REGISTRY_PATH)
    failures: list[str] = []
    failures.extend(validate_number_ranges(registry))
    for kind, destination in PACKAGED_ROOTS.items():
        failures.extend(sync_packaged_files(registry, kind, destination, check=args.check, prune=True))
        failures.extend(sync_manifest(registry, kind, destination, check=args.check))

    if failures:
        for failure in failures:
            print(failure)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
