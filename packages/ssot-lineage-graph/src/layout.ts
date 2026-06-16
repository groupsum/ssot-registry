import { familyRank } from "./constants";
import type { DepthSetting, LineageEdge, LineageNode, PositionedNode } from "./types";

export interface ForceLayoutOptions {
  springStrength?: number;
  repulsionStrength?: number;
}

export function normalizeNodes(nodes: LineageNode[]): PositionedNode[] {
  return nodes.map((node, index) => ({
    id: node.id,
    family: node.family,
    label: node.label || node.id,
    status: node.status || "",
    tier: node.tier || "",
    origin: node.origin || "",
    path: node.path || "",
    degree: Number(node.degree || 0),
    x: Number.isFinite(node.x) ? Number(node.x) : (index % 100) * 46,
    y: Number.isFinite(node.y) ? Number(node.y) : Math.floor(index / 100) * 46,
    vx: Number(node.vx || 0),
    vy: Number(node.vy || 0),
    pinned: Boolean(node.pinned),
  }));
}

export function resolveDepth(
  edges: LineageEdge[],
  seeds: string[],
  depth: DepthSetting,
  edgeType = "",
): { ids: Set<string>; edges: LineageEdge[] } {
  const ids = new Set(seeds);
  const usedEdges: LineageEdge[] = [];
  let frontier = new Set(seeds);
  const maxDepth = depth === "max" ? Number.POSITIVE_INFINITY : Number(depth);

  for (let hop = 0; hop < maxDepth && frontier.size > 0; hop += 1) {
    const next = new Set<string>();
    for (const edge of edges) {
      if (edgeType && edge.type !== edgeType) {
        continue;
      }
      const fromFrontier = frontier.has(edge.from);
      const toFrontier = frontier.has(edge.to);
      if (!fromFrontier && !toFrontier) {
        continue;
      }
      usedEdges.push(edge);
      if (!ids.has(edge.from)) {
        ids.add(edge.from);
        next.add(edge.from);
      }
      if (!ids.has(edge.to)) {
        ids.add(edge.to);
        next.add(edge.to);
      }
    }
    frontier = next;
    if (depth === "max" && next.size === 0) {
      break;
    }
  }

  return { ids, edges: usedEdges };
}

export function applyLineageLayout(nodes: PositionedNode[], xScale: number, yScale: number): PositionedNode[] {
  const layerGap = 210 * xScale;
  const rankGap = 90 * yScale;
  const byRank = new Map<number, PositionedNode[]>();
  for (const node of nodes) {
    const rank = familyRank(node.family);
    const layer = byRank.get(rank) || [];
    layer.push(node);
    byRank.set(rank, layer);
  }
  for (const [rank, layer] of byRank) {
    layer.sort((left, right) => left.id.localeCompare(right.id));
    layer.forEach((node, index) => {
      node.x = 80 + index * layerGap;
      node.y = 70 + rank * rankGap;
      node.vx = 0;
      node.vy = 0;
    });
  }
  return nodes;
}

export function applyForceLayoutStep(
  nodes: PositionedNode[],
  edges: LineageEdge[],
  iterations = 1,
  options: ForceLayoutOptions = {},
): PositionedNode[] {
  const springStrength = options.springStrength ?? 1;
  const repulsionStrength = options.repulsionStrength ?? 1;
  sanitizeForceNodes(nodes);
  const byId = new Map(nodes.map((node) => [node.id, node]));
  for (let iteration = 0; iteration < iterations; iteration += 1) {
    for (const edge of edges) {
      const source = byId.get(edge.from);
      const target = byId.get(edge.to);
      if (!source || !target) {
        continue;
      }
      const dx = target.x - source.x;
      const dy = target.y - source.y;
      const distance = Math.hypot(dx, dy) || 1;
      if (!Number.isFinite(distance)) {
        continue;
      }
      const spring = Math.max(-4, Math.min(4, (distance - 140) * 0.015 * springStrength));
      const fx = (dx / distance) * spring;
      const fy = (dy / distance) * spring;
      if (!source.pinned) {
        source.vx += fx;
        source.vy += fy;
      }
      if (!target.pinned) {
        target.vx -= fx;
        target.vy -= fy;
      }
    }

    applyBarnesHutRepulsion(nodes, repulsionStrength);

    for (const node of nodes) {
      if (node.pinned) {
        node.vx = 0;
        node.vy = 0;
        continue;
      }
      node.vx = clampFinite(node.vx * 0.82, -24, 24);
      node.vy = clampFinite(node.vy * 0.82, -24, 24);
      node.x += node.vx;
      node.y += node.vy;
      if (!Number.isFinite(node.x) || !Number.isFinite(node.y)) {
        node.x = 0;
        node.y = 0;
        node.vx = 0;
        node.vy = 0;
      } else {
        node.x = clampFinite(node.x, -1_000_000, 1_000_000);
        node.y = clampFinite(node.y, -1_000_000, 1_000_000);
      }
    }
  }
  return nodes;
}

