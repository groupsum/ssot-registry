import React from "react";
import { familyClassName } from "../constants";
import type { LineageNode, SelectionState } from "../types";

export function SelectedNodePanel({
  selectedNode,
  centerId,
  setCenterId,
  setSelection,
}: {
  selectedNode?: LineageNode;
  centerId: string | null;
  setCenterId: (id: string | null) => void;
  setSelection: React.Dispatch<React.SetStateAction<SelectionState>>;
}): React.ReactElement {
  if (!selectedNode) {
    return <div className="ssot-empty">Select a node for details. Use Focus to make it the lineage center.</div>;
  }
  const title = selectedNode.label || selectedNode.id;
  const metadata = [
    ["Status", selectedNode.status || "none"],
    ["Tier", selectedNode.tier || "none"],
    ["Origin", selectedNode.origin || "none"],
    ["Degree", String(selectedNode.degree || 0)],
  ];
  return (
    <div className="ssot-selected-card">
      <div className="ssot-selected-card-header">
        <span className={`ssot-selected-family-dot ${familyClassName(selectedNode.family)}`} />
        <div className="ssot-selected-heading">
          <div className="ssot-selected-title">{title}</div>
          <div className="ssot-selected-id">{selectedNode.id}</div>
        </div>
      </div>
      <div className="ssot-selected-badges">
        <span>{selectedNode.family}</span>
        <span>{selectedNode.status || "status unavailable"}</span>
        <span>degree {selectedNode.degree || 0}</span>
      </div>
      <div className="ssot-selected-meta">
        {metadata.map(([label, value]) => (
          <div className="ssot-selected-meta-item" key={label}>
            <span>{label}</span>
            <b>{value}</b>
          </div>
        ))}
      </div>
      {selectedNode.path ? (
        <div className="ssot-selected-path">
          <span>Path</span>
          <b>{selectedNode.path}</b>
        </div>
      ) : null}
      <div className="ssot-chip-row">
        <button className="primary" type="button" onClick={() => setCenterId(selectedNode.id)}>
          Focus
        </button>
        <button type="button" onClick={() => setSelection({ selectedNodeId: null, selectedEdgeIndex: null, focusNodeId: centerId })}>
          Deselect
        </button>
      </div>
    </div>
  );
}
