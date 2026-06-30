from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from collections import Counter
import json
from importlib.resources import files
from typing import Any

from ssot_views.graph import build_graph_dot, build_graph_json
from ssot_registry.util.jsonio import save_json

from .load import load_registry


_IMAGE_FORMATS = {"png", "svg"}
_FAMILY_BY_PREFIX = {
    "adr": "ADR",
    "bnd": "Boundary",
    "clm": "Claim",
    "evd": "Evidence",
    "feat": "Feature",
    "iss": "Issue",
    "prf": "Profile",
    "rel": "Release",
    "rsk": "Risk",
    "spc": "Spec",
    "tst": "Test",
}
_LINEAGE_ASSET_PACKAGE = "ssot_registry.assets.lineage_graph"
_LINEAGE_JS = "ssot-lineage-graph.js"
_LINEAGE_CSS = "ssot-lineage-graph.css"


def _family_from_id(entity_id: str) -> str:
    prefix = entity_id.split(":", 1)[0]
    return _FAMILY_BY_PREFIX.get(prefix, prefix.upper())


def _title_for(item: dict[str, Any]) -> str:
    for key in ("title", "name", "summary", "description"):
        value = item.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return str(item.get("id", ""))


def _string_value(value: Any) -> str:
    return value.strip() if isinstance(value, str) and value.strip() else ""


def _string_list(*values: Any) -> list[str]:
    result: list[str] = []
    for value in values:
        items = value if isinstance(value, list) else [value]
        for item in items:
            if isinstance(item, str) and item.strip() and item.strip() not in result:
                result.append(item.strip())
    return result


def _maybe_source(item: dict[str, Any]) -> dict[str, Any] | None:
    source = item.get("source") if isinstance(item.get("source"), dict) else {}
    path = _string_value(item.get("path")) or _string_value(source.get("path"))
    url = _string_value(item.get("url")) or _string_value(source.get("url"))
    document_id = _string_value(item.get("document_id")) or _string_value(source.get("documentId"))
    line = item.get("line") if isinstance(item.get("line"), int) else source.get("line")
    payload: dict[str, Any] = {}
    if path:
        payload["path"] = path
    if isinstance(line, int):
        payload["line"] = line
    if url:
        payload["url"] = url
    if document_id:
        payload["documentId"] = document_id
    return payload or None


def _validation_for(item: dict[str, Any]) -> dict[str, Any]:
    raw = item.get("validation") if isinstance(item.get("validation"), dict) else {}
    status = _string_value(raw.get("status")) or _string_value(item.get("validation_status")) or "unknown"
    issues = _string_list(raw.get("issues"), item.get("validation_issues"))
    payload: dict[str, Any] = {"status": status}
    if issues:
        payload["issues"] = issues
    last_checked_at = _string_value(raw.get("lastCheckedAt")) or _string_value(item.get("last_checked_at"))
    if last_checked_at:
        payload["lastCheckedAt"] = last_checked_at
    return payload


def _proof_for(item: dict[str, Any], family: str) -> dict[str, Any] | None:
    raw = item.get("proof") if isinstance(item.get("proof"), dict) else {}
    plan = item.get("plan") if isinstance(item.get("plan"), dict) else {}
    payload: dict[str, Any] = {}
    claim_tier = _string_value(raw.get("claimTier")) or _string_value(item.get("tier")) or _string_value(plan.get("target_claim_tier"))
    if claim_tier:
        payload["claimTier"] = claim_tier
    if family == "Test":
        payload["testStatus"] = _string_value(item.get("status")) or "unknown"
    if family == "Evidence":
        payload["evidenceStatus"] = _string_value(item.get("status")) or "unknown"
    if family == "Release":
        payload["releaseStatus"] = _string_value(item.get("status")) or "unknown"
    completeness = raw.get("completeness")
    if isinstance(completeness, (int, float)):
        payload["completeness"] = completeness
    return payload or None


