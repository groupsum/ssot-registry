import React, { useState, useRef } from "react";
import { NodePositions, GraphViewMode } from "../../types";

interface UseNodeDraggingProps {
  positions: NodePositions;
  zoom: number;
  mode: GraphViewMode;
  onUpdatePositions: (next: NodePositions) => void;
}

export function useNodeDragging({
  positions,
  zoom,
  mode,
  onUpdatePositions,
}: UseNodeDraggingProps) {
  const [draggedNodeId, setDraggedNodeId] = useState<string | null>(null);
  const dragStartMouseRef = useRef({ x: 0, y: 0 });
  const dragStartPosRef = useRef({ x: 0, y: 0 });
  const hasDraggedRef = useRef(false);

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

  return {
    draggedNodeId,
    setDraggedNodeId,
    hasDragged: hasDraggedRef.current,
    handleNodePointerDown,
    handleNodePointerMove,
    handleNodePointerUp,
    handleNodeDoubleClick,
    handleTogglePinNode,
  };
}
