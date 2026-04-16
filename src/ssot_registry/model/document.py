from __future__ import annotations

import re
from importlib import resources
import json
from pathlib import Path
from typing import Any, TypedDict


DOCUMENT_KINDS = ("adr", "spec")
DOCUMENT_SECTIONS = {
    "adr": "adrs",
    "spec": "specs",
}
DOCUMENT_ID_PREFIXES = {
    "adr": "adr:",
    "spec": "spc:",
}
DOCUMENT_FILENAME_PREFIXES = {
    "adr": "ADR",
    "spec": "SPEC",
}
DOCUMENT_PATH_KEYS = {
    "adr": "adr_root",
    "spec": "spec_root",
}
DOCUMENT_TEMPLATE_PACKAGES = {
    "adr": "ssot_registry.templates.adr",
    "spec": "ssot_registry.templates.specs",
}
DOCUMENT_RESERVATION_KEYS = {
    "adr": "adr",
    "spec": "spec",
}
DOCUMENT_ORIGINS = {"ssot-core", "ssot-origin", "repo-local"}
DOCUMENT_STATUSES = ("draft", "in_review", "accepted", "rejected", "superseded", "withdrawn", "retired")
CREATE_ALLOWED_STATUSES = ("draft", "in_review", "accepted", "rejected", "withdrawn")
TERMINAL_STATUSES = ("rejected", "withdrawn", "superseded", "retired")
TRANSITION_RULES = {
    "draft": {"in_review", "accepted", "rejected", "withdrawn"},
    "in_review": {"draft", "accepted", "rejected", "withdrawn"},
    "accepted": {"superseded", "retired"},
    "rejected": set(),
    "withdrawn": set(),
    "superseded": set(),
    "retired": set(),
}
SPEC_KINDS = {"normative", "operational", "governance", "local-policy"}
DOCUMENT_SLUG_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
DOCUMENT_FILENAME_PATTERNS = {
    "adr": re.compile(r"^ADR-(?P<number>\d{4})-(?P<slug>[a-z0-9-]+)\.md$"),
    "spec": re.compile(r"^SPEC-(?P<number>\d{4})-(?P<slug>[a-z0-9-]+)\.md$"),
}
DEFAULT_SSOT_ORIGIN_RANGE = {
    "owner": "ssot-origin",
    "start": 1,
    "end": 499,
    "immutable": True,
    "deletable": False,
    "assignable_by_repo": False,
}
DEFAULT_SSOT_CORE_RANGE = {
    "owner": "ssot-core",
    "start": 500,
    "end": 999,
    "immutable": True,
    "deletable": False,
    "assignable_by_repo": False,
}
DEFAULT_REPO_LOCAL_RANGE = {
    "owner": "repo-local-default",
    "start": 1000,
    "end": 4999,
    "immutable": False,
    "deletable": True,
    "assignable_by_repo": True,
}


class StatusNote(TypedDict, total=False):
    status: str
    note: str
    at: str
    actor: str
    reason: str


def format_document_number(number: int) -> str:
    return f"{number:04d}"


def normalize_document_id(kind: str, number: int) -> str:
    return f"{DOCUMENT_ID_PREFIXES[kind]}{format_document_number(number)}"


def build_document_filename(kind: str, number: int, slug: str) -> str:
    return f"{DOCUMENT_FILENAME_PREFIXES[kind]}-{format_document_number(number)}-{slug}.md"


def build_document_path(paths: dict[str, str], kind: str, number: int, slug: str) -> str:
    root = paths[DOCUMENT_PATH_KEYS[kind]].strip("/\\")
    return Path(root, build_document_filename(kind, number, slug)).as_posix()


def parse_document_filename(kind: str, filename: str) -> tuple[int, str] | None:
    match = DOCUMENT_FILENAME_PATTERNS[kind].match(filename)
    if match is None:
        return None
    return int(match.group("number")), match.group("slug")


def reservation_kind_key(kind: str) -> str:
    return DOCUMENT_RESERVATION_KEYS[kind]


def section_for_document_kind(kind: str) -> str:
    return DOCUMENT_SECTIONS[kind]


def default_document_id_reservations() -> dict[str, list[dict[str, Any]]]:
    return {
        "adr": [dict(DEFAULT_SSOT_ORIGIN_RANGE), dict(DEFAULT_SSOT_CORE_RANGE), dict(DEFAULT_REPO_LOCAL_RANGE)],
        "spec": [dict(DEFAULT_SSOT_ORIGIN_RANGE), dict(DEFAULT_SSOT_CORE_RANGE), dict(DEFAULT_REPO_LOCAL_RANGE)],
    }


def load_document_manifest(kind: str) -> list[dict[str, Any]]:
    manifest_text = resources.files(DOCUMENT_TEMPLATE_PACKAGES[kind]).joinpath("manifest.json").read_text(encoding="utf-8")
    manifest = json.loads(manifest_text)
    if not isinstance(manifest, list):
        raise ValueError(f"Packaged {kind} manifest must be a list")
    return manifest


def read_packaged_document_text(kind: str, filename: str) -> str:
    return resources.files(DOCUMENT_TEMPLATE_PACKAGES[kind]).joinpath(filename).read_text(encoding="utf-8")


def read_packaged_document_bytes(kind: str, filename: str) -> bytes:
    return resources.files(DOCUMENT_TEMPLATE_PACKAGES[kind]).joinpath(filename).read_bytes()
