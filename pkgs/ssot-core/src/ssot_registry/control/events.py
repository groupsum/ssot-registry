from __future__ import annotations

import json
from typing import Any


def format_sse_event(event: dict[str, Any]) -> str:
    event_id = event.get("event_id")
    kind = event.get("kind", "message")
    data = json.dumps(event, sort_keys=True, separators=(",", ":"))
    return f"id: {event_id}\nevent: {kind}\ndata: {data}\n\n"


def event_cursor(events: list[dict[str, Any]]) -> int:
    if not events:
        return 0
    return max(int(event.get("event_id", 0)) for event in events)
