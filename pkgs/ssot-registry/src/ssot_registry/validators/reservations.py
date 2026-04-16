from __future__ import annotations

from typing import Any


def validate_document_reservations(registry: dict[str, Any], failures: list[str]) -> None:
    reservations = registry.get("document_id_reservations")
    if not isinstance(reservations, dict):
        failures.append("document_id_reservations must be an object")
        return

    for kind in ("adr", "spec"):
        rows = reservations.get(kind)
        if not isinstance(rows, list):
            failures.append(f"document_id_reservations.{kind} must be a list")
            continue

        intervals: list[tuple[int, int, str]] = []
        for index, row in enumerate(rows):
            prefix = f"document_id_reservations.{kind}[{index}]"
            if not isinstance(row, dict):
                failures.append(f"{prefix} must be an object")
                continue

            owner = row.get("owner")
            start = row.get("start")
            end = row.get("end")
            if not isinstance(owner, str) or not owner.strip():
                failures.append(f"{prefix}.owner must be a non-empty string")
            if not isinstance(start, int) or start < 1:
                failures.append(f"{prefix}.start must be an integer >= 1")
            if not isinstance(end, int) or end < 1:
                failures.append(f"{prefix}.end must be an integer >= 1")
            if isinstance(start, int) and isinstance(end, int) and start > end:
                failures.append(f"{prefix}.start must be <= {prefix}.end")
            for bool_field in ("immutable", "deletable", "assignable_by_repo"):
                if not isinstance(row.get(bool_field), bool):
                    failures.append(f"{prefix}.{bool_field} must be a boolean")

            if isinstance(owner, str) and isinstance(start, int) and isinstance(end, int) and start <= end:
                intervals.append((start, end, owner))

        intervals.sort(key=lambda item: (item[0], item[1], item[2]))
        for current, nxt in zip(intervals, intervals[1:]):
            if nxt[0] <= current[1]:
                failures.append(
                    f"document_id_reservations.{kind} ranges overlap: {current[2]} {current[0]}-{current[1]} and {nxt[2]} {nxt[0]}-{nxt[1]}"
                )
