from __future__ import annotations

from importlib import resources


def list_schema_names() -> list[str]:
    return sorted(entry.name for entry in resources.files(__package__).iterdir() if entry.name.endswith(".json"))


def load_schema_text(name: str) -> str:
    return resources.files(__package__).joinpath(name).read_text(encoding="utf-8")
