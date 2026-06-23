/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useRef, useState, useEffect } from "react";
import { motion, AnimatePresence } from "motion/react";
import { LineagePayload, LineageNode, LineageEdge, GraphViewMode, ViewSettings, LineageFamily, Position, NodePositions } from "../types";
import { columnForNode, computeGraphIndices, generateSvgLinkCurve } from "../utils/graphHelpers";
import { ZoomIn, ZoomOut, Maximize, RefreshCw, Hand, ShieldAlert, CheckCircle, HelpCircle, Pin, PinOff, Plus, Minus, Check, X, Eye, EyeOff, Map as MapIcon } from "lucide-react";

interface LineageGraphCanvasProps {
  payload: LineagePayload;
  positions: NodePositions;
  mode: GraphViewMode;
  selectedNodeId: string | null;
  selectedNodeIds?: Set<string>;
  focusNodeId: string | null;
  collapsedNodeIds: Set<string>;
  hiddenNodeIds: Set<string>;
  onSelectNode: (id: string | null, isShiftPressed?: boolean) => void;
  onToggleCollapse: (id: string) => void;
  onToggleHideNode: (id: string) => void;
  onClearHiddenNodes: () => void;
  onUpdatePositions: (next: NodePositions) => void;
  viewSettings: ViewSettings;
  precomputedIndices?: {
    nodeMap: Map<string, LineageNode>;
    incoming: Map<string, string[]>;
    outgoing: Map<string, string[]>;
    edgeMap: Map<string, LineageEdge[]>;
  };
  egoHops?: number;
  onAddGroup?: (group: any) => void;
  onBulkHideNodes?: (ids: string[]) => void;
  onBulkHighlightNodes?: (ids: string[]) => void;
  highlightedNodeIds?: Set<string>;
  customGroups?: { id: string; label: string; nodeIds: string[] }[];
  isolateEgo?: boolean;
}

// Map families to specific visual colors
export const FAMILY_COLORS: Record<string, { bg: string; text: string; border: string; glow: string }> = {
  ADR: { bg: "bg-amber-100", text: "text-amber-800", border: "border-amber-300", glow: "shadow-amber-200" },
  Spec: { bg: "bg-blue-100", text: "text-blue-800", border: "border-blue-300", glow: "shadow-blue-200" },
  SPEC: { bg: "bg-blue-100", text: "text-blue-800", border: "border-blue-300", glow: "shadow-blue-200" },
  Feature: { bg: "bg-indigo-100", text: "text-indigo-800", border: "border-indigo-300", glow: "shadow-indigo-200" },
  Claim: { bg: "bg-purple-100", text: "text-purple-800", border: "border-purple-300", glow: "shadow-purple-200" },
  Test: { bg: "bg-rose-100", text: "text-rose-800", border: "border-rose-300", glow: "shadow-rose-200" },
  Evidence: { bg: "bg-emerald-100", text: "text-emerald-800", border: "border-emerald-300", glow: "shadow-emerald-200" },
  Release: { bg: "bg-teal-100", text: "text-teal-800", border: "border-teal-300", glow: "shadow-teal-200" },
  Boundary: { bg: "bg-slate-100", text: "text-slate-800", border: "border-slate-300", glow: "shadow-slate-200" },
  Profile: { bg: "bg-gray-100", text: "text-gray-800", border: "border-gray-300", glow: "shadow-gray-200" },
  Risk: { bg: "bg-orange-100", text: "text-orange-800", border: "border-orange-300", glow: "shadow-orange-200" },
  Issue: { bg: "bg-red-100", text: "text-red-800", border: "border-red-300", glow: "shadow-red-200" },
};

// Generate perpendicular offsets on bezier curves or straight lines for parallel double-edges
export function generateGhostParallelPaths(
  startX: number,
  startY: number,
  endX: number,
  endY: number,
  mode: string,
  offset: number
): string {
  if (mode === "lineage" || mode === "proof" || mode === "packs") {
    const midX = (startX + endX) / 2;
    return `M ${startX} ${startY + offset} C ${midX} ${startY + offset}, ${midX} ${endY + offset}, ${endX} ${endY + offset}`;
  }

  // Straight line normal factor translation for force layouts
  const dx = endX - startX;
  const dy = endY - startY;
  const len = Math.sqrt(dx * dx + dy * dy) || 1;
  const nx = -dy / len;
  const ny = dx / len;

  const ox = nx * offset;
  const oy = ny * offset;

  return `M ${startX + ox} ${startY + oy} L ${endX + ox} ${endY + oy}`;
}

