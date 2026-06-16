import React from "react";
import { createRoot } from "react-dom/client";
import { LineageGraphApp } from "./LineageGraphApp";
import type { LineagePayload } from "./types";

declare global {
  interface Window {
    __SSOT_LINEAGE_PAYLOAD__?: LineagePayload;
  }
}

const payload = window.__SSOT_LINEAGE_PAYLOAD__ || { nodes: [], edges: [], summary: { nodeCount: 0, edgeCount: 0 } };
const root = document.getElementById("ssot-lineage-root") || document.body.appendChild(document.createElement("div"));
createRoot(root).render(<LineageGraphApp payload={payload} />);
