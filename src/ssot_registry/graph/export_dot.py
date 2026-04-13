from __future__ import annotations

from ssot_registry.graph.export_json import build_graph_json


def build_graph_dot(registry: dict[str, object]) -> str:
    graph = build_graph_json(registry)
    lines = ["digraph ssot_registry {"]
    for node in graph["nodes"]:
        lines.append(f'  "{node["id"]}" [label="{node["id"]}\n({node["kind"]})"];')
    for edge in graph["edges"]:
        lines.append(f'  "{edge["from"]}" -> "{edge["to"]}" [label="{edge["type"]}"];')
    lines.append("}")
    return "\n".join(lines) + "\n"
