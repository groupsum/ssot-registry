import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";
import { familyClassName } from "./constants";
import { createStandaloneHtml } from "./html";
import { LineageGraph } from "./LineageGraph";
import { LineageGraphApp } from "./LineageGraphApp";
import { applyForceLayoutStep, applyLineageLayout, normalizeNodes, resolveDepth } from "./layout";
import {
  computeDeterministicLayout as computeWorkspaceLayout,
  computeGraphIndices as computeWorkspaceIndices,
  hasCollapsedUpstreamAncestor,
} from "./workspace/utils/graphHelpers";
import type { LineagePayload } from "./types";
import type { LineagePayload as WorkspaceLineagePayload } from "./workspace/types";

const families = ["ADR", "Spec", "Feature", "Claim", "Test", "Evidence", "Boundary", "Profile", "Release", "Issue", "Risk"];

function payload(): LineagePayload {
  return {
    package: { name: "fixture", version: "0.1.0" },
    nodes: families.map((family, index) => ({ id: `${family.toLowerCase()}:${index}`, family, label: `${family} node` })),
    edges: families.slice(1).map((family, index) => ({
      from: `${families[index].toLowerCase()}:${index}`,
      to: `${family.toLowerCase()}:${index + 1}`,
      type: "RELATES_TO",
    })),
    summary: { nodeCount: families.length, edgeCount: families.length - 1 },
  };
}

describe("createStandaloneHtml", () => {
  it("embeds payloads without external runtime dependencies", () => {
    const html = createStandaloneHtml(payload(), { script: "window.__ready=true;", style: ".x{color:red}" });
    expect(html).toContain("ssot-lineage-root");
    expect(html).toContain("window.__SSOT_LINEAGE_PAYLOAD__");
    expect(html).toContain("window.__ready=true;");
    expect(html).not.toContain("https://");
    expect(html).not.toContain("<script src=");
  });
});

describe("lineage layout", () => {
  it("left-aligns top-down layers and scales both axes", () => {
    const nodes = normalizeNodes(payload().nodes);
    applyLineageLayout(nodes, 100, 10);
    const adr = nodes.find((node) => node.family === "ADR");
    const spec = nodes.find((node) => node.family === "Spec");
    expect(adr?.x).toBe(80);
    expect(spec?.x).toBe(80);
    expect((spec?.y || 0) - (adr?.y || 0)).toBe(900);
  });

  it("resolves one hop as only the selected node and immediate neighbors", () => {
    const graph = payload();
    const result = resolveDepth(graph.edges, ["feature:2"], "1");
    expect([...result.ids].sort()).toEqual(["claim:3", "feature:2", "spec:1"]);
  });
});

describe("force layout", () => {
  it("updates every visible SSOT family, not only ADRs", () => {
    const nodes = normalizeNodes(payload().nodes);
    const before = new Map(nodes.map((node) => [node.family, `${node.x}:${node.y}`]));
    applyForceLayoutStep(nodes, payload().edges, 4);
    for (const family of families) {
      const node = nodes.find((candidate) => candidate.family === family);
      expect(`${node?.x}:${node?.y}`).not.toBe(before.get(family));
    }
  });

  it("keeps dense visible graph positions finite across repeated force ticks", () => {
    const nodes = normalizeNodes(
      Array.from({ length: 1600 }, (_, index) => ({
        id: `node:${index}`,
        family: families[index % families.length],
        label: `Node ${index}`,
        degree: 16,
      })),
    );
    const edges = Array.from({ length: 12000 }, (_, index) => ({
      from: `node:${index % nodes.length}`,
      to: `node:${(index * 17 + 31) % nodes.length}`,
      type: "RELATES_TO",
    }));

    for (let tick = 0; tick < 80; tick += 1) {
      applyForceLayoutStep(nodes, edges, 2);
    }

    expect(nodes.every((node) => Number.isFinite(node.x) && Number.isFinite(node.y))).toBe(true);
  });
});

