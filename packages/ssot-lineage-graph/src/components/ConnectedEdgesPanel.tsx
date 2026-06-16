import React from "react";
import type { LineageEdge, SelectionState } from "../types";

export function ConnectedEdgesPanel({
  connectedEdges,
  selectedNodeId,
  centerId,
  setCenterId,
  setSelection,
}: {
  connectedEdges: LineageEdge[];
  selectedNodeId: string | null;
  centerId: string | null;
  setCenterId: (id: string | null) => void;
  setSelection: React.Dispatch<React.SetStateAction<SelectionState>>;
}): React.ReactElement {
  if (!connectedEdges.length) {
    return <div className="ssot-empty">{selectedNodeId ? "No connected edges." : "No selected node."}</div>;
  }

  return (
    <>
      {connectedEdges.slice(0, 120).map((edge, index) => {
        const other = edge.from === selectedNodeId ? edge.to : edge.from;
        return (
          <div className="ssot-edge-row" key={`${edge.from}-${edge.to}-${index}`}>
            <b>{edge.type || "RELATED"}</b>
            {edge.from} -&gt; {edge.to}
            <br />
            <button type="button" onClick={() => setSelection({ selectedNodeId: edge.from, selectedEdgeIndex: index, focusNodeId: centerId })}>
              From
            </button>
            <button type="button" onClick={() => setSelection({ selectedNodeId: edge.to, selectedEdgeIndex: index, focusNodeId: centerId })}>
              To
            </button>
            <button
              type="button"
              onClick={() => {
                setSelection({ selectedNodeId: other, selectedEdgeIndex: index, focusNodeId: other });
                setCenterId(other);
              }}
            >
              Focus other
            </button>
          </div>
        );
      })}
    </>
  );
}
