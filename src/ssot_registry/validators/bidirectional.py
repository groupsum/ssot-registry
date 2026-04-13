from __future__ import annotations

from ssot_registry.model.enums import BIDIRECTIONAL_LINKS


def validate_bidirectional_links(
    index: dict[str, dict[str, dict[str, object]]],
    failures: list[str],
) -> None:
    for left_section, left_field, right_section, right_field in BIDIRECTIONAL_LINKS:
        for left_id, left_row in index[left_section].items():
            for right_id in left_row.get(left_field, []):
                right_row = index[right_section].get(right_id)
                if right_row is None:
                    continue
                if left_id not in right_row.get(right_field, []):
                    failures.append(
                        f"Bidirectional link drift: {left_section}.{left_id}.{left_field} contains {right_id} "
                        f"but {right_section}.{right_id}.{right_field} does not contain {left_id}"
                    )
