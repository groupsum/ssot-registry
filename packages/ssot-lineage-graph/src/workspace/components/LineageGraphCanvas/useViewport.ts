import React, { useState, useEffect, useRef } from "react";
import { LineagePayload, NodePositions, Position } from "../../types";

interface UseViewportProps {
  positions: NodePositions;
  payload: LineagePayload;
  focusNodeId: string | null;
  draggedNodeId: string | null;
  onClickBackground?: () => void;
}

export function useViewport({
  positions,
  payload,
  focusNodeId,
  draggedNodeId,
  onClickBackground,
}: UseViewportProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [pan, setPan] = useState({ x: 50, y: 50 });
  const [zoom, setZoom] = useState(0.85);
  const [isPanning, setIsPanning] = useState(false);
  const startPanRef = useRef({ x: 0, y: 0 });
  const pointerDownCoordsRef = useRef<{ x: number; y: number } | null>(null);
  const prevPayloadRef = useRef<any>(null);

  // Web scale rendering optimization: Visual Debounce of culling recalculations during fast panning or zoom sweeps.
  const [debouncedBounds, setDebouncedBounds] = useState(() => {
    const left = (0 - 50) / 0.85;
    const top = (0 - 50) / 0.85;
    const right = (1100 - 50) / 0.85;
    const bottom = (620 - 50) / 0.85;
    return { left, right, top, bottom, zoom: 0.85 };
  });

  // Keyboard navigation shortcuts: Arrow keys to pan, +/- to zoom
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
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

  useEffect(() => {
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
    pointerDownCoordsRef.current = { x: e.clientX, y: e.clientY };
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

      if (pointerDownCoordsRef.current && onClickBackground) {
        const dx = e.clientX - pointerDownCoordsRef.current.x;
        const dy = e.clientY - pointerDownCoordsRef.current.y;
        const dist = Math.sqrt(dx * dx + dy * dy);
        if (dist < 5) {
          onClickBackground();
        }
      }
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

  return {
    containerRef,
    pan,
    setPan,
    zoom,
    setZoom,
    isPanning,
    setIsPanning,
    debouncedBounds,
    handleWorkspacePointerDown,
    handleWorkspacePointerMove,
    handleWorkspacePointerUp,
    handleWheel,
    handleFitView,
    handleResetZoom,
  };
}
