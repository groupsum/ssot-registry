from __future__ import annotations

import re

ID_PATTERN = re.compile(r"^[a-z][a-z0-9-]*:[a-z0-9][a-z0-9._-]*$")


def is_normalized_id(value: str) -> bool:
    return bool(ID_PATTERN.match(value))


def filesystem_safe_id(value: str) -> str:
    return value.replace(":", "__")
