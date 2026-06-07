from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from collections import Counter
import json
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


def _family_from_id(entity_id: str) -> str:
    prefix = entity_id.split(":", 1)[0]
    return _FAMILY_BY_PREFIX.get(prefix, prefix.upper())


def _title_for(item: dict[str, Any]) -> str:
    for key in ("title", "name", "summary", "description"):
        value = item.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return str(item.get("id", ""))


def _lineage_payload(registry: dict[str, Any]) -> dict[str, Any]:
    graph = build_graph_json(registry)
    edges = [
        {"from": edge["from"], "to": edge["to"], "type": edge.get("type", "RELATED")}
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
            nodes[entity_id] = {
                "id": entity_id,
                "family": _family_from_id(entity_id),
                "label": _title_for(item) or entity_id,
                "status": item.get("status") or lifecycle.get("stage") or "",
                "tier": item.get("tier") or plan.get("target_claim_tier") or "",
                "origin": item.get("origin") or "",
                "path": item.get("path") or "",
            }
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
                    "path": "",
                },
            )

    degree_counts: Counter[str] = Counter()
    for edge in edges:
        degree_counts[edge["from"]] += 1
        degree_counts[edge["to"]] += 1
    for entity_id, node in nodes.items():
        node["degree"] = degree_counts[entity_id]

    return {
        "nodes": sorted(nodes.values(), key=lambda item: item["id"]),
        "edges": edges,
        "summary": {
            "nodeCount": len(nodes),
            "edgeCount": len(edges),
            "families": dict(sorted(Counter(node["family"] for node in nodes.values()).items())),
            "edgeTypes": dict(sorted(Counter(edge["type"] for edge in edges).items())),
        },
    }


