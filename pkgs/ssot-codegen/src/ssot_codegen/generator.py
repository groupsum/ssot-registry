from __future__ import annotations

import json
from pathlib import Path

from ssot_contracts import CONTRACT_DATA, load_document_manifest


def generate_python_artifacts(output_root: str | Path) -> list[Path]:
    target_root = Path(output_root)
    target_root.mkdir(parents=True, exist_ok=True)
    json_outputs = {
        "contracts.index.json": {
            "schema_version": CONTRACT_DATA["schema_version"],
            "adr_manifest_ids": [entry["id"] for entry in load_document_manifest("adr")],
            "spec_manifest_ids": [entry["id"] for entry in load_document_manifest("spec")],
        },
        "cli.metadata.json": {
            "output_formats": CONTRACT_DATA["output_formats"],
            "entity_sections": CONTRACT_DATA["entity_sections"],
        },
        "tui.metadata.json": {
            "entity_sections": CONTRACT_DATA["entity_sections"],
        },
    }
    python_outputs = {
        "enums.py": (
            "SCHEMA_VERSION = "
            + repr(CONTRACT_DATA["schema_version"])
            + "\nENTITY_PREFIXES = "
            + repr(CONTRACT_DATA["entity_prefixes"])
            + "\nGRAPH_NODE_KIND = "
            + repr(CONTRACT_DATA["graph_node_kind"])
            + "\n"
        ),
        "cli_metadata.py": (
            "OUTPUT_FORMATS = "
            + repr(tuple(CONTRACT_DATA["output_formats"]))
            + "\nCLI_COMMAND_LABELS = "
            + repr(tuple(section["key"] for section in CONTRACT_DATA["entity_sections"]))
            + "\n"
        ),
        "tui_metadata.py": (
            "ENTITY_SECTIONS = "
            + repr(tuple((section["key"], section["label"]) for section in CONTRACT_DATA["entity_sections"]))
            + "\n"
        ),
    }
    written: list[Path] = []
    for name, payload in json_outputs.items():
        path = target_root / name
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        written.append(path)
    for name, text in python_outputs.items():
        path = target_root / name
        path.write_text(text, encoding="utf-8")
        written.append(path)
    return written
