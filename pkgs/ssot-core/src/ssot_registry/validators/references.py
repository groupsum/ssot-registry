from __future__ import annotations

from typing import Any

from ssot_registry.model.enums import REF_FIELD_TARGETS
from ssot_registry.model.ids import is_normalized_id


SINGULAR = {
    "features": "feature",
    "profiles": "profile",
    "tests": "test",
    "claims": "claim",
    "evidence": "evidence",
    "issues": "issue",
    "risks": "risk",
    "boundaries": "boundary",
    "releases": "release",
    "adrs": "ADR",
    "specs": "spec",
}


def validate_references(
    registry: dict[str, Any],
    index: dict[str, dict[str, dict[str, Any]]],
    failures: list[str],
) -> None:
    program = registry.get("program", {})
    active_boundary_id = program.get("active_boundary_id")
    active_release_id = program.get("active_release_id")
    if isinstance(active_boundary_id, str):
        if not is_normalized_id(active_boundary_id):
            failures.append(f"program.active_boundary_id is not a normalized id: {active_boundary_id}")
        elif active_boundary_id not in index["boundaries"]:
            failures.append(f"program.active_boundary_id references missing boundary {active_boundary_id}")
    if isinstance(active_release_id, str):
        if not is_normalized_id(active_release_id):
            failures.append(f"program.active_release_id is not a normalized id: {active_release_id}")
        elif active_release_id not in index["releases"]:
            failures.append(f"program.active_release_id references missing release {active_release_id}")

    for (section, field_name), target_section in REF_FIELD_TARGETS.items():
        for entity_id, row in index[section].items():
            value = row.get(field_name)
            if field_name.endswith("_ids"):
                if isinstance(value, list):
                    for ref_id in value:
                        if not isinstance(ref_id, str) or not is_normalized_id(ref_id):
                            failures.append(f"{section}.{entity_id}.{field_name} contains a non-normalized id {ref_id!r}")
                        elif ref_id not in index[target_section]:
                            failures.append(
                                f"{section}.{entity_id}.{field_name} references missing {SINGULAR[target_section]} {ref_id}"
                            )
            else:
                if isinstance(value, str):
                    if not is_normalized_id(value):
                        failures.append(f"{section}.{entity_id}.{field_name} is not a normalized id: {value}")
                    elif value not in index[target_section]:
                        failures.append(
                            f"{section}.{entity_id}.{field_name} references missing {SINGULAR[target_section]} {value}"
                        )