def _lineage_payload(registry: dict[str, Any]) -> dict[str, Any]:
    graph = build_graph_json(registry)
    repo = registry.get("repo") if isinstance(registry.get("repo"), dict) else {}
    edges = [
        {
            "from": edge["from"],
            "to": edge["to"],
            "type": edge.get("type", "RELATED"),
            "label": edge.get("label") or edge.get("type", "RELATED"),
            "status": edge.get("status") or "active",
            "originKind": edge.get("originKind") or edge.get("origin_kind") or "direct",
        }
        for edge in graph.get("edges", [])
        if isinstance(edge, dict) and isinstance(edge.get("from"), str) and isinstance(edge.get("to"), str)
    ]
    nodes: dict[str, dict[str, Any]] = {}
    for values in registry.values():
        if not isinstance(values, list):
            continue
        for item in values:
            if not isinstance(item, dict):
                continue
            entity_id = item.get("id")
            if not isinstance(entity_id, str):
                continue
            plan = item.get("plan") if isinstance(item.get("plan"), dict) else {}
            lifecycle = item.get("lifecycle") if isinstance(item.get("lifecycle"), dict) else {}
            family = _family_from_id(entity_id)
            governance_packs = _string_list(item.get("governance_packs"), item.get("governance_pack_ids"))
            contract_packs = _string_list(item.get("contract_packs"), item.get("contract_pack_ids"))
            packs = _string_list(item.get("packs"), item.get("pack_ids"), governance_packs, contract_packs)
            proof = _proof_for(item, family)
            source = _maybe_source(item)
            nodes[entity_id] = {
                "id": entity_id,
                "family": family,
                "label": _title_for(item) or entity_id,
                "title": _string_value(item.get("title")) or _title_for(item) or entity_id,
                "summary": _string_value(item.get("summary")),
                "description": _string_value(item.get("description")) or _string_value(item.get("body")),
                "status": item.get("status") or lifecycle.get("stage") or "",
                "lifecycle": lifecycle,
                "tier": item.get("tier") or plan.get("target_claim_tier") or "",
                "origin": item.get("origin") or "",
                "originKind": item.get("origin_kind") or item.get("origin") or "unknown",
                "originRef": item.get("origin_ref") or item.get("package_version") or "",
                "source": source,
                "path": item.get("path") or "",
                "tags": _string_list(item.get("tags"), item.get("robustness_dimensions")),
                "packs": packs,
                "governancePacks": governance_packs,
                "contractPacks": contract_packs,
                "boundaries": _string_list(item.get("boundary_id"), item.get("boundary_ids")),
                "releases": _string_list(item.get("release_id"), item.get("release_ids")),
                "profiles": _string_list(item.get("profile_id"), item.get("profile_ids")),
                "validation": _validation_for(item),
                "proof": proof,
            }
            if source is None:
                nodes[entity_id].pop("source")
            if proof is None:
                nodes[entity_id].pop("proof")
    for edge in edges:
        for entity_id in (edge["from"], edge["to"]):
            nodes.setdefault(
                entity_id,
                {
                    "id": entity_id,
                    "family": _family_from_id(entity_id),
                    "label": entity_id,
                    "status": "",
                    "tier": "",
                    "origin": "",
                    "originKind": "unknown",
                    "path": "",
                    "tags": [],
                    "packs": [],
                    "governancePacks": [],
                    "contractPacks": [],
                    "boundaries": [],
                    "releases": [],
                    "profiles": [],
                    "validation": {"status": "unknown"},
                },
            )

    degree_counts: Counter[str] = Counter()
    upstream_counts: Counter[str] = Counter()
    downstream_counts: Counter[str] = Counter()
    for edge in edges:
        degree_counts[edge["from"]] += 1
        degree_counts[edge["to"]] += 1
        downstream_counts[edge["from"]] += 1
        upstream_counts[edge["to"]] += 1
    for entity_id, node in nodes.items():
        node["degree"] = degree_counts[entity_id]
        node["metrics"] = {
            "upstreamCount": upstream_counts[entity_id],
            "downstreamCount": downstream_counts[entity_id],
        }

    status_counts = Counter(_string_value(node.get("status")) or "unknown" for node in nodes.values())
    origin_counts = Counter(_string_value(node.get("originKind")) or "unknown" for node in nodes.values())
    tier_counts = Counter(_string_value(node.get("tier")) or "unknown" for node in nodes.values())
    family_counts = Counter(node["family"] for node in nodes.values())
    edge_type_counts = Counter(edge["type"] for edge in edges)

    return {
        "schemaVersion": "2",
        "generator": {
            "name": "ssot-registry",
            "command": "ssot graph lineage",
        },
        "registry": {
            "schemaVersion": registry.get("schema_version") or registry.get("schemaVersion") or "",
            "validationStatus": "unknown",
        },
        "package": {
            "id": repo.get("id") or "",
            "name": repo.get("name") or "",
            "version": repo.get("version") or "",
            "kind": repo.get("kind") or "",
            "repositoryUrl": repo.get("repository_url") or repo.get("repositoryUrl") or "",
            "canonicalUrl": repo.get("canonical_url") or repo.get("canonicalUrl") or "",
        },
        "nodes": sorted(nodes.values(), key=lambda item: item["id"]),
        "edges": edges,
        "summaries": {
            "counts": {
                "nodes": len(nodes),
                "edges": len(edges),
                "families": dict(sorted(family_counts.items())),
                "statuses": dict(sorted(status_counts.items())),
                "origins": dict(sorted(origin_counts.items())),
                "tiers": dict(sorted(tier_counts.items())),
            }
        },
        "summary": {
            "nodeCount": len(nodes),
            "edgeCount": len(edges),
            "families": dict(sorted(family_counts.items())),
            "edgeTypes": dict(sorted(edge_type_counts.items())),
        },
    }


