from __future__ import annotations

from ssot_contracts.contract_data import CONTRACT_DATA

ENTITY_SECTIONS = tuple((section["key"], section["label"]) for section in CONTRACT_DATA["entity_sections"])
ENTITY_VIEW_SECTIONS = {
    "features": ("id", "title", "implementation_status"),
    "profiles": ("id", "title", "status"),
    "tests": ("id", "title", "status"),
    "claims": ("id", "title", "status"),
    "evidence": ("id", "title", "status"),
    "issues": ("id", "title", "status"),
    "risks": ("id", "title", "status"),
    "boundaries": ("id", "title", "status"),
    "releases": ("id", "version", "status"),
    "adrs": ("id", "title", "status"),
    "specs": ("id", "title", "status"),
}
