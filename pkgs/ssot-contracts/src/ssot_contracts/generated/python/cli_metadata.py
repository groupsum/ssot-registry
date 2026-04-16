from __future__ import annotations

from ssot_contracts.contract_data import CONTRACT_DATA

OUTPUT_FORMATS = tuple(CONTRACT_DATA["output_formats"])
CLI_COMMAND_LABELS = tuple(section["key"] for section in CONTRACT_DATA["entity_sections"] if section["key"] not in {"adrs", "specs"})
