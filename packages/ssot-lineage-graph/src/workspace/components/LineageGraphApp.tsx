/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState, useEffect, useRef, useMemo } from "react";
import { LineagePayload, LineageNode, LineageEdge, GraphViewMode, GraphFilters, ViewSettings, LineageFamily, OriginKind, Position, NodePositions } from "../types";
import { LeftSidebar } from "./LeftSidebar";
import { LineageGraphCanvas } from "./LineageGraphCanvas";
import { RightInspector } from "./RightInspector";
import { computeDeterministicLayout, computeGraphIndices, hasCollapsedUpstreamAncestor, runForceSimulationStep } from "../utils/graphHelpers";
import { Shield, Settings, Sliders, FileDown, BookOpen, Layers, Network, Zap, Eye, CheckCircle, EyeOff, X, Map as MapIcon } from "lucide-react";
import { StorybookDocs } from "./StorybookDocs";

interface LineageGraphAppProps {
  payload: LineagePayload;
  selectedRegistryKey?: string;
  onChangeRegistry?: (key: string) => void;
  registryOptions?: Array<{ key: string; label: string }>;
  defaultMode?: GraphViewMode;
  theme?: ViewSettings["theme"];
  showDocumentation?: boolean;
  precomputedIndices?: {
    nodeMap: Map<string, LineageNode>;
    incoming: Map<string, string[]>;
    outgoing: Map<string, string[]>;
    edgeMap: Map<string, LineageEdge[]>;
  };
}