function clampFinite(value: number, min: number, max: number): number {
  if (!Number.isFinite(value)) {
    return 0;
  }
  return Math.max(min, Math.min(max, value));
}

function sanitizeForceNodes(nodes: PositionedNode[]): void {
  nodes.forEach((node, index) => {
    if (!Number.isFinite(node.x)) {
      node.x = (index % 100) * 46;
    }
    if (!Number.isFinite(node.y)) {
      node.y = Math.floor(index / 100) * 46;
    }
    node.vx = clampFinite(node.vx, -24, 24);
    node.vy = clampFinite(node.vy, -24, 24);
  });
}

interface Quad {
  x: number;
  y: number;
  size: number;
  mass: number;
  cx: number;
  cy: number;
  node: PositionedNode | null;
  children: Quad[] | null;
}

function makeQuad(x: number, y: number, size: number): Quad {
  return { x, y, size, mass: 0, cx: 0, cy: 0, node: null, children: null };
}

function childFor(quad: Quad, index: number): Quad {
  const half = quad.size / 2;
  return makeQuad(quad.x + (index & 1 ? half : 0), quad.y + (index & 2 ? half : 0), half);
}

function childIndex(quad: Quad, node: PositionedNode): number {
  const midX = quad.x + quad.size / 2;
  const midY = quad.y + quad.size / 2;
  return (node.x > midX ? 1 : 0) + (node.y > midY ? 2 : 0);
}

function insert(quad: Quad, node: PositionedNode, depth = 0): void {
  if (!quad.node && !quad.children) {
    quad.node = node;
    return;
  }
  if (!quad.children) {
    quad.children = [0, 1, 2, 3].map((index) => childFor(quad, index));
    const existing = quad.node;
    quad.node = null;
    if (existing) {
      insert(quad.children[childIndex(quad, existing)], existing, depth + 1);
    }
  }
  if (depth < 32) {
    insert(quad.children[childIndex(quad, node)], node, depth + 1);
  }
}

function accumulate(quad: Quad): void {
  if (quad.children) {
    for (const child of quad.children) {
      accumulate(child);
      quad.mass += child.mass;
      quad.cx += child.cx * child.mass;
      quad.cy += child.cy * child.mass;
    }
    if (quad.mass > 0) {
      quad.cx /= quad.mass;
      quad.cy /= quad.mass;
    }
  } else if (quad.node) {
    quad.mass = 1;
    quad.cx = quad.node.x;
    quad.cy = quad.node.y;
  }
}

function applyBarnesHutRepulsion(nodes: PositionedNode[], repulsionStrength = 1): void {
  if (nodes.length < 2) {
    return;
  }
  const finiteNodes = nodes.filter((node) => Number.isFinite(node.x) && Number.isFinite(node.y));
  if (finiteNodes.length < 2) {
    return;
  }
  let minX = Number.POSITIVE_INFINITY;
  let minY = Number.POSITIVE_INFINITY;
  let maxX = Number.NEGATIVE_INFINITY;
  let maxY = Number.NEGATIVE_INFINITY;
  for (const node of finiteNodes) {
    minX = Math.min(minX, node.x);
    minY = Math.min(minY, node.y);
    maxX = Math.max(maxX, node.x);
    maxY = Math.max(maxY, node.y);
  }
  const size = Math.max(1, maxX - minX, maxY - minY) + 2;
  const root = makeQuad(minX - 1, minY - 1, size);
  for (const node of finiteNodes) {
    insert(root, node);
  }
  accumulate(root);

  const apply = (quad: Quad, node: PositionedNode): void => {
    if (quad.mass === 0 || quad.node === node || node.pinned) {
      return;
    }
    const dx = quad.cx - node.x;
    const dy = quad.cy - node.y;
    const distance = Math.hypot(dx, dy) || 1;
    if (!quad.children || quad.size / distance < 0.7) {
      if (!Number.isFinite(distance)) {
        return;
      }
      const force = Math.min(2.5, ((1400 * repulsionStrength) * quad.mass) / (distance * distance));
      node.vx -= dx * force * 0.01;
      node.vy -= dy * force * 0.01;
      return;
    }
    for (const child of quad.children) {
      apply(child, node);
    }
  };

  for (const node of finiteNodes) {
    apply(root, node);
  }
}
