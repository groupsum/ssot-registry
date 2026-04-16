from __future__ import annotations

from typing import Any

from ssot_registry.model.enums import REF_FIELD_TARGETS


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
}


def validate_references(
    registry: dict[str, Any],
    index: dict[str, dict[str, dict[str, Any]]],
    failures: list[str],
) -> None:
    program = registry.get("program", {})
    active_boundary_id = program.get("active_boundary_id")
    active_release_id = program.get("active_release_id")
    if isinstance(active_boundary_id, str) and active_boundary_id not in index["boundaries"]:
        failures.append(f"program.active_boundary_id references missing boundary {active_boundary_id}")
    if isinstance(active_release_id, str) and active_release_id not in index["releases"]:
        failures.append(f"program.active_release_id references missing release {active_release_id}")

    for (section, field_name), target_section in REF_FIELD_TARGETS.items():
        for entity_id, row in index[section].items():
            value = row.get(field_name)
            if field_name.endswith("_ids"):
                if isinstance(value, list):
                    for ref_id in value:
                        if ref_id not in index[target_section]:
                            failures.append(
                                f"{section}.{entity_id}.{field_name} references missing {SINGULAR[target_section]} {ref_id}"
                            )
            else:
                if isinstance(value, str) and value not in index[target_section]:
                    failures.append(
                        f"{section}.{entity_id}.{field_name} references missing {SINGULAR[target_section]} {value}"
                    )
