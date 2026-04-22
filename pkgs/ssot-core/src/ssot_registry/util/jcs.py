from __future__ import annotations

import json
from typing import Any


def _reject_non_finite(token: str) -> Any:
    raise ValueError(f"Non-finite JSON number is not allowed by RFC 8785 JCS: {token}")


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate object key is not allowed by RFC 8785 JCS: {key!r}")
        result[key] = value
    return result


def load_jcs_json(text: str, *, source: str = "<json>") -> Any:
    try:
        return json.loads(
            text,
            object_pairs_hook=_unique_object,
            parse_constant=_reject_non_finite,
        )
    except ValueError as exc:
        raise ValueError(f"Invalid JSON for {source}: {exc}") from exc


def dump_jcs_json(data: Any) -> str:
    try:
        return json.dumps(
            data,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
    except ValueError as exc:
        raise ValueError(f"JSON value cannot be serialized as RFC 8785 JCS: {exc}") from exc


def assert_jcs_canonical_text(text: str, *, source: str = "<json>") -> None:
    value = load_jcs_json(text, source=source)
    canonical = dump_jcs_json(value)
    if text != canonical:
        if text.endswith("\n") and text[:-1] == canonical:
            raise ValueError("trailing newline is not allowed in canonical RFC 8785 JCS JSON")
        raise ValueError("content is not canonical RFC 8785 JCS JSON")
