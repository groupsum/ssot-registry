/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import { LineagePayload, LineageNode, LineageEdge, OriginKind, Position, NodePositions, GraphViewMode } from "../types";

// Map lineage families to deterministic columns for hierarchical lineage mode
export const FAMILY_LAYERS: Record<string, number> = {
  ADR: 0,
  Spec: 1,
  SPEC: 1,
  Feature: 2,
  Claim: 3,
  Test: 4,
  Evidence: 5,
  Release: 6,
  Boundary: 1, // Boundary groups with Spec/Feature columns
  Profile: 1,
  Risk: 3,     // Threatens Claim/Feature
  Issue: 4,    // Paired near Test/Release blockers
};

export function columnForNode(node: LineageNode, viewMode?: GraphViewMode): number {
  let col = FAMILY_LAYERS[node.family] ?? 3;

  if (viewMode === "packs") {
    const hasGov = (node.governancePacks && node.governancePacks.length > 0) || (node.packs && node.packs.some(p => p.includes("governance") || p.includes("core")));
    const hasContract = (node.contractPacks && node.contractPacks.length > 0) || (node.packs && node.packs.some(p => p.includes("contract")));
    const hasOtherPack = (node.packs && node.packs.length > 0);

    if (hasGov) {
      col = 1;
    } else if (hasContract) {
      col = 2;
    } else if (hasOtherPack) {
      col = 3;
    } else {
      col = 0;
    }
  } else if (viewMode === "validation") {
    const vStatus = node.validation?.status || (node.status === "certified" ? "pass" : "unknown");
    if (vStatus === "pass") {
      col = 0;
    } else if (vStatus === "warn") {
      col = 1;
    } else if (vStatus === "fail") {
      col = 2;
    } else {
      col = 3;
    }
  } else if (viewMode === "release") {
    const isRelease = node.family === "Release";
    const rStatus = node.status || "active";
    if (isRelease) {
      col = 3;
    } else if (rStatus === "certified") {
      col = 2;
    } else if (rStatus === "active") {
      col = 1;
    } else {
      col = 0;
    }
  } else if (viewMode === "origins") {
    const kind = node.originKind || "unknown";
    if (kind === "ssot-core") col = 0;
    else if (kind === "ssot-origin") col = 1;
    else if (kind === "repo-local") col = 2;
    else if (kind === "extension-pack" || kind === "generated") col = 3;
    else col = 4;
  } else if (viewMode === "proof") {
    if (node.family === "ADR" || node.family === "Spec" || node.family === "SPEC") col = 0;
    else if (node.family === "Feature") col = 1;
    else if (node.family === "Claim") col = 2;
    else if (node.family === "Test" || node.family === "Evidence") col = 3;
    else col = 4;
  }

  return col;
}

// Compute adjacency maps for instant sub-graph traversals
export function computeGraphIndices(payload: LineagePayload) {
  const nodeMap = new Map<string, LineageNode>();
  payload.nodes.forEach((n) => nodeMap.set(n.id, n));

  const incoming = new Map<string, string[]>();
  const outgoing = new Map<string, string[]>();
  const edgeMap = new Map<string, LineageEdge[]>();

  payload.edges.forEach((edge) => {
    // Collect outgoing
    const fromList = outgoing.get(edge.from) || [];
    fromList.push(edge.to);
    outgoing.set(edge.from, fromList);

    // Collect incoming
    const toList = incoming.get(edge.to) || [];
    toList.push(edge.from);
    incoming.set(edge.to, toList);

    // Collect edges
    const nodeFromEdges = edgeMap.get(edge.from) || [];
    nodeFromEdges.push(edge);
    edgeMap.set(edge.from, nodeFromEdges);

    const nodeToEdges = edgeMap.get(edge.to) || [];
    nodeToEdges.push(edge);
    edgeMap.set(edge.to, nodeToEdges);
  });

  return { nodeMap, incoming, outgoing, edgeMap };
}

export function hasCollapsedUpstreamAncestor(
  id: string,
  incoming: Map<string, string[]>,
  collapsedIds: Set<string>
): boolean {
  let current = id;
  const visited = new Set<string>();

  while (current) {
    if (visited.has(current)) return false;
    visited.add(current);

    const parents = incoming.get(current);
    if (!parents || parents.length === 0) return false;

    const parent = parents[0];
    if (collapsedIds.has(parent)) return true;
    current = parent;
  }

  return false;
}

