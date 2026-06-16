import React, { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { familyColor } from "../constants";
import { applyForceLayoutStep, applyLineageLayout, normalizeNodes, resolveDepth } from "../layout";
import type { DepthSetting, LayoutMode, LineageEdge, LineagePayload, PositionedNode, RendererMode, SelectionState, ViewportState } from "../types";

const MIN_ZOOM = 0.0001;
const MAX_ZOOM = 50;

interface InternalOptions {
  mode: LayoutMode;
  depth: DepthSetting;
  nodeLimit: number | "all";
  edgeType: string;
  search: string;
  familyVisible: Record<string, boolean>;
  centerId: string | null;
  renderer: "auto" | "webgl" | "canvas";
  xScale: number;
  yScale: number;
  edgeOpacity: number;
  edgeWidth: number;
  ribbonCulling: "off" | "light" | "strong";
  forceCutoff: number;
  forceStrength: number;
  repulsionStrength: number;
  selectedNodeId?: string | null;
  selectedEdgeIndex?: number | null;
}

export interface LineageGraphHandle {
  fit: () => void;
  exportPng: () => void;
  exportSvg: () => void;
}

export interface LineageGraphRuntimeState {
  visibleNodes: PositionedNode[];
  visibleEdges: LineageEdge[];
  rendererMode: RendererMode;
  viewport: ViewportState;
}

function cullEdges(edges: LineageEdge[], strength: InternalOptions["ribbonCulling"]): LineageEdge[] {
  if (strength === "off") {
    return edges;
  }
  const cap = strength === "strong" ? 2 : 8;
  const counts = new Map<string, number>();
  return edges.filter((edge) => {
    const key = `${edge.from}:${edge.to}:${edge.type || "RELATED"}`;
    const count = counts.get(key) || 0;
    counts.set(key, count + 1);
    return count < cap;
  });
}

function useVisibleGraph(nodes: PositionedNode[], edges: LineageEdge[], options: InternalOptions): LineageGraphRuntimeState {
  const [layoutTick, setLayoutTick] = useState(0);
  const [viewport, setViewport] = useState<ViewportState>({ x: 0, y: 0, zoom: 1 });
  const rendererMode = options.renderer === "canvas" ? "canvas" : "webgl";

  const visible = useMemo(() => {
    const query = options.search.trim().toLowerCase();
    const allSeedIds = query
      ? nodes
          .filter((node) => `${node.id} ${node.label} ${node.family}`.toLowerCase().includes(query))
          .map((node) => node.id)
      : nodes.map((node) => node.id);
    const seeds = options.centerId ? [options.centerId] : allSeedIds;
    const depth = options.centerId ? options.depth : "1";
    const depthResult = resolveDepth(edges, seeds, depth, options.edgeType);
    let visibleNodes = nodes.filter((node) => depthResult.ids.has(node.id));
    visibleNodes = visibleNodes.filter(
      (node) =>
        options.familyVisible[node.family] !== false ||
        node.id === options.centerId ||
        node.id === options.selectedNodeId,
    );
    if (!options.centerId && !query) {
      visibleNodes = [...visibleNodes].sort((left, right) => {
        const degreeDelta = right.degree - left.degree;
        return degreeDelta || left.id.localeCompare(right.id);
      });
    }
    if (options.nodeLimit !== "all") {
      visibleNodes = visibleNodes.slice(0, options.nodeLimit);
    }
    if (options.selectedNodeId && !visibleNodes.some((node) => node.id === options.selectedNodeId)) {
      const selected = nodes.find((node) => node.id === options.selectedNodeId);
      if (selected) {
        visibleNodes = [selected, ...visibleNodes];
      }
    }
    const visibleIds = new Set(visibleNodes.map((node) => node.id));
    const baseEdges = (options.centerId ? depthResult.edges : edges).filter(
      (edge) =>
        visibleIds.has(edge.from) &&
        visibleIds.has(edge.to) &&
        (!options.edgeType || edge.type === options.edgeType),
    );
    if (options.mode === "lineage") {
      applyLineageLayout(visibleNodes, options.xScale, options.yScale);
    } else if (visibleNodes.length <= options.forceCutoff) {
      applyForceLayoutStep(visibleNodes, baseEdges, 2, {
        springStrength: options.forceStrength,
        repulsionStrength: options.repulsionStrength,
      });
    }
    const visibleEdges = cullEdges(baseEdges, options.mode === "lineage" ? options.ribbonCulling : "off");
    return { visibleNodes, visibleEdges };
  }, [edges, nodes, options, layoutTick]);

  useEffect(() => {
    if (options.mode !== "network" || visible.visibleNodes.length > options.forceCutoff) {
      return;
    }
    const id = window.setInterval(() => setLayoutTick((value) => value + 1), 34);
    return () => window.clearInterval(id);
  }, [options.mode, options.forceCutoff, visible.visibleNodes.length]);

  return { ...visible, rendererMode, viewport };
}

function drawCanvas(
  ctx: CanvasRenderingContext2D,
  nodes: PositionedNode[],
  edges: LineageEdge[],
  viewport: ViewportState,
  selectedNodeId: string | null,
  selectedEdgeIndex: number | null,
  edgeOpacity: number,
  edgeWidth: number,
): void {
  const width = ctx.canvas.clientWidth;
  const height = ctx.canvas.clientHeight;
  ctx.clearRect(0, 0, width, height);
  const byId = new Map(nodes.map((node) => [node.id, node]));
  const project = (node: PositionedNode) => ({ x: node.x * viewport.zoom + viewport.x, y: node.y * viewport.zoom + viewport.y });
  for (const [index, edge] of edges.entries()) {
    const source = byId.get(edge.from);
    const target = byId.get(edge.to);
    if (!source || !target) {
      continue;
    }
    const a = project(source);
    const b = project(target);
    if (!Number.isFinite(a.x + a.y + b.x + b.y)) {
      continue;
    }
    const selected = selectedEdgeIndex === index || selectedNodeId === edge.from || selectedNodeId === edge.to;
    ctx.lineWidth = selected ? edgeWidth + 2.2 : edgeWidth;
    ctx.strokeStyle = selected ? "#be123c" : `rgba(8,145,178,${edgeOpacity})`;
    ctx.beginPath();
    ctx.moveTo(a.x, a.y);
    ctx.lineTo(b.x, b.y);
    ctx.stroke();
  }
  for (const node of nodes) {
    const point = project(node);
    if (!Number.isFinite(point.x + point.y)) {
      continue;
    }
    const active = node.id === selectedNodeId;
    ctx.fillStyle = familyColor(node.family);
    ctx.strokeStyle = active ? "#111827" : "#fff";
    ctx.lineWidth = active ? 3 : 1.5;
    ctx.beginPath();
    ctx.arc(point.x, point.y, active ? 8 : 6, 0, Math.PI * 2);
    ctx.fill();
    ctx.stroke();
    if (viewport.zoom > 0.45 && nodes.length < 1200) {
      ctx.fillStyle = "#111827";
      ctx.font = "11px system-ui";
      ctx.fillText(node.id, point.x + 9, point.y + 4);
    }
  }
}

function useCanvasSize(canvasRef: React.RefObject<HTMLCanvasElement | null>): number {
  const [version, setVersion] = useState(0);
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) {
      return;
    }
    const resize = () => {
      const rect = canvas.getBoundingClientRect();
      const dpr = window.devicePixelRatio || 1;
      canvas.width = Math.max(1, Math.floor(rect.width * dpr));
      canvas.height = Math.max(1, Math.floor(rect.height * dpr));
      const ctx = canvas.getContext("2d");
      if (ctx) {
        ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      }
      setVersion((value) => value + 1);
    };
    resize();
    const observer = new ResizeObserver(resize);
    observer.observe(canvas);
    return () => observer.disconnect();
  }, [canvasRef]);
  return version;
}

