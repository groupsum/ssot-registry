/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState } from "react";
import { BookOpen, Code, Play, CheckCircle, Copy, HelpCircle, FileJson, Cpu, Eye } from "lucide-react";

export const StorybookDocs: React.FC = () => {
  const [activeTab, setActiveTab] = useState<"api" | "stories" | "cli" | "matrix">("matrix");
  const [copiedText, setCopiedText] = useState<string | null>(null);

  const triggerCopy = (code: string, label: string) => {
    navigator.clipboard.writeText(code);
    setCopiedText(label);
    setTimeout(() => setCopiedText(null), 2000);
  };

  const reactCodeExample = `import { LineageGraphApp } from "@ssot-registry/lineage-graph";
import { LineagePayload } from "./types";

const payload: LineagePayload = {
  schemaVersion: "2.4.0",
  generatedAt: "2026-06-21T21:00:00-07:00",
  nodes: [
    { id: "adr:01", family: "ADR", label: "ADR-01: Offline Portability", status: "active" },
    { id: "spec:01", family: "SPEC", label: "SPEC: Schema v2", status: "certified" }
  ],
  edges: [
    { from: "adr:01", to: "spec:01", type: "defines" }
  ]
};

export default function App() {
  return (
    <div className="w-screen h-screen">
      <LineageGraphApp 
        payload={payload} 
        defaultMode="lineage"
        theme="light"
      />
    </div>
  );
}`;

  const pythonPayloadExample = `def _lineage_payload(self) -> dict:
    """
    Python backend generator mapping active compliance records 
    into standard LineagePayload JSON contracts.
    """
    nodes = []
    edges = []
    
    # Trace ADRs, SPECs, Features, and releases to build proof chains
    for entity in self.registry.get_entities():
        nodes.append({
            "id": entity.id,
            "family": entity.family,
            "label": entity.label,
            "status": entity.status,
            "originKind": "repo-local" if entity.is_local else "ssot-origin",
            "path": entity.relative_path
        })
        
    for link in self.registry.get_links():
        edges.append({
            "from": link.source_id,
            "to": link.target_id,
            "type": link.relationship_type,
            "status": "active"
        })
        
    return {
        "schemaVersion": "2.4.0",
        "generatedAt": "2026-06-21T22:20:00-07:00",
        "nodes": nodes,
        "edges": edges,
        "registry": { "validationStatus": "valid" }
    }`;

  const cliSnippet = `uv run ssot graph lineage . --output .ssot/graphs/registry.lineage.html`;

  return (
    <div className="flex-1 bg-slate-50 overflow-y-auto font-sans p-6">
      {/* Upper banner branding info */}
      <div className="max-w-4xl mx-auto mb-8 bg-gradient-to-r from-indigo-700 to-indigo-900 border border-indigo-950 p-6 rounded-2xl shadow-xl text-white">
        <div className="flex items-center gap-3 mb-2">
          <BookOpen className="text-indigo-200 animate-pulse" size={24} />
          <span className="text-[10px] font-mono tracking-widest text-indigo-200 uppercase bg-indigo-800/80 px-2.5 py-0.5 rounded-full font-bold">
            Interactive Documentation System
          </span>
        </div>
        <h1 className="text-xl sm:text-2xl font-extrabold tracking-tight">
          @ssot-registry/lineage-graph
        </h1>
        <p className="text-sm text-indigo-100 max-w-2xl mt-1.5 leading-relaxed">
          The canonical visual React workspace for proving, validating, and explaining how Single Source of Truth repositories release certified products. Fully typed, offline capable, rendering with high-speed coordinate canvas bounds.
        </p>

        {/* Tab switcher buttons under banner */}
        <div className="flex bg-indigo-950/40 p-1 rounded-lg mt-6 max-w-xl border border-indigo-800/40 overflow-x-auto whitespace-nowrap">
          <button
            onClick={() => setActiveTab("matrix")}
            className={`flex-1 py-1.5 px-3 rounded text-xs font-semibold select-none transition ${
              activeTab === "matrix" ? "bg-indigo-600 text-white shadow" : "text-indigo-200 hover:text-white"
            }`}
          >
            UIX Interactivity Matrix
          </button>
          <button
            onClick={() => setActiveTab("api")}
            className={`flex-1 py-1.5 px-3 rounded text-xs font-semibold select-none transition ${
              activeTab === "api" ? "bg-indigo-600 text-white shadow" : "text-indigo-200 hover:text-white"
            }`}
          >
            React API Reference
          </button>
          <button
            onClick={() => setActiveTab("stories")}
            className={`flex-1 py-1.5 px-3 rounded text-xs font-semibold select-none transition ${
              activeTab === "stories" ? "bg-indigo-600 text-white shadow" : "text-indigo-200 hover:text-white"
            }`}
          >
            Interactive Stories
          </button>
          <button
            onClick={() => setActiveTab("cli")}
            className={`flex-1 py-1.5 px-3 rounded text-xs font-semibold select-none transition ${
              activeTab === "cli" ? "bg-indigo-600 text-white shadow" : "text-indigo-200 hover:text-white"
            }`}
          >
            SSOT CLI Exports
          </button>
        </div>
      </div>

      <div className="max-w-5xl mx-auto bg-white border border-slate-200 rounded-xl shadow-md p-6">
        {activeTab === "matrix" && (
          <div className="space-y-6 animate-fadeIn">
            <div>
              <h2 className="text-base font-bold text-slate-800 mb-1 flex items-center gap-1.5 border-b border-slate-100 pb-2">
                <Eye size={18} className="text-indigo-600" /> Interaction & UIX State Behavior Matrix
              </h2>
              <p className="text-xs text-slate-500 leading-relaxed mt-2">
                This specification matrix outlines the precise expected behavior of nodes, edges, and filtering layers in all visual interaction states.
              </p>
            </div>

            <div className="overflow-x-auto border border-slate-200 rounded-xl">
              <table className="w-full text-left border-collapse text-xs">
                <thead>
                  <tr className="bg-slate-50 border-b border-slate-200 font-sans text-[11px] font-bold text-slate-600">
                    <th className="p-3.5 border-r border-slate-200 min-w-[140px]">Interactive State Configuration</th>
                    <th className="p-3.5 border-r border-slate-200 min-w-[160px]">Node Highlighting (Focus Center)</th>
                    <th className="p-3.5 border-r border-slate-200 min-w-[170px]">Ego-Neighborhood (Hops Highlight)</th>
                    <th className="p-3.5 border-r border-slate-200 min-w-[170px]">Edge Visual Styling (Ribbons & Flows)</th>
                    <th className="p-3.5 border-r border-slate-200 min-w-[160px]">Hops vs Node Limit Order</th>
                    <th className="p-3.5 min-w-[140px]">Non-Neighborhood Isolation</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-200 text-[11.5px] leading-relaxed text-slate-600">
                  <tr className="hover:bg-indigo-50/30 transition">
                    <td className="p-3.5 border-r border-slate-200 font-bold bg-slate-50/50 text-indigo-700">
                      Hovered Node
                      <div className="text-[10px] text-slate-400 font-normal mt-0.5">Immediate cursor activation</div>
                    </td>
                    <td className="p-3.5 border-r border-slate-200">
                      <span className="inline-block px-2 py-0.5 rounded bg-amber-100 text-amber-800 font-bold text-[10px] mb-1">Amber Ring</span>
                      <div>Glow underlay, scales to 1.10x with high depth priority (<code className="font-mono text-[10px]">z-50</code>).</div>
                    </td>
                    <td className="p-3.5 border-r border-slate-200">
                      <span className="inline-block px-2 py-0.5 rounded bg-amber-50 text-amber-700 font-bold text-[10px] mb-1">Amber Border</span>
                      <div>Hop neighbors show thin Amber border (<code className="font-mono text-[10px]">z-30</code>) and soft Amber backgrounds.</div>
                    </td>
                    <td className="p-3.5 border-r border-slate-200">
                      <span className="inline-block px-2 py-0.5 rounded bg-amber-100 text-amber-800 font-bold text-[10px] mb-1">Amber Ribbons & Dashes</span>
                      <div>Direct and hop edges turn Amber with animated flow-dashes; other edges dimmed to 8%.</div>
                    </td>
                    <td className="p-3.5 border-r border-slate-200 font-medium">
                      <strong className="text-slate-700">Hops First, then Node Limit</strong>
                      <div className="text-[10.5px] text-slate-500 mt-0.5">Applies hop limits first to ensure neighborhood remains complete, then crops by node limit.</div>
                    </td>
                    <td className="p-3.5">
                      <strong className="text-slate-700">Dimmed to 25% / 8%</strong>
                      <div className="text-[10.5px] text-slate-500 mt-0.5 font-sans">Non-neighborhood nodes and edges are heavily grayed-out but kept visible.</div>
                    </td>
                  </tr>

                  <tr className="hover:bg-indigo-50/30 transition">
                    <td className="p-3.5 border-r border-slate-200 font-bold bg-slate-50/50 text-indigo-700">
                      Selected Node
                      <div className="text-[10px] text-slate-400 font-normal mt-0.5">Explicit mouse click</div>
                    </td>
                    <td className="p-3.5 border-r border-slate-200">
                      <span className="inline-block px-2 py-0.5 rounded bg-indigo-100 text-indigo-800 font-bold text-[10px] mb-1">Indigo Ring</span>
                      <div>Offset Indigo ring, scales to 1.05x (<code className="font-mono text-[10px]">z-45</code>) with medium depth.</div>
                    </td>
                    <td className="p-3.5 border-r border-slate-200">
                      <span className="inline-block px-2 py-0.5 rounded bg-indigo-50 text-indigo-700 font-bold text-[10px] mb-1">Indigo Border</span>
                      <div>Hop neighbors show thin Indigo border (<code className="font-mono text-[10px]">z-25</code>) and soft Indigo backgrounds.</div>
                    </td>
                    <td className="p-3.5 border-r border-slate-200">
                      <span className="inline-block px-2 py-0.5 rounded bg-indigo-100 text-indigo-800 font-bold text-[10px] mb-1">Indigo Ribbons & Dashes</span>
                      <div>Direct and hop edges turn Indigo with animated flow-dashes; other edges dimmed to 8%.</div>
                    </td>
                    <td className="p-3.5 border-r border-slate-200 font-medium">
                      <strong className="text-slate-700">Hops First, then Node Limit</strong>
                      <div className="text-[10.5px] text-slate-500 mt-0.5">Applies hop limits first to ensure neighborhood remains complete, then crops by node limit.</div>
                    </td>
                    <td className="p-3.5">
                      <strong className="text-slate-700">Dimmed to 25% / 8%</strong>
                      <div className="text-[10.5px] text-slate-500 mt-0.5">Non-neighborhood nodes and edges are heavily grayed-out but kept visible.</div>
                    </td>
                  </tr>

                  <tr className="hover:bg-indigo-50/30 transition">
                    <td className="p-3.5 border-r border-slate-200 font-bold bg-slate-50/50 text-indigo-700">
                      Focused Node
                      <div className="text-[10px] text-slate-400 font-normal mt-0.5">Explicit double-click / search selection</div>
                    </td>
                    <td className="p-3.5 border-r border-slate-200">
                      <span className="inline-block px-2 py-0.5 rounded bg-teal-100 text-teal-800 font-bold text-[10px] mb-1">Teal Ring</span>
                      <div>Offset Teal ring, scales to 1.05x (<code className="font-mono text-[10px]">z-40</code>) with standard depth.</div>
                    </td>
                    <td className="p-3.5 border-r border-slate-200">
                      <span className="inline-block px-2 py-0.5 rounded bg-teal-50 text-teal-700 font-bold text-[10px] mb-1">Teal Border</span>
                      <div>Hop neighbors show thin Teal border (<code className="font-mono text-[10px]">z-20</code>) and soft Teal backgrounds.</div>
                    </td>
                    <td className="p-3.5 border-r border-slate-200">
                      <span className="inline-block px-2 py-0.5 rounded bg-cyan-100 text-cyan-800 font-bold text-[10px] mb-1">Directional Cyan / Pink</span>
                      <div>Incoming direct edges turn Cyan; outgoing edges turn Pink. Hop edges turn Teal. Other edges dimmed to 8%.</div>
                    </td>
                    <td className="p-3.5 border-r border-slate-200 font-medium">
                      <strong className="text-slate-700">Hops First, then Node Limit</strong>
                      <div className="text-[10.5px] text-slate-500 mt-0.5">Applies hop limits first to ensure neighborhood remains complete, then crops by node limit.</div>
                    </td>
                    <td className="p-3.5">
                      <strong className="text-slate-700">Dimmed to 25% / 8%</strong>
                      <div className="text-[10.5px] text-slate-500 mt-0.5">Non-neighborhood nodes and edges are heavily grayed-out but kept visible.</div>
                    </td>
                  </tr>

                  <tr className="hover:bg-indigo-50/30 transition">
                    <td className="p-3.5 border-r border-slate-200 font-bold bg-slate-50/50 text-indigo-700">
                      Isolated Active Focus
                      <div className="text-[10px] text-slate-400 font-normal mt-0.5">"Isolate focus hops" filter is turned ON</div>
                    </td>
                    <td className="p-3.5 border-r border-slate-200">
                      <span className="inline-block px-2 py-0.5 rounded bg-slate-100 text-slate-800 font-bold text-[10px] mb-1">Respective Active Ring</span>
                      <div>Node keeps its respective color ring but is showcased against an empty canvas.</div>
                    </td>
                    <td className="p-3.5 border-r border-slate-200">
                      <span className="inline-block px-2 py-0.5 rounded bg-slate-100 text-slate-800 font-bold text-[10px] mb-1 font-mono">Unchanged Neighbors</span>
                      <div>Only neighbors within the hop limit remain in the viewport.</div>
                    </td>
                    <td className="p-3.5 border-r border-slate-200">
                      <span className="inline-block px-2 py-0.5 rounded bg-slate-100 text-slate-800 font-bold text-[10px] mb-1 font-mono">Pristine Connections</span>
                      <div>All edges not in the active neighborhood are filtered out. Only active connections are shown.</div>
                    </td>
                    <td className="p-3.5 border-r border-slate-200 font-medium">
                      <strong className="text-slate-700">Hops First, then Node Limit</strong>
                      <div className="text-[10.5px] text-slate-500 mt-0.5 font-bold text-indigo-600">Strictly enforced first</div>
                    </td>
                    <td className="p-3.5 bg-indigo-50/10 font-semibold text-rose-600">
                      Completely Hidden
                      <div className="text-[10px] text-slate-400 font-normal mt-0.5">All nodes outside the active ego neighborhood are completely filtered and hidden from the viewport.</div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        )}

        {activeTab === "api" && (
          <div className="space-y-6">
            <div>
              <h2 className="text-base font-bold text-slate-800 mb-1 flex items-center gap-1.5 border-b border-slate-100 pb-2">
                <Code size={18} className="text-indigo-600" /> Component Signatures
              </h2>
              <p className="text-xs text-slate-500 leading-relaxed mt-2">
                The visual widget package exports a main application workspace wrapper <strong className="font-mono text-[11px] bg-slate-100 p-0.5 rounded text-slate-800">LineageGraphApp</strong> that houses all coordinate math, filter buttons, searches, legends, and sidebars.
              </p>
            </div>

            {/* API props details */}
            <div className="space-y-4">
              <h3 className="text-xs font-bold text-slate-700 uppercase tracking-wider font-mono">
                LineageGraphApp Props Layout
              </h3>
              <div className="overflow-x-auto border border-slate-100 rounded-lg">
                <table className="w-full text-left border-collapse text-xs">
                  <thead>
                    <tr className="bg-slate-50 border-b border-slate-200 font-mono text-slate-500">
                      <th className="p-2.5 font-bold">Prop Name</th>
                      <th className="p-2.5 font-bold">Type</th>
                      <th className="p-2.5 font-bold">Required</th>
                      <th className="p-2.5 font-bold">Description</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100 text-[11px] font-mono text-slate-600">
                    <tr>
                      <td className="p-2.5 font-bold text-indigo-600">payload</td>
                      <td className="p-2.5">LineagePayload</td>
                      <td className="p-2.5 text-rose-500 font-bold">Yes</td>
                      <td className="p-2.5 text-slate-500 font-sans">The complete typed SSOT registry JSON payload structure.</td>
                    </tr>
                    <tr>
                      <td className="p-2.5 font-bold text-indigo-600">defaultMode</td>
                      <td className="p-2.5">"network" | "lineage" | "proof" | "origins"</td>
                      <td className="p-2.5 text-slate-400">No</td>
                      <td className="p-2.5 text-slate-500 font-sans">Initial render mode. Defaults to "lineage".</td>
                    </tr>
                    <tr>
                      <td className="p-2.5 font-bold text-indigo-600">theme</td>
                      <td className="p-2.5">"light" | "steel-dark"</td>
                      <td className="p-2.5 text-slate-400">No</td>
                      <td className="p-2.5 text-slate-500 font-sans">Color theme preset. Defaults to "light".</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            {/* Code Highlight Block */}
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-slate-700">React Embed Code Example</span>
                <button
                  onClick={() => triggerCopy(reactCodeExample, "react")}
                  className="text-[10px] text-slate-500 hover:text-indigo-600 flex items-center gap-1 font-mono hover:underline"
                >
                  <Copy size={11} /> {copiedText === "react" ? "Copied!" : "Copy Code"}
                </button>
              </div>
              <pre className="bg-slate-900 text-slate-100 p-4 rounded-xl text-[10px] font-mono overflow-x-auto leading-relaxed border border-slate-950">
                {reactCodeExample}
              </pre>
            </div>
          </div>
        )}

        {activeTab === "stories" && (
          <div className="space-y-6">
            <h2 className="text-base font-bold text-slate-800 flex items-center gap-1.5 border-b border-slate-100 pb-2">
              <Play size={18} className="text-indigo-600" /> Live Visual Testing Stories
            </h2>

            <div className="grid sm:grid-cols-2 gap-4">
              {/* Story 1 */}
              <div className="p-4 border border-slate-150 rounded-xl hover:shadow-md transition">
                <span className="text-[9px] font-mono font-bold bg-amber-50 text-amber-700 px-2 py-0.5 rounded border border-amber-200">
                  Story #1: Tree Structure Collapse
                </span>
                <h3 className="text-xs font-bold text-slate-800 mt-2">Recursive Sub-tree Collapsible Nodes</h3>
                <p className="text-[11px] text-slate-500 mt-1 leading-relaxed">
                  Clicking the circle expansion badge <strong className="font-mono text-slate-800">[+]</strong> or <strong className="font-mono text-slate-800">[-]</strong> at the base of the circular nodes dynamically hides or reveals children subtrees cleanly. Perfect for reducing visual noise in deep registries.
                </p>
              </div>

              {/* Story 2 */}
              <div className="p-4 border border-slate-150 rounded-xl hover:shadow-md transition">
                <span className="text-[9px] font-mono font-bold bg-emerald-50 text-emerald-700 px-2 py-0.5 rounded border border-emerald-200">
                  Story #2: Ego-Centric Filtering Triggers
                </span>
                <h3 className="text-xs font-bold text-slate-800 mt-2">Instant Ego Neighborhood Hover Analysis</h3>
                <p className="text-[11px] text-slate-500 mt-1 leading-relaxed">
                  Hovering over any node dynamically highlights connected outgoing specifications and upstream ADR ancestors while executing a fluid, 60fps linear opacity fade on unrelated components.
                </p>
              </div>

              {/* Story 3 */}
              <div className="p-4 border border-slate-150 rounded-xl hover:shadow-md transition">
                <span className="text-[9px] font-mono font-bold bg-indigo-50 text-indigo-700 px-2 py-0.5 rounded border border-indigo-200">
                  Story #3: Draggable Reposition Node Locking
                </span>
                <h3 className="text-xs font-bold text-slate-800 mt-2">Frictionless Free-form Layout Repositioning</h3>
                <p className="text-[11px] text-slate-500 mt-1 leading-relaxed">
                  At any point, grab and slide circular elements manually to alter connections. Layout positions are computed dividing coordinate movements by scale coefficients, ensuring zero drifting under variable zoom viewports.
                </p>
              </div>

              {/* Story 4 */}
              <div className="p-4 border border-slate-150 rounded-xl hover:shadow-md transition">
                <span className="text-[9px] font-mono font-bold bg-red-50 text-red-700 px-2 py-0.5 rounded border border-red-200">
                  Story #4: Validation Drift Spotlighting
                </span>
                <h3 className="text-xs font-bold text-slate-800 mt-2">Dotted Stale Link Warning Metrics</h3>
                <p className="text-[11px] text-slate-500 mt-1 leading-relaxed">
                  Validation drifts trigger color alerts on the canvas node rims (red alerts) and draw invalid links with dotted ruby traces. The right inspector immediately lists failure issue lines.
                </p>
              </div>
            </div>
          </div>
        )}

        {activeTab === "cli" && (
          <div className="space-y-6">
            <h2 className="text-base font-bold text-slate-800 flex items-center gap-1.5 border-b border-slate-100 pb-2">
              <Cpu size={18} className="text-indigo-600" /> CLI Standalone Exporters
            </h2>

            <div className="space-y-4 text-xs text-slate-600">
              <p className="leading-relaxed">
                The visual React package compiles directly to an inline static single-page viewer containing no external runtime CDN links or package dependencies. 
                PyPI users invoke this build engine via the Python command-line utility to generate completely offline *.html assets.
              </p>

              {/* Python execution snip */}
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-slate-700">Python CLI trigger terminal snip</span>
                  <button
                    onClick={() => triggerCopy(cliSnippet, "cli")}
                    className="text-[10px] text-slate-500 hover:text-indigo-600 flex items-center gap-1 font-mono hover:underline"
                  >
                    <Copy size={11} /> {copiedText === "cli" ? "Copied!" : "Copy Command"}
                  </button>
                </div>
                <pre className="bg-slate-900 text-slate-100 p-3 rounded-xl font-mono text-[10.5px] border border-slate-950 overflow-x-auto select-all">
                  $ {cliSnippet}
                </pre>
              </div>

              {/* Python generator code block */}
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-slate-700">Primary Python payload producer schema mapping</span>
                  <button
                    onClick={() => triggerCopy(pythonPayloadExample, "python")}
                    className="text-[10px] text-slate-500 hover:text-indigo-600 flex items-center gap-1 font-mono hover:underline"
                  >
                    <Copy size={11} /> {copiedText === "python" ? "Copy Code" : "Copy Code"}
                  </button>
                </div>
                <pre className="bg-slate-900 text-slate-100 p-4 rounded-xl text-[10px] font-mono overflow-x-auto leading-relaxed border border-slate-950">
                  {pythonPayloadExample}
                </pre>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
