from __future__ import annotations

import re
from pathlib import Path
from typing import Any, TypedDict

from ssot_contracts import load_document_manifest as contracts_load_document_manifest
from ssot_contracts import read_packaged_document_bytes as contracts_read_packaged_document_bytes
from ssot_contracts import read_packaged_document_text as contracts_read_packaged_document_text
from ssot_contracts.contract_data import CONTRACT_DATA


DOCUMENT_KINDS = ("adr", "spec")
DOCUMENT_SECTIONS = CONTRACT_DATA["document_contract"]["sections"]
DOCUMENT_ID_PREFIXES = {"adr": "adr:", "spec": "spc:"}
DOCUMENT_FILENAME_PREFIXES = CONTRACT_DATA["document_contract"]["filename_prefixes"]
DOCUMENT_PATH_KEYS = CONTRACT_DATA["document_contract"]["path_keys"]
DOCUMENT_RESERVATION_KEYS = CONTRACT_DATA["document_contract"]["reservation_keys"]
DOCUMENT_ORIGINS = {"ssot-core", "ssot-origin", "repo-local"}
DOCUMENT_STATUSES = tuple(CONTRACT_DATA["choice_sets"]["document_statuses"])
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
SPEC_KINDS = set(CONTRACT_DATA["choice_sets"]["spec_kinds"])
DOCUMENT_SLUG_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
DOCUMENT_FILENAME_PATTERNS = {
    "adr": re.compile(r"^ADR-(?P<number>\d{4})-(?P<slug>[a-z0-9-]+)\.yaml$"),
    "spec": re.compile(r"^SPEC-(?P<number>\d{4})-(?P<slug>[a-z0-9-]+)\.yaml$"),
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
    return f"{DOCUMENT_FILENAME_PREFIXES[kind]}-{format_document_number(number)}-{slug}.yaml"


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
    reservations = CONTRACT_DATA["document_contract"]["default_reservations"]
    return {
        "adr": [dict(row) for row in reservations["adr"]],
        "spec": [dict(row) for row in reservations["spec"]],
    }


def load_document_manifest(kind: str) -> list[dict[str, Any]]:
    return contracts_load_document_manifest(kind)


def read_packaged_document_text(kind: str, filename: str) -> str:
    return contracts_read_packaged_document_text(kind, filename)


def read_packaged_document_bytes(kind: str, filename: str) -> bytes:
    return contracts_read_packaged_document_bytes(kind, filename)
