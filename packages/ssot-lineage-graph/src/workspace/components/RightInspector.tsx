/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React from "react";
import { LineagePayload, LineageNode, LineageEdge } from "../types";
import { X, Copy, ExternalLink, Link, Anchor, ShieldAlert, FileText, CheckCircle2, ChevronRight, ChevronLeft, Activity, Trash } from "lucide-react";
import { FAMILY_COLORS } from "./LineageGraphCanvas";

interface RightInspectorProps {
  payload: LineagePayload;
  selectedNodeId: string | null;
  focusNodeId: string | null;
  onSelectNode: (id: string | null) => void;
  onSetFocusNode: (id: string | null) => void;
  onClearFocusNode: () => void;
  isCollapsed: boolean;
  onToggleCollapse: () => void;
}

export const RightInspector: React.FC<RightInspectorProps> = ({
  payload,
  selectedNodeId,
  focusNodeId,
  onSelectNode,
  onSetFocusNode,
  onClearFocusNode,
  isCollapsed,
  onToggleCollapse,
}) => {
  const [copySuccessText, setCopySuccessText] = React.useState<string | null>(null);

  // Parse matched node record
  const selectedNode = React.useMemo(() => {
    if (!selectedNodeId) return null;
    return payload.nodes.find((n) => n.id === selectedNodeId) || null;
  }, [selectedNodeId, payload.nodes]);

  // Find linked upstream/downstream connections
  const connections = React.useMemo(() => {
    if (!selectedNodeId) return { incoming: [] as { node: LineageNode; edge: LineageEdge }[], outgoing: [] as { node: LineageNode; edge: LineageEdge }[] };
    const incoming: { node: LineageNode; edge: LineageEdge }[] = [];
    const outgoing: { node: LineageNode; edge: LineageEdge }[] = [];

    payload.edges.forEach((edge) => {
      if (edge.to === selectedNodeId) {
        const fromNode = payload.nodes.find((n) => n.id === edge.from);
        if (fromNode) incoming.push({ node: fromNode, edge });
      }
      if (edge.from === selectedNodeId) {
        const toNode = payload.nodes.find((n) => n.id === edge.to);
        if (toNode) outgoing.push({ node: toNode, edge });
      }
    });

    return { incoming, outgoing };
  }, [selectedNodeId, payload.nodes, payload.edges]);

  const triggerCopyText = (text: string, label: string) => {
    navigator.clipboard.writeText(text);
    setCopySuccessText(label);
    setTimeout(() => setCopySuccessText(null), 2000);
  };

  if (isCollapsed) {
    return (
      <div className="w-12 h-full border-l border-slate-200 bg-slate-50 flex flex-col items-center py-4 gap-4 shrink-0 overflow-hidden font-sans select-none shadow-[-1px_0_6px_-2px_rgba(0,0,0,0.05)] z-10 animate-fadeIn">
        {/* Toggle Button to Expand */}
        <button
          onClick={onToggleCollapse}
          className="p-1.5 hover:bg-slate-200 rounded-lg text-slate-500 hover:text-slate-800 transition"
          title="Expand inspector panel"
        >
          <ChevronLeft size={18} />
        </button>

        <div className="w-6 border-b border-slate-200/60 my-1" />

        {selectedNode ? (
          <div className="flex flex-col items-center gap-4 flex-1 w-full relative">
            {/* Family indicator dot */}
            <div 
              className={`w-3.5 h-3.5 rounded-full relative group cursor-pointer shadow-sm border border-slate-200 ${FAMILY_COLORS[selectedNode.family]?.bg || "bg-indigo-400"}`}
              onClick={onToggleCollapse}
            >
              <div className="absolute right-14 top-1/2 -translate-y-1/2 bg-slate-800 text-white text-[10px] px-2.5 py-1 rounded-md shadow-lg opacity-0 pointer-events-none group-hover:opacity-100 transition duration-150 whitespace-nowrap z-50 font-sans font-medium">
                {selectedNode.family}: {selectedNode.id}
              </div>
            </div>

            {/* Quick Action: Copy ID */}
            <button
              onClick={() => triggerCopyText(selectedNode.id, "ID")}
              className="p-2 text-slate-400 hover:text-slate-600 hover:bg-slate-200/50 rounded-lg transition relative group"
            >
              <Copy size={14} />
              <div className="absolute right-14 top-1/2 -translate-y-1/2 bg-slate-800 text-white text-[10px] px-2.5 py-1 rounded-md shadow-lg opacity-0 pointer-events-none group-hover:opacity-100 transition duration-150 whitespace-nowrap z-50 font-sans">
                {copySuccessText === "ID" ? "Copied!" : "Copy Node ID"}
              </div>
            </button>

            {/* Quick Action: Focus Node */}
            {selectedNode.id !== focusNodeId ? (
              <button
                onClick={() => onSetFocusNode(selectedNode.id)}
                className="p-2 text-teal-600 hover:text-teal-800 hover:bg-teal-50 rounded-lg transition relative group"
              >
                <Anchor size={14} />
                <div className="absolute right-14 top-1/2 -translate-y-1/2 bg-slate-800 text-white text-[10px] px-2.5 py-1 rounded-md shadow-lg opacity-0 pointer-events-none group-hover:opacity-100 transition duration-150 whitespace-nowrap z-50 font-sans">
                  Focus Node
                </div>
              </button>
            ) : (
              <button
                onClick={onClearFocusNode}
                className="p-2 text-amber-600 hover:text-amber-800 hover:bg-amber-50 rounded-lg transition relative group"
              >
                <X size={14} />
                <div className="absolute right-14 top-1/2 -translate-y-1/2 bg-slate-800 text-white text-[10px] px-2.5 py-1 rounded-md shadow-lg opacity-0 pointer-events-none group-hover:opacity-100 transition duration-150 whitespace-nowrap z-50 font-sans">
                  Unfocus
                </div>
              </button>
            )}

            <div className="flex-1" />

            {/* Clear Selection X Button at bottom */}
            <button
              onClick={() => onSelectNode(null)}
              className="p-2 text-slate-400 hover:text-rose-600 hover:bg-rose-50 rounded-lg transition relative group"
            >
              <Trash size={14} />
              <div className="absolute right-14 top-1/2 -translate-y-1/2 bg-slate-800 text-white text-[10px] px-2.5 py-1 rounded-md shadow-lg opacity-0 pointer-events-none group-hover:opacity-100 transition duration-150 whitespace-nowrap z-50 font-sans">
                Deselect Node
              </div>
            </button>
          </div>
        ) : (
          <div className="flex flex-col items-center gap-4 flex-1 justify-center opacity-45">
            <Activity size={16} className="text-slate-400 animate-pulse" />
            <span className="text-[9px] text-slate-400 font-extrabold tracking-widest uppercase pointer-events-none select-none [writing-mode:vertical-lr] my-auto rotate-180">
              Inspector Empty
            </span>
          </div>
        )}
      </div>
    );
  }

  if (!selectedNode) {
    return (
      <div className="w-80 h-full border-l border-slate-200 bg-slate-50 flex flex-col items-center justify-center p-6 text-center select-none shrink-0 shadow-[-2px_0_12px_-4px_rgba(0,0,0,0.04)] relative">
        <button
          onClick={onToggleCollapse}
          className="absolute top-4 right-4 p-1.5 hover:bg-slate-200/60 text-slate-400 hover:text-slate-600 rounded-lg transition"
          title="Collapse inspector"
        >
          <ChevronRight size={16} />
        </button>
        <Activity size={32} className="text-slate-300 mb-2 animate-pulse" />
        <p className="text-xs font-semibold text-slate-500">
          No Element Selected
        </p>
        <p className="text-[10px] text-slate-400 max-w-[200px] mt-1">
          Click any circular node in the lineage graph to view source provenance, tests, claims, and relations.
        </p>
      </div>
    );
  }

  const colColors = FAMILY_COLORS[selectedNode.family] || FAMILY_COLORS.Profile;

  return (
    <div className="w-80 h-full border-l border-slate-200 bg-white flex flex-col shrink-0 overflow-hidden font-sans shadow-[-2px_0_12px_-4px_rgba(0,0,0,0.06)] z-10 animate-slideIn">
      {/* Header Close elements bar */}
      <div className="p-4 border-b border-slate-100 flex items-center justify-between bg-slate-50/40">
        <div className="flex items-center gap-1.5">
          <span className={`text-[9px] font-mono font-extrabold px-1.5 py-0.5 rounded uppercase ${colColors.bg} ${colColors.text} border ${colColors.border}`}>
            {selectedNode.family}
          </span>
          <span className="text-xs font-bold text-slate-800 font-mono truncate max-w-[125px]">
            {selectedNode.id}
          </span>
        </div>
        <div className="flex items-center gap-1">
          <button
            onClick={() => onSelectNode(null)}
            className="text-slate-400 hover:text-slate-600 p-1 hover:bg-slate-100 rounded-lg transition"
            title="Collapse inspector"
          >
            <ChevronRight size={15} />
          </button>
          <button
            onClick={() => onSelectNode(null)}
            className="text-slate-400 hover:text-slate-600 p-1 hover:bg-slate-100 rounded-full transition"
            title="Close Inspector"
          >
            <X size={15} />
          </button>
        </div>
      </div>

      {/* Action Toolbar buttons */}
      <div className="px-4 py-2 bg-slate-50 border-b border-slate-100 flex items-center gap-1.5">
        <button
          onClick={() => triggerCopyText(selectedNode.id, "ID")}
          className="flex-1 py-1 px-2.5 text-[9px] font-mono font-bold text-slate-600 bg-white border border-slate-200 rounded hover:bg-slate-100 hover:text-slate-800 transition flex items-center justify-center gap-1"
          title="Copy node ID to clipboard"
        >
          <Copy size={10} />
          <span>{copySuccessText === "ID" ? "Copied!" : "Copy Node ID"}</span>
        </button>
        {selectedNode.id !== focusNodeId ? (
          <button
            onClick={() => onSetFocusNode(selectedNode.id)}
            className="flex-1 py-1 px-2.5 text-[9px] font-bold text-teal-700 bg-teal-50/60 border border-teal-200 rounded hover:bg-teal-100 hover:text-teal-900 transition flex items-center justify-center gap-1"
            title="Focus graph layout center around this node"
          >
            <Anchor size={11} />
            <span>Focus Node</span>
          </button>
        ) : (
          <button
            onClick={onClearFocusNode}
            className="flex-1 py-1 px-2.5 text-[9px] font-bold text-amber-700 bg-amber-50/60 border border-amber-200 rounded hover:bg-amber-100 hover:text-amber-900 transition flex items-center justify-center gap-1"
            title="Clear manual layout focus center"
          >
            <X size={10} />
            <span>Unfocus</span>
          </button>
        )}
      </div>

      {/* Main Details scroll panel */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {/* Core Description / Body block */}
        <div className="space-y-1.5">
          <h1 className="text-xs font-bold text-slate-800">
            {selectedNode.title || selectedNode.label || selectedNode.id}
          </h1>
          {selectedNode.body ? (
            <div className="bg-slate-50/80 border border-slate-200/60 rounded-lg p-3 text-[10.5px] leading-relaxed text-slate-600 font-mono whitespace-pre-wrap max-h-48 overflow-y-auto shadow-inner">
              {selectedNode.body}
            </div>
          ) : (
            <p className="text-[11px] leading-relaxed text-slate-500">
              {selectedNode.description || selectedNode.summary || "No description document supplied in registry payload definition."}
            </p>
          )}
        </div>

        {/* Dynamic status/completeness panel */}
        <div className="bg-slate-50/70 border border-slate-100 rounded-lg p-2.5 space-y-1.5">
          <div className="flex items-center justify-between text-[11px]">
            <span className="text-slate-400 font-medium">Compliance status</span>
            <span className="font-mono uppercase font-bold text-indigo-600 bg-indigo-50 px-1.5 py-0.5 rounded text-[9px]">
              {selectedNode.status || "active"}
            </span>
          </div>
          
          {selectedNode.tier && (
            <div className="flex items-center justify-between text-[11px]">
              <span className="text-slate-400 font-medium">SLA Tier level</span>
              <span className="font-mono text-[9px] text-slate-600 font-semibold">{selectedNode.tier}</span>
            </div>
          )}

          {selectedNode.proof?.completeness !== undefined && (
            <div className="space-y-1 pt-1.5 border-t border-slate-200/50">
              <div className="flex items-center justify-between text-[10px] font-mono">
                <span className="text-slate-500 font-bold">Proof Progress</span>
                <span className="text-slate-700 font-black">{selectedNode.proof.completeness}%</span>
              </div>
              <div className="w-full bg-slate-200 h-1 rounded-full overflow-hidden">
                <div
                  className={`h-full rounded-full transition-all duration-500 ${
                    selectedNode.proof.completeness === 100 ? "bg-emerald-500" : "bg-indigo-500"
                  }`}
                  style={{ width: `${selectedNode.proof.completeness}%` }}
                />
              </div>
            </div>
          )}
        </div>

        {/* Provenance Origin Source file location */}
        <div className="space-y-1.5">
          <h3 className="text-[10px] font-bold uppercase tracking-wider text-slate-400 font-mono">
            Origin Provenance
          </h3>
          <div className="text-xs border border-slate-100 rounded-lg p-2.5 space-y-1 bg-white">
            <div className="flex items-center justify-between">
              <span className="text-slate-400 text-[10px]">Registry package:</span>
              <span className="font-mono text-[10px] text-slate-600 capitalize">
                {selectedNode.originKind || "Local"}
              </span>
            </div>
            {selectedNode.path && (
              <div className="space-y-1 pt-1">
                <div className="text-slate-400 text-[10px]">File path:</div>
                <div className="flex items-center gap-1 bg-slate-50 hover:bg-slate-100 p-1 rounded border border-slate-200/50">
                  <FileText size={10} className="text-slate-400" />
                  <span className="font-mono text-[10px] text-slate-700 truncate select-all flex-1">
                    {selectedNode.path}
                  </span>
                  <button
                    onClick={() => triggerCopyText(selectedNode.path || "", "FilePath")}
                    className="p-0.5 text-slate-400 hover:text-slate-700"
                    title="Copy relative file coordinate path"
                  >
                    <Copy size={9} />
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Validation issues list */}
        {selectedNode.validation && selectedNode.validation.status !== "pass" && (
          <div className="space-y-1.5">
            <h3 className="text-[10px] font-bold uppercase tracking-wider text-red-500 font-mono flex items-center gap-1">
              <ShieldAlert size={12} />
              Validation Warnings
            </h3>
            <div className="bg-red-50/50 border border-red-100 rounded-lg p-2.5 space-y-1.5 max-h-[140px] overflow-y-auto">
              {(selectedNode.validation.issues || []).map((issue, idx) => (
                <div key={idx} className="text-[10px] text-red-700 leading-relaxed font-mono flex items-start gap-1">
                  <span>-</span>
                  <span>{issue}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Upstream / Downstream Connections block */}
        <div className="space-y-3 pt-1 border-t border-slate-100">
          {/* Upstream Direct elements */}
          <div className="space-y-1.5">
            <h3 className="text-[10px] font-bold uppercase tracking-wider text-slate-400 font-mono">
              Upstream Ancestors ({connections.incoming.length})
            </h3>
            {connections.incoming.length === 0 ? (
              <p className="text-[10px] text-slate-400 italic">No incoming connections.</p>
            ) : (
              <div className="space-y-1">
                {connections.incoming.map(({ node, edge }, idx) => {
                  const subColors = FAMILY_COLORS[node.family];
                  return (
                    <div
                      key={`${node.id}-${edge.type || "incoming"}-${idx}`}
                      onClick={() => onSelectNode(node.id)}
                      className="p-1 px-2 border border-slate-100 rounded hover:bg-slate-50 cursor-pointer flex items-center justify-between text-[11px] transition"
                    >
                      <div className="flex items-center gap-1.5 truncate max-w-[160px]">
                        <span className={`text-[8px] font-mono px-1 rounded uppercase ${subColors?.bg} ${subColors?.text}`}>
                          {node.family.substring(0, 3)}
                        </span>
                        <span className="font-mono text-[10px] font-semibold text-slate-700 truncate">{node.id}</span>
                      </div>
                      <span className="text-[9px] text-indigo-500 font-mono font-bold lowercase">
                        {edge.type || "drives"}
                      </span>
                    </div>
                  );
                })}
              </div>
            )}
          </div>

          {/* Downstream Descendants elements */}
          <div className="space-y-1.5">
            <h3 className="text-[10px] font-bold uppercase tracking-wider text-slate-400 font-mono">
              Downstream Relations ({connections.outgoing.length})
            </h3>
            {connections.outgoing.length === 0 ? (
              <p className="text-[10px] text-slate-400 italic">No outgoing connections.</p>
            ) : (
              <div className="space-y-1">
                {connections.outgoing.map(({ node, edge }, idx) => {
                  const subColors = FAMILY_COLORS[node.family];
                  return (
                    <div
                      key={`${node.id}-${edge.type || "outgoing"}-${idx}`}
                      onClick={() => onSelectNode(node.id)}
                      className="p-1 px-2 border border-slate-100 rounded hover:bg-slate-50 cursor-pointer flex items-center justify-between text-[11px] transition"
                    >
                      <div className="flex items-center gap-1.5 truncate max-w-[160px]">
                        <span className={`text-[8px] font-mono px-1 rounded uppercase ${subColors?.bg} ${subColors?.text}`}>
                          {node.family.substring(0, 3)}
                        </span>
                        <span className="font-mono text-[10px] font-semibold text-slate-700 truncate">{node.id}</span>
                      </div>
                      <span className="text-[9px] text-slate-400 font-mono font-bold lowercase">
                        {edge.type || "triggers"}
                      </span>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
