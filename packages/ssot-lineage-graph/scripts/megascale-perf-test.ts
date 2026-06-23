/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import { performance } from "perf_hooks";
import { LineageNode, LineageEdge, LineageFamily, LineagePayload, Position } from "../src/types.js";
import { computeGraphIndices, traceSubGraph } from "../src/workspace/utils/graphHelpers.js";

// Beautiful terminal visual layout colors
const RESET = "\x1b[0m";
const BOLD = "\x1b[1m";
const GREEN = "\x1b[32m";
const CYAN = "\x1b[36m";
const YELLOW = "\x1b[33m";
const RED = "\x1b[31m";
const PURPLE = "\x1b[35m";
const GRAY = "\x1b[90m";

// Benchmark execution configuration
const STRESS_NODES_COUNT = 100_000;
const STRESS_EDGES_COUNT = 1_000_000;
const REPEATS = 5; // Measurements iterations for standard deviation calculation

interface TestSummary {
  name: string;
  durations: number[];
  averageMs: number;
  minMs: number;
  maxMs: number;
  opsPerSecond: number;
}

/**
 * Generate a highly dense, realistic lineage graph structure containing 100k nodes and 1M edges.
 * Arranges nodes across standard lineage columns: ADR -> SPEC -> Feature -> Claim -> Test -> Evidence -> Release
 */
function generateMegascaleData(nodeCount: number, edgeCount: number): { nodes: LineageNode[]; edges: LineageEdge[] } {
  const families: LineageFamily[] = ["ADR", "SPEC", "Feature", "Claim", "Test", "Evidence", "Release", "Boundary", "Profile", "Risk", "Issue"];

  console.log(`${GRAY}  Generating ${nodeCount.toLocaleString()} nodes...${RESET}`);
  const nodes: LineageNode[] = new Array(nodeCount);
  for (let i = 0; i < nodeCount; i++) {
    const family = families[i % families.length];
    nodes[i] = {
      id: `node-${i}`,
      family,
      title: `Megascale System Node ${i}`,
      summary: `Synthetic payload item supporting verification scale validations at index ${i}`,
      status: i % 10 === 0 ? "deprecated" : i % 5 === 0 ? "planned" : "active",
      tier: i % 3 === 0 ? "Tier 1" : i % 3 === 1 ? "Tier 2" : "Tier 3",
      validation: {
        status: i % 12 === 0 ? "fail" : i % 30 === 0 ? "warn" : "pass",
        issues: i % 12 === 0 ? ["Simulated megascale verification link fault"] : []
      }
    };
  }

  console.log(`${GRAY}  Connecting ${edgeCount.toLocaleString()} cross-column directed edges...${RESET}`);
  const edges: LineageEdge[] = new Array(edgeCount);
  for (let i = 0; i < edgeCount; i++) {
    // Connect nodes in proximity or progressive columns to represent realistic pipeline lineages
    const sourceIdx = i % nodeCount;
    // Create density by adding forward clusters
    const targetOffset = 1 + (Math.floor(i / nodeCount) + (i % 23)) % 100;
    const targetIdx = (sourceIdx + targetOffset) % nodeCount;

    edges[i] = {
      from: `node-${sourceIdx}`,
      to: `node-${targetIdx}`,
      type: i % 4 === 0 ? "verifies" : i % 4 === 1 ? "implements" : "depends_on",
      status: "active"
    };
  }

  return { nodes, edges };
}

/**
 * Generates Cartesian 2D positions for viewport bounds and layout calculations
 */
function generateMockPositions(nodes: LineageNode[]): Record<string, Position> {
  const positions: Record<string, Position> = {};
  nodes.forEach((n, idx) => {
    // Generate layout columns
    const colX = (idx % 10) * 400; // 10 columns
    const rowY = Math.floor(idx / 10) * 120; // layered grid row height
    positions[n.id] = {
      x: colX + (idx % 3) * 10,  // slight horizontal jitter
      y: rowY + (idx % 5) * 5,   // slight vertical jitter
    };
  });
  return positions;
}

/**
 * Execute a specific synchronous task multiple times and capture robust stats
 */
function benchmarkPhase(name: string, fn: () => void, iterations: number = REPEATS): TestSummary {
  // Warm up running iteration once
  fn();

  const durations: number[] = [];
  for (let i = 0; i < iterations; i++) {
    const start = performance.now();
    fn();
    const end = performance.now();
    durations.push(end - start);
  }

  const averageMs = durations.reduce((a, b) => a + b, 0) / durations.length;
  const minMs = Math.min(...durations);
  const maxMs = Math.max(...durations);
  const opsPerSecond = 1000 / (averageMs || 1);

  return {
    name,
    durations,
    averageMs,
    minMs,
    maxMs,
    opsPerSecond,
  };
}

