import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";
import { familyClassName } from "./constants";
import { createStandaloneHtml } from "./html";
import { LineageGraph } from "./LineageGraph";
import { LineageGraphApp } from "./LineageGraphApp";
import { applyForceLayoutStep, applyLineageLayout, normalizeNodes, resolveDepth } from "./layout";
import type { LineagePayload } from "./types";

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

  it("keeps results scrollable and both rails collapsible", () => {
    const app = readFileSync(new URL("./views/LineageGraphAppView.tsx", import.meta.url), "utf-8");
    const section = readFileSync(new URL("./subcomponents/Section.tsx", import.meta.url), "utf-8");
    const results = readFileSync(new URL("./components/ResultsList.tsx", import.meta.url), "utf-8");
    const styles = readFileSync(new URL("./styles.css", import.meta.url), "utf-8");
    expect(app).toContain("leftSidebarCollapsed");
    expect(app).toContain("rightSidebarCollapsed");
    expect(app).toContain("ssot-sidebar-toggle-left");
    expect(app).toContain("ssot-sidebar-toggle-right");
    expect(app).toContain("collapsible");
    expect(results).toContain("ssot-results-list");
    expect(section).toContain("<details");
    expect(styles).toContain(".ssot-results-section");
    expect(styles).toContain(".ssot-accordion-section");
    expect(styles).toContain(".ssot-lineage-app-left-collapsed");
    expect(styles).toContain(".ssot-lineage-app-right-collapsed");
  });

  it("uses a selected-node card, right-side legend accordion, center zoom, and force controls", () => {
    const app = readFileSync(new URL("./views/LineageGraphAppView.tsx", import.meta.url), "utf-8");
    const selectedNode = readFileSync(new URL("./components/SelectedNodePanel.tsx", import.meta.url), "utf-8");
    const controls = readFileSync(new URL("./components/ViewControls.tsx", import.meta.url), "utf-8");
    const canvas = readFileSync(new URL("./components/LineageGraphCanvas.tsx", import.meta.url), "utf-8");
    const styles = readFileSync(new URL("./styles.css", import.meta.url), "utf-8");
    expect(selectedNode).toContain("ssot-selected-card");
    expect(selectedNode).not.toContain("KeyValue");
    expect(app.indexOf("rightSidebarClassName")).toBeLessThan(app.indexOf('title="Legend" collapsible'));
    expect(app.indexOf("<PackageSummary")).toBeLessThan(app.indexOf('title="View" collapsible'));
    expect(app).toContain('title="Families" collapsible');
    expect(app).toContain('title="Results" className="ssot-results-section" collapsible');
    expect(controls).toContain("Force Strength");
    expect(controls).toContain("Repulsion");
    expect(canvas).toContain("springStrength: options.forceStrength");
    expect(canvas).toContain("repulsionStrength: options.repulsionStrength");
    expect(canvas).toContain("const zoomBy");
    expect(canvas).toContain("centerX - worldX * zoom");
    expect(styles).toContain(".ssot-selected-card");
  });

  it("allows zooming below one percent for very large graph extents", () => {
    const canvas = readFileSync(new URL("./components/LineageGraphCanvas.tsx", import.meta.url), "utf-8");
    expect(canvas).toContain("const MIN_ZOOM = 0.0001");
    expect(canvas).toContain("Math.max(MIN_ZOOM");
    expect(canvas).not.toContain("Math.max(0.02");
  });
});