describe("viewer behavior contracts", () => {
  it("keeps organized component exports available from stable public entry points", () => {
    expect(typeof LineageGraph).toBe("function");
    expect(typeof LineageGraphApp).toBe("function");
    expect(familyClassName("ADR")).toBe("ssot-family-adr");
  });

  it("keeps canvas selection controlled by the app shell", () => {
    const source = String.raw`${createStandaloneHtml}`;
    expect(source).toContain("window.__SSOT_LINEAGE_PAYLOAD__");
  });

  it("supports canvas panning, visible force motion, and high-contrast edges", () => {
    const source = readFileSync(new URL("./components/LineageGraphCanvas.tsx", import.meta.url), "utf-8");
    expect(source).toContain('kind: node ? "node" : "pan"');
    expect(source).toContain("x: next.x + dx");
    expect(source).toContain("y: next.y + dy");
    expect(source).toContain("rgba(8,145,178");
    expect(source).not.toContain("[fit, canvasVersion");
  });

  it("routes the public app shell to the latest workspace implementation", () => {
    const app = readFileSync(new URL("./views/LineageGraphAppView.tsx", import.meta.url), "utf-8");
    const workspace = readFileSync(new URL("./workspace/components/LineageGraphApp.tsx", import.meta.url), "utf-8");
    const sidebar = readFileSync(new URL("./workspace/components/LeftSidebar.tsx", import.meta.url), "utf-8");
    const styles = readFileSync(new URL("./workspace/index.css", import.meta.url), "utf-8");
    expect(app).toContain("WorkspaceLineageGraphApp");
    expect(app).toContain("../workspace/index.css");
    expect(workspace).toContain("showDocumentation = false");
    expect(workspace).toContain("Export Payload JSON");
    expect(workspace).not.toContain("https://cdn.tailwindcss.com");
    expect(sidebar).toContain("registryOptions");
    expect(sidebar).toContain('"Spec"');
    expect(styles).toContain('@import "tailwindcss"');
    expect(styles).not.toContain("fonts.googleapis");
  });

  it("keeps the legacy canvas export while the workspace owns the forward UI", () => {
    const readme = readFileSync(new URL("../README.md", import.meta.url), "utf-8");
    const workspaceCanvas = readFileSync(new URL("./workspace/components/LineageGraphCanvas.tsx", import.meta.url), "utf-8");
    const inspector = readFileSync(new URL("./workspace/components/RightInspector.tsx", import.meta.url), "utf-8");
    expect(readme).toContain("`LineageGraphApp` is the forward path");
    expect(readme).toContain("LineageGraph` canvas export remains available for compatibility");
    expect(workspaceCanvas).toContain("onPointerDown={handleWorkspacePointerDown}");
    expect(workspaceCanvas).toContain("onWheel={handleWheel}");
    expect(workspaceCanvas).toContain("FAMILY_COLORS");
    expect(inspector).toContain("Upstream Ancestors");
    expect(inspector).toContain("Downstream Relations");
  });

  it("allows zooming below one percent for very large graph extents", () => {
    const canvas = readFileSync(new URL("./components/LineageGraphCanvas.tsx", import.meta.url), "utf-8");
    expect(canvas).toContain("const MIN_ZOOM = 0.0001");
    expect(canvas).toContain("Math.max(MIN_ZOOM");
    expect(canvas).not.toContain("Math.max(0.02");
  });

  it("tiles dense workspace lanes instead of making skinny vertical ribbons", () => {
    const graph: WorkspaceLineagePayload = {
      nodes: Array.from({ length: 1376 }, (_, index) => ({
        id: `clm:dense.${index}`,
        family: "Claim",
        label: `Claim ${index}`,
      })),
      edges: [],
      summary: { nodeCount: 1376, edgeCount: 0 },
    };
    const indices = computeWorkspaceIndices(graph);
    const positions = computeWorkspaceLayout(graph.nodes, indices.incoming, indices.outgoing, new Set(), 210, 90, 1100, 620, "lineage");
    const xs = Object.values(positions).map((pos) => pos.x);
    const ys = Object.values(positions).map((pos) => pos.y);
    const width = Math.max(...xs) - Math.min(...xs);
    const height = Math.max(...ys) - Math.min(...ys);

    expect(width).toBeGreaterThan(1000);
    expect(height).toBeLessThan(6000);
  });

  it("bounds collapsed-ancestor checks when registry lineage contains an incoming cycle", () => {
    const incoming = new Map<string, string[]>([
      ["adr:0641", ["feat:graph.lineage-html-open-flag"]],
      ["feat:graph.lineage-html-open-flag", ["spec:lineage"]],
      ["spec:lineage", ["adr:0641"]],
    ]);

    expect(hasCollapsedUpstreamAncestor("adr:0641", incoming, new Set())).toBe(false);
    expect(hasCollapsedUpstreamAncestor("adr:0641", incoming, new Set(["spec:lineage"]))).toBe(true);
  });

  it("keeps full edge context available when node limits cap rendered nodes", () => {
    const workspace = readFileSync(new URL("./workspace/components/LineageGraphApp.tsx", import.meta.url), "utf-8");

    expect(workspace).toContain("nodes: displayNodes");
    expect(workspace).not.toContain("edges: payload.edges.filter");
    expect(workspace).toContain("computeDeterministicLayout(\n        payload.nodes");
  });
});
