from __future__ import annotations

from ssot_contracts.generated.python.ids import ID_PATTERN


def is_normalized_id(value: str) -> bool:
    return bool(ID_PATTERN.match(value))


def filesystem_safe_id(value: str) -> str:
    return value.replace(":", "__")
