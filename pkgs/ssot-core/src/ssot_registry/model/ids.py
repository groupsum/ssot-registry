from __future__ import annotations

from ssot_contracts.generated.python.ids import ID_PATTERN, MAX_NORMALIZED_ID_LENGTH


def is_normalized_id(value: str) -> bool:
    return len(value) <= MAX_NORMALIZED_ID_LENGTH and bool(ID_PATTERN.match(value))


def filesystem_safe_id(value: str) -> str:
    return value.replace(":", "__")