export const LineageGraphCanvas: React.FC<LineageGraphCanvasProps> = ({
  payload,
  positions,
  mode,
  selectedNodeId,
  selectedNodeIds = new Set<string>(),
  focusNodeId,
  collapsedNodeIds,
  hiddenNodeIds,
  onSelectNode,
  onToggleCollapse,
  onToggleHideNode,
  onClearHiddenNodes,
  onUpdatePositions,
  viewSettings,
  precomputedIndices,
  egoHops = 1,
  onAddGroup,
  onBulkHideNodes,
  onBulkHighlightNodes,
  highlightedNodeIds = new Set<string>(),
  customGroups = [],
  isolateEgo = false,
}) => {
  const containerRef = useRef<HTMLDivElement>(null);

  const isPhysicsMode = mode === "network" || mode === "flow-force";
  const transitionClass = isPhysicsMode ? "" : "transition-all duration-300";

  // Pan-and-zoom viewport offsets
  const [pan, setPan] = useState({ x: 50, y: 50 });
  const [zoom, setZoom] = useState(0.85);
  const [isPanning, setIsPanning] = useState(false);
  const startPanRef = useRef({ x: 0, y: 0 });

  // Interactive Minimap dragging state
  const [isMinimapDragging, setIsMinimapDragging] = useState(false);

  // Ego hovering state to highlight connected lines and fade out neighbors
  const [hoveredNodeId, setHoveredNodeId] = useState<string | null>(null);

  // Dragging a specific node parameters
  const [draggedNodeId, setDraggedNodeId] = useState<string | null>(null);
  const dragStartMouseRef = useRef({ x: 0, y: 0 });
  const dragStartPosRef = useRef({ x: 0, y: 0 });
  const hasDraggedRef = useRef(false);
  const prevPayloadRef = useRef<any>(null);

  // Keyboard navigation shortcuts: Arrow keys to pan, +/- to zoom
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Ignore if user is currently typing in input boxes or search boxes
      const target = e.target as HTMLElement;
      if (target && (target.tagName === "INPUT" || target.tagName === "TEXTAREA" || target.isContentEditable)) {
        return;
      }

      const panDelta = 35 / zoom; // Pan speed relative to scale zoom levels
      if (e.key === "ArrowUp") {
        e.preventDefault();
        setPan((p) => ({ ...p, y: p.y + panDelta }));
      } else if (e.key === "ArrowDown") {
        e.preventDefault();
        setPan((p) => ({ ...p, y: p.y - panDelta }));
      } else if (e.key === "ArrowLeft") {
        e.preventDefault();
        setPan((p) => ({ ...p, x: p.x + panDelta }));
      } else if (e.key === "ArrowRight") {
        e.preventDefault();
        setPan((p) => ({ ...p, x: p.x - panDelta }));
      } else if (e.key === "+" || e.key === "=") {
        e.preventDefault();
        setZoom((z) => Math.min(z * 1.15, 3.0));
      } else if (e.key === "-") {
        e.preventDefault();
        setZoom((z) => Math.max(z / 1.15, 0.15));
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => {
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, [zoom]);

  // Web scale rendering optimization: Visual Debounce of culling recalculations during fast panning or zoom sweeps.
  // The viewport boundaries used for active culling are debounced, so during fast panning, no React render cycles
  // or heavy list culls are triggered. Elements are transformed strictly and fluidly on the GPU.
  const [debouncedBounds, setDebouncedBounds] = useState(() => {
    const left = (0 - 50) / 0.85;
    const top = (0 - 50) / 0.85;
    const right = (1100 - 50) / 0.85;
    const bottom = (620 - 50) / 0.85;
    return { left, right, top, bottom, zoom: 0.85 };
  });

  useEffect(() => {
    // If panning or dragging on the canvas is NOT active, update bounds immediately.
    // Otherwise, apply a debounce delay to avoid main-thread congestion during motion sweeps.
    const isInteracting = isPanning || draggedNodeId !== null;
    const debounceDelay = isInteracting ? 55 : 0;

    const handler = setTimeout(() => {
      const w = containerRef.current?.clientWidth || 1100;
      const h = containerRef.current?.clientHeight || 620;
      const left = (0 - pan.x) / (zoom || 1);
      const top = (0 - pan.y) / (zoom || 1);
      const right = (w - pan.x) / (zoom || 1);
      const bottom = (h - pan.y) / (zoom || 1);

      setDebouncedBounds({
        left,
        right,
        top,
        bottom,
        zoom,
      });
    }, debounceDelay);

    return () => {
      clearTimeout(handler);
    };
  }, [pan.x, pan.y, zoom, isPanning, draggedNodeId]);

  const indices = React.useMemo(() => {
    if (precomputedIndices) return precomputedIndices;
    return computeGraphIndices(payload);
  }, [payload, precomputedIndices]);

  // Active focus node (hovered node has higher precedence, otherwise currently selected node)
  const activeFocusNodeId = hoveredNodeId || selectedNodeId;

  // Autofocus viewport to fit focusNodeId changes smoothly
  useEffect(() => {
    if (focusNodeId && positions[focusNodeId] && containerRef.current) {
      const nodePos = positions[focusNodeId];
      const container = containerRef.current;
      const { width: cw, height: ch } = container.getBoundingClientRect();

      const targetZoom = Math.max(zoom, 1.0);
      setZoom(targetZoom);
      setPan({
        x: cw / 2 - nodePos.x * targetZoom,
        y: ch / 2 - nodePos.y * targetZoom,
      });
    }
  }, [focusNodeId]);

  // Automatically fit view when a new dataset's positions are loaded
  useEffect(() => {
    if (Object.keys(positions).length > 0 && payload !== prevPayloadRef.current) {
      prevPayloadRef.current = payload;
      if (payload.nodes.length > 1500) {
        return;
      }
      setTimeout(() => {
        handleFitView();
      }, 50);
    }
  }, [payload, positions]);

  // Workspace canvas pointer-down for modern touch, pen and pointer input
  const handleWorkspacePointerDown = (e: React.PointerEvent<HTMLDivElement>) => {
    const target = e.target as HTMLElement;
    if (target.closest(".graph-node-avatar") || target.closest(".canvas-button")) {
      return;
    }
    setIsPanning(true);
    e.currentTarget.setPointerCapture(e.pointerId);
    startPanRef.current = { x: e.clientX - pan.x, y: e.clientY - pan.y };
  };

  const handleWorkspacePointerMove = (e: React.PointerEvent<HTMLDivElement>) => {
    if (isPanning) {
      setPan({
        x: e.clientX - startPanRef.current.x,
        y: e.clientY - startPanRef.current.y,
      });
    }
  };

  const handleWorkspacePointerUp = (e: React.PointerEvent<HTMLDivElement>) => {
    if (isPanning) {
      e.currentTarget.releasePointerCapture(e.pointerId);
      setIsPanning(false);
    }
  };

  // Node Repositioning with support for Pointer Capture and anchoring pins!
  const handleNodePointerDown = (id: string, e: React.PointerEvent<HTMLDivElement>) => {
    e.stopPropagation();

    // Lock mouse movements to this node, enabling unlimited fluid travel off node boundaries
    e.currentTarget.setPointerCapture(e.pointerId);

    setDraggedNodeId(id);
    hasDraggedRef.current = false;
    const startPos = positions[id] || { x: 0, y: 0 };
    dragStartMouseRef.current = { x: e.clientX, y: e.clientY };
    dragStartPosRef.current = { x: startPos.x, y: startPos.y };
  };

  const handleNodePointerMove = (id: string, e: React.PointerEvent<HTMLDivElement>) => {
    if (draggedNodeId !== id) return;
    e.stopPropagation();

    const dx = e.clientX - dragStartMouseRef.current.x;
    const dy = e.clientY - dragStartMouseRef.current.y;

    if (Math.abs(dx) > 3 || Math.abs(dy) > 3) {
      hasDraggedRef.current = true;
    }

    const zoomAdjustedDx = dx / zoom;
    const zoomAdjustedDy = dy / zoom;

    const nextPositions = { ...positions };
    if (nextPositions[id]) {
      const targetX = dragStartPosRef.current.x + zoomAdjustedDx;
      const targetY = dragStartPosRef.current.y + zoomAdjustedDy;
      nextPositions[id] = {
        ...nextPositions[id],
        fx: targetX,
        fy: targetY,
        x: targetX,
        y: targetY,
      };
      onUpdatePositions(nextPositions);
    }
  };

  const handleNodePointerUp = (id: string, e: React.PointerEvent<HTMLDivElement>) => {
    if (draggedNodeId !== id) return;
    e.stopPropagation();

    e.currentTarget.releasePointerCapture(e.pointerId);

    const dx = e.clientX - dragStartMouseRef.current.x;
    const dy = e.clientY - dragStartMouseRef.current.y;
    const zoomAdjustedDx = dx / zoom;
    const zoomAdjustedDy = dy / zoom;

    const finalX = dragStartPosRef.current.x + zoomAdjustedDx;
    const finalY = dragStartPosRef.current.y + zoomAdjustedDy;

    const nextPositions = { ...positions };
    if (nextPositions[id]) {
      if (mode === "network") {
        nextPositions[id] = {
          ...nextPositions[id],
          fx: finalX,
          fy: finalY,
          x: finalX,
          y: finalY,
        };
      } else {
        nextPositions[id] = {
          ...nextPositions[id],
          fx: null,
          fy: null,
          x: finalX,
          y: finalY,
        };
      }
      onUpdatePositions(nextPositions);
    }
    setDraggedNodeId(null);
  };

  // Double-clicking a node toggles physical layout anchor
  const handleNodeDoubleClick = (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (mode !== "network") return;

    const nextPositions = { ...positions };
    if (nextPositions[id]) {
      nextPositions[id] = {
        ...nextPositions[id],
        fx: null,
        fy: null,
      };
      onUpdatePositions(nextPositions);
    }
  };

  // Click handler to explicitly toggle pin / unpin state of any node with custom physical fx/fy positions
  const handleTogglePinNode = (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    const nextPositions = { ...positions };
    const pos = nextPositions[id];
    if (pos) {
      const isPinned = pos.fx !== null && pos.fx !== undefined;
      nextPositions[id] = {
        ...pos,
        fx: isPinned ? null : pos.x,
        fy: isPinned ? null : pos.y,
      };
      onUpdatePositions(nextPositions);
    }
  };

  // Wheel Zoom (centers zoom smoothly on coordinates pointer)
  const handleWheel = (e: React.WheelEvent<HTMLDivElement>) => {
    e.preventDefault();
    const zoomFactor = 1.1;
    const container = containerRef.current;
    if (!container) return;

    const rect = container.getBoundingClientRect();
    const mouseX = e.clientX - rect.left;
    const mouseY = e.clientY - rect.top;

    // Relative mouse position on the canvas before zoom change
    const canvasX = (mouseX - pan.x) / zoom;
    const canvasY = (mouseY - pan.y) / zoom;

    let nextZoom = zoom;
    if (e.deltaY < 0) {
      nextZoom = Math.min(zoom * zoomFactor, 3.0);
    } else {
      nextZoom = Math.max(zoom / zoomFactor, 0.15);
    }

    setZoom(nextZoom);
    // Shift pan coordinates to center zoom on mouse pointer
    setPan({
      x: mouseX - canvasX * nextZoom,
      y: mouseY - canvasY * nextZoom,
    });
  };

  // Fit view automatically
  const handleFitView = () => {
    const coords = Object.values(positions) as Position[];
    if (coords.length === 0) return;

    const xs = coords.map((c) => c.x);
    const ys = coords.map((c) => c.y);
    const minX = Math.min(...xs);
    const maxX = Math.max(...xs);
    const minY = Math.min(...ys);
    const maxY = Math.max(...ys);

    const graphWidth = maxX - minX + 200;
    const graphHeight = maxY - minY + 200;

    const container = containerRef.current;
    if (!container) return;
    const { width: cw, height: ch } = container.getBoundingClientRect();

    const nextZoom = Math.min(cw / graphWidth, ch / graphHeight, 1.2);
    setZoom(nextZoom);
    setPan({
      x: (cw - (maxX + minX) * nextZoom) / 2,
      y: (ch - (maxY + minY) * nextZoom) / 2,
    });
  };

  const handleResetZoom = () => {
    setZoom(0.85);
    setPan({ x: 80, y: 70 });
  };

  // Precalculate the set of all node IDs that are descendants of any collapsed node
  const collapsedDescendants = React.useMemo(() => {
    const set = new Set<string>();
    if (collapsedNodeIds.size === 0) return set;

    const queue: string[] = Array.from(collapsedNodeIds);
    const visited = new Set<string>();

    while (queue.length > 0) {
      const current = queue.shift()!;
      if (visited.has(current)) continue;
      visited.add(current);

      const children = indices.outgoing.get(current) || [];
      for (const child of children) {
        set.add(child);
        if (!visited.has(child)) {
          queue.push(child);
        }
      }
    }
    return set;
  }, [collapsedNodeIds, indices.outgoing]);

  // BFS helper to check if a node has any ancestors in the collapsed list
  const hasCollapsedAncestor = React.useCallback((id: string): boolean => {
    return collapsedDescendants.has(id);
  }, [collapsedDescendants]);

  // Check hidden descendant tree elements to skip rendering connection lines
  const isLinkHidden = React.useCallback((edge: LineageEdge) => {
    if (collapsedNodeIds.has(edge.from) || collapsedNodeIds.has(edge.to)) {
      return true;
    }
    return collapsedDescendants.has(edge.from) || collapsedDescendants.has(edge.to);
  }, [collapsedNodeIds, collapsedDescendants]);

  // Node helper signals for specific statuses in modes
  const getNodeBadgeClass = (node: LineageNode) => {
    if (mode === "validation") {
      switch (node.validation?.status) {
        case "fail":
          return "bg-rose-500 text-white animate-pulse";
        case "warn":
          return "bg-orange-400 text-white";
        default:
          return "bg-emerald-500 text-white";
      }
    }
    if (mode === "proof") {
      if (node.proof?.testStatus === "failed") return "bg-rose-500 text-white";
      if (node.proof?.testStatus === "passed") return "bg-indigo-500 text-white";
    }
    return "";
  };

  const getNodeBadgeInfo = (node: LineageNode) => {
    // Determine status precisely based on view mode first, fallback to generic props next
    if (mode === "validation") {
      switch (node.validation?.status) {
        case "fail":
          return {
            className: "bg-rose-500 text-white animate-pulse",
            icon: "fail",
            label: "ValidationError"
          };
        case "warn":
          return {
            className: "bg-amber-500 text-white",
            icon: "warn",
            label: "Warning"
          };
        default:
          return {
            className: "bg-emerald-500 text-white",
            icon: "verified",
            label: "Verified Proof"
          };
      }
    }

    if (mode === "proof") {
      if (node.proof?.testStatus === "failed") {
        return {
          className: "bg-rose-500 text-white animate-pulse",
          icon: "fail",
          label: "ValidationError"
        };
      }
      if (node.proof?.testStatus === "passed") {
        return {
          className: "bg-indigo-500 text-white",
          icon: "pass",
          label: "Active Layer Node"
        };
      }
    }

    // Generic fallbacks across all other modes so the legend is always active and correct
    if (node.validation?.status === "fail" || node.proof?.testStatus === "failed") {
      return {
        className: "bg-rose-500 text-white animate-pulse",
        icon: "fail",
        label: "ValidationError"
      };
    }
    if (node.proof?.testStatus === "passed") {
      return {
        className: "bg-indigo-500 text-white",
        icon: "pass",
        label: "Active Layer Node"
      };
    }
    if (node.validation?.status === "pass" || node.status === "certified") {
      return {
        className: "bg-emerald-500 text-white",
        icon: "verified",
        label: "Verified Proof"
      };
    }
    if (node.validation?.status === "warn") {
      return {
        className: "bg-amber-500 text-white",
        icon: "warn",
        label: "Warning"
      };
    }

    return null;
  };

  const columnHeaders = React.useMemo(() => {
    switch (mode) {
      case "lineage":
      case "flow-force":
        return [
          { col: 0, title: "ADR Setup" },
          { col: 1, title: "Specification" },
          { col: 2, title: "Core Features" },
          { col: 3, title: "Claims" },
          { col: 4, title: "Verifications" },
          { col: 5, title: "Certificates" },
          { col: 6, title: "Releases" },
        ];
      case "proof":
        return [
          { col: 0, title: "Specifications" },
          { col: 1, title: "Implementations" },
          { col: 2, title: "Claims assertions" },
          { col: 3, title: "Verification Tests" },
          { col: 4, title: "Target Releases/Risks" },
        ];
      case "origins":
        return [
          { col: 0, title: "Core Rules" },
          { col: 1, title: "Specification Registry" },
          { col: 2, title: "Local Repo Implementations" },
          { col: 3, title: "Custom Extensions" },
          { col: 4, title: "External Dependencies" },
        ];
      case "packs":
        return [
          { col: 0, title: "Core Registry (General)" },
          { col: 1, title: "Governance Standards" },
          { col: 2, title: "Contract Packs" },
          { col: 3, title: "Extension Packs" },
        ];
      case "validation":
        return [
          { col: 0, title: "Passing (No Drift)" },
          { col: 1, title: "Warnings (Drift Risk)" },
          { col: 2, title: "Failures (Blockers)" },
          { col: 3, title: "Draft / Unknown" },
        ];
      case "release":
        return [
          { col: 0, title: "Planned Backlog" },
          { col: 1, title: "Active Development" },
          { col: 2, title: "Certified Checked" },
          { col: 3, title: "Official Release checkpoints" },
        ];
      default:
        return [];
    }
  }, [mode]);

  const columnGuidePositions = React.useMemo(() => {
    const guides = new Map<number, { left: number; center: number; width: number }>();

    payload.nodes.forEach((node) => {
      if (hiddenNodeIds.has(node.id) || hasCollapsedAncestor(node.id)) return;
      const pos = positions[node.id];
      if (!pos) return;

      const col = columnForNode(node, mode);
      const current = guides.get(col);
      if (current) {
        current.left = Math.min(current.left, pos.x);
        current.width = Math.max(current.width, pos.x);
      } else {
        guides.set(col, { left: pos.x, center: pos.x, width: pos.x });
      }
    });

    guides.forEach((guide, col) => {
      const minX = guide.left;
      const maxX = guide.width;
      guides.set(col, {
        left: minX - 70,
        center: (minX + maxX) / 2,
        width: Math.max(200, maxX - minX + 140),
      });
    });

    return guides;
  }, [payload.nodes, positions, mode, hiddenNodeIds, hasCollapsedAncestor]);

  // --- MINIMAP NAVIGATION SYSTEM ---
  const minimapWidth = 180;
  const minimapHeight = 110;

  const {
    minX,
    maxX,
    minY,
    maxY,
    mapScale,
    offsetX,
    offsetY,
    visibleNodes,
  } = React.useMemo(() => {
    const isLarge = payload.nodes.length > 5000;
    const rawFiltered = isLarge
      ? payload.nodes.filter((node, idx) => {
          if (hiddenNodeIds.has(node.id) || hasCollapsedAncestor(node.id)) return false;
          const match = node.id.match(/-(\d+)$/);
          const megaIdx = match ? parseInt(match[1], 10) : -1;
          if (megaIdx !== -1) {
            return megaIdx <= 150 || megaIdx % 500 === 0;
          }
          return idx % 50 === 0;
        })
      : payload.nodes.filter(node => !hiddenNodeIds.has(node.id) && !hasCollapsedAncestor(node.id));

    // Deduplicate on node id for maximum robustness
    const seenIds = new Set<string>();
    const vNodes = rawFiltered.filter(node => {
      if (seenIds.has(node.id)) return false;
      seenIds.add(node.id);
      return true;
    });

    let mx1 = Infinity;
    let mx2 = -Infinity;
    let my1 = Infinity;
    let my2 = -Infinity;

    vNodes.forEach(node => {
      const pos = positions[node.id];
      if (pos) {
        if (pos.x < mx1) mx1 = pos.x;
        if (pos.x > mx2) mx2 = pos.x;
        if (pos.y < my1) my1 = pos.y;
        if (pos.y > my2) my2 = pos.y;
      }
    });

    if (mx1 === Infinity || mx2 === -Infinity) {
      mx1 = 0;
      mx2 = 1100;
    }
    if (my1 === Infinity || my2 === -Infinity) {
      my1 = 0;
      my2 = 620;
    }

    const padding = 100;
    mx1 -= padding;
    mx2 += padding;
    my1 -= padding;
    my2 += padding;

    const bWidth = Math.max(1, mx2 - mx1);
    const bHeight = Math.max(1, my2 - my1);

    const sX = (minimapWidth - 12) / bWidth;
    const sY = (minimapHeight - 12) / bHeight;
    const mScale = Math.max(0.001, Math.min(sX, sY));

    const offX = (minimapWidth - bWidth * mScale) / 2;
    const offY = (minimapHeight - bHeight * mScale) / 2;

    return {
      minX: mx1,
      maxX: mx2,
      minY: my1,
      maxY: my2,
      mapScale: mScale,
      offsetX: offX,
      offsetY: offY,
      visibleNodes: vNodes,
    };
  }, [payload.nodes, positions, hiddenNodeIds, collapsedNodeIds]);

  // Determine connected neighborhood nodes for validation highlighting ("ego hover") up to configurable num of hops.
  // We automatically bridge through non-visible (hidden/filtered) nodes to treat them as a single visual hop.
  const egoNeighborhood = React.useMemo(() => {
    if (!activeFocusNodeId) return null;
    const connected = new Set<string>([activeFocusNodeId]);

    const visibleNodeIds = new Set(visibleNodes.map((n) => n.id));
    let currentLevel = new Set<string>([activeFocusNodeId]);
    const hops = egoHops || 1;

    for (let h = 0; h < hops; h++) {
      const nextLevel = new Set<string>();
      currentLevel.forEach((nodeId) => {
        // Find visible neighbors (direct or bridged via hidden/filtered nodes)
        const visitedInSearch = new Set<string>([nodeId]);
        const queue: { id: string; d: number }[] = [{ id: nodeId, d: 0 }];

        while (queue.length > 0) {
          const { id, d } = queue.shift()!;
          const incoming = indices.incoming.get(id) || [];
          const outgoing = indices.outgoing.get(id) || [];
          const neighbors = [...incoming, ...outgoing];

          for (const neighbor of neighbors) {
            if (visitedInSearch.has(neighbor)) continue;
            visitedInSearch.add(neighbor);

            if (visibleNodeIds.has(neighbor)) {
              if (!connected.has(neighbor)) {
                connected.add(neighbor);
                nextLevel.add(neighbor);
              }
            } else {
              // It's a hidden/filtered node, bridge through it up to depth 3
              if (d < 3) {
                queue.push({ id: neighbor, d: d + 1 });
              }
            }
          }
        }
      });
      currentLevel = nextLevel;
    }

    return connected;
  }, [activeFocusNodeId, indices, egoHops, visibleNodes]);

  const getMiniCoords = (x: number, y: number) => {
    return {
      x: (x - minX) * mapScale + offsetX,
      y: (y - minY) * mapScale + offsetY,
    };
  };

  const visibleEdges = React.useMemo(() => {
    const isLarge = payload.nodes.length > 5000;
    if (isLarge) {
      const visibleNodeIds = new Set(visibleNodes.map(n => n.id));
      return payload.edges.filter(edge =>
        visibleNodeIds.has(edge.from) &&
        visibleNodeIds.has(edge.to) &&
        !isLinkHidden(edge)
      );
    }
    return payload.edges.filter(edge => !isLinkHidden(edge));
  }, [payload.edges, visibleNodes, isLinkHidden]);

  const viewportWidth = containerRef.current?.clientWidth || 1100;
  const viewportHeight = containerRef.current?.clientHeight || 620;

  const leftCanvas = debouncedBounds.left;
  const topCanvas = debouncedBounds.top;
  const rightCanvas = debouncedBounds.right;
  const bottomCanvas = debouncedBounds.bottom;

  const { renderedNodes, renderedEdges } = React.useMemo(() => {
    // Dynamic scale buffer based on zoom levels
    const buffer = 250 / Math.max(0.1, debouncedBounds.zoom);
    const xMin = leftCanvas - buffer;
    const xMax = rightCanvas + buffer;
    const yMin = topCanvas - buffer;
    const yMax = bottomCanvas + buffer;

    const rNodes: LineageNode[] = [];
    const nodeAdded = new Set<string>();

    // 1. Filter nodes inside the viewport bounds from the downsampled visibleNodes list
    visibleNodes.forEach((node) => {
      const pos = positions[node.id];
      if (!pos) return;
      if (pos.x >= xMin && pos.x <= xMax && pos.y >= yMin && pos.y <= yMax) {
        if (!nodeAdded.has(node.id)) {
          rNodes.push(node);
          nodeAdded.add(node.id);
        }
      }
    });

    // 2. Always make sure selectedNode, focusNode, and draggedNode are included in rendered list
    // even if they are slightly offscreen (to preserve lines or interaction states)
    const criticalNodeIds = [selectedNodeId, focusNodeId, draggedNodeId].filter(id => id ? true : false) as string[];
    criticalNodeIds.forEach(id => {
      if (!nodeAdded.has(id)) {
        const node = indices.nodeMap.get(id);
        if (node && !hiddenNodeIds.has(id) && !hasCollapsedAncestor(id)) {
          rNodes.push(node);
          nodeAdded.add(id);
        }
      }
    });

    // 3. Collect active edges whose endpoints are part of the rendered viewport set.
    // Pulling every incident edge for visible high-degree nodes can re-render
    // thousands of offscreen SVG paths and make repo-scale graphs sluggish.
    const rEdges: LineageEdge[] = [];
    const edgeAdded = new Set<string>();
    const renderedNodeIds = new Set(rNodes.map((node) => node.id));
    const criticalNodeIdsSet = new Set(criticalNodeIds);
    const maxRenderedEdges = payload.edges.length > 2000 ? 900 : 2000;

    for (const edge of visibleEdges) {
      const touchesCriticalNode = criticalNodeIdsSet.has(edge.from) || criticalNodeIdsSet.has(edge.to);
      if (rEdges.length >= maxRenderedEdges && !touchesCriticalNode) continue;

      const edgeId = `${edge.from}->${edge.to}:${edge.type || ""}`;
      if (edgeAdded.has(edgeId)) continue;

      if (hiddenNodeIds.has(edge.from) || hiddenNodeIds.has(edge.to)) continue;
      if (isLinkHidden(edge)) continue;
      if ((!renderedNodeIds.has(edge.from) || !renderedNodeIds.has(edge.to)) && !touchesCriticalNode) continue;

      const start = positions[edge.from];
      const end = positions[edge.to];
      if (!start || !end) continue;

      const edgeBuffer = 180 / Math.max(0.05, debouncedBounds.zoom);
      const minEdgeX = Math.min(start.x, end.x) - edgeBuffer;
      const maxEdgeX = Math.max(start.x, end.x) + edgeBuffer;
      const minEdgeY = Math.min(start.y, end.y) - edgeBuffer;
      const maxEdgeY = Math.max(start.y, end.y) + edgeBuffer;
      const isEdgeVisible =
        maxEdgeX >= leftCanvas &&
        minEdgeX <= rightCanvas &&
        maxEdgeY >= topCanvas &&
        minEdgeY <= bottomCanvas;

      if (!isEdgeVisible && !touchesCriticalNode) continue;

      rEdges.push(edge);
      edgeAdded.add(edgeId);
    }

    return { renderedNodes: rNodes, renderedEdges: rEdges };
  }, [
    visibleNodes,
    visibleEdges,
    positions,
    leftCanvas,
    rightCanvas,
    topCanvas,
    bottomCanvas,
    debouncedBounds.zoom,
    selectedNodeId,
    focusNodeId,
    draggedNodeId,
    indices.nodeMap,
    hiddenNodeIds,
    collapsedNodeIds,
    isLinkHidden,
  ]);

  // Calculate dynamic Ghost Edges that bypass hidden/filtered-out nodes
  const ghostEdges = React.useMemo(() => {
    const list: Array<{
      from: string;
      to: string;
      type: string;
      originalEdges: LineageEdge[];
      ghostNodeIds: string[];
      isGhost: true;
    }> = [];
    const seenPaths = new Set<string>();

    const visibleNodeIds = new Set(visibleNodes.map((n) => n.id));

    visibleNodes.forEach((startNode) => {
      const traverse = (
        currId: string,
        currentPath: string[],
        currentEdges: LineageEdge[]
      ) => {
        const outgoingEdges = indices.edgeMap.get(currId) || [];
        outgoingEdges.forEach((edge) => {
          if (edge.from !== currId) return;

          const targetId = edge.to;
          if (targetId === startNode.id) return; // ignore loops

          if (visibleNodeIds.has(targetId)) {
            if (currentPath.length > 0) {
              const pathKey = `${startNode.id}->${targetId}`;
              if (!seenPaths.has(pathKey)) {
                seenPaths.add(pathKey);
                list.push({
                  from: startNode.id,
                  to: targetId,
                  type: [...currentEdges, edge].map((e) => e.type || e.label || "link").join(" -> "),
                  originalEdges: [...currentEdges, edge],
                  ghostNodeIds: currentPath,
                  isGhost: true,
                });
              }
            }
          } else {
            // Check if we are still under the depth limit and not looping
            if (currentPath.length < 3 && !currentPath.includes(targetId)) {
              traverse(
                targetId,
                [...currentPath, targetId],
                [...currentEdges, edge]
              );
            }
          }
        });
      };

      traverse(startNode.id, [], []);
    });

    return list;
  }, [visibleNodes, indices.edgeMap]);

  const viewTopLeft = getMiniCoords(leftCanvas, topCanvas);
  const viewBottomRight = getMiniCoords(rightCanvas, bottomCanvas);

  const viewX = Math.max(0, Math.min(minimapWidth, viewTopLeft.x));
  const viewY = Math.max(0, Math.min(minimapHeight, viewTopLeft.y));
  const viewW = Math.max(4, Math.min(minimapWidth - viewX, viewBottomRight.x - viewTopLeft.x));
  const viewH = Math.max(4, Math.min(minimapHeight - viewY, viewBottomRight.y - viewTopLeft.y));

  const handleMinimapNav = (e: React.PointerEvent<HTMLDivElement>) => {
    if (!containerRef.current) return;
    const rect = e.currentTarget.getBoundingClientRect();
    const clickX = e.clientX - rect.left;
    const clickY = e.clientY - rect.top;

    const canvasX = (clickX - offsetX) / (mapScale || 1) + minX;
    const canvasY = (clickY - offsetY) / (mapScale || 1) + minY;

    const cw = containerRef.current.clientWidth;
    const ch = containerRef.current.clientHeight;

    setPan({
      x: cw / 2 - canvasX * zoom,
      y: ch / 2 - canvasY * zoom,
    });
  };

  const handleMinimapPointerDown = (e: React.PointerEvent<HTMLDivElement>) => {
    e.stopPropagation();
    e.preventDefault();
    setIsMinimapDragging(true);
    e.currentTarget.setPointerCapture(e.pointerId);
    handleMinimapNav(e);
  };

  const handleMinimapPointerMove = (e: React.PointerEvent<HTMLDivElement>) => {
    if (isMinimapDragging) {
      e.stopPropagation();
      handleMinimapNav(e);
    }
  };

  const handleMinimapPointerUp = (e: React.PointerEvent<HTMLDivElement>) => {
    if (isMinimapDragging) {
      e.stopPropagation();
      setIsMinimapDragging(false);
      e.currentTarget.releasePointerCapture(e.pointerId);
    }
  };

  const getFamilySvgColor = (family: LineageFamily): string => {
    switch (family) {
      case "ADR": return "#d97706";
      case "SPEC": return "#2563eb";
      case "Feature": return "#4f46e5";
      case "Claim": return "#9333ea";
      case "Test": return "#e11d48";
      case "Evidence": return "#059669";
      case "Release": return "#0d9488";
      case "Boundary": return "#475569";
      case "Risk": return "#ea580c";
      case "Issue": return "#dc2626";
      default: return "#4b5563";
    }
  };

  return (
    <div
      ref={containerRef}
      id="lineage-graph-viewport"
      className={`relative w-full h-full overflow-hidden select-none cursor-grab active:cursor-grabbing transition-colors duration-300 ${
        viewSettings.theme === "steel-dark" ? "bg-slate-900 border border-slate-800" : "bg-slate-50/50 border border-slate-200"
      }`}
      onPointerDown={handleWorkspacePointerDown}
      onPointerMove={handleWorkspacePointerMove}
      onPointerUp={handleWorkspacePointerUp}
      onPointerLeave={handleWorkspacePointerUp}
      onWheel={handleWheel}
    >
      {/* Background Dot Grid */}
      <div
        className="absolute inset-0 pointer-events-none opacity-40"
        style={{
          backgroundImage: `radial-gradient(${
            viewSettings.theme === "steel-dark" ? "#ffffff33" : "#00000018"
          } 1px, transparent 1px)`,
          backgroundSize: "24px 24px",
          transform: `translate(${pan.x}px, ${pan.y}px)`,
        }}
      />

      {/* Standalone Canvas UI Overlay Title */}
      <div className="absolute top-4 left-4 pointer-events-none z-10 hidden sm:block">
        <span className="text-[10px] font-mono tracking-wider text-slate-400 uppercase bg-slate-800/80 px-2 py-0.5 rounded border border-slate-700/80">
          {mode.slice(0, 1).toUpperCase() + mode.slice(1)} Mode
        </span>
      </div>

      {/* Infinite Scale Workspace Transform Container */}
      <div
        className={`absolute w-0 h-0 origin-top-left ${
          isPanning || draggedNodeId !== null ? "" : "transition-transform duration-300 ease-out"
        }`}
        style={{
          transform: `translate(${pan.x}px, ${pan.y}px) scale(${zoom})`,
        }}
      >
        {/* Layer 0: Column guidelines & lane headings */}
        {mode !== "network" && columnHeaders.map((head) => {
          const guide = columnGuidePositions.get(head.col);
          const x = guide?.center ?? 60 + head.col * 210;
          return (
            <div
              key={head.col}
              className="absolute pointer-events-none flex flex-col items-center"
              style={{
                left: guide?.left ?? x - 100,
                top: -30,
                width: guide?.width ?? 200,
                height: 1200,
              }}
            >
              {/* Vertical dotted lane guide */}
              <div
                className={`w-0 h-[850px] border-l border-dashed my-8 opacity-20 ${
                  viewSettings.theme === "steel-dark" ? "border-slate-500" : "border-indigo-400"
                }`}
              />

              {/* Lane Heading label card */}
              <div
                className={`absolute top-0 px-2.5 py-1 rounded-full text-[9px] font-bold font-mono tracking-wider uppercase border shadow-sm backdrop-blur-md transition-colors ${
                  viewSettings.theme === "steel-dark"
                    ? "bg-slate-800/90 text-slate-300 border-slate-700/80"
                    : "bg-white/95 text-indigo-800 border-indigo-100"
                }`}
              >
                {head.title}
              </div>
            </div>
          );
        })}
        {/* Layer 1: Links & Edge Curves */}
        <svg className="absolute overflow-visible pointer-events-none z-0" style={{ width: 1, height: 1 }}>
          <style>{`
            @keyframes line-flow-active {
              to {
                stroke-dashoffset: -20;
              }
            }
            .flow-active-dash {
              animation: line-flow-active 0.85s linear infinite;
            }
          `}</style>
          <defs>
            {/* Edge line arrow marker endings */}
            <marker id="arrow" viewBox="0 0 10 10" refX="18" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
              <path d="M 0 0 L 10 5 L 0 10 z" fill="#94a3b8" />
            </marker>
            <marker id="arrow-selected" viewBox="0 0 10 10" refX="18" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
              <path d="M 0 0 L 10 5 L 0 10 z" fill="#6366f1" />
            </marker>
            <marker id="arrow-error" viewBox="0 0 10 10" refX="18" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
              <path d="M 0 0 L 10 5 L 0 10 z" fill="#ef4444" />
            </marker>
            <marker id="arrow-success" viewBox="0 0 10 10" refX="18" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
              <path d="M 0 0 L 10 5 L 0 10 z" fill="#10b981" />
            </marker>
            <marker id="arrow-incoming" viewBox="0 0 10 10" refX="18" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
              <path d="M 0 0 L 10 5 L 0 10 z" fill="#06b6d4" />
            </marker>
            <marker id="arrow-outgoing" viewBox="0 0 10 10" refX="18" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
              <path d="M 0 0 L 10 5 L 0 10 z" fill="#ec4899" />
            </marker>
          </defs>

          {renderedEdges.map((edge, idx) => {
            const start = positions[edge.from];
            const end = positions[edge.to];
            if (!start || !end) return null;
            if (hiddenNodeIds.has(edge.from) || hiddenNodeIds.has(edge.to)) return null;
            if (isLinkHidden(edge)) return null;

            // Isolate active focus hops filter
            if (isolateEgo && egoNeighborhood && (!egoNeighborhood.has(edge.from) || !egoNeighborhood.has(edge.to))) {
              return null;
            }

            // Performance: Edge Viewport Bounding-Box Culling logic
            const edgeBuffer = 180 / Math.max(0.05, zoom);
            const minEdgeX = Math.min(start.x, end.x) - edgeBuffer;
            const maxEdgeX = Math.max(start.x, end.x) + edgeBuffer;
            const minEdgeY = Math.min(start.y, end.y) - edgeBuffer;
            const maxEdgeY = Math.max(start.y, end.y) + edgeBuffer;

            const isEdgeVisible =
              maxEdgeX >= leftCanvas &&
              minEdgeX <= rightCanvas &&
              maxEdgeY >= topCanvas &&
              minEdgeY <= bottomCanvas;

            const isSelected = selectedNodeId === edge.from || selectedNodeId === edge.to;
            const isFocused = focusNodeId === edge.from || focusNodeId === edge.to;
            const isDragged = draggedNodeId === edge.from || draggedNodeId === edge.to;

            if (!isEdgeVisible && !isSelected && !isFocused && !isDragged) {
              return null;
            }

            // Highlight connections on hover or explicit selection
            const isHovered = hoveredNodeId === edge.from || hoveredNodeId === edge.to;
            const hasFocus = isFocused;

            // Directional trace calculations relative to active focus nodes
            const isIncomingToFocus = activeFocusNodeId === edge.to;
            const isOutgoingFromFocus = activeFocusNodeId === edge.from;
            const isConnectedToFocus = isIncomingToFocus || isOutgoingFromFocus;

            // Check if BOTH ends are in the active focus ego neighborhood (all hops)
            const isEdgeInEgo = !!(activeFocusNodeId && egoNeighborhood && egoNeighborhood.has(edge.from) && egoNeighborhood.has(edge.to));

            // Determine active layout highlighting
            let strokeColor = "#94a3b8"; // Slate-400
            let strokeWidth = viewSettings.edgeWidth;
            let opacity = viewSettings.edgeOpacity;
            let marker = "url(#arrow)";

            if (mode === "validation" && (edge.status === "stale" || edge.status === "missing" || edge.proof?.blocker)) {
              strokeColor = "#ef4444"; // Blocker red
              strokeWidth = viewSettings.edgeWidth + 1.2;
              marker = "url(#arrow-error)";
            } else if (mode === "proof") {
              if (edge.status === "active") {
                strokeColor = "#10b981"; // Success emerald
                marker = "url(#arrow-success)";
              } else {
                strokeColor = "#f59e0b"; // Warning amber
                marker = "url(#arrow-error)";
              }
            }

            // Normal highlight overlay override
            if (isSelected || hasFocus || isDragged) {
              strokeColor = "#6366f1"; // Indigo selection
              strokeWidth = viewSettings.edgeWidth + 2.5;
              opacity = 1.0;
              marker = "url(#arrow-selected)";
            }

            // High aesthetic priority directional ribbons if there is an active focus node
            if (activeFocusNodeId) {
              if (isConnectedToFocus) {
                opacity = 1.0;
                strokeWidth = viewSettings.edgeWidth + 2.0;
                strokeColor = isIncomingToFocus ? "#06b6d4" : "#ec4899";
                marker = isIncomingToFocus ? "url(#arrow-incoming)" : "url(#arrow-outgoing)";
              } else if (isEdgeInEgo) {
                // Highlight ribbon for all hops within the neighborhood
                opacity = 1.0;
                strokeWidth = viewSettings.edgeWidth + 1.2;
                strokeColor = "#818cf8"; // Violet/Indigo slate
                marker = "url(#arrow-selected)";
              } else {
                opacity = 0.10; // Drastic dimming for non-connected elements to make selected ribbon pop!
                strokeWidth = Math.max(1, viewSettings.edgeWidth - 0.5);
              }
            } else if (hoveredNodeId) {
              if (isHovered) {
                opacity = 1.0;
                strokeWidth = viewSettings.edgeWidth + 1.5;
              } else {
                opacity = 0.12;
              }
            }

            // Render path curves
            const curvePath = generateSvgLinkCurve(start.x, start.y, end.x, end.y, mode);

            return (
              <g key={`${edge.from}-${edge.to}-${idx}`} className={transitionClass}>
                {/* Invisible hover helper line for clickability */}
                <path
                  d={curvePath}
                  fill="none"
                  stroke="transparent"
                  strokeWidth={14}
                  className="cursor-pointer pointer-events-auto"
                />

                {/* Soft glow ribbon underlay for active connections */}
                {activeFocusNodeId && (isConnectedToFocus || isEdgeInEgo) && (
                  <path
                    d={curvePath}
                    fill="none"
                    stroke={isConnectedToFocus ? (isIncomingToFocus ? "#06b6d4" : "#ec4899") : "#818cf8"}
                    strokeWidth={strokeWidth + 5}
                    opacity={0.16}
                    className={`${transitionClass} blur-[2px]`}
                  />
                )}

                {/* Animated dash ribbon flow running along curve paths */}
                {activeFocusNodeId && (isConnectedToFocus || isEdgeInEgo) && (
                  <path
                    d={curvePath}
                    fill="none"
                    stroke={isConnectedToFocus ? (isIncomingToFocus ? "#06b6d4" : "#ec4899") : "#818cf8"}
                    strokeWidth={strokeWidth}
                    strokeDasharray="6,6"
                    opacity={0.8}
                    className={`flow-active-dash ${transitionClass}`}
                  />
                )}

                {/* Visual Connection line path */}
                <path
                  d={curvePath}
                  fill="none"
                  stroke={strokeColor}
                  strokeWidth={strokeWidth}
                  strokeDasharray={
                    activeFocusNodeId && (isConnectedToFocus || isEdgeInEgo)
                      ? undefined
                      : (edge.status === "planned" || edge.status === "stale" ? "5,5" : undefined)
                  }
                  opacity={opacity}
                  markerEnd={marker}
                  className={transitionClass}
                />

                {/* Connected edge compact metadata text label */}
                {viewSettings.showLabels && edge.type && (
                  <text
                    x={(start.x + end.x) / 2}
                    y={(start.y + end.y) / 2 - 4}
                    fill={viewSettings.theme === "steel-dark" ? "#94a3b8" : "#475569"}
                    fontSize={9}
                    fontFamily="monospace"
                    textAnchor="middle"
                    opacity={opacity}
                  >
                    {edge.type}
                  </text>
                )}
              </g>
            );
          })}

          {/* Layer 1.5: Ghost Edges bridging hidden nodes */}
          {ghostEdges.map((edge, idx) => {
            const start = positions[edge.from];
            const end = positions[edge.to];
            if (!start || !end) return null;

            // Isolate active focus hops filter
            if (isolateEgo && egoNeighborhood && (!egoNeighborhood.has(edge.from) || !egoNeighborhood.has(edge.to))) {
              return null;
            }

            // Highlighting
            const isSelected = selectedNodeId === edge.from || selectedNodeId === edge.to;
            const isFocused = focusNodeId === edge.from || focusNodeId === edge.to;
            const isDragged = draggedNodeId === edge.from || draggedNodeId === edge.to;
            const isHovered = hoveredNodeId === edge.from || hoveredNodeId === edge.to;
            const hasFocus = isFocused;

            const isIncomingToFocus = activeFocusNodeId === edge.to;
            const isOutgoingFromFocus = activeFocusNodeId === edge.from;
            const isConnectedToFocus = isIncomingToFocus || isOutgoingFromFocus;

            // Check if BOTH ends are in the active focus ego neighborhood (all hops)
            const isEdgeInEgo = !!(activeFocusNodeId && egoNeighborhood && egoNeighborhood.has(edge.from) && egoNeighborhood.has(edge.to));

            let strokeColor = viewSettings.theme === "steel-dark" ? "#a78bfa" : "#8b5cf6"; // Violet/Purple for ghost
            let strokeWidth = viewSettings.edgeWidth || 2;
            let opacity = (viewSettings.edgeOpacity || 0.6) * 0.95;
            let marker = "url(#arrow-selected)"; // ghost arrow marker with elegant styling

            if (isSelected || hasFocus || isDragged) {
              strokeColor = "#7c3aed"; // Rich Indigo/Purple
              strokeWidth = (viewSettings.edgeWidth || 2) + 2.0;
              opacity = 1.0;
            }

            if (activeFocusNodeId) {
              if (isConnectedToFocus) {
                opacity = 1.0;
                strokeWidth = (viewSettings.edgeWidth || 2) + 1.5;
                strokeColor = isIncomingToFocus ? "#06b6d4" : "#ec4899";
                marker = isIncomingToFocus ? "url(#arrow-incoming)" : "url(#arrow-outgoing)";
              } else if (isEdgeInEgo) {
                opacity = 1.0;
                strokeWidth = (viewSettings.edgeWidth || 2) + 1.0;
                strokeColor = "#818cf8";
              } else {
                opacity = 0.10;
              }
            } else if (hoveredNodeId) {
              if (isHovered) {
                opacity = 1.0;
                strokeWidth = (viewSettings.edgeWidth || 2) + 1.2;
              } else {
                opacity = 0.12;
              }
            }

            // Math for midpoint (Ghost node visual location)
            const midX = (start.x + end.x) / 2;
            const midY = (start.y + end.y) / 2;

            // Compute wavy/curly parallel curves offset left and right
            const spacing = 4.0;
            const pathLeft = generateGhostParallelPaths(start.x, start.y, end.x, end.y, mode, -spacing);
            const pathRight = generateGhostParallelPaths(start.x, start.y, end.x, end.y, mode, spacing);

            // First bypassed node family letter
            const firstBypassedNode = indices.nodeMap.get(edge.ghostNodeIds[0]);
            let ghostLabelLetter = "G";
            if (firstBypassedNode) {
              const family = (firstBypassedNode.family || "").toUpperCase();
              if (family.startsWith("SPEC")) ghostLabelLetter = "S";
              else if (family.startsWith("ADR")) ghostLabelLetter = "A";
              else if (family.startsWith("FEAT")) ghostLabelLetter = "F";
              else if (family.startsWith("CLAIM")) ghostLabelLetter = "C";
              else if (family.startsWith("TEST")) ghostLabelLetter = "T";
              else if (family.startsWith("EVID")) ghostLabelLetter = "E";
              else if (family.startsWith("RELE")) ghostLabelLetter = "R";
              else if (family.startsWith("RISK")) ghostLabelLetter = "R";
              else if (family.startsWith("BOU")) ghostLabelLetter = "B";
              else if (family.startsWith("ISS")) ghostLabelLetter = "I";
              else ghostLabelLetter = family.charAt(0) || "G";
            }

            // Display the 2 skip labels (left label / right label)
            const label1 = edge.originalEdges[0]?.type || edge.originalEdges[0]?.label || "link";
            const label2 = edge.originalEdges[edge.originalEdges.length - 1]?.type || edge.originalEdges[edge.originalEdges.length - 1]?.label || "link";

            // Positions for labels: halfway between start and mid, and mid and end
            const lx1 = (start.x + midX) / 2;
            const ly1 = (start.y + midY) / 2 - 8;
            const lx2 = (midX + end.x) / 2;
            const ly2 = (midY + end.y) / 2 - 8;

            const textWidth1 = label1.length * 5.2;
            const textWidth2 = label2.length * 5.2;

            return (
              <g key={`ghost-${edge.from}-${edge.to}-${idx}`} className={transitionClass}>
                {/* Visual Connection line paths (parallel double-dashed) */}
                <path
                  d={pathLeft}
                  fill="none"
                  stroke={strokeColor}
                  strokeWidth={strokeWidth - 0.5}
                  strokeDasharray="4,4"
                  opacity={opacity}
                  markerEnd={marker}
                  className={transitionClass}
                />
                <path
                  d={pathRight}
                  fill="none"
                  stroke={strokeColor}
                  strokeWidth={strokeWidth - 0.5}
                  strokeDasharray="4,4"
                  opacity={opacity}
                  markerEnd={marker}
                  className={transitionClass}
                />

                {/* Soft glow ribbon underlay for active connections */}
                {activeFocusNodeId && (isConnectedToFocus || isEdgeInEgo) && (
                  <path
                    d={pathLeft}
                    fill="none"
                    stroke={isConnectedToFocus ? (isIncomingToFocus ? "#06b6d4" : "#ec4899") : "#818cf8"}
                    strokeWidth={strokeWidth + 4}
                    opacity={0.14}
                    className={`${transitionClass} blur-[2px]`}
                  />
                )}

                {/* Mask / mask background circle representing the Ghost Node join */}
                <circle
                  cx={midX}
                  cy={midY}
                  r={12}
                  fill={viewSettings.theme === "steel-dark" ? "#1e293b" : "#f8fafc"}
                  stroke={strokeColor}
                  strokeWidth={2}
                  strokeDasharray="3,2"
                  opacity={opacity}
                />
                <text
                  x={midX}
                  y={midY + 3.5}
                  fill={strokeColor}
                  fontSize={10}
                  fontWeight="bold"
                  fontFamily="monospace"
                  textAnchor="middle"
                  opacity={opacity}
                >
                  {ghostLabelLetter}
                </text>

                {/* Left side label */}
                {viewSettings.showLabels && label1 && (
                  <g opacity={opacity}>
                    <rect
                      x={lx1 - textWidth1 / 2 - 2}
                      y={ly1 - 7}
                      width={textWidth1 + 4}
                      height={11}
                      rx={2}
                      fill={viewSettings.theme === "steel-dark" ? "#111827" : "#ffffff"}
                      stroke={strokeColor}
                      strokeWidth={0.5}
                      strokeOpacity={0.4}
                      opacity={0.9}
                    />
                    <text
                      x={lx1}
                      y={ly1 + 1}
                      fill={viewSettings.theme === "steel-dark" ? "#cbd5e1" : "#1e293b"}
                      fontSize={8}
                      fontFamily="monospace"
                      textAnchor="middle"
                    >
                      {label1}
                    </text>
                  </g>
                )}

                {/* Right side label */}
                {viewSettings.showLabels && label2 && (
                  <g opacity={opacity}>
                    <rect
                      x={lx2 - textWidth2 / 2 - 2}
                      y={ly2 - 7}
                      width={textWidth2 + 4}
                      height={11}
                      rx={2}
                      fill={viewSettings.theme === "steel-dark" ? "#111827" : "#ffffff"}
                      stroke={strokeColor}
                      strokeWidth={0.5}
                      strokeOpacity={0.4}
                      opacity={0.9}
                    />
                    <text
                      x={lx2}
                      y={ly2 + 1}
                      fill={viewSettings.theme === "steel-dark" ? "#cbd5e1" : "#1e293b"}
                      fontSize={8}
                      fontFamily="monospace"
                      textAnchor="middle"
                    >
                      {label2}
                    </text>
                  </g>
                )}
              </g>
            );
          })}
        </svg>

        {/* Layer 2: Node Div Avatars */}
        {renderedNodes.map((node) => {
          if (hiddenNodeIds.has(node.id)) return null;
          const pos = positions[node.id];
          if (!pos) return null;

          // Check if parent collapsed
          if (hasCollapsedAncestor(node.id)) return null;

          // Viewport Culling logic to maintain pristine performance for very large datasets (1000+ nodes)
          // We scale the boundary buffer with current zoom level to avoid premature clipping
          const buffer = 150 / Math.max(0.05, zoom);
          const isVisible =
            pos.x >= leftCanvas - buffer &&
            pos.x <= rightCanvas + buffer &&
            pos.y >= topCanvas - buffer &&
            pos.y <= bottomCanvas + buffer;

          const isSelected = selectedNodeId === node.id || (selectedNodeIds && selectedNodeIds.has(node.id));
          const isFocused = focusNodeId === node.id;
          const isHighlighted = highlightedNodeIds && highlightedNodeIds.has(node.id);
          const hasHighlights = highlightedNodeIds && highlightedNodeIds.size > 0;
          const fadeOpacityStyle = hasHighlights && !isHighlighted ? "opacity-35 grayscale" : "opacity-100";

          if (!isVisible && !isSelected && !isFocused && draggedNodeId !== node.id && !isHighlighted) {
            return null;
          }

          const isEgoInScope = egoNeighborhood === null || egoNeighborhood.has(node.id);

          // Completely hide non-hop nodes in focus if isolateEgo is active
          if (isolateEgo && egoNeighborhood && !egoNeighborhood.has(node.id)) {
            return null;
          }

          const hasChildren = (indices.outgoing.get(node.id) || []).length > 0;
          const isCollapsed = collapsedNodeIds.has(node.id);

          const isEgoHopNode = !!(activeFocusNodeId && egoNeighborhood && egoNeighborhood.has(node.id) && node.id !== activeFocusNodeId);
          const isActiveFocusCenter = activeFocusNodeId === node.id;

          let colors = FAMILY_COLORS[node.family] || FAMILY_COLORS.Profile;

          if (isEgoHopNode) {
            colors = {
              bg:
                node.family === "ADR" ? "bg-amber-200/95" :
                node.family === "SPEC" ? "bg-blue-200/95" :
                node.family === "Feature" ? "bg-indigo-200/95" :
                node.family === "Claim" ? "bg-purple-200/95" :
                node.family === "Test" ? "bg-rose-200/95" :
                node.family === "Evidence" ? "bg-emerald-200/95" :
                node.family === "Release" ? "bg-teal-200/95" :
                node.family === "Boundary" ? "bg-slate-200/95" :
                node.family === "Risk" ? "bg-orange-200/95" :
                node.family === "Issue" ? "bg-red-200/95" : "bg-slate-300",
              text:
                node.family === "ADR" ? "text-amber-950 font-extrabold" :
                node.family === "SPEC" ? "text-blue-950 font-extrabold" :
                node.family === "Feature" ? "text-indigo-950 font-extrabold" :
                node.family === "Claim" ? "text-purple-950 font-extrabold" :
                node.family === "Test" ? "text-rose-950 font-extrabold" :
                node.family === "Evidence" ? "text-emerald-950 font-extrabold" :
                node.family === "Release" ? "text-teal-950 font-extrabold" :
                node.family === "Boundary" ? "text-slate-950 font-extrabold" :
                node.family === "Risk" ? "text-orange-950 font-extrabold" :
                node.family === "Issue" ? "text-red-950 font-extrabold" : "text-black",
              border:
                node.family === "ADR" ? "border-amber-600" :
                node.family === "SPEC" ? "border-blue-600" :
                node.family === "Feature" ? "border-indigo-600" :
                node.family === "Claim" ? "border-purple-600" :
                node.family === "Test" ? "border-rose-600" :
                node.family === "Evidence" ? "border-emerald-600" :
                node.family === "Release" ? "border-teal-600" :
                node.family === "Boundary" ? "border-slate-700" :
                node.family === "Risk" ? "border-orange-600" :
                node.family === "Issue" ? "border-red-600" : "border-slate-800",
              glow: "shadow-lg shadow-slate-350/50"
            };
          }

          // Determine specific avatar display borders
          let borderOverlay = isSelected
            ? "ring-4 ring-offset-2 ring-indigo-500 scale-105 z-40 shadow-indigo-400"
            : isFocused
            ? "ring-4 ring-offset-2 ring-teal-500 scale-105 z-40 shadow-teal-300"
            : isActiveFocusCenter
            ? "ring-4 ring-offset-2 ring-indigo-600 scale-110 z-50 shadow-indigo-500 shadow-2xl font-black"
            : isEgoHopNode
            ? `${colors.border} border-[3.5px] scale-105 z-30 shadow-xl`
            : isHighlighted
            ? "ring-4 ring-offset-1 ring-amber-500 shadow-amber-300 scale-105 animate-pulse z-35"
            : "border-slate-300 border-2";

          if (viewSettings.theme === "steel-dark" && !isSelected && !isFocused && !isActiveFocusCenter && !isEgoHopNode && !isHighlighted) {
            borderOverlay = "border-slate-600 border";
          }

          const nodeGroup = customGroups?.find((g) => g.nodeIds.includes(node.id));

          return (
            <motion.div
              id={`node-${node.id}`}
              key={node.id}
              className={`absolute graph-node-avatar group flex flex-col items-center justify-center ${transitionClass} ${
                isEgoInScope ? "scale-100" : "opacity-25 scale-90 blur-[1px]"
              } ${fadeOpacityStyle}`}
              style={{
                left: pos.x - 30, // center on (x,y) coordinates
                top: pos.y - 30,
                width: 60,
                height: 60,
              }}
              onMouseEnter={() => setHoveredNodeId(node.id)}
              onMouseLeave={() => setHoveredNodeId(null)}
              onClick={(e) => {
                e.stopPropagation();
                if (hasDraggedRef.current) {
                  return; // Avoid selecting node while dragging it
                }
                onSelectNode(node.id, e.shiftKey);
              }}
              onPointerDown={(e) => handleNodePointerDown(node.id, e)}
              onPointerMove={(e) => handleNodePointerMove(node.id, e)}
              onPointerUp={(e) => handleNodePointerUp(node.id, e)}
              onDoubleClick={(e) => handleNodeDoubleClick(node.id, e)}
              title={mode === "network" ? "Drag to place - Double-click to unpin" : "Drag to reposition"}
            >
              {nodeGroup && (
                <span className="absolute -top-3 bg-slate-900 border border-slate-700 text-amber-300 font-extrabold px-1.5 py-0.2 rounded text-[7.5px] font-mono tracking-wider shadow z-50 whitespace-nowrap uppercase select-none">
                  * {nodeGroup.label}
                </span>
              )}
              {/* Circular HTML element with custom CSS border radius */}
              <div
                className={`w-12 h-12 rounded-full flex items-center justify-center font-bold text-xs shadow-md transition-transform duration-200 relative ${
                  draggedNodeId === node.id
                    ? "cursor-grabbing scale-110 shadow-2xl ring-4 ring-indigo-500"
                    : "cursor-grab hover:cursor-grab active:cursor-grabbing hover:scale-115 active:scale-95"
                } ${colors.bg} ${colors.text} ${borderOverlay} ${colors.glow}`}
              >
                {/* Node icon family symbol */}
                <span className="text-[10px] font-mono select-none pointer-events-none">
                  {node.family.substring(0, 3).toUpperCase()}
                </span>

                {/* Subtree recursive expand-collapse helper circular button */}
                {hasChildren && (
                  <button
                    className="absolute -bottom-1 -right-1 w-5 h-5 rounded-full bg-slate-800 text-white flex items-center justify-center border border-slate-600 hover:bg-slate-700 pointer-events-auto shadow-sm transition-colors z-20"
                    onClick={(e) => {
                      e.stopPropagation();
                      onToggleCollapse(node.id);
                    }}
                    title={isCollapsed ? "Expand Subtree" : "Collapse Subtree"}
                  >
                    {isCollapsed ? (
                      <Plus size={10} className="stroke-[3] text-emerald-400" />
                    ) : (
                      <Minus size={10} className="stroke-[3] text-slate-300" />
                    )}
                  </button>
                )}

                {/* Interactive Pin button on top-left: Click to toggle pin/unpin coordinates fixed state */}
                <button
                  className={`absolute -top-1.5 -left-1.5 rounded-full w-5 h-5 flex items-center justify-center border shadow-sm transition-all pointer-events-auto z-30 ${
                    (pos as any).fx !== null && (pos as any).fx !== undefined
                      ? "bg-indigo-600 border-indigo-500 text-white hover:bg-indigo-700 scale-100 opacity-100"
                      : "bg-white border-slate-300 text-slate-400 opacity-0 group-hover:opacity-100 hover:text-slate-600 hover:bg-slate-50 scale-90 group-hover:scale-100"
                  }`}
                  onClick={(e) => handleTogglePinNode(node.id, e)}
                  title={(pos as any).fx !== null && (pos as any).fx !== undefined ? "Click to unpin node (Release physics)" : "Click to pin node in current position"}
                >
                  <Pin size={9} className={(pos as any).fx !== null && (pos as any).fx !== undefined ? "rotate-45 fill-white" : "rotate-45"} />
                </button>

                {/* Persistent Status Badge on top-right: always visible to match bottom-left legend */}
                {getNodeBadgeInfo(node) && (() => {
                  const badge = getNodeBadgeInfo(node)!;
                  return (
                    <div
                      className={`absolute -top-1.5 -right-1.5 rounded-full w-5 h-5 flex items-center justify-center border border-white shadow-md z-30 pointer-events-none ${badge.className}`}
                      title={badge.label}
                    >
                      {badge.icon === "fail" && <X size={10} className="stroke-[4] text-white" />}
                      {badge.icon === "warn" && <HelpCircle size={10} className="stroke-[3] text-white" />}
                      {badge.icon === "verified" && <Check size={10} className="stroke-[4] text-white" />}
                      {badge.icon === "pass" && <Check size={10} className="stroke-[4] text-white" />}
                    </div>
                  );
                })()}

                {/* Interactive Hide button on bottom-left: shown on hover, uses clear indicator to hide node from graph */}
                <button
                  className="absolute -bottom-1.5 -left-1.5 rounded-full w-5 h-5 bg-white border border-slate-300 text-slate-400 hover:text-rose-500 hover:border-rose-300 flex items-center justify-center shadow-sm transition-all pointer-events-auto z-30 scale-90 group-hover:scale-100 opacity-0 group-hover:opacity-100 hover:bg-rose-50 cursor-pointer"
                  onClick={(e) => {
                    e.stopPropagation();
                    onToggleHideNode(node.id);
                  }}
                  title="Hide this node from view"
                >
                  <EyeOff size={9} className="stroke-[2.5]" />
                </button>
              </div>

              {/* Node ID / Title label tag overlay */}
              {viewSettings.showLabels && (
                <div
                  className={`absolute top-13 pointer-events-none text-[10px] font-medium tracking-tight truncate max-w-[120px] text-center px-1.5 py-0.5 rounded shadow-sm border ${
                    viewSettings.theme === "steel-dark"
                      ? "bg-slate-800 text-slate-200 border-slate-700"
                      : "bg-white text-slate-700 border-slate-200"
                  }`}
                >
                  {node.label || node.id}
                </div>
              )}
            </motion.div>
          );
        })}
      </div>

      {/* Floating Canvas Camera Control Panel Toolbar */}
      <div className="absolute bottom-4 right-4 flex items-center gap-1.5 bg-slate-900/90 border border-slate-700/80 rounded-lg p-1.5 shadow-xl backdrop-blur-md z-10">
        <button
          onClick={() => setZoom((z) => Math.max(z / 1.25, 0.15))}
          className="canvas-button p-2 text-slate-300 hover:text-white rounded hover:bg-slate-800 transition"
          title="Zoom Out"
        >
          <ZoomOut size={16} />
        </button>
        <button
          onClick={() => setZoom((z) => Math.min(z * 1.25, 3.0))}
          className="canvas-button p-2 text-slate-300 hover:text-white rounded hover:bg-slate-800 transition"
          title="Zoom In"
        >
          <ZoomIn size={16} />
        </button>
        <button
          onClick={handleFitView}
          className="canvas-button p-2 text-slate-300 hover:text-white rounded hover:bg-slate-800 transition"
          title="Fit Viewport on Nodes"
        >
          <Maximize size={16} />
        </button>
        <button
          onClick={handleResetZoom}
          className="canvas-button p-2 text-slate-300 hover:text-white rounded hover:bg-slate-850 transition"
          title="Reset Zoom to 100%"
        >
          <RefreshCw size={16} />
        </button>
        {mode === "network" && (
          <button
            onClick={() => {
              const nextPositions = { ...positions };
              Object.keys(nextPositions).forEach((id) => {
                nextPositions[id] = {
                  ...nextPositions[id],
                  fx: null,
                  fy: null,
                };
              });
              onUpdatePositions(nextPositions);
            }}
            className="canvas-button p-2 text-slate-300 hover:text-indigo-400 rounded hover:bg-slate-800 transition border-l border-slate-700 pl-2"
            title="Unpin All Anchors (Release Physics)"
          >
            <PinOff size={16} />
          </button>
        )}
        {hiddenNodeIds.size > 0 && (
          <button
            onClick={onClearHiddenNodes}
            className="canvas-button p-2 text-rose-400 hover:text-white rounded hover:bg-slate-800 transition border-l border-slate-700 pl-2 flex items-center gap-1 text-xs font-bold"
            title={`Reveal all ${hiddenNodeIds.size} hidden nodes`}
          >
            <Eye size={15} />
            <span>Show All ({hiddenNodeIds.size})</span>
          </button>
        )}
      </div>



      {/* Floating Bottom Tooltip / Legend */}
      <div className={`absolute bottom-4 left-4 pointer-events-none hidden lg:flex items-center gap-4 px-3 py-2 rounded-lg border shadow-lg z-10 font-sans backdrop-blur-md ${
        viewSettings.theme === "steel-dark"
          ? "bg-slate-900/90 border-slate-700/80 text-slate-300"
          : "bg-white/95 border-slate-200 text-slate-600"
      }`}>
        <div className="flex items-center gap-1.5">
          <div className="w-2.5 h-2.5 rounded-full bg-indigo-500 shadow-sm" />
          <span className="text-[10px] font-semibold">Active Layer Node</span>
        </div>
        <div className="flex items-center gap-1.5">
          <div className="w-2.5 h-2.5 rounded-full bg-emerald-500 shadow-sm" />
          <span className="text-[10px] font-semibold">Verified Proof</span>
        </div>
        <div className="flex items-center gap-1.5">
          <div className="w-2.5 h-2.5 rounded-full bg-rose-500 animate-pulse" />
          <span className="text-[10px] font-semibold">ValidationError</span>
        </div>
      </div>

      {/* Interactive Floating Minimap Navigation Overview Panel */}
      <AnimatePresence>
        {viewSettings.showMinimap && (
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: -10 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: -10 }}
            transition={{ duration: 0.18, ease: "easeOut" }}
            className={`absolute top-4 right-4 rounded-xl border overflow-hidden shadow-2xl backdrop-blur-md z-30 transition-shadow duration-300 ${
              viewSettings.theme === "steel-dark"
                ? "bg-slate-900/90 border-slate-800 shadow-indigo-950/25"
                : "bg-white/95 border-slate-200/90 shadow-slate-200/40"
            }`}
          >
            {/* Tiny Header bar */}
            <div className={`px-2.5 py-1.5 border-b flex items-center justify-between text-[9px] font-bold tracking-wider uppercase select-none ${
              viewSettings.theme === "steel-dark"
                ? "border-slate-800 text-slate-400 bg-slate-950/40"
                : "border-slate-100 text-slate-500 bg-slate-50/50"
            }`}>
              <div className="flex items-center gap-1">
                <MapIcon size={10} className="text-indigo-500" />
                <span>Navigation Overview</span>
              </div>
              <span className="font-mono text-[8px] opacity-75">
                {Math.round(zoom * 100)}%
              </span>
            </div>

            {/* Click/drag interactive minimap arena */}
            <div
              className="relative cursor-crosshair overflow-hidden"
              style={{ width: minimapWidth, height: minimapHeight }}
              onPointerDown={handleMinimapPointerDown}
              onPointerMove={handleMinimapPointerMove}
              onPointerUp={handleMinimapPointerUp}
            >
              {/* Subtle background grid pattern */}
              <div
                className="absolute inset-0 pointer-events-none opacity-[0.12]"
                style={{
                  backgroundImage: `radial-gradient(${
                    viewSettings.theme === "steel-dark" ? "#ffffff" : "#000000"
                  } 1px, transparent 1px)`,
                  backgroundSize: "12px 12px",
                }}
              />

              <svg width="100%" height="100%" className="absolute inset-0 pointer-events-none">
                {/* SVG Connections/Edges - skip if extremely dense to avoid spaghetti and keep fast */}
                {visibleEdges.length <= 400 && visibleEdges.map((edge, idx) => {
                  const p1 = positions[edge.from];
                  const p2 = positions[edge.to];
                  if (!p1 || !p2) return null;
                  const pt1 = getMiniCoords(p1.x, p1.y);
                  const pt2 = getMiniCoords(p2.x, p2.y);
                  return (
                    <line
                      key={`mini-edge-${idx}`}
                      x1={pt1.x}
                      y1={pt1.y}
                      x2={pt2.x}
                      y2={pt2.y}
                      stroke={viewSettings.theme === "steel-dark" ? "rgba(100, 116, 139, 0.3)" : "rgba(148, 163, 184, 0.45)"}
                      strokeWidth={1}
                    />
                  );
                })}

                {/* SVG Active Dots */}
                {visibleNodes.map((n) => {
                  const pos = positions[n.id];
                  if (!pos) return null;
                  const mapped = getMiniCoords(pos.x, pos.y);

                  const isSelected = selectedNodeId === n.id;
                  const isFocused = focusNodeId === n.id;
                  const dotColor = getFamilySvgColor(n.family);

                  return (
                    <g key={`mini-node-${n.id}`}>
                      {(isSelected || isFocused) && (
                        <circle
                          cx={mapped.x}
                          cy={mapped.y}
                          r={isSelected ? 5.5 : 4.5}
                          fill="none"
                          stroke={isSelected ? "#6366f1" : "#14b8a6"}
                          strokeWidth={1.5}
                        />
                      )}
                      <circle
                        cx={mapped.x}
                        cy={mapped.y}
                        r={isSelected ? 3.2 : isFocused ? 2.5 : 2}
                        fill={dotColor}
                        opacity={isSelected || isFocused ? 1 : 0.8}
                      />
                    </g>
                  );
                })}
              </svg>

              {/* Viewport tracking frame rectangle indicator */}
              <div
                className="absolute border border-indigo-500 bg-indigo-500/10 pointer-events-none transition-all duration-75"
                style={{
                  left: viewX,
                  top: viewY,
                  width: viewW,
                  height: viewH,
                  boxShadow: "0 0 8px rgba(99, 102, 241, 0.25)",
                }}
              />
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};