function printStatsHeader() {
  console.log(`\n${BOLD}${CYAN}================================================================================${RESET}`);
  console.log(`    ${BOLD}${GREEN}MEGASCALE PERFORMANCE TEST SUITE${RESET} - Graph Data Integrity & Scale Benchmarks`);
  console.log(`    Scale Target: ${BOLD}${YELLOW}${STRESS_NODES_COUNT.toLocaleString()}${RESET} Nodes, ${BOLD}${YELLOW}${STRESS_EDGES_COUNT.toLocaleString()}${RESET} Edges`);
  console.log(`${BOLD}${CYAN}================================================================================${RESET}\n`);
}

function printSummaryTable(summaries: TestSummary[]) {
  console.log(`\n${BOLD}${CYAN}------------------------------- PERFORMANCE RESULTS SUMMARY -------------------------------${RESET}`);
  console.log(
    `${BOLD}${"BENCHMARK PHASE".padEnd(35)} | ${"AVERAGE TIME".padEnd(15)} | ${"THROUGHPUT (ops/sec)".padEnd(20)} | ${"MIN/MAX MS".padEnd(15)}${RESET}`
  );
  console.log(`${GRAY}-------------------------------------------------------------------------------------------${RESET}`);

  summaries.forEach((s) => {
    const avgStr = `${s.averageMs.toFixed(3)} ms`;
    const throughputStr = s.opsPerSecond >= 100000
      ? "Ultra-Fast (>100k)"
      : `${s.opsPerSecond.toFixed(2)} ops/sec`;
    const minMaxStr = `${s.minMs.toFixed(2)}/${s.maxMs.toFixed(2)}`;
    console.log(
      `${CYAN}${s.name.padEnd(35)}${RESET} | ${avgStr.padEnd(15)} | ${throughputStr.padEnd(20)} | ${minMaxStr.padEnd(15)}`
    );
  });
  console.log(`${GRAY}-------------------------------------------------------------------------------------------${RESET}\n`);
}