// Trace upstream/downstream connections for a given nodeId (high-performance recursive trace)
export function traceSubGraph(
  nodeId: string,
  incoming: Map<string, string[]>,
  outgoing: Map<string, string[]>,
  depth: number = 3
): { nodes: Set<string>; edges: Set<string> } {
  const connectedNodes = new Set<string>([nodeId]);
  const connectedEdges = new Set<string>();

  function traverse(currentId: string, currentDepth: number, direction: "upstream" | "downstream") {
    if (currentDepth <= 0) return;
    const neighbors = direction === "upstream" ? incoming.get(currentId) : outgoing.get(currentId);
    if (!neighbors) return;

    neighbors.forEach((neighbor) => {
      connectedNodes.add(neighbor);
      const edgeKey = direction === "upstream" ? `${neighbor}->${currentId}` : `${currentId}->${neighbor}`;
      connectedEdges.add(edgeKey);
      traverse(neighbor, currentDepth - 1, direction);
    });
  }

  traverse(nodeId, depth, "upstream");
  traverse(nodeId, depth, "downstream");

  return { nodes: connectedNodes, edges: connectedEdges };
}

// Compute deterministic layout position matrix
export function computeDeterministicLayout(
  nodes: LineageNode[],
  incoming: Map<string, string[]>,
  outgoing: Map<string, string[]>,
  collapsedIds: Set<string>,
  scaleX: number = 220,
  scaleY: number = 90,
  width: number = 1000,
  height: number = 600,
  viewMode?: GraphViewMode,
  userHiddenIds?: Set<string>
): NodePositions {
  const positions: NodePositions = {};

  // Group nodes by their defined layers
  const layerNodes: Record<number, string[]> = {};
  for (let l = 0; l <= 6; l++) {
    layerNodes[l] = [];
  }

  // Filter out nodes that are children of collapsed parent paths
  // A node is hidden if any of its upstream paths are collapsed
  const hiddenNodeIds = new Set<string>();
  if (userHiddenIds) {
    userHiddenIds.forEach((id) => hiddenNodeIds.add(id));
  }

  // BFS search to find all descendants of any collapsed node, and add them to hiddenNodeIds
  const queue = Array.from(collapsedIds);
  const visited = new Set<string>();
  while (queue.length > 0) {
    const current = queue.shift()!;
    if (visited.has(current)) continue;
    visited.add(current);

    const children = outgoing.get(current) || [];
    for (const child of children) {
      hiddenNodeIds.add(child);
      if (!visited.has(child)) {
        queue.push(child);
      }
    }
  }

  const isLarge = nodes.length > 5000;
  nodes.forEach((node, idx) => {
    if (isLarge) {
      const match = node.id.match(/-(\d+)$/);
      const megaIdx = match ? parseInt(match[1], 10) : -1;
      if (megaIdx !== -1) {
        if (megaIdx > 150 && megaIdx % 500 !== 0) return;
      } else {
        if (idx % 50 !== 0) return;
      }
    }
    if (hiddenNodeIds.has(node.id)) return;

    const col = columnForNode(node, viewMode);

    if (!layerNodes[col]) layerNodes[col] = [];
    layerNodes[col].push(node.id);
  });

  // Calculate coordinates. Dense lanes use adaptive subcolumns so repo-scale
  // families form compact tiles instead of 30k-pixel vertical ribbons.
  const startX = 60;
  const laneGap = 120;
  const minLaneWidth = 200;
  const subColWidth = 52;
  const maxSubCols = 32;
  let laneCursor = startX;

  Object.entries(layerNodes).forEach(([, nodeIds]) => {
    const totalNodes = nodeIds.length;
    if (totalNodes === 0) return;

    let numSubCols = Math.min(4, Math.ceil(totalNodes / 15));
    if (totalNodes > 60) {
      const targetRows = Math.max(12, Math.ceil(Math.sqrt(totalNodes) * 1.5));
      numSubCols = Math.min(maxSubCols, Math.max(4, Math.ceil(totalNodes / targetRows)));
    }

    // Total rows we need
    const numRows = Math.ceil(totalNodes / numSubCols);
    const totalHeight = (numRows - 1) * scaleY;
    const startY = Math.max(90, (height - totalHeight) / 2);
    const laneWidth = Math.max(minLaneWidth, (numSubCols - 1) * subColWidth + 120);
    const x = laneCursor + laneWidth / 2;

    nodeIds.forEach((id, index) => {
      const subCol = index % numSubCols;
      const subRow = Math.floor(index / numSubCols);

      // Center the grid of sub-columns perfectly inside the lane's main horizontal center
      const xOffset = (subCol - (numSubCols - 1) / 2) * subColWidth;

      positions[id] = {
        x: x + xOffset,
        y: startY + subRow * scaleY,
      };
    });

    laneCursor += laneWidth + laneGap;
  });

  return positions;
}