_LINEAGE_HTML_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>SSOT Lineage Graph</title>
  <style>
    :root { color-scheme: light; --bg:#f7f8fa; --panel:#fff; --text:#111827; --muted:#64748b; --line:#d7dde8; --accent:#0f766e; --accent2:#2563eb; }
    * { box-sizing: border-box; }
    body { margin:0; height:100vh; overflow:hidden; font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; background:var(--bg); color:var(--text); }
    .app { display:grid; grid-template-columns:320px 1fr 340px; height:100vh; }
    aside { overflow:auto; background:var(--panel); border-right:1px solid var(--line); }
    aside.detail { border-right:0; border-left:1px solid var(--line); }
    .section { padding:14px; border-bottom:1px solid var(--line); }
    h1 { margin:0 0 6px; font-size:18px; letter-spacing:0; }
    h2 { margin:0 0 10px; font-size:12px; color:var(--muted); text-transform:uppercase; letter-spacing:.08em; }
    label { display:block; margin:10px 0 5px; color:var(--muted); font-size:12px; font-weight:650; }
    input, select, button { width:100%; min-height:34px; border:1px solid var(--line); border-radius:6px; padding:7px 9px; background:#fff; color:var(--text); font:inherit; font-size:13px; }
    button { cursor:pointer; font-weight:650; background:#f8fafc; }
    button.primary { background:var(--accent); border-color:var(--accent); color:white; }
    button:disabled { opacity:.5; cursor:not-allowed; }
    .row { display:grid; grid-template-columns:1fr 1fr; gap:8px; }
    .stats { display:grid; grid-template-columns:1fr 1fr; gap:8px; }
    .stat { padding:8px; border:1px solid var(--line); border-radius:6px; background:#f8fafc; }
    .stat b { display:block; font-size:18px; }
    .muted, .empty { color:var(--muted); font-size:12px; line-height:1.4; }
    .chips { display:flex; gap:6px; flex-wrap:wrap; }
    .chip { width:auto; min-height:28px; padding:5px 8px; }
    .families { display:grid; grid-template-columns:1fr 1fr; gap:6px; }
    .families label { display:flex; align-items:center; gap:7px; margin:0; color:var(--text); font-weight:500; }
    .families input { width:auto; min-height:0; }
    canvas { display:block; width:100%; height:100%; background:linear-gradient(#fff, #f9fafb); }
    main { min-width:0; min-height:0; position:relative; }
    .toolbar { position:absolute; top:12px; left:12px; right:12px; display:flex; gap:8px; pointer-events:none; }
    .toolbar button, .toolbar .pill { pointer-events:auto; width:auto; }
    .pill { padding:8px 10px; border:1px solid var(--line); border-radius:6px; background:rgba(255,255,255,.92); font-size:12px; color:var(--muted); }
    .result { border:1px solid var(--line); border-radius:6px; padding:8px; margin-bottom:6px; cursor:pointer; background:#fff; }
    .result.active { border-color:var(--accent); box-shadow:inset 3px 0 0 var(--accent); }
    .result b { display:block; font-size:12px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
    .result span { color:var(--muted); font-size:11px; }
    pre { white-space:pre-wrap; word-break:break-word; font-size:12px; line-height:1.45; margin:0; }
    @media (max-width: 980px) { .app { grid-template-columns:1fr; grid-template-rows:260px 1fr 240px; } aside, aside.detail { border:0; border-bottom:1px solid var(--line); } }
  </style>
</head>
<body>
  <div class="app">
    <aside>
      <section class="section">
        <h1>SSOT Lineage Graph</h1>
        <div class="stats"><div class="stat"><b id="nodeCount">0</b><span>nodes</span></div><div class="stat"><b id="edgeCount">0</b><span>edges</span></div></div>
      </section>
      <section class="section">
        <h2>View</h2>
        <label>Search</label><input id="search" placeholder="id, title, family">
        <div class="row">
          <div><label>Mode</label><select id="mode"><option value="network">Network</option><option value="lineage">Top-down lineage</option></select></div>
          <div><label>Edge Type</label><select id="edgeType"><option value="">All</option></select></div>
        </div>
        <div class="row">
          <div><label>Depth</label><select id="depth"><option value="1">1 hop</option><option value="2">2 hops</option><option value="3">3 hops</option><option value="max">Maximum</option></select></div>
          <div><label>Node Limit</label><select id="limit"><option>250</option><option>1000</option><option>5000</option><option value="all">All</option></select></div>
        </div>
        <div class="row">
          <div><label>X Scale</label><input id="xScale" type="range" min="-1" max="3" step=".05" value="0"></div>
          <div><label>Y Scale</label><input id="yScale" type="range" min="-1" max="3" step=".05" value="0"></div>
        </div>
        <div class="empty" id="scaleReadout">x 1x / y 1x</div>
      </section>
      <section class="section">
        <h2>Families</h2>
        <div class="chips"><button class="chip" id="showAll">Show all</button><button class="chip" id="hideAll">Hide all</button></div>
        <div class="families" id="families"></div>
      </section>
      <section class="section">
        <h2>Results</h2>
        <div id="results"></div>
      </section>
    </aside>
    <main>
      <canvas id="canvas"></canvas>
      <div class="toolbar"><button id="fit">Fit</button><button id="focus" class="primary" disabled>Focus</button><button id="deselect" disabled>Deselect</button><span class="pill" id="visibleStats"></span></div>
    </main>
    <aside class="detail">
      <section class="section"><h2>Selected</h2><div id="selected" class="empty">Select a node for details. Use Focus to make it the lineage center.</div></section>
      <section class="section"><h2>Summary</h2><pre id="summary"></pre></section>
    </aside>
  </div>
  <script>
    const DATA = __PAYLOAD__;
    const nodes = DATA.nodes.map((n, i) => ({...n, x:(i%80)*28, y:Math.floor(i/80)*28, vx:0, vy:0}));
    const edges = DATA.edges;
    const byId = new Map(nodes.map(n => [n.id, n]));
    const colors = {ADR:"#7c3aed",Spec:"#2563eb",Feature:"#0f766e",Claim:"#b45309",Test:"#dc2626",Evidence:"#64748b",Boundary:"#0891b2",Profile:"#9333ea",Release:"#16a34a",Issue:"#e11d48",Risk:"#ea580c"};
    const ranks = {ADR:0,Spec:1,Feature:2,Claim:3,Test:4,Evidence:5,Boundary:6,Profile:7,Release:8,Issue:9,Risk:10};
    const c = document.getElementById("canvas"), ctx = c.getContext("2d");
    const els = Object.fromEntries(["search","mode","edgeType","depth","limit","xScale","yScale","families","results","nodeCount","edgeCount","fit","focus","deselect","visibleStats","selected","summary","scaleReadout","showAll","hideAll"].map(id => [id, document.getElementById(id)]));
    let selectedId = null, centerId = null, visibleNodes = [], visibleEdges = [], tx = 0, ty = 0, zoom = 1, dragging = false, last = null;
    const familyState = new Map([...new Set(nodes.map(n => n.family))].sort().map(f => [f, true]));
    els.nodeCount.textContent = DATA.summary.nodeCount; els.edgeCount.textContent = DATA.summary.edgeCount; els.summary.textContent = JSON.stringify(DATA.summary, null, 2);
    for (const type of [...new Set(edges.map(e => e.type))].sort()) els.edgeType.append(new Option(type, type));
    function renderFamilies(){ els.families.innerHTML = ""; for (const [family, checked] of familyState) { const label = document.createElement("label"); label.innerHTML = `<input type="checkbox" ${checked ? "checked" : ""}> ${family}`; label.querySelector("input").onchange = e => { familyState.set(family, e.target.checked); update(); }; els.families.append(label); } }
    function scale(v){ return 10 ** Number(v); }
    function limit(){ return els.limit.value === "all" ? Infinity : Number(els.limit.value); }
    function neighbors(seeds, maxDepth){ const ids = new Set(seeds); const usedEdges = []; let frontier = new Set(seeds); const cap = maxDepth === "max" ? Infinity : Number(maxDepth); for (let d=0; d<cap && frontier.size; d++){ const next = new Set(); for (const e of edges){ if (els.edgeType.value && e.type !== els.edgeType.value) continue; const a = frontier.has(e.from), b = frontier.has(e.to); if (!a && !b) continue; usedEdges.push(e); for (const id of [e.from, e.to]) if (!ids.has(id)) { ids.add(id); next.add(id); } } frontier = next; if (cap === Infinity && ids.size === nodes.length) break; } return {ids, usedEdges}; }
    function seeds(){ const q = els.search.value.trim().toLowerCase(); if (centerId) return [centerId]; if (!q) return nodes.map(n => n.id); return nodes.filter(n => `${n.id} ${n.label} ${n.family}`.toLowerCase().includes(q)).map(n => n.id); }
    function rank(n){ return ranks[n.family] ?? 99; }
    function layoutLineage(){ const groups = new Map(); for (const n of visibleNodes) { const r = rank(n); if (!groups.has(r)) groups.set(r, []); groups.get(r).push(n); } const xs = 210 * scale(els.xScale.value), ys = 90 * scale(els.yScale.value); for (const [r, group] of groups) { group.sort((a,b)=>a.id.localeCompare(b.id)); group.forEach((n,i)=>{ n.x = 80 + i * xs; n.y = 70 + r * ys; n.vx = n.vy = 0; }); } els.scaleReadout.textContent = `x ${scale(els.xScale.value).toFixed(2)}x / y ${scale(els.yScale.value).toFixed(2)}x`; }
    function layoutGrid(){ visibleNodes.forEach((n,i)=>{ if (!Number.isFinite(n.x) || !Number.isFinite(n.y)) { n.x=(i%120)*38; n.y=Math.floor(i/120)*38; } }); }
    function update(){ const found = neighbors(seeds(), centerId ? els.depth.value : "1"); const familyOk = n => familyState.get(n.family) !== false; visibleNodes = [...found.ids].map(id => byId.get(id)).filter(Boolean).filter(familyOk).slice(0, limit()); const set = new Set(visibleNodes.map(n => n.id)); visibleEdges = (centerId ? found.usedEdges : edges).filter(e => set.has(e.from) && set.has(e.to) && (!els.edgeType.value || e.type === els.edgeType.value)); if (els.mode.value === "lineage") layoutLineage(); else layoutGrid(); renderResults(); renderSelected(); fit(); }
    function tick(){ if (els.mode.value !== "network" || visibleNodes.length > 2500) return; const set = new Set(visibleNodes.map(n=>n.id)); for (const e of visibleEdges){ const a=byId.get(e.from), b=byId.get(e.to); if(!a||!b) continue; const dx=b.x-a.x, dy=b.y-a.y, dist=Math.hypot(dx,dy)||1, f=(dist-90)*.002; a.vx+=dx*f; a.vy+=dy*f; b.vx-=dx*f; b.vy-=dy*f; } for (let i=0;i<visibleNodes.length;i++){ const a=visibleNodes[i]; for (let j=i+1;j<visibleNodes.length;j++){ const b=visibleNodes[j], dx=b.x-a.x, dy=b.y-a.y, d2=dx*dx+dy*dy+1, f=Math.min(2, 900/d2); a.vx-=dx*f*.01; a.vy-=dy*f*.01; b.vx+=dx*f*.01; b.vy+=dy*f*.01; } } for (const n of visibleNodes){ n.vx*=.85; n.vy*=.85; n.x+=n.vx; n.y+=n.vy; } }
    function fit(){ if (!visibleNodes.length) return; const xs=visibleNodes.map(n=>n.x), ys=visibleNodes.map(n=>n.y); const minX=Math.min(...xs), maxX=Math.max(...xs), minY=Math.min(...ys), maxY=Math.max(...ys); zoom=Math.min(c.width/(maxX-minX+220), c.height/(maxY-minY+220)); tx=(c.width-(minX+maxX)*zoom)/2; ty=(c.height-(minY+maxY)*zoom)/2; draw(); }
    function screen(n){ return {x:n.x*zoom+tx, y:n.y*zoom+ty}; }
    function draw(){ ctx.clearRect(0,0,c.width,c.height); ctx.lineWidth=1; for (const e of visibleEdges){ const a=byId.get(e.from), b=byId.get(e.to); if(!a||!b) continue; const A=screen(a), B=screen(b); ctx.strokeStyle = selectedId && (e.from===selectedId || e.to===selectedId) ? "#111827" : "rgba(100,116,139,.34)"; ctx.beginPath(); ctx.moveTo(A.x,A.y); ctx.lineTo(B.x,B.y); ctx.stroke(); } for (const n of visibleNodes){ const p=screen(n), active=n.id===selectedId; ctx.fillStyle=colors[n.family]||"#475569"; ctx.strokeStyle=active?"#111827":"#fff"; ctx.lineWidth=active?3:1.5; ctx.beginPath(); ctx.arc(p.x,p.y,active?8:6,0,Math.PI*2); ctx.fill(); ctx.stroke(); if (zoom > .45 && visibleNodes.length < 1200){ ctx.fillStyle="#111827"; ctx.font="11px system-ui"; ctx.fillText(n.id,p.x+9,p.y+4); } } els.visibleStats.textContent = `${visibleNodes.length} visible nodes / ${visibleEdges.length} visible edges`; }
    function resize(){ const r=c.getBoundingClientRect(); c.width=Math.max(1,Math.floor(r.width*devicePixelRatio)); c.height=Math.max(1,Math.floor(r.height*devicePixelRatio)); ctx.setTransform(devicePixelRatio,0,0,devicePixelRatio,0,0); c.width=r.width; c.height=r.height; fit(); }
    function pick(x,y){ let best=null, bd=14; for(const n of visibleNodes){ const p=screen(n), d=Math.hypot(p.x-x,p.y-y); if(d<bd){ best=n; bd=d; } } return best; }
    function renderResults(){ els.results.innerHTML=""; for (const n of visibleNodes.slice(0,80)){ const div=document.createElement("div"); div.className=`result ${n.id===selectedId?"active":""}`; div.innerHTML=`<b>${n.id}</b><span>${n.family} · degree ${n.degree||0}</span>`; div.onclick=()=>select(n.id); els.results.append(div); } }
    function renderSelected(){ const n=byId.get(selectedId); els.focus.disabled=!n; els.deselect.disabled=!n; els.selected.innerHTML = n ? `<pre>${JSON.stringify(n,null,2)}</pre>` : "Select a node for details. Use Focus to make it the lineage center."; }
    function select(id){ selectedId = selectedId === id ? null : id; renderResults(); renderSelected(); draw(); }
    c.addEventListener("click", e => { const n=pick(e.offsetX,e.offsetY); if(n) select(n.id); });
    c.addEventListener("wheel", e => { e.preventDefault(); const f=e.deltaY<0?1.1:.9; zoom*=f; draw(); }, {passive:false});
    c.addEventListener("mousedown", e => { dragging=true; last={x:e.clientX,y:e.clientY}; });
    addEventListener("mouseup",()=>dragging=false); addEventListener("mousemove", e=>{ if(!dragging) return; tx+=e.clientX-last.x; ty+=e.clientY-last.y; last={x:e.clientX,y:e.clientY}; draw(); });
    for (const el of [els.search,els.mode,els.edgeType,els.depth,els.limit,els.xScale,els.yScale]) el.addEventListener("input",()=>{ if(el!==els.depth) centerId=null; update(); });
    els.fit.onclick=fit; els.focus.onclick=()=>{ if(selectedId){ centerId=selectedId; update(); } }; els.deselect.onclick=()=>{ selectedId=null; renderSelected(); renderResults(); draw(); };
    els.showAll.onclick=()=>{ for(const f of familyState.keys()) familyState.set(f,true); renderFamilies(); update(); }; els.hideAll.onclick=()=>{ for(const f of familyState.keys()) familyState.set(f,false); renderFamilies(); update(); };
    function animate(){ tick(); draw(); requestAnimationFrame(animate); }
    renderFamilies(); resize(); update(); animate(); addEventListener("resize", resize);
  </script>
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
    output_path.parent.mkdir(parents=True, exist_ok=True)
    html = _LINEAGE_HTML_TEMPLATE.replace("__PAYLOAD__", json.dumps(payload, separators=(",", ":")))
    output_path.write_text(html, encoding="utf-8")
    return {
        "passed": True,
        "registry_path": registry_path.as_posix(),
        "output_path": output_path.as_posix(),
        "format": "html",
        "node_count": payload["summary"]["nodeCount"],
        "edge_count": payload["summary"]["edgeCount"],
    }
