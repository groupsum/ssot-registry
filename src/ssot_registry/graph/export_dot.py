from __future__ import annotations

from ssot_registry.graph.export_json import build_graph_json


def _dot_escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n").replace("\r", "")


def build_graph_dot(registry: dict[str, object]) -> str:
    graph = build_graph_json(registry)
    lines = ["digraph ssot_registry {"]
    for node in graph["nodes"]:
        node_id = _dot_escape(node["id"])
        label = _dot_escape(f'{node["id"]}\\n({node["kind"]})')
        lines.append(f'  "{node_id}" [label="{label}"];')
    for edge in graph["edges"]:
        edge_from = _dot_escape(edge["from"])
        edge_to = _dot_escape(edge["to"])
        edge_type = _dot_escape(edge["type"])
        lines.append(f'  "{edge_from}" -> "{edge_to}" [label="{edge_type}"];')
    lines.append("}")
    return "\n".join(lines) + "\n"