// Lightweight modular Force Directed simulation math solver
export function runForceSimulationStep(
  nodes: LineageNode[],
  edges: LineageEdge[],
  positions: NodePositions,
  disabledIds: Set<string>,
  width: number = 1000,
  height: number = 600,
  centerGravity: number = 0.05,
  repulsionConstant: number = 3200,
  springConstant: number = 0.06,
  restLength: number = 130,
  viewMode?: string
): NodePositions {
  const nextPositions = { ...positions };

  // 1. Initialize node position vectors if nonexistent
  nodes.forEach((n) => {
    if (disabledIds.has(n.id)) return;
    if (!nextPositions[n.id]) {
      // Scatter randomly around center
      nextPositions[n.id] = {
        x: width / 2 + (Math.random() - 0.5) * 200,
        y: height / 2 + (Math.random() - 0.5) * 200,
        vx: 0,
        vy: 0,
      };
    } else {
      if (nextPositions[n.id].vx === undefined) nextPositions[n.id].vx = 0;
      if (nextPositions[n.id].vy === undefined) nextPositions[n.id].vy = 0;
    }
  });

  // 2. Pairwise Repulsion forces (Coulomb-like node avoidance)
  const nodeKeys = nodes.filter(n => !disabledIds.has(n.id)).map(n => n.id);
  const len = nodeKeys.length;

  if (len > 100) {
    // Spatial grid partitioning
    const cellSize = 250;
    const grid = new Map<string, string[]>();

    nodeKeys.forEach((id) => {
      const pos = nextPositions[id];
      if (!pos) return;
      const cx = Math.floor(pos.x / cellSize);
      const cy = Math.floor(pos.y / cellSize);
      const key = `${cx},${cy}`;
      if (!grid.has(key)) {
        grid.set(key, []);
      }
      grid.get(key)!.push(id);
    });

    const processedPairs = new Set<string>();

    nodeKeys.forEach((idA) => {
      const posA = nextPositions[idA];
      if (!posA) return;

      const cx = Math.floor(posA.x / cellSize);
      const cy = Math.floor(posA.y / cellSize);

      // Check current cell and 8 adjacent cells
      for (let dxCell = -1; dxCell <= 1; dxCell++) {
        for (let dyCell = -1; dyCell <= 1; dyCell++) {
          const neighborKey = `${cx + dxCell},${cy + dyCell}`;
          const neighborIds = grid.get(neighborKey);
          if (!neighborIds) continue;

          for (const idB of neighborIds) {
            if (idA === idB) continue;

            // Avoid double calculating the force for symmetric pairs
            const pairKey = idA < idB ? `${idA}:${idB}` : `${idB}:${idA}`;
            if (processedPairs.has(pairKey)) continue;
            processedPairs.add(pairKey);

            const posB = nextPositions[idB];
            if (!posB) continue;

            const dx = posA.x - posB.x;
            const dy = posA.y - posB.y;
            const distanceSq = dx * dx + dy * dy + 0.1; // avoid divide by zero
            const distance = Math.sqrt(distanceSq);

            if (distance < 450) {
              // Cap maximum repulsion to prevent high-velocity explosive spikes
              const force = Math.min(8, repulsionConstant / (distanceSq + 400));
              const fx = (dx / distance) * force;
              const fy = (dy / distance) * force;

              if (posA.fx === undefined || posA.fx === null) {
                posA.vx = (posA.vx || 0) + fx;
                posA.vy = (posA.vy || 0) + fy;
              }
              if (posB.fx === undefined || posB.fx === null) {
                posB.vx = (posB.vx || 0) - fx;
                posB.vy = (posB.vy || 0) - fy;
              }
            }
          }
        }
      }
    });
  } else {
    // Normal naive O(N^2) loop for small graphs (saves hash lookup overhead)
    for (let i = 0; i < len; i++) {
      const idA = nodeKeys[i];
      const posA = nextPositions[idA];
      if (!posA) continue;

      for (let j = i + 1; j < len; j++) {
        const idB = nodeKeys[j];
        const posB = nextPositions[idB];
        if (!posB) continue;

        const dx = posA.x - posB.x;
        const dy = posA.y - posB.y;
        const distanceSq = dx * dx + dy * dy + 0.1; // avoid divide by zero
        const distance = Math.sqrt(distanceSq);

        if (distance < 450) {
          // Cap maximum repulsion
          const force = Math.min(8, repulsionConstant / (distanceSq + 400));
          const fx = (dx / distance) * force;
          const fy = (dy / distance) * force;

          // Apply force to velocities if elements aren't currently being dragged
          if (posA.fx === undefined || posA.fx === null) {
            posA.vx = (posA.vx || 0) + fx;
            posA.vy = (posA.vy || 0) + fy;
          }
          if (posB.fx === undefined || posB.fx === null) {
            posB.vx = (posB.vx || 0) - fx;
            posB.vy = (posB.vy || 0) - fy;
          }
        }
      }
    }
  }

  // 3. Spring Edge Attraction forces (Hooke's-like law)
  edges.forEach((edge) => {
    if (disabledIds.has(edge.from) || disabledIds.has(edge.to)) return;
    const posFrom = nextPositions[edge.from];
    const posTo = nextPositions[edge.to];
    if (!posFrom || !posTo) return;

    const dx = posTo.x - posFrom.x;
    const dy = posTo.y - posFrom.y;
    const distance = Math.sqrt(dx * dx + dy * dy) || 1;

    // Displacement from relaxed spring length
    const displacement = distance - restLength;
    // Cap spring extension attraction forces to prevent visual whipping
    const force = Math.max(-12, Math.min(12, springConstant * displacement));
    const fx = (dx / distance) * force;
    const fy = (dy / distance) * force;

    if (posFrom.fx === undefined || posFrom.fx === null) {
      posFrom.vx = (posFrom.vx || 0) + fx;
      posFrom.vy = (posFrom.vy || 0) + fy;
    }
    if (posTo.fx === undefined || posTo.fx === null) {
      posTo.vx = (posTo.vx || 0) - fx;
      posTo.vy = (posTo.vy || 0) - fy;
    }
  });

  // 4. Center Gravity & Inertia Friction damping
  const cx = width / 2;
  const cy = height / 2;
  const damping = viewMode === "flow-force" ? 0.72 : 0.62; // Faster, snappier flows with higher motion persistence

  const nodeMap = new Map<string, LineageNode>();
  nodes.forEach(n => nodeMap.set(n.id, n));

  nodeKeys.forEach((id) => {
    const pos = nextPositions[id];
    if (!pos) return;

    // Drag constraints: if active drag position is set (fx/fy), enforce it immediately
    if (pos.fx !== undefined && pos.fx !== null && pos.fy !== undefined && pos.fy !== null) {
      pos.x = pos.fx;
      pos.y = pos.fy;
      pos.vx = 0;
      pos.vy = 0;
      return;
    }

    if (viewMode === "flow-force") {
      const nodeObj = nodeMap.get(id);
      const col = nodeObj ? columnForNode(nodeObj) : 3;
      // Setup horizontal alignments aligned to column scaleX (220 to match deterministic views)
      const targetX = 60 + col * 220;

      // Anchor columns at the poles (ADR at col 0, Release at col 6) with heavy weight
      let kX = 0.28;
      if (col === 0 || col === 6) {
        kX = 0.85; // Anchored heavily at the left and right borders of the swimlanes
      }
      const xForce = (targetX - pos.x) * kX;
      pos.vx = (pos.vx || 0) + xForce;

      const yForce = (cy - pos.y) * 0.075; // Significantly heavier y-axis pull to keep nodes aligned near center x-axis line
      pos.vy = (pos.vy || 0) + yForce;
    } else {
      // Pull toward gravitational layout center
      const gdx = cx - pos.x;
      const gdy = cy - pos.y;
      pos.vx = (pos.vx || 0) + gdx * centerGravity;
      pos.vy = (pos.vy || 0) + gdy * centerGravity;
    }

    // Apply velocity step with dampener
    pos.x += (pos.vx || 0) * damping;
    pos.y += (pos.vy || 0) * damping;

    // Decelerate velocities
    pos.vx *= damping;
    pos.vy *= damping;

    // Boundary constraints: clip to prevent flying offviewport margins
    const margin = 40;
    if (pos.x < margin) { pos.x = margin; pos.vx = 0; }
    if (pos.x > width - margin) { pos.x = width - margin; pos.vx = 0; }
    if (pos.y < margin) { pos.y = margin; pos.vy = 0; }
    if (pos.y > height - margin) { pos.y = height - margin; pos.vy = 0; }
  });

  return nextPositions;
}

// Generate smooth cubic bezier SVG curves connecting nodes
export function generateSvgLinkCurve(
  startX: number,
  startY: number,
  endX: number,
  endY: number,
  mode: string
): string {
  if (mode === "lineage" || mode === "proof" || mode === "packs") {
    // Left-to-right neat curves using control-point handles
    const midX = (startX + endX) / 2;
    return `M ${startX} ${startY} C ${midX} ${startY}, ${midX} ${endY}, ${endX} ${endY}`;
  }

  // Standard direct line or slightly curved bezier line for network modes
  const dx = endX - startX;
  const dy = endY - startY;
  const dist = Math.sqrt(dx * dx + dy * dy);

  if (dist < 40) {
    return `M ${startX} ${startY} L ${endX} ${endY}`;
  }

  // Slight curvature for overlapping back-edges or neat networks
  const controlOffset = 25;
  const mx = (startX + endX) / 2 - (dy / dist) * controlOffset;
  const my = (startY + endY) / 2 + (dx / dist) * controlOffset;
  return `M ${startX} ${startY} Q ${mx} ${my}, ${endX} ${endY}`;
}