export const LineageGraphApp: React.FC<LineageGraphAppProps> = ({
  payload,
  selectedRegistryKey = payload.package?.id || payload.package?.name || "current",
  onChangeRegistry = () => undefined,
  registryOptions = [],
  defaultMode = "lineage",
  theme = "light",
  showDocumentation = false,
  precomputedIndices,
}) => {
  const [activeWorkspaceTab, setActiveWorkspaceTab] = useState<"workspace" | "storybook">("workspace");

  // Selection states
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);
  const [selectedNodeIds, setSelectedNodeIds] = useState<Set<string>>(new Set());
  const [highlightedNodeIds, setHighlightedNodeIds] = useState<Set<string>>(new Set());
  const [customGroups, setCustomGroups] = useState<{ id: string; label: string; nodeIds: string[] }[]>([]);
  const [nodeLimit, setNodeLimit] = useState<number>(300);
  const [egoHops, setEgoHops] = useState<number>(1);
  const [isolateEgo, setIsolateEgo] = useState<boolean>(false);

  const [focusNodeId, setFocusNodeId] = useState<string | null>(null);
  const [focusHistory, setFocusHistory] = useState<string[]>([]);
  const [collapsedNodeIds, setCollapsedNodeIds] = useState<Set<string>>(new Set());
  const [hiddenNodeIds, setHiddenNodeIds] = useState<Set<string>>(new Set());

  // View modes "network" | "lineage" | "proof" | "release" | "origins" | "packs" | "validation"
  const [viewMode, setViewMode] = useState<GraphViewMode>(defaultMode);

  // View options customization
  const [viewSettings, setViewSettings] = useState<ViewSettings>({
    showLabels: true,
    edgeWidth: 2,
    edgeOpacity: 0.6,
    showMinimap: false,
    theme,
  });

  // Collapsible Sidebars state
  const [isLeftCollapsed, setIsLeftCollapsed] = useState(false);
  const [isRightCollapsed, setIsRightCollapsed] = useState(false);

  const initialFamilies = useMemo<LineageFamily[]>(
    () =>
      Array.from(
        new Set<LineageFamily>([
          "ADR",
          "Spec",
          "SPEC",
          "Feature",
          "Claim",
          "Test",
          "Evidence",
          "Release",
          "Boundary",
          "Profile",
          "Risk",
          "Issue",
          ...payload.nodes.map((node) => node.family),
        ]),
      ),
    [payload.nodes],
  );
  const initialOriginKinds = useMemo<OriginKind[]>(
    () =>
      Array.from(
        new Set<OriginKind>([
          "ssot-core",
          "ssot-origin",
          "repo-local",
          "extension-pack",
          "generated",
          "unknown",
          ...payload.nodes.map((node) => node.originKind).filter((kind): kind is OriginKind => Boolean(kind)),
        ]),
      ),
    [payload.nodes],
  );

  // Composeable Filter checkboxes states
  const [filters, setFilters] = useState<GraphFilters>({
    search: "",
    families: new Set<LineageFamily>(initialFamilies),
    statuses: new Set<string>(),
    originKinds: new Set<OriginKind>(initialOriginKinds),
    tiers: new Set<string>(),
    packs: new Set<string>(),
    validationStatuses: new Set<string>(),
    edgeTypes: new Set<string>(),
  });

  // Coordinates node positions state driven by layout math or physics simulation
  const [positions, setPositions] = useState<NodePositions>({});

  // Real-time animation paint tickers
  const animationFrameRef = useRef<number | null>(null);
  const canvasWidth = 1100;
  const canvasHeight = 620;

  // Print console logs as proof of events
  useEffect(() => {
    console.log("[LineageGraphApp] Ready! Graph initialized successfully");
  }, []);

  useEffect(() => {
    console.log(`[LineageGraphApp] View Mode changed to: ${viewMode.toUpperCase()}`);
  }, [viewMode]);

  useEffect(() => {
    if (selectedNodeId) {
      console.log(`[LineageGraphApp] Node Selected: ${selectedNodeId}`);
      setIsRightCollapsed(false);
    } else {
      console.log("[LineageGraphApp] Node Selection Cleared");
      setIsRightCollapsed(true);
    }
  }, [selectedNodeId]);

  useEffect(() => {
    if (focusNodeId) {
      console.log(`[LineageGraphApp] Viewport camera locked onto focus node: ${focusNodeId}`);
    }
  }, [focusNodeId]);

  useEffect(() => {
    if (!showDocumentation && activeWorkspaceTab === "storybook") {
      setActiveWorkspaceTab("workspace");
    }
  }, [activeWorkspaceTab, showDocumentation]);

  useEffect(() => {
    setFilters((previous) => ({
      ...previous,
      families: new Set<LineageFamily>([...initialFamilies, ...previous.families]),
      originKinds: new Set<OriginKind>([...initialOriginKinds, ...previous.originKinds]),
    }));
  }, [initialFamilies, initialOriginKinds]);

  const indices = useMemo(() => {
    if (precomputedIndices) return precomputedIndices;
    return computeGraphIndices(payload);
  }, [payload, precomputedIndices]);

  const selectedNode = useMemo(() => {
    if (!selectedNodeId) return null;
    return payload.nodes.find((n) => n.id === selectedNodeId) || null;
  }, [selectedNodeId, payload.nodes]);

  // Aggregate all unique packs and tiers inside payload
  const { allPacks, allTiers, allOriginKinds } = useMemo(() => {
    const packsSet = new Set<string>();
    const tiersSet = new Set<string>();
    const kindsSet = new Set<OriginKind>();

    const isLarge = payload.nodes.length > 5000;
    payload.nodes.forEach((node, idx) => {
      if (isLarge && idx % 10 !== 0) return;
      if (node.packs) node.packs.forEach((p) => packsSet.add(p));
      if (node.tier) tiersSet.add(node.tier);
      if (node.originKind) kindsSet.add(node.originKind);
    });

    return {
      allPacks: Array.from(packsSet).sort(),
      allTiers: Array.from(tiersSet).sort(),
      allOriginKinds: Array.from(kindsSet).sort(),
    };
  }, [payload.nodes]);

  // Handle recursive collapse toggles
  const handleToggleCollapse = (nodeId: string) => {
    setCollapsedNodeIds((prev) => {
      const next = new Set<string>(prev);
      if (next.has(nodeId)) {
        next.delete(nodeId);
      } else {
        next.add(nodeId);
      }
      return next;
    });
  };

  // Composeable layout and search query evaluators
  const filteredNodes = useMemo(() => {
    return payload.nodes.filter((node) => {
      // 1. Search text filter matches
      if (filters.search) {
        const query = filters.search.toLowerCase();
        const matchesId = node.id.toLowerCase().includes(query);
        const matchesLabel = (node.label || "").toLowerCase().includes(query);
        const matchesTitle = (node.title || "").toLowerCase().includes(query);
        const matchesDesc = (node.description || "").toLowerCase().includes(query);
        const matchesPath = (node.path || "").toLowerCase().includes(query);
        const matchesTags = (node.tags || []).some((t) => t.toLowerCase().includes(query));

        if (!matchesId && !matchesLabel && !matchesTitle && !matchesDesc && !matchesPath && !matchesTags) {
          return false;
        }
      }

      // 2. Family level filters
      if (!filters.families.has(node.family)) return false;

      // 3. Status level filters
      if (filters.statuses.size > 0 && node.status && !filters.statuses.has(node.status)) {
        return false;
      }

      // 4. Origin level kinds taxonomy
      if (node.originKind && !filters.originKinds.has(node.originKind)) return false;

      // 5. Tier levels compliance
      if (filters.tiers.size > 0 && node.tier && !filters.tiers.has(node.tier)) {
        return false;
      }

      // 6. Packs filter
      if (filters.packs && filters.packs.size > 0) {
        if (!node.packs || !node.packs.some((p) => filters.packs.has(p))) {
          return false;
        }
      }

      // 7. Validation statuses filter
      if (filters.validationStatuses && filters.validationStatuses.size > 0) {
        const vStatus = node.validation?.status || "unknown";
        if (!filters.validationStatuses.has(vStatus)) {
          return false;
        }
      }

      return true;
    });
  }, [payload.nodes, filters]);

  // Compute active nodes being displayed on the canvas, honoring the nodeLimit
  const displayNodes = useMemo(() => {
    if (nodeLimit && filteredNodes.length > nodeLimit) {
      return filteredNodes.slice(0, nodeLimit);
    }
    return filteredNodes;
  }, [filteredNodes, nodeLimit]);

  const displayPayload = useMemo(() => {
    return {
      ...payload,
      nodes: displayNodes,
    };
  }, [payload, displayNodes]);

  // Handle multi-selection state with shift key support
  const handleSelectNode = (id: string | null, isShiftPressed?: boolean) => {
    if (!id) {
      setSelectedNodeId(null);
      setSelectedNodeIds(new Set());
      return;
    }

    if (isShiftPressed) {
      setSelectedNodeIds((prev) => {
        const next = new Set(prev);
        if (next.has(id)) {
          next.delete(id);
          if (selectedNodeId === id) {
            setSelectedNodeId(next.size > 0 ? Array.from(next)[next.size - 1] : null);
          }
        } else {
          next.add(id);
          setSelectedNodeId(id);
        }
        return next;
      });
    } else {
      setSelectedNodeId(id);
      setSelectedNodeIds(new Set([id]));
    }
  };

  // Focus navigation trail triggers
  const handleSetFocusNode = (id: string | null) => {
    setFocusNodeId(id);
    if (id) {
      setFocusHistory((prev) => [...prev, id]);
    }
  };

  const handleClearFocusNode = () => {
    setFocusNodeId(null);
  };

  const handleToggleHideNode = (nodeId: string) => {
    setHiddenNodeIds((prev) => {
      const next = new Set(prev);
      if (next.has(nodeId)) {
        next.delete(nodeId);
      } else {
        next.add(nodeId);
        if (selectedNodeId === nodeId) {
          setSelectedNodeId(null);
        }
        if (focusNodeId === nodeId) {
          setFocusNodeId(null);
        }
      }
      return next;
    });
  };

  const handleClearHiddenNodes = () => {
    setHiddenNodeIds(new Set());
  };

  // Find nodes visible in the hierarchy (not collapsed or user hidden)
  const visibleUnderTree = useMemo(() => {
    const isLarge = payload.nodes.length > 5000;
    const rawFiltered = isLarge
      ? displayNodes.filter((node, idx) => {
          if (hiddenNodeIds.has(node.id)) return false;
          // Check if parent path collapsed
          if (hasCollapsedUpstreamAncestor(node.id, indices.incoming, collapsedNodeIds)) return false;
          const match = node.id.match(/-(\d+)$/);
          const megaIdx = match ? parseInt(match[1], 10) : -1;
          if (megaIdx !== -1) {
            return megaIdx <= 150 || megaIdx % 500 === 0;
          }
          return idx % 50 === 0;
        })
      : displayNodes.filter(node => {
          if (hiddenNodeIds.has(node.id)) return false;
          return !hasCollapsedUpstreamAncestor(node.id, indices.incoming, collapsedNodeIds);
        });
    return new Set(rawFiltered.map(n => n.id));
  }, [displayNodes, hiddenNodeIds, collapsedNodeIds, indices]);

  // Compute the ego neighborhood in the App context to align deterministic packings
  const appEgoNeighborhood = useMemo(() => {
    const activeFocusNodeId = focusNodeId || selectedNodeId;
    if (!isolateEgo || !activeFocusNodeId) return null;
    const connected = new Set<string>([activeFocusNodeId]);

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

            if (visibleUnderTree.has(neighbor)) {
              if (!connected.has(neighbor)) {
                connected.add(neighbor);
                nextLevel.add(neighbor);
              }
            } else {
              // It's a hidden/filtered/collapsed node, bridge through it up to depth 3
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
  }, [isolateEgo, focusNodeId, selectedNodeId, egoHops, visibleUnderTree, indices]);

  // Recalculate static deterministic layout positions upon filter/mode/active focus changes
  useEffect(() => {
    if (viewMode !== "network" && viewMode !== "flow-force") {
      // Stop physics integration loop immediately
      if (animationFrameRef.current !== null) {
        cancelAnimationFrame(animationFrameRef.current);
        animationFrameRef.current = null;
      }

      // If isolateEgo is active, we hide all other nodes so deterministic layout packs focus nodes tightly
      const layoutHiddenNodeIds = new Set<string>(hiddenNodeIds);
      if (isolateEgo && appEgoNeighborhood) {
        payload.nodes.forEach(n => {
          if (!appEgoNeighborhood.has(n.id)) {
            layoutHiddenNodeIds.add(n.id);
          }
        });
      }

      const nextPositions = computeDeterministicLayout(
        payload.nodes,
        indices.incoming,
        indices.outgoing,
        collapsedNodeIds,
        210, // scaleX horizontal column gap width
        90,  // scaleY row margins gap heights
        canvasWidth,
        canvasHeight,
        viewMode,
        layoutHiddenNodeIds
      );
      setPositions(nextPositions);
    } else {
      // Initialize physics coordinates loop
      const layoutHiddenNodeIds = new Set<string>(hiddenNodeIds);
      if (isolateEgo && appEgoNeighborhood) {
        payload.nodes.forEach(n => {
          if (!appEgoNeighborhood.has(n.id)) {
            layoutHiddenNodeIds.add(n.id);
          }
        });
      }

      const initialPositions = computeDeterministicLayout(
        payload.nodes,
        indices.incoming,
        indices.outgoing,
        collapsedNodeIds,
        210,
        90,
        canvasWidth,
        canvasHeight,
        viewMode,
        layoutHiddenNodeIds
      );
      setPositions(initialPositions);
    }
  }, [
    viewMode,
    payload,
    collapsedNodeIds,
    hiddenNodeIds,
    isolateEgo,
    appEgoNeighborhood,
    indices
  ]);

  // Spring force simulator loop ticker for "Network mode" or "Flow Force" mode
  useEffect(() => {
    if (viewMode === "network" || viewMode === "flow-force") {
      // If dataset is extremely large (MegaScale), bypass the live simulation loop entirely.
      // This keeps the user interface responsive and buttery smooth with static layouts, eliminating intermittent freezing.
      if (payload.nodes.length > 1500) {
        return;
      }

      const disabledIds = new Set<string>();
      payload.nodes.forEach(n => {
        // User-individually hidden nodes
        if (hiddenNodeIds.has(n.id)) {
          disabledIds.add(n.id);
          return;
        }

        // Exclude nodes that are not in the active ego neighborhood when focused isolation is enabled
        if (isolateEgo && appEgoNeighborhood && !appEgoNeighborhood.has(n.id)) {
          disabledIds.add(n.id);
          return;
        }

        // Hide elements that are collapsed inside tree views
        if (hasCollapsedUpstreamAncestor(n.id, indices.incoming, collapsedNodeIds)) {
          disabledIds.add(n.id);
        }
      });

      const tick = () => {
        setPositions((prev) => {
          const isFlowForce = viewMode === "flow-force";
          return runForceSimulationStep(
            payload.nodes,
            payload.edges,
            prev,
            disabledIds,
            canvasWidth,
            canvasHeight,
            isFlowForce ? 0.015 : 0.012, // centerGravity
            isFlowForce ? 12000 : 25000, // repulsionConstant (slightly lower repulsion to let columns stay tighter)
            isFlowForce ? 0.08 : 0.03,   // springConstant (enhanced connection stiffness for dominant linking)
            isFlowForce ? 130 : 220,     // restLength (crisper resting connection distance)
            viewMode       // Pass viewMode (handles "flow-force" column pulling!)
          );
        });
        animationFrameRef.current = requestAnimationFrame(tick);
      };
      animationFrameRef.current = requestAnimationFrame(tick);

      return () => {
        if (animationFrameRef.current !== null) {
          cancelAnimationFrame(animationFrameRef.current);
          animationFrameRef.current = null;
        }
      };
    }
  }, [viewMode, payload, collapsedNodeIds, hiddenNodeIds, isolateEgo, appEgoNeighborhood, indices]);

  // The package build owns standalone HTML generation; the in-app export keeps
  // to portable payload data so it never depends on CDN scripts or fonts.
  const handleDownloadPayloadJson = () => {
    const stringifiedPayload = JSON.stringify(payload, null, 2);

    const blob = new Blob([stringifiedPayload], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `${payload.package?.id?.replace(/[\\/]/g, "_") || "registry"}_lineage_payload.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  return (
    <div id="graph-application-shell" className="h-full w-full flex flex-col bg-slate-50 select-none overflow-hidden font-sans">
      {/* Upper Navigation Workspace Header */}
      <header className="h-14 border-b border-slate-200 bg-white flex items-center justify-between px-6 shrink-0 shadow-sm z-30">
        {/* Logo and registry information */}
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center text-white font-bold shadow-md shadow-indigo-100 shrink-0">
            <Zap size={16} className="animate-pulse" />
          </div>
          <div>
            <div className="flex items-center gap-1.5">
              <h1 className="text-xs font-black text-slate-800 tracking-tight">SSOT Lineage</h1>
              <span className="bg-slate-100 text-slate-500 text-[8px] font-extrabold px-1 py-0.2 rounded font-mono uppercase">
                Interactive Viewer
              </span>
            </div>
            <p className="text-[10px] text-slate-400 font-medium truncate max-w-[180px] sm:max-w-none">
              {payload.package?.name || "SSOT-Registry"} - v{payload.package?.version || "0.0.1"}
            </p>
          </div>
        </div>

        {/* Storybook / Workspace Tab toggler switches */}
        {showDocumentation && (
          <div className="flex bg-slate-100 p-1 rounded-md border border-slate-200/50 text-xs font-medium">
            <button
              onClick={() => setActiveWorkspaceTab("workspace")}
              className={`flex items-center gap-1.5 px-3 py-1 rounded transition select-none ${
                activeWorkspaceTab === "workspace"
                  ? "bg-white text-slate-800 font-bold shadow-sm"
                  : "text-slate-500 hover:text-slate-800"
              }`}
            >
              <Layers size={13} />
              <span>Interactive Graph</span>
            </button>
            <button
              onClick={() => setActiveWorkspaceTab("storybook")}
              className={`flex items-center gap-1.5 px-3 py-1 rounded transition select-none ${
                activeWorkspaceTab === "storybook"
                  ? "bg-white text-slate-800 font-bold shadow-sm"
                  : "text-slate-500 hover:text-slate-800"
              }`}
            >
              <BookOpen size={13} />
              <span>Storybook Docs</span>
            </button>
          </div>
        )}

        {/* Upper Export toolbar button */}
        <div className="flex items-center gap-2">
          {/* Active Connection Labels Toggle */}
          <button
            onClick={() =>
              setViewSettings((prev) => ({
                ...prev,
                showLabels: !prev.showLabels,
              }))
            }
            className={`p-2 border rounded-lg transition flex items-center gap-1.5 text-xs font-semibold select-none ${
              viewSettings.showLabels
                ? "bg-indigo-50 border-indigo-200 text-indigo-700 hover:bg-indigo-100"
                : "border-slate-200 text-slate-500 hover:text-slate-800 hover:bg-slate-50"
            }`}
            title="Toggle displaying descriptive connection labels directly on graph edges (show/hide)"
          >
            <Sliders size={14} className={viewSettings.showLabels ? "text-indigo-600 stroke-[2.5]" : ""} />
            <span className="hidden md:inline">Connection Labels</span>
            <span className={`w-1.5 h-1.5 rounded-full ${viewSettings.showLabels ? "bg-indigo-600 animate-pulse" : "bg-slate-300"}`} />
          </button>

          {/* Interactive Minimap UI Toggler */}
          <button
            onClick={() =>
              setViewSettings((prev) => ({
                ...prev,
                showMinimap: !prev.showMinimap,
              }))
            }
            className={`p-2 border rounded-lg transition flex items-center gap-1.5 text-xs font-semibold select-none ${
              viewSettings.showMinimap
                ? "bg-indigo-50 border-indigo-200 text-indigo-700 hover:bg-indigo-100"
                : "border-slate-200 text-slate-500 hover:text-slate-800 hover:bg-slate-50"
            }`}
            title="Toggle Minimap navigation overview (show/hide)"
          >
            <MapIcon size={14} className={viewSettings.showMinimap ? "stroke-[2.5]" : ""} />
            <span className="hidden md:inline">Minimap</span>
            <span className={`w-1.5 h-1.5 rounded-full ${viewSettings.showMinimap ? "bg-indigo-600" : "bg-slate-300"}`} />
          </button>

          {/* Quick theme toggler */}
          <button
            onClick={() =>
              setViewSettings((prev) => ({
                ...prev,
                theme: prev.theme === "light" ? "steel-dark" : "light",
              }))
            }
            className="p-2 border border-slate-200 text-slate-500 hover:text-slate-800 hover:bg-slate-50 rounded-lg transition"
            title="Toggle canvas color scheme"
          >
            <Settings size={14} />
          </button>

          {/* Portable compilation build trigger */}
          <button
            onClick={handleDownloadPayloadJson}
            className="flex items-center gap-1.5 px-3 py-1.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-xs font-extrabold transition shadow-lg shadow-indigo-100 hover:shadow-indigo-200"
            title="Download the current lineage payload JSON"
          >
            <FileDown size={13} />
            <span className="hidden sm:inline">Export Payload JSON</span>
          </button>
        </div>
      </header>

      {/* Main viewport frame switcher panel */}
      {showDocumentation && activeWorkspaceTab === "storybook" ? (
        <StorybookDocs />
      ) : (
        <div className="flex-1 flex overflow-hidden">
          {/* Left search/filter Sidebar component */}
          <LeftSidebar
            payload={payload}
            filters={filters}
            onUpdateFilters={setFilters}
            viewMode={viewMode}
            onChangeViewMode={setViewMode}
            selectedRegistryKey={selectedRegistryKey}
            onChangeRegistry={onChangeRegistry}
            registryOptions={registryOptions}
            allPacks={allPacks}
            allTiers={allTiers}
            allOriginKinds={allOriginKinds}
            filteredNodes={filteredNodes}
            isCollapsed={isLeftCollapsed}
            onToggleCollapse={() => setIsLeftCollapsed(!isLeftCollapsed)}
            onSelectNode={handleSelectNode}
            onFocusNode={handleSetFocusNode}
            nodeLimit={nodeLimit}
            onUpdateNodeLimit={setNodeLimit}
            egoHops={egoHops}
            onUpdateEgoHops={setEgoHops}
            isolateEgo={isolateEgo}
            onUpdateIsolateEgo={setIsolateEgo}
          />

          {/* Central main stage layout: Canvas on top, custom specs + events log panel on bottom */}
          <div className="flex-1 h-full flex flex-col overflow-hidden bg-slate-100">
            {/* Top portion: Visual lineage canvas */}
            <div className="flex-1 relative overflow-hidden">
              <LineageGraphCanvas
                payload={displayPayload}
                positions={positions}
                mode={viewMode}
                selectedNodeId={selectedNodeId}
                selectedNodeIds={selectedNodeIds}
                focusNodeId={focusNodeId}
                collapsedNodeIds={collapsedNodeIds}
                hiddenNodeIds={hiddenNodeIds}
                onSelectNode={handleSelectNode}
                onToggleCollapse={handleToggleCollapse}
                onToggleHideNode={handleToggleHideNode}
                onClearHiddenNodes={handleClearHiddenNodes}
                onUpdatePositions={setPositions}
                viewSettings={viewSettings}
                precomputedIndices={precomputedIndices}
                egoHops={egoHops}
                highlightedNodeIds={highlightedNodeIds}
                customGroups={customGroups}
                isolateEgo={isolateEgo}
              />

              {/* Multi-Select Floating Actions Overlay Panel */}
              {selectedNodeIds.size > 1 && (
                <div
                  id="multi-select-actions-bar"
                  className="absolute bottom-6 left-1/2 -translate-x-1/2 bg-slate-900/95 backdrop-blur border border-slate-800 text-white px-5 py-3 rounded-full flex items-center gap-4 shadow-2xl z-50 transition-all duration-300"
                >
                  <div className="flex items-center gap-2 pr-3 border-r border-slate-800">
                    <span className="w-2.5 h-2.5 rounded-full bg-indigo-500 animate-pulse" />
                    <span className="text-xs font-mono font-bold text-slate-300">
                      {selectedNodeIds.size} NODES SELECTED
                    </span>
                  </div>

                  <button
                    onClick={() => {
                      setHighlightedNodeIds(new Set(selectedNodeIds));
                      console.log("[LineageGraphApp] Highlighted nodes:", Array.from(selectedNodeIds));
                    }}
                    className="px-3.5 py-1.5 bg-amber-500 hover:bg-amber-600 text-slate-950 rounded-full font-bold text-xs flex items-center gap-1.5 transition-all active:scale-95 cursor-pointer"
                    title="Highlight all multi-selected nodes"
                  >
                    <Zap size={13} />
                    <span>Highlight</span>
                  </button>

                  <button
                    onClick={() => {
                      const label = prompt("Enter a label/contract zone name for this node group:", `Module Spec Group ${customGroups.length + 1}`) || `Group ${customGroups.length + 1}`;
                      const newGrp = {
                        id: `group-custom-${Date.now()}`,
                        label,
                        nodeIds: Array.from(selectedNodeIds),
                      };
                      setCustomGroups((prev) => [...prev, newGrp]);
                      setSelectedNodeIds(new Set());
                      setSelectedNodeId(null);
                      console.log("[LineageGraphApp] Created custom group:", newGrp);
                    }}
                    className="px-3.5 py-1.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-full font-bold text-xs flex items-center gap-1.5 transition-all active:scale-95 cursor-pointer"
                    title="Group selected nodes into a custom boundary zone"
                  >
                    <Layers size={13} />
                    <span>Group</span>
                  </button>

                  <button
                    onClick={() => {
                      setHiddenNodeIds((prev) => {
                        const next = new Set(prev);
                        selectedNodeIds.forEach(id => next.add(id));
                        return next;
                      });
                      setSelectedNodeIds(new Set());
                      setSelectedNodeId(null);
                      console.log("[LineageGraphApp] Bulk-hid nodes:", Array.from(selectedNodeIds));
                    }}
                    className="px-3.5 py-1.5 bg-rose-600 hover:bg-rose-700 text-white rounded-full font-bold text-xs flex items-center gap-1.5 transition-all active:scale-95 cursor-pointer"
                    title="Deselect and bulk-hide selected nodes from view"
                  >
                    <EyeOff size={13} className="text-rose-100" />
                    <span>Bulk-Hide</span>
                  </button>

                  {highlightedNodeIds.size > 0 && (
                    <button
                      onClick={() => {
                        setHighlightedNodeIds(new Set());
                      }}
                      className="px-3.5 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-full font-bold text-xs flex items-center gap-1.5 transition-all active:scale-95 cursor-pointer"
                      title="Clear all highlights"
                    >
                      <X size={13} />
                      <span>Clear Highlights</span>
                    </button>
                  )}

                  <button
                    onClick={() => {
                      setSelectedNodeIds(new Set());
                      setSelectedNodeId(null);
                    }}
                    className="text-slate-400 hover:text-white p-1 rounded-full hover:bg-slate-800 transition cursor-pointer"
                    title="Deselect all nodes"
                  >
                    <X size={15} />
                  </button>
                </div>
              )}
            </div>
          </div>

          {/* Right Structured details card inspector */}
          <RightInspector
            payload={payload}
            selectedNodeId={selectedNodeId}
            focusNodeId={focusNodeId}
            onSelectNode={setSelectedNodeId}
            onSetFocusNode={handleSetFocusNode}
            onClearFocusNode={handleClearFocusNode}
            isCollapsed={isRightCollapsed}
            onToggleCollapse={() => setIsRightCollapsed(!isRightCollapsed)}
          />
        </div>
      )}
    </div>
  );
};
export default LineageGraphApp;