def _read_lineage_asset(name: str) -> str:
    return files(_LINEAGE_ASSET_PACKAGE).joinpath(name).read_text(encoding="utf-8")


def _render_lineage_html(payload: dict[str, Any]) -> str:
    css = _read_lineage_asset(_LINEAGE_CSS)
    js = _read_lineage_asset(_LINEAGE_JS)
    payload_json = json.dumps(payload, separators=(",", ":")).replace("</", "<\\/")
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>SSOT Lineage Graph</title>
  <style>html,body,#ssot-lineage-root{{width:100%;height:100%;margin:0}}body{{overflow:hidden}}#ssot-lineage-root{{min-height:100vh}}{css}</style>
</head>
<body>
  <div id="ssot-lineage-root"></div>
  <script>window.__SSOT_LINEAGE_PAYLOAD__={payload_json};</script>
  <script>{js}</script>
</body>
</html>
"""



def _render_dot_image(dot_text: str, output_path: Path, image_format: str) -> None:
    dot_bin = shutil.which("dot")
    if dot_bin is None:
        raise ValueError("Graphviz 'dot' binary is required for image export but was not found in PATH")
    process = subprocess.run(
        [dot_bin, f"-T{image_format}", "-o", output_path.as_posix()],
        input=dot_text,
        text=True,
        capture_output=True,
        check=False,
    )
    if process.returncode != 0:
        detail = process.stderr.strip() or process.stdout.strip() or "unknown error"
        raise ValueError(f"dot image export failed: {detail}")


def export_graph(path: str | Path, output_format: str, output: str | None = None) -> dict[str, object]:
    registry_path, repo_root, registry = load_registry(path)

    if output_format == "json":
        artifact = build_graph_json(registry)
        output_path = Path(output) if output is not None else repo_root / ".ssot" / "graphs" / "registry.graph.json"
        save_json(output_path, artifact)
    elif output_format == "dot":
        artifact = build_graph_dot(registry)
        output_path = Path(output) if output is not None else repo_root / ".ssot" / "graphs" / "registry.graph.dot"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(artifact, encoding="utf-8")
    elif output_format in _IMAGE_FORMATS:
        dot_text = build_graph_dot(registry)
        output_path = Path(output) if output is not None else repo_root / ".ssot" / "graphs" / f"registry.graph.{output_format}"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        _render_dot_image(dot_text, output_path, output_format)
    else:
        raise ValueError(f"Unsupported graph format: {output_format}")

    return {
        "passed": True,
        "registry_path": registry_path.as_posix(),
        "output_path": output_path.as_posix(),
        "format": output_format,
    }


def export_lineage_graph(path: str | Path, output: str | None = None) -> dict[str, object]:
    registry_path, repo_root, registry = load_registry(path)
    payload = _lineage_payload(registry)
    output_path = Path(output) if output is not None else repo_root / ".ssot" / "graphs" / "registry.lineage.html"
    if output_path.exists() and output_path.is_dir():
        raise ValueError(f"Lineage graph output path must be a file, not a directory: {output_path}")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    html = _render_lineage_html(payload)
    output_path.write_text(html, encoding="utf-8")
    return {
        "passed": True,
        "registry_path": registry_path.as_posix(),
        "output_path": output_path.as_posix(),
        "format": "html",
        "node_count": payload["summary"]["nodeCount"],
        "edge_count": payload["summary"]["edgeCount"],
    }