function fitViewport(nodes: PositionedNode[], width: number, height: number): ViewportState {
  const finite = nodes.filter((node) => Number.isFinite(node.x) && Number.isFinite(node.y));
  if (!finite.length) {
    return { x: 0, y: 0, zoom: 1 };
  }
  const minX = Math.min(...finite.map((node) => node.x));
  const maxX = Math.max(...finite.map((node) => node.x));
  const minY = Math.min(...finite.map((node) => node.y));
  const maxY = Math.max(...finite.map((node) => node.y));
  const nextZoom = Math.min(width / Math.max(1, maxX - minX + 220), height / Math.max(1, maxY - minY + 220));
  const zoom = Number.isFinite(nextZoom) && nextZoom > 0 ? Math.max(MIN_ZOOM, Math.min(MAX_ZOOM, nextZoom)) : 1;
  return {
    x: Number.isFinite(minX + maxX) ? (width - (minX + maxX) * zoom) / 2 : 0,
    y: Number.isFinite(minY + maxY) ? (height - (minY + maxY) * zoom) / 2 : 0,
    zoom,
  };
}

export function LineageGraph({
  payload,
  options,
  className,
  onSelectionChange,
}: {
  payload: LineagePayload;
  options?: Partial<InternalOptions>;
  className?: string;
  onSelectionChange?: (selection: SelectionState) => void;
}): React.ReactElement {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const nodesRef = useRef(normalizeNodes(payload.nodes));
  const dragRef = useRef<{ kind: "node" | "pan"; nodeId: string | null; lastX: number; lastY: number; moved: boolean } | null>(null);
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);
  const [selectedEdgeIndex, setSelectedEdgeIndex] = useState<number | null>(null);
  const [viewport, setViewport] = useState<ViewportState>({ x: 0, y: 0, zoom: 1 });
  const canvasVersion = useCanvasSize(canvasRef);
  const runtimeOptions: InternalOptions = {
    mode: options?.mode || "network",
    depth: options?.depth || "1",
    nodeLimit: options?.nodeLimit || 250,
    edgeType: options?.edgeType || "",
    search: options?.search || "",
    familyVisible: options?.familyVisible || {},
    centerId: options?.centerId || null,
    renderer: options?.renderer || "auto",
    xScale: options?.xScale || 1,
    yScale: options?.yScale || 1,
    edgeOpacity: options?.edgeOpacity ?? 0.92,
    edgeWidth: options?.edgeWidth ?? 2.25,
    ribbonCulling: options?.ribbonCulling || "light",
    forceCutoff: options?.forceCutoff || 10000,
    forceStrength: options?.forceStrength ?? 1,
    repulsionStrength: options?.repulsionStrength ?? 1,
    selectedNodeId: options?.selectedNodeId,
    selectedEdgeIndex: options?.selectedEdgeIndex,
  };
  const runtime = useVisibleGraph(nodesRef.current, payload.edges, runtimeOptions);
  const effectiveSelectedNodeId = runtimeOptions.selectedNodeId !== undefined ? runtimeOptions.selectedNodeId : selectedNodeId;
  const effectiveSelectedEdgeIndex =
    runtimeOptions.selectedEdgeIndex !== undefined ? runtimeOptions.selectedEdgeIndex : selectedEdgeIndex;
  const commitSelection = (nextNodeId: string | null, nextEdgeIndex: number | null) => {
    setSelectedNodeId(nextNodeId);
    setSelectedEdgeIndex(nextEdgeIndex);
    onSelectionChange?.({
      selectedNodeId: nextNodeId,
      selectedEdgeIndex: nextEdgeIndex,
      focusNodeId: runtimeOptions.centerId,
    });
  };

  const fit = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas) {
      return;
    }
    const width = Math.max(1, canvas.clientWidth || canvas.width || 1);
    const height = Math.max(1, canvas.clientHeight || canvas.height || 1);
    setViewport(fitViewport(runtime.visibleNodes, width, height));
  }, [runtime.visibleNodes]);

  const zoomBy = (factor: number) => {
    const canvas = canvasRef.current;
    const centerX = (canvas?.clientWidth || canvas?.width || 1) / 2;
    const centerY = (canvas?.clientHeight || canvas?.height || 1) / 2;
    setViewport((next) => {
      const safeZoom = Number.isFinite(next.zoom) && next.zoom > 0 ? next.zoom : 1;
      const worldX = (centerX - next.x) / safeZoom;
      const worldY = (centerY - next.y) / safeZoom;
      const zoom = Math.max(MIN_ZOOM, Math.min(MAX_ZOOM, safeZoom * factor));
      return { x: centerX - worldX * zoom, y: centerY - worldY * zoom, zoom };
    });
  };

  useEffect(() => {
    fit();
  }, [
    canvasVersion,
    runtimeOptions.mode,
    runtimeOptions.centerId,
    runtimeOptions.nodeLimit,
    runtimeOptions.depth,
    runtimeOptions.edgeType,
    runtimeOptions.search,
    runtimeOptions.xScale,
    runtimeOptions.yScale,
    runtimeOptions.forceStrength,
    runtimeOptions.repulsionStrength,
  ]);

  useEffect(() => {
    const canvas = canvasRef.current;
    const ctx = canvas?.getContext("2d");
    if (!ctx) {
      return;
    }
    drawCanvas(
      ctx,
      runtime.visibleNodes,
      runtime.visibleEdges,
      viewport,
      effectiveSelectedNodeId,
      effectiveSelectedEdgeIndex,
      runtimeOptions.edgeOpacity,
      runtimeOptions.edgeWidth,
    );
  }, [
    runtime.visibleNodes,
    runtime.visibleEdges,
    viewport,
    effectiveSelectedNodeId,
    effectiveSelectedEdgeIndex,
    runtimeOptions.edgeOpacity,
    runtimeOptions.edgeWidth,
  ]);

  useEffect(() => {
    onSelectionChange?.({
      selectedNodeId: effectiveSelectedNodeId ?? null,
      selectedEdgeIndex: effectiveSelectedEdgeIndex ?? null,
      focusNodeId: runtimeOptions.centerId,
    } satisfies SelectionState);
  }, [onSelectionChange, effectiveSelectedNodeId, effectiveSelectedEdgeIndex, runtimeOptions.centerId]);

  const project = (node: PositionedNode) => ({ x: node.x * viewport.zoom + viewport.x, y: node.y * viewport.zoom + viewport.y });
  const pickNode = (x: number, y: number): PositionedNode | null => {
    let best: PositionedNode | null = null;
    let bestDistance = 14;
    for (const node of runtime.visibleNodes) {
      const point = project(node);
      const distance = Math.hypot(point.x - x, point.y - y);
      if (distance < bestDistance) {
        best = node;
        bestDistance = distance;
      }
    }
    return best;
  };

  const exportPng = () => {
    const link = document.createElement("a");
    link.href = canvasRef.current?.toDataURL("image/png") || "";
    link.download = "ssot-lineage-graph.png";
    link.click();
  };

  const exportSvg = () => {
    const byId = new Map(runtime.visibleNodes.map((node) => [node.id, node]));
    const parts: string[] = [];
    for (const edge of runtime.visibleEdges) {
      const source = byId.get(edge.from);
      const target = byId.get(edge.to);
      if (!source || !target) {
        continue;
      }
      const a = project(source);
      const b = project(target);
      parts.push(`<line x1="${a.x}" y1="${a.y}" x2="${b.x}" y2="${b.y}" stroke="#0891b2" stroke-width="2.25"/>`);
    }
    for (const node of runtime.visibleNodes) {
      const point = project(node);
      parts.push(`<circle cx="${point.x}" cy="${point.y}" r="6" fill="${familyColor(node.family)}"/>`);
    }
    const blob = new Blob(
      [`<svg xmlns="http://www.w3.org/2000/svg" width="${canvasRef.current?.clientWidth || 1}" height="${canvasRef.current?.clientHeight || 1}">${parts.join("")}</svg>`],
      { type: "image/svg+xml" },
    );
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = "ssot-lineage-graph.svg";
    link.click();
    setTimeout(() => URL.revokeObjectURL(link.href), 1000);
  };

  return (
    <main className={`ssot-canvas-stage ${className || ""}`} data-renderer={runtime.rendererMode}>
      <canvas
        ref={canvasRef}
        data-testid="ssot-lineage-canvas"
        onDoubleClick={fit}
        onClick={(event) => {
          if (dragRef.current?.moved) {
            dragRef.current = null;
            return;
          }
          const node = pickNode(event.nativeEvent.offsetX, event.nativeEvent.offsetY);
          if (node) {
            commitSelection(node.id, null);
          }
        }}
        onMouseDown={(event) => {
          const node = pickNode(event.nativeEvent.offsetX, event.nativeEvent.offsetY);
          dragRef.current = {
            kind: node ? "node" : "pan",
            nodeId: node?.id || null,
            lastX: event.clientX,
            lastY: event.clientY,
            moved: false,
          };
        }}
        onMouseMove={(event) => {
          const drag = dragRef.current;
          if (!drag) {
            return;
          }
          const dx = event.clientX - drag.lastX;
          const dy = event.clientY - drag.lastY;
          if (Math.abs(dx) + Math.abs(dy) > 1) {
            drag.moved = true;
          }
          if (drag.kind === "pan") {
            drag.lastX = event.clientX;
            drag.lastY = event.clientY;
            setViewport((next) => ({ ...next, x: next.x + dx, y: next.y + dy }));
            return;
          }
          const node = nodesRef.current.find((candidate) => candidate.id === drag.nodeId);
          if (node) {
            node.x += dx / viewport.zoom;
            node.y += dy / viewport.zoom;
            node.vx = 0;
            node.vy = 0;
            node.pinned = true;
          }
          drag.lastX = event.clientX;
          drag.lastY = event.clientY;
          setViewport((next) => ({ ...next }));
        }}
        onMouseUp={() => {
          dragRef.current = null;
        }}
        onMouseLeave={() => {
          dragRef.current = null;
        }}
        onWheel={(event) => {
          event.preventDefault();
          const factor = event.deltaY < 0 ? 1.1 : 0.9;
          const wx = (event.nativeEvent.offsetX - viewport.x) / viewport.zoom;
          const wy = (event.nativeEvent.offsetY - viewport.y) / viewport.zoom;
          const zoom = Math.max(MIN_ZOOM, Math.min(MAX_ZOOM, viewport.zoom * factor));
          setViewport({ x: event.nativeEvent.offsetX - wx * zoom, y: event.nativeEvent.offsetY - wy * zoom, zoom });
        }}
      />
      <div className="ssot-toolbar">
        <button type="button" onClick={fit}>
          Fit
        </button>
        <button type="button" onClick={() => zoomBy(1.25)}>
          +
        </button>
        <button type="button" onClick={() => zoomBy(0.8)}>
          -
        </button>
        <button type="button" onClick={() => setViewport({ x: 0, y: 0, zoom: 1 })}>
          100%
        </button>
        <button type="button" onClick={exportPng}>
          PNG
        </button>
        <button type="button" onClick={exportSvg}>
          SVG
        </button>
        <span className="pill">
          {runtime.visibleNodes.length} visible nodes / {runtime.visibleEdges.length} visible edges - zoom{" "}
          {Number.isFinite(viewport.zoom) ? Math.round(viewport.zoom * 100) : 100}%
        </span>
      </div>
    </main>
  );
}
