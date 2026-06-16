import React from "react";
import type { LineageNode, SelectionState } from "../types";

export function ResultsList({
  nodes,
  search,
  selection,
  setSelection,
}: {
  nodes: LineageNode[];
  search: string;
  selection: SelectionState;
  setSelection: React.Dispatch<React.SetStateAction<SelectionState>>;
}): React.ReactElement {
  return (
    <div className="ssot-results-list">
      {nodes
        .filter((node) => `${node.id} ${node.label || ""} ${node.family}`.toLowerCase().includes(search.toLowerCase()))
        .slice(0, 80)
        .map((node) => (
          <div
            className={`ssot-result ${node.id === selection.selectedNodeId ? "active" : ""}`}
            key={node.id}
            onClick={() =>
              setSelection((next) => ({
                ...next,
                selectedNodeId: node.id,
                selectedEdgeIndex: null,
              }))
            }
          >
            <b>{node.id}</b>
            <span>
              {node.family} | degree {node.degree || 0}
            </span>
          </div>
        ))}
    </div>
  );
}
