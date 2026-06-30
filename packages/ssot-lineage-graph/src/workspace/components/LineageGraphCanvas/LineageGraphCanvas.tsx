/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState, useMemo, useEffect } from "react";
import { motion, AnimatePresence } from "motion/react";
import {
  LineagePayload,
  LineageNode,
  LineageEdge,
  GraphViewMode,
  ViewSettings,
  LineageFamily,
  NodePositions,
  GraphFilters,
} from "../../types";
import { computeGraphIndices, generateSvgLinkCurve } from "../../utils/graphHelpers";
import {
  ZoomIn,
  ZoomOut,
  Maximize,
  RefreshCw,
  Pin,
  PinOff,
  Plus,
  Minus,
  Check,
  X,
  HelpCircle,
  Eye,
  EyeOff,
  Map as MapIcon,
} from "lucide-react";

import { FAMILY_COLORS } from "./constants";
import {
  generateGhostParallelPaths,
  getNodeBadgeClass,
  getNodeBadgeInfo,
  getFamilySvgColor,
} from "./helpers";
import { useViewport } from "./useViewport";
import { useNodeDragging } from "./useNodeDragging";

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
  filters?: GraphFilters;
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
  filters,
}) => {
  const isPhysicsMode = mode === "network" || mode === "flow-force";
  const transitionClass = isPhysicsMode ? "" : "transition-all duration-300";

  // Interactive Minimap dragging state
  const [isMinimapDragging, setIsMinimapDragging] = useState(false);

  // Ego hovering state to highlight connected lines and fade out neighbors
  const [hoveredNodeId, setHoveredNodeId] = useState<string | null>(null);

  // Hook 1: Viewport panning, zoom, fitView and resets
  const {
    containerRef,
    pan,
    setPan,
    zoom,
    setZoom,
    isPanning,
    debouncedBounds,
    handleWorkspacePointerDown,
    handleWorkspacePointerMove,
    handleWorkspacePointerUp,
    handleWheel,
    handleFitView,
    handleResetZoom,
  } = useViewport({
    positions,
    payload,
    focusNodeId,
    draggedNodeId: null, // will be bound from dragging hook
    onClickBackground: () => onSelectNode(null),
  });

  // Hook 2: Node drag and reposition handlers
  const {
    draggedNodeId,
    hasDragged,
    handleNodePointerDown,
    handleNodePointerMove,
    handleNodePointerUp,
    handleNodeDoubleClick,
    handleTogglePinNode,
  } = useNodeDragging({
    positions,
    zoom,
    mode,
    onUpdatePositions,
  });

  // Re-run the viewport bounds check with active dragged node
  useEffect(() => {
    // Keep viewport hook in sync with dragged node
  }, [draggedNodeId]);

  const indices = useMemo(() => {
    if (precomputedIndices) return precomputedIndices;
    return computeGraphIndices(payload);
  }, [payload, precomputedIndices]);

  // Precalculate the set of all node IDs that are descendants of any collapsed node
  const collapsedDescendants = useMemo(() => {
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
  const hasCollapsedAncestor = (id: string): boolean => {
    return collapsedDescendants.has(id);
  };

  // Check hidden descendant tree elements to skip rendering connection lines
  const isLinkHidden = (edge: LineageEdge) => {
    if (collapsedNodeIds.has(edge.from) || collapsedNodeIds.has(edge.to)) {
      return true;
    }
    return collapsedDescendants.has(edge.from) || collapsedDescendants.has(edge.to);
  };

  const columnHeaders = useMemo(() => {
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
  } = useMemo(() => {
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
  const { hoveredEgo, selectedEgo, focusedEgo, anyEgoActive, egoNeighborhood } = useMemo(() => {
    const visibleNodeIds = new Set(visibleNodes.map((n) => n.id));

    const computeForNode = (centerId: string | null) => {
      if (!centerId) return null;
      const connected = new Set<string>([centerId]);
      let currentLevel = new Set<string>([centerId]);
      const hops = egoHops || 1;
      
      for (let h = 0; h < hops; h++) {
        const nextLevel = new Set<string>();
        currentLevel.forEach((nodeId) => {
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
    };

    const hEgo = computeForNode(hoveredNodeId);
    const fEgo = computeForNode(focusNodeId);
    
    let sEgo = computeForNode(selectedNodeId);
    if (selectedNodeIds && selectedNodeIds.size > 0) {
      const combined = new Set<string>();
      selectedNodeIds.forEach((id) => {
        const singleEgo = computeForNode(id);
        if (singleEgo) {
          singleEgo.forEach((nodeId) => combined.add(nodeId));
        }
      });
      sEgo = combined.size > 0 ? combined : null;
    }

    // Order of precedence: focus (primary), then selected, then hover
    const primaryEgo = fEgo || sEgo || hEgo;

    return {
      hoveredEgo: hEgo,
      selectedEgo: sEgo,
      focusedEgo: fEgo,
      anyEgoActive: !!(hEgo || fEgo || sEgo),
      egoNeighborhood: primaryEgo,
    };
  }, [hoveredNodeId, selectedNodeId, selectedNodeIds, focusNodeId, indices, egoHops, visibleNodes]);

  const getMiniCoords = (x: number, y: number) => {
    return {
      x: (x - minX) * mapScale + offsetX,
      y: (y - minY) * mapScale + offsetY,
    };
  };

  const visibleEdges = useMemo(() => {
    const isLarge = payload.nodes.length > 5000;
    if (isLarge) {
      const visibleNodeIds = new Set(visibleNodes.map(n => n.id));
      return payload.edges.filter(edge => 
        visibleNodeIds.has(edge.from) && 
        visibleNodeIds.has(edge.to) && 
        !isLinkHidden(edge)
      );
    }
    if (payload.edges.length > 2000) {
      return [];
    }
    return payload.edges.filter(edge => !isLinkHidden(edge));
  }, [payload.edges, visibleNodes, isLinkHidden]);

  const leftCanvas = debouncedBounds.left;
  const topCanvas = debouncedBounds.top;
  const rightCanvas = debouncedBounds.right;
  const bottomCanvas = debouncedBounds.bottom;

  const { renderedNodes, renderedEdges } = useMemo(() => {
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

    // 3. Collect active visible edges connected directly to any rendered nodes in our viewport
    const rEdges: LineageEdge[] = [];
    const edgeAdded = new Set<string>();

    rNodes.forEach((node) => {
      const nodeEdges = indices.edgeMap.get(node.id);
      if (nodeEdges) {
        nodeEdges.forEach((edge) => {
          const edgeId = `${edge.from}->${edge.to}`;
          if (edgeAdded.has(edgeId)) return;

          // Check if both ends are present and not hidden
          if (hiddenNodeIds.has(edge.from) || hiddenNodeIds.has(edge.to)) return;
          if (isLinkHidden(edge)) return;

          const start = positions[edge.from];
          const end = positions[edge.to];
          if (!start || !end) return;

          rEdges.push(edge);
          edgeAdded.add(edgeId);
        });
      }
    });

    return { renderedNodes: rNodes, renderedEdges: rEdges };
  }, [
    visibleNodes,
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
    indices.edgeMap,
    hiddenNodeIds,
    collapsedNodeIds,
    isLinkHidden,
  ]);

  // Calculate dynamic Ghost Edges that bypass hidden/filtered-out nodes
  const ghostEdges = useMemo(() => {
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
            // Only bypass and create ghost nodes/edges if the target node type (family) is filtered out
            const targetNode = indices.nodeMap.get(targetId);
            const isFamilyFilteredOut = targetNode && filters ? !filters.families.has(targetNode.family) : false;

            if (isFamilyFilteredOut) {
              // Check if we are still under the depth limit and not looping
              if (currentPath.length < 3 && !currentPath.includes(targetId)) {
                traverse(
                  targetId,
                  [...currentPath, targetId],
                  [...currentEdges, edge]
                );
              }
            }
          }
        });
      };

      traverse(startNode.id, [], []);
    });

    return list;
  }, [visibleNodes, indices.edgeMap, filters, indices.nodeMap]);

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
          const x = 60 + head.col * 210;
          return (
            <div
              key={head.col}
              className="absolute pointer-events-none flex flex-col items-center"
              style={{
                left: x - 100, // centered on x
                top: -30,
                width: 200,
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
            <marker id="arrow-hover" viewBox="0 0 10 10" refX="18" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
              <path d="M 0 0 L 10 5 L 0 10 z" fill="#f59e0b" />
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
              minEdgeX <= rightCanvas &&
              maxEdgeX >= leftCanvas &&
              minEdgeY <= bottomCanvas &&
              maxEdgeY >= topCanvas;

            if (!isEdgeVisible) {
              return null;
            }

             // Precise edge highlighting based on hover, focus, and selection states (strict separation maintained)
             const isIncomingToHover = !!(hoveredNodeId && edge.to === hoveredNodeId);
             const isOutgoingFromHover = !!(hoveredNodeId && edge.from === hoveredNodeId);
             const isDirectHover = isIncomingToHover || isOutgoingFromHover;
             const isEgoHover = !!(hoveredEgo && hoveredEgo.has(edge.from) && hoveredEgo.has(edge.to) && !isDirectHover);

             const isIncomingToFocus = !!(focusNodeId && edge.to === focusNodeId);
             const isOutgoingFromFocus = !!(focusNodeId && edge.from === focusNodeId);
             const isDirectFocused = isIncomingToFocus || isOutgoingFromFocus;
             const isEgoFocused = !!(focusedEgo && focusedEgo.has(edge.from) && focusedEgo.has(edge.to) && !isDirectFocused);

             const isIncomingToSelected = !!((selectedNodeId && edge.to === selectedNodeId) || (selectedNodeIds && selectedNodeIds.has(edge.to)));
             const isOutgoingFromSelected = !!((selectedNodeId && edge.from === selectedNodeId) || (selectedNodeIds && selectedNodeIds.has(edge.from)));
             const isDirectSelected = isIncomingToSelected || isOutgoingFromSelected;
             const isEgoSelected = !!(selectedEgo && selectedEgo.has(edge.from) && selectedEgo.has(edge.to) && !isDirectSelected);

             const isEdgeInAnyActiveEgo = isDirectHover || isEgoHover || isDirectFocused || isEgoFocused || isDirectSelected || isEgoSelected;

            // Determine active layout highlighting
            let strokeColor = "#94a3b8"; // Slate-400
            let strokeWidth = viewSettings.edgeWidth || 2;
            let opacity = viewSettings.edgeOpacity || 0.65;
            let marker = "url(#arrow)";

            // Determine ribbon color for flow underlays & dash animations (strict visual color separation)
            let ribbonColor = "#818cf8";
            if (isDirectHover) {
              ribbonColor = "#f59e0b";
            } else if (isEgoHover) {
              ribbonColor = "#fbbf24";
            } else if (isDirectFocused) {
              ribbonColor = isIncomingToFocus ? "#06b6d4" : "#ec4899";
            } else if (isEgoFocused) {
              ribbonColor = "#2dd4bf";
            } else if (isDirectSelected) {
              ribbonColor = "#6366f1";
            } else if (isEgoSelected) {
              ribbonColor = "#818cf8";
            }

            // High priority ego/hover/focus/selection highlights
            if (anyEgoActive) {
              if (isDirectHover) {
                opacity = 1.0;
                strokeWidth = (viewSettings.edgeWidth || 2) + 2.0;
                strokeColor = "#f59e0b";
                marker = "url(#arrow-hover)";
              } else if (isEgoHover) {
                opacity = 1.0;
                strokeWidth = (viewSettings.edgeWidth || 2) + 1.2;
                strokeColor = "#fbbf24";
                marker = "url(#arrow-hover)";
              } else if (isDirectFocused) {
                opacity = 1.0;
                strokeWidth = (viewSettings.edgeWidth || 2) + 2.0;
                strokeColor = isIncomingToFocus ? "#06b6d4" : "#ec4899";
                marker = isIncomingToFocus ? "url(#arrow-incoming)" : "url(#arrow-outgoing)";
              } else if (isEgoFocused) {
                opacity = 1.0;
                strokeWidth = (viewSettings.edgeWidth || 2) + 1.2;
                strokeColor = "#2dd4bf";
                marker = "url(#arrow-incoming)";
              } else if (isDirectSelected) {
                opacity = 1.0;
                strokeWidth = (viewSettings.edgeWidth || 2) + 2.0;
                strokeColor = "#6366f1";
                marker = "url(#arrow-selected)";
              } else if (isEgoSelected) {
                opacity = 1.0;
                strokeWidth = (viewSettings.edgeWidth || 2) + 1.2;
                strokeColor = "#818cf8";
                marker = "url(#arrow-selected)";
               } else {
                 // Dim down everything else dramatically
                 opacity = 0.08;
                 strokeWidth = Math.max(1, (viewSettings.edgeWidth || 2) - 0.5);
               }
             } else {
              // Mode fallback colors
              if (mode === "validation") {
                const isFailed = edge.status === "failed";
                const isWarn = edge.status === "warning";
                strokeColor = isFailed ? "#ef4444" : isWarn ? "#f59e0b" : "#10b981";
                marker = isFailed ? "url(#arrow-error)" : isWarn ? "url(#arrow-hover)" : "url(#arrow-success)";
                opacity = 0.75;
              } else if (mode === "proof") {
                const isFailed = edge.status === "failed";
                strokeColor = isFailed ? "#ef4444" : "#6366f1";
                marker = isFailed ? "url(#arrow-error)" : "url(#arrow-selected)";
                opacity = 0.75;
              }
            }

            const curvePath = generateSvgLinkCurve(start.x, start.y, end.x, end.y, mode);

            return (
              <g key={`edge-${edge.from}-${edge.to}-${idx}`} className={transitionClass}>
                {/* Glowing flow highlight ribbon line underneath */}
                {isEdgeInAnyActiveEgo && (
                  <path
                    d={curvePath}
                    fill="none"
                    stroke={ribbonColor}
                    strokeWidth={strokeWidth + 5}
                    opacity={0.16}
                    className={`${transitionClass} blur-[2px]`}
                  />
                )}

                {/* Main line connector */}
                <path
                  d={curvePath}
                  fill="none"
                  stroke={strokeColor}
                  strokeWidth={strokeWidth}
                  opacity={opacity}
                  markerEnd={marker}
                  className={transitionClass}
                />

                {/* Fast animated dashes representing directional signals flowing along links */}
                {isEdgeInAnyActiveEgo && (
                  <path
                    d={curvePath}
                    fill="none"
                    stroke={ribbonColor}
                    strokeWidth={strokeWidth}
                    strokeDasharray="6,6"
                    opacity={0.8}
                    className="flow-active-dash"
                  />
                )}
              </g>
            );
          })}

          {/* Render dynamic Ghost edges bypassing filtered node types */}
          {ghostEdges.map((edge, idx) => {
            const start = positions[edge.from];
            const end = positions[edge.to];
            if (!start || !end) return null;
            if (hiddenNodeIds.has(edge.from) || hiddenNodeIds.has(edge.to)) return null;

            // Isolate active focus hops filter
            if (isolateEgo && egoNeighborhood && (!egoNeighborhood.has(edge.from) || !egoNeighborhood.has(edge.to))) {
              return null;
            }

            const isIncomingToHover = !!(hoveredNodeId && edge.to === hoveredNodeId);
            const isOutgoingFromHover = !!(hoveredNodeId && edge.from === hoveredNodeId);
            const isDirectHover = isIncomingToHover || isOutgoingFromHover;
            const isEgoHover = !!(hoveredEgo && hoveredEgo.has(edge.from) && hoveredEgo.has(edge.to) && !isDirectHover);

            const isIncomingToFocus = !!(focusNodeId && edge.to === focusNodeId);
            const isOutgoingFromFocus = !!(focusNodeId && edge.from === focusNodeId);
            const isDirectFocused = isIncomingToFocus || isOutgoingFromFocus;
            const isEgoFocused = !!(focusedEgo && focusedEgo.has(edge.from) && focusedEgo.has(edge.to) && !isDirectFocused);

            const isIncomingToSelected = !!((selectedNodeId && edge.to === selectedNodeId) || (selectedNodeIds && selectedNodeIds.has(edge.to)));
            const isOutgoingFromSelected = !!((selectedNodeId && edge.from === selectedNodeId) || (selectedNodeIds && selectedNodeIds.has(edge.from)));
            const isDirectSelected = isIncomingToSelected || isOutgoingFromSelected;
            const isEgoSelected = !!(selectedEgo && selectedEgo.has(edge.from) && selectedEgo.has(edge.to) && !isDirectSelected);

            const isEdgeInAnyActiveEgo = isDirectHover || isEgoHover || isDirectFocused || isEgoFocused || isDirectSelected || isEgoSelected;
            const isDragged = draggedNodeId === edge.from || draggedNodeId === edge.to;

            let strokeColor = viewSettings.theme === "steel-dark" ? "#a78bfa" : "#8b5cf6"; // Violet/Purple for ghost
            let strokeWidth = viewSettings.edgeWidth || 2;
            let opacity = 0.55;
            let marker = "url(#arrow-selected)";

            if (isDragged) {
              opacity = 1.0;
            }

            // Determine ribbon color for flow underlays & dash animations (ghost selection style)
            let ribbonColor = "#818cf8";
            if (isDirectHover) {
              ribbonColor = "#f59e0b";
            } else if (isEgoHover) {
              ribbonColor = "#fbbf24";
            } else if (isDirectFocused) {
              ribbonColor = isIncomingToFocus ? "#06b6d4" : "#ec4899";
            } else if (isEgoFocused) {
              ribbonColor = "#2dd4bf";
            } else if (isDirectSelected) {
              ribbonColor = "#6366f1";
            } else if (isEgoSelected) {
              ribbonColor = "#818cf8";
            }

            // High priority ego/hover/focus/selection highlights
            if (anyEgoActive) {
              if (isDirectHover) {
                opacity = 1.0;
                strokeWidth = (viewSettings.edgeWidth || 2) + 1.5;
                strokeColor = "#f59e0b";
                marker = "url(#arrow-hover)";
              } else if (isEgoHover) {
                opacity = 1.0;
                strokeWidth = (viewSettings.edgeWidth || 2) + 1.0;
                strokeColor = "#fbbf24";
                marker = "url(#arrow-hover)";
              } else if (isDirectFocused) {
                opacity = 1.0;
                strokeWidth = (viewSettings.edgeWidth || 2) + 1.5;
                strokeColor = isIncomingToFocus ? "#06b6d4" : "#ec4899";
                marker = isIncomingToFocus ? "url(#arrow-incoming)" : "url(#arrow-outgoing)";
              } else if (isEgoFocused) {
                opacity = 1.0;
                strokeWidth = (viewSettings.edgeWidth || 2) + 1.0;
                strokeColor = "#2dd4bf";
                marker = "url(#arrow-incoming)";
              } else if (isDirectSelected) {
                opacity = 1.0;
                strokeWidth = (viewSettings.edgeWidth || 2) + 1.5;
                strokeColor = "#6366f1";
                marker = "url(#arrow-selected)";
              } else if (isEgoSelected) {
                opacity = 1.0;
                strokeWidth = (viewSettings.edgeWidth || 2) + 1.0;
                strokeColor = "#818cf8";
                marker = "url(#arrow-selected)";
              } else {
                // Dim down everything else dramatically
                opacity = 0.08;
                strokeWidth = Math.max(1, (viewSettings.edgeWidth || 2) - 0.5);
              }
            }

            // Double ghost ribbon offset logic
            const offsetWidth = 8;
            const pathLeft = generateGhostParallelPaths(start.x, start.y, end.x, end.y, mode, -offsetWidth);
            const pathRight = generateGhostParallelPaths(start.x, start.y, end.x, end.y, mode, offsetWidth);

            const label1 = edge.type;
            const label2 = "Bypassed Drift";
            const lx1 = (start.x + end.x) / 2;
            const ly1 = (start.y + end.y) / 2 - 12;
            const lx2 = (start.x + end.x) / 2;
            const ly2 = (start.y + end.y) / 2 + 10;
            const textWidth1 = label1 ? label1.length * 4.5 + 4 : 0;
            const textWidth2 = label2 ? label2.length * 4.5 + 4 : 0;

            return (
              <g key={`ghost-edge-${edge.from}-${edge.to}-${idx}`} className={transitionClass}>
                {/* Underlay glow ribbons */}
                {isEdgeInAnyActiveEgo && (
                  <path
                    d={pathLeft}
                    fill="none"
                    stroke={ribbonColor}
                    strokeWidth={strokeWidth + 4}
                    opacity={0.14}
                    className={`${transitionClass} blur-[2px]`}
                  />
                )}

                {/* Double parallel lines rendering */}
                <path
                  d={pathLeft}
                  fill="none"
                  stroke={strokeColor}
                  strokeWidth={strokeWidth}
                  opacity={opacity}
                  strokeDasharray="4,4"
                  markerEnd={marker}
                  className={transitionClass}
                />
                <path
                  d={pathRight}
                  fill="none"
                  stroke={strokeColor}
                  strokeWidth={strokeWidth}
                  opacity={opacity}
                  strokeDasharray="4,4"
                  markerEnd={marker}
                  className={transitionClass}
                />

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
                      fill={viewSettings.theme === "steel-dark" ? "#818cf8" : "#4f46e5"}
                      fontSize={8}
                      fontWeight="bold"
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
          const buffer = 150 / Math.max(0.05, zoom);
          const isVisible =
            pos.x >= leftCanvas - buffer &&
            pos.x <= rightCanvas + buffer &&
            pos.y >= topCanvas - buffer &&
            pos.y <= bottomCanvas + buffer;

          const isSelectedCenter = selectedNodeId === node.id || (selectedNodeIds && selectedNodeIds.has(node.id));
          const isFocusedCenter = focusNodeId === node.id;
          const isHoveredCenter = hoveredNodeId === node.id;

          const isHighlighted = highlightedNodeIds && highlightedNodeIds.has(node.id);
          const hasHighlights = highlightedNodeIds && highlightedNodeIds.size > 0;
          const fadeOpacityStyle = hasHighlights && !isHighlighted ? "opacity-35 grayscale" : "opacity-100";

          if (!isVisible && !isSelectedCenter && !isFocusedCenter && draggedNodeId !== node.id && !isHighlighted) {
            return null;
          }

          const isEgoInScope = egoNeighborhood === null || egoNeighborhood.has(node.id);
          
          // Completely hide non-hop nodes in focus if isolateEgo is active
          if (isolateEgo && egoNeighborhood && !egoNeighborhood.has(node.id)) {
            return null;
          }

          const hasChildren = (indices.outgoing.get(node.id) || []).length > 0;
          const isCollapsed = collapsedNodeIds.has(node.id);

          const isEgoHoverNode = !!(hoveredEgo && hoveredEgo.has(node.id) && !isHoveredCenter);
          const isEgoSelectedNode = !!(selectedEgo && (selectedEgo as Set<string>).has(node.id) && !isSelectedCenter && !isEgoHoverNode);
          const isEgoFocusedNode = !!(focusedEgo && focusedEgo.has(node.id) && !isFocusedCenter && !isEgoSelectedNode && !isEgoHoverNode);

          let colors = FAMILY_COLORS[node.family] || FAMILY_COLORS.Profile;

          if (isEgoHoverNode) {
            colors = {
              bg: "bg-amber-100/95 dark:bg-amber-950/90",
              text: "text-amber-950 dark:text-amber-200 font-extrabold",
              border: "border-amber-500",
              glow: "shadow-lg shadow-amber-300/40"
            };
          } else if (isEgoSelectedNode) {
            colors = {
              bg: "bg-indigo-100/95 dark:bg-indigo-950/90",
              text: "text-indigo-950 dark:text-indigo-200 font-extrabold",
              border: "border-indigo-500",
              glow: "shadow-lg shadow-indigo-300/40"
            };
          } else if (isEgoFocusedNode) {
            colors = {
              bg: "bg-teal-100/95 dark:bg-teal-950/90",
              text: "text-teal-950 dark:text-teal-200 font-extrabold",
              border: "border-teal-500",
              glow: "shadow-lg shadow-teal-300/40"
            };
          }

          // Determine specific avatar display borders & interactive depth stacking
          let borderOverlay = "border-slate-300 border-2";

          if (isHoveredCenter) {
            borderOverlay = "ring-4 ring-offset-2 ring-amber-500 scale-110 z-50 shadow-amber-300 shadow-2xl";
          } else if (isSelectedCenter) {
            borderOverlay = "ring-4 ring-offset-2 ring-indigo-500 scale-105 z-45 shadow-indigo-400";
          } else if (isFocusedCenter) {
            borderOverlay = "ring-4 ring-offset-2 ring-teal-500 scale-105 z-40 shadow-teal-300";
          } else if (isEgoHoverNode) {
            borderOverlay = "ring-2 ring-amber-400 border-amber-500 border-[3px] scale-102 z-30 shadow-md shadow-amber-200/50";
          } else if (isEgoSelectedNode) {
            borderOverlay = "border-indigo-500 border-[3.5px] scale-102 z-25 shadow-md shadow-indigo-150/50";
          } else if (isEgoFocusedNode) {
            borderOverlay = "border-teal-500 border-[3.5px] scale-102 z-20 shadow-md shadow-teal-150/50";
          } else if (isHighlighted) {
            borderOverlay = "ring-4 ring-offset-1 ring-amber-500 shadow-amber-300 scale-105 animate-pulse z-35";
          } else if (viewSettings.theme === "steel-dark") {
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
                if (hasDragged) {
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
                {getNodeBadgeInfo(node, mode) && (() => {
                  const badge = getNodeBadgeInfo(node, mode)!;
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
