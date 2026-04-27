from __future__ import annotations

import re
from typing import Any


SEMVER_PATTERN = re.compile(r"^(?P<major>0|[1-9]\d*)\.(?P<minor>0|[1-9]\d*)\.(?P<patch>0|[1-9]\d*)$")
LEGACY_SCHEMA_VERSIONS = (3, 4, 5, 6, 7, 8, 9, 10)
SUPPORTED_SEMVER_SCHEMA_VERSIONS = ("0.1.0", "0.2.0", "0.3.0")


def is_semver_schema_version(value: Any) -> bool:
    return isinstance(value, str) and SEMVER_PATTERN.match(value) is not None


def parse_semver_schema_version(value: str) -> tuple[int, int, int]:
    match = SEMVER_PATTERN.match(value)
    if match is None:
        raise ValueError(f"Unsupported schema_version: {value!r}")
    return (int(match.group("major")), int(match.group("minor")), int(match.group("patch")))


def schema_version_sort_key(value: Any) -> tuple[int, ...]:
    if isinstance(value, int) and value in LEGACY_SCHEMA_VERSIONS:
        return (0, value)
    if is_semver_schema_version(value):
        return (1, *parse_semver_schema_version(value))
    raise ValueError(f"Unsupported schema_version: {value!r}")


def is_known_schema_version(value: Any, current_schema_version: str) -> bool:
    return (
        (isinstance(value, int) and value in LEGACY_SCHEMA_VERSIONS)
        or value == current_schema_version
        or value in SUPPORTED_SEMVER_SCHEMA_VERSIONS
    )


def schema_version_is_older(value: Any, current_schema_version: str) -> bool:
    try:
        return schema_version_sort_key(value) < schema_version_sort_key(current_schema_version)
    except ValueError:
        return False


def schema_version_meets_minimum(current_value: Any, minimum_value: Any) -> bool:
    return schema_version_sort_key(current_value) >= schema_version_sort_key(minimum_value)
