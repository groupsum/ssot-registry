from __future__ import annotations

import json
from importlib import resources


def load_template_text(name: str) -> str:
    return resources.files(__package__).joinpath(name).read_text(encoding="utf-8")


def load_document_manifest(kind: str) -> list[dict[str, object]]:
    package = f"{__package__}.{ 'adr' if kind == 'adr' else 'specs' }"
    text = resources.files(package).joinpath("manifest.json").read_text(encoding="utf-8")
    manifest = json.loads(text)
    if not isinstance(manifest, list):
        raise ValueError(f"Packaged {kind} manifest must be a list")
    return manifest


def list_document_manifest_entries(kind: str) -> list[str]:
    return [str(entry["id"]) for entry in load_document_manifest(kind)]


def read_packaged_document_text(kind: str, filename: str) -> str:
    package = f"{__package__}.{ 'adr' if kind == 'adr' else 'specs' }"
    return resources.files(package).joinpath(filename).read_text(encoding="utf-8")


def read_packaged_document_bytes(kind: str, filename: str) -> bytes:
    package = f"{__package__}.{ 'adr' if kind == 'adr' else 'specs' }"
    return resources.files(package).joinpath(filename).read_bytes()