function runBenchmark() {
  printStatsHeader();

  const initialMemory = process.memoryUsage().heapUsed;

  // --- Phase 1: High Density Payload Gen ---
  console.log(`[Phase 1/5] ${BOLD}Generating Synthetic Megascale Graph...${RESET}`);
  const genStart = performance.now();
  const payload: LineagePayload = generateMegascaleData(STRESS_NODES_COUNT, STRESS_EDGES_COUNT);
  const genEnd = performance.now();
  const postGenMemory = process.memoryUsage().heapUsed;

  const genMemoryMb = (postGenMemory - initialMemory) / 1024 / 1024;
  console.log(`   ${GREEN}[OK] Generation Finished in ${(genEnd - genStart).toFixed(2)} ms${RESET}`);
  console.log(`   ${GREEN}[OK] Simulated Payload Active Heap Memory Growth: ${genMemoryMb.toFixed(2)} MB${RESET}\n`);

  // --- Phase 2: Index Construction Speed ---
  console.log(`[Phase 2/5] ${BOLD}Benchmarking Index Map Construction (computeGraphIndices)...${RESET}`);
  let primaryIndices: any = null;
  const indexSummary = benchmarkPhase("Index Compilation (computeGraphIndices)", () => {
    primaryIndices = computeGraphIndices(payload);
  });
  console.log(`   ${GREEN}[OK] Average time: ${indexSummary.averageMs.toFixed(2)} ms (${indexSummary.opsPerSecond.toFixed(2)} ops/sec)${RESET}`);
  console.log(`   ${GRAY}  - Compiled ${primaryIndices.nodeMap.size.toLocaleString()} nodes to Map lookups.${RESET}`);
  console.log(`   ${GRAY}  - Map indices size (outgoing/incoming): ${primaryIndices.outgoing.size.toLocaleString()} heads.${RESET}`);

  // --- Phase 3: Spatial Viewport Bounds Culling & Culling Rate ---
  console.log(`\n[Phase 3/5] ${BOLD}Creating coordinate layouts & benchmarking Spatial Viewport culling...${RESET}`);
  const positions = generateMockPositions(payload.nodes);

  // A typical viewport bounds search inside viewport (e.g. Canvas coordinate box)
  const bounds = {
    left: 2000,
    right: 3200,
    top: 5000,
    bottom: 9000
  };

  const cullSummary = benchmarkPhase("Spatial Bounds Culling (100k nodes)", () => {
    const nodesInViewport: string[] = [];
    // Iterate 100k positions to cull instantly
    const keys = Object.keys(positions);
    for (let i = 0; i < keys.length; i++) {
      const id = keys[i];
      const pos = positions[id];
      if (pos.x >= bounds.left && pos.x <= bounds.right && pos.y >= bounds.top && pos.y <= bounds.bottom) {
        nodesInViewport.push(id);
      }
    }
  });
  console.log(`   ${GREEN}[OK] Average Culling execution: ${cullSummary.averageMs.toFixed(3)} ms (${cullSummary.opsPerSecond.toFixed(1)} ops/sec)${RESET}`);

  // --- Phase 4: Full Ancestry and Dependency Upstream/Downstream relative Traversals ---
  console.log(`\n[Phase 4/5] ${BOLD}Benchmarking High-Throughput Sub-Graph Dependency Traversals...${RESET}`);

  // Pick some target nodes spread across the graph to trace their lineages
  const testNodeIds = ["node-5", "node-500", "node-12000", "node-45000", "node-85000"];
  const traversalSummary = benchmarkPhase("High-Throughput Sub-Graph Traversals", () => {
    testNodeIds.forEach((id) => {
      // Trace lineage with recursive depth=4 upstream & downstream
      traceSubGraph(id, primaryIndices.incoming, primaryIndices.outgoing, 4);
    });
  });
  console.log(`   ${GREEN}[OK] Average Trace (5 separate nodes, depth=4): ${traversalSummary.averageMs.toFixed(3)} ms (${traversalSummary.opsPerSecond.toFixed(2)} ops/sec)${RESET}`);

  // --- Phase 5: Recursive Collapsed Ancestry Detection (O(Depth) Traversal for Visibility Check) ---
  console.log(`\n[Phase 5/5] ${BOLD}Evaluating O(Depth) Recursive Collapsed Node Ancestry logic...${RESET}`);
  const mockCollapsedSet = new Set(["node-0", "node-200", "node-5000", "node-20000", "node-50000"]);

  // Check ancestral paths of nodes to check if any of their parents are collapsed (used by render pipelines)
  const hasCollapsedAncestorBenchmark = () => {
    let collapsedCheckHits = 0;
    // Iterate the entire node tree to find collapsed parents
    for (let i = 0; i < 1000; i++) { // Check ancestry of 1000 nodes randomly
      let currentId = `node-${i * 99}`; // distribute probes
      let visits = 0;
      while (currentId && visits < 10) {
        visits++;
        if (mockCollapsedSet.has(currentId)) {
          collapsedCheckHits++;
          break;
        }
        // fetch incoming parents
        const parents = primaryIndices.incoming.get(currentId);
        if (parents && parents.length > 0) {
          // move up to first parent
          currentId = parents[0];
        } else {
          break;
        }
      }
    }
    return collapsedCheckHits;
  };

  const collapseSummary = benchmarkPhase("Recursive Dependency Parent Resolution checks", () => {
    hasCollapsedAncestorBenchmark();
  });
  console.log(`   ${GREEN}[OK] Average Collapse Detection Resolution: ${collapseSummary.averageMs.toFixed(3)} ms (${collapseSummary.opsPerSecond.toFixed(2)} ops/sec)${RESET}`);

  // Print pretty graphical summary table
  printSummaryTable([
    indexSummary,
    cullSummary,
    traversalSummary,
    collapseSummary
  ]);

  // General evaluation verdict
  console.log(`${BOLD}[VERDICT] SYSTEM STRESS ASSESSMENT:${RESET}`);
  const overallAvg = indexSummary.averageMs + cullSummary.averageMs + traversalSummary.averageMs + collapseSummary.averageMs;
  if (overallAvg < 250) {
    console.log(`  ${BOLD}${GREEN}[HIGHLY CONVERSANT]${RESET} JavaScript heap and V8 compiler processed 100k nodes in under ${overallAvg.toFixed(1)}ms execution thread time! Highly responsive and capable of handling production payloads smoothly.`);
  } else if (overallAvg < 800) {
    console.log(`  ${BOLD}${YELLOW}[ACCEPTABLE PERFORMANCE]${RESET} Cumulative CPU block is ${overallAvg.toFixed(1)}ms. Recommend visual viewport downsampling or Web Worker encapsulation for ultra-smooth rendering.`);
  } else {
    console.log(`  ${BOLD}${RED}[DEGRADED PERFORMANCE]${RESET} Latency block exceeds ${overallAvg.toFixed(1)}ms. Needs visual debounce or IndexedDB offloading to maintain 60 FPS.`);
  }
}

// Invoke the benchmark
runBenchmark();
