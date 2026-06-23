/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import { LineagePayload, LineageNode, LineageEdge } from "../types";

// Helper to create basic metadata summary
function generateSummaries(nodes: LineageNode[], edges: LineageEdge[]) {
  const families: Record<string, number> = {};
  const statuses: Record<string, number> = {};
  const origins: Record<string, number> = {};
  const tiers: Record<string, number> = {};

  nodes.forEach((n) => {
    families[n.family] = (families[n.family] || 0) + 1;
    if (n.status) statuses[n.status] = (statuses[n.status] || 0) + 1;
    if (n.originKind) origins[n.originKind] = (origins[n.originKind] || 0) + 1;
    if (n.tier) tiers[n.tier] = (tiers[n.tier] || 0) + 1;
  });

  return {
    counts: {
      nodes: nodes.length,
      edges: edges.length,
      families,
      statuses,
      origins,
      tiers,
    },
    proof: {
      completeChains: nodes.filter((n) => n.family === "Claim" && n.proof?.completeness === 100).length,
      incompleteChains: nodes.filter((n) => n.family === "Claim" && (n.proof?.completeness ?? 0) < 100).length,
      blockedReleases: nodes.filter((n) => n.family === "Release" && n.proof?.releaseStatus === "blocked").length,
      missingEvidence: nodes.filter((n) => n.family === "Evidence" && n.proof?.evidenceStatus === "missing").length,
      missingTests: nodes.filter((n) => n.family === "Test" && n.proof?.testStatus === "missing").length,
    },
    packs: {
      governancePacks: 2,
      contractPacks: 1,
      extensionPacks: 1,
    },
    hotspots: [
      { nodeId: "claim:supports-offline-standalone", reason: "Multiple critical downstream tests dependent on single certificate", score: 85 },
      { nodeId: "spec:lineage-payload-v2", reason: "Highly connected hub representing specifications core format", score: 92 },
    ],
  };
}

// ==========================================
// DATASET 1: CANONICAL CORE SSOT REGISTRY (Demo Success Case)
// ==========================================
const coreNodes: LineageNode[] = [
  // ADRs
  {
    id: "adr:001-offline-portability",
    family: "ADR",
    label: "ADR-001: Offline Portability",
    title: "Offline Portability & Standalone Assemblies",
    summary: "Establishment of standalone offline-first browser executable graphs using embedded inline bundles.",
    description: "Requires that all components, visualization rendering logic, styles, and payloads reside within a single portable *.html file with no runtime external HTTP requests.",
    status: "active",
    tier: "T1",
    origin: "ssot-core-specs",
    originKind: "ssot-core",
    path: "docs/adr/001-offline-portability.md",
    lifecycle: { stage: "Accepted", state: "Implemented", promotedAt: "2026-01-10" },
    validation: { status: "pass", issues: [] },
    links: [
      { label: "View Markdown ADR", href: "https://github.com/ssot-registry/spec/adr/001", kind: "source" },
    ],
    proof: { completeness: 100 },
  },
  {
    id: "adr:002-deterministic-layering",
    family: "ADR",
    label: "ADR-002: Deterministic Lineage Layout",
    title: "Deterministic Hierarchical Family Layers",
    summary: "Standardizes strict genealogical hierarchy ordering across the registry.",
    description: "Forces horizontal layering in top-down node rank order: ADR -> Spec -> Feature -> Claim -> Test -> Evidence -> Release.",
    status: "active",
    tier: "T2",
    origin: "ssot-core-specs",
    originKind: "ssot-core",
    path: "docs/adr/002-deterministic-layering.md",
    lifecycle: { stage: "Accepted", state: "Implemented", promotedAt: "2026-02-15" },
    validation: { status: "pass", issues: [] },
  },

  // SPECIFICATON
  {
    id: "spec:lineage-payload-v2",
    family: "SPEC",
    label: "SPEC: Lineage Payload v2",
    title: "Lineage Payload JSON Schema Specifications",
    summary: "The schema layout containing metadata, validated nodes, connected edges, and aggregated summaries.",
    description: "Specifies strict typing contracts for nodes and edges, backing extensible compliance metadata, and ensuring backward compatibility with v1 layout parsers.",
    status: "active",
    tier: "T1",
    origin: "ssot-core-specs",
    originKind: "ssot-origin",
    path: "schema/lineage-v2.json",
    lifecycle: { stage: "Stable", state: "Active" },
    validation: { status: "pass", issues: [], lastCheckedAt: "2026-06-20" },
    packs: ["governance-pack:core-standard-v2"],
    links: [{ label: "Schema Spec Link", href: "https://ssot.dev/schemas/v2", kind: "docs" }],
  },

  // FEATURES
  {
    id: "feat:portable-lineage-export",
    family: "Feature",
    label: "Feat: Portable Canvas Exporter",
    title: "Standalone Portable Interactive Canvas Exporter",
    summary: "Compiler asset builder generating self-contained HTML reports.",
    description: "Compiles React tree bundle, embeds user registry payload safely, and triggers native HTML down-downloads.",
    status: "certified",
    tier: "T1",
    origin: "repo-local-impl",
    originKind: "repo-local",
    path: "packages/exporter/index.ts",
    tags: ["export", "offline", "cli"],
    governancePacks: ["core-standards"],
  },
  {
    id: "feat:top-down-engine",
    family: "Feature",
    label: "Feat: Deterministic Layout Engine",
    title: "Top-Down Columnar Layout Layout Engine",
    summary: "Renders nodes strictly partitioned into sequence-aligned lineage chains.",
    description: "Controls scaling coefficients, margins, ribbon line opacity, zoom level bindings under compact screen environments.",
    status: "certified",
    tier: "T2",
    origin: "repo-local-impl",
    originKind: "repo-local",
    path: "packages/viewer/layout.ts",
  },

  // CLAIMS
  {
    id: "claim:supports-offline-standalone",
    family: "Claim",
    label: "Claim: Zero-Network Portable Viewer",
    title: "Completely Offline Standalone Interactivity",
    summary: "Guarantees full interactive features, searching, filtering, and inspectors on standalone HTML.",
    description: "Asserts that when exporting via ssot CLI, the resulting HTML file needs zero remote assets. Previews run instantly inside isolated sandboxed web containers.",
    status: "active",
    tier: "T1",
    origin: "repo-local-impl",
    originKind: "repo-local",
    validation: { status: "pass" },
    proof: { claimTier: "Strict Compliance", testStatus: "passed", evidenceStatus: "signed", completeness: 100 },
  },
  {
    id: "claim:provable-visual-lineage",
    family: "Claim",
    label: "Claim: Provable Visual Link Chain",
    title: "Traceability of Decisions from ADR to Delivery",
    summary: "Assures visual validation of every claim's full connection list.",
    description: "Ensures no visual disconnected orphans can bypass certification checkpoints.",
    status: "active",
    tier: "T0",
    origin: "repo-local-impl",
    originKind: "repo-local",
    proof: { claimTier: "Standard Compliance", testStatus: "passed", evidenceStatus: "signed", completeness: 100 },
  },
  {
    id: "claim:high-performance-rendering",
    family: "Claim",
    label: "Claim: 60fps Real-time Layout Redraw",
    title: "High Performance Real-time Layout Rendering",
    summary: "Guarantees highly performant canvas drag interactions operating at 60 frames per second on heavy structures.",
    description: "Requires that adjacent coordinates and connecting SVG stroke curves draw fluidly under intensive rendering environments.",
    status: "active",
    tier: "T2",
    origin: "repo-local-impl",
    originKind: "repo-local",
    validation: { status: "pass" },
    proof: { claimTier: "Strict Compliance", testStatus: "passed", evidenceStatus: "signed", completeness: 100 },
  },
  {
    id: "claim:zero-telemetry-isolation",
    family: "Claim",
    label: "Claim: Zero-Telemetry Sandboxed Security",
    title: "Enforced Non-network Isolation Boundary",
    summary: "Ensures no external requests or tracking telemetries occur inside sandboxed browser tabs.",
    description: "Strict isolation audit preventing unauthorized call leakages and tracking signatures completely.",
    status: "active",
    tier: "T3",
    origin: "security-pack",
    originKind: "extension-pack",
    validation: { status: "pass" },
    proof: { claimTier: "Strict Compliance", testStatus: "passed", evidenceStatus: "signed", completeness: 100 },
  },

  // TESTS (Vitest / Pytest)
  {
    id: "test:standalone-integrity-checks",
    family: "Test",
    label: "Test: HTML Compiler Core Integrity",
    title: "Vitest Integrity Test Suites for Self-Contained Assets",
    summary: "Unit tests evaluating that HTML compiler asset injects the string cleanly.",
    description: "Performs script sanity tests, asserts CSS integrity, and validates JSON escape sequences in exported template files.",
    status: "active",
    tier: "T1",
    origin: "repo-local-impl",
    originKind: "repo-local",
    path: "packages/exporter/tests/export.test.ts",
    proof: { testStatus: "passed" },
  },
  {
    id: "test:layout-rank-alignment",
    family: "Test",
    label: "Test: Layout Rank Determination",
    title: "Layout Multi-tier Ranking Test Suites",
    summary: "Confirms nodes are allocated to standard columns correctly without overlap.",
    description: "Asserts hierarchy layout dimensions, coordinates bounding boxes, and detects overlap overlaps.",
    status: "active",
    tier: "T2",
    origin: "repo-local-impl",
    originKind: "repo-local",
    path: "packages/viewer/tests/layout.test.ts",
    proof: { testStatus: "passed" },
  },

  // EVIDENCE
  {
    id: "ev:standalone-html-hash-signatures",
    family: "Evidence",
    label: "Evidence: Build Hash SHA-256 Logs",
    title: "SHA-256 Compilation Build Checksum Signatures",
    summary: "A cryptographically signed hash index of standalone output builds.",
    description: "Verified during automated release cycles, checking template outputs against security limits and white-listed script references.",
    status: "active",
    tier: "T1",
    origin: "repo-local-impl",
    originKind: "repo-local",
    path: "dist/checksums.json",
    proof: { evidenceStatus: "signed" },
    links: [{ label: "Verify Build Signature", href: "https://checksums.ssot.dev/v2", kind: "external" }],
  },
  {
    id: "ev:visual-regression-artifacts",
    family: "Evidence",
    label: "Evidence: Visual Regression Backstop Docs",
    title: "Playwright Visual Snapshot Alignment Proofs",
    summary: "Visual alignment backstop test summaries validating SVG line paths.",
    description: "Captured snapshots matching top-down layout output against golden layout templates across all viewport breakpoints.",
    status: "active",
    tier: "T2",
    origin: "repo-local-impl",
    originKind: "repo-local",
    path: "packages/viewer/test-snapshots/lineage-desktop.png",
    proof: { evidenceStatus: "signed" },
  },

  // RELEASES
  {
    id: "rel:v2.0.0-gold-compliance",
    family: "Release",
    label: "Release: v2.0.0 (Certified)",
    title: "SSOT Compliance Release v2.0.0",
    summary: "The fully validated, certified, and compliant release of the SSOT workspace.",
    description: "Passes all core constraints. Contains complete proof chains tracing back to ADR-001 and ADR-002 requirements.",
    status: "certified",
    tier: "T1",
    origin: "release-registry",
    originKind: "repo-local",
    path: "releases/v2.0.0.json",
    lifecycle: { stage: "Release", state: "Published", certifiedAt: "2026-06-20", publishedAt: "2026-06-21" },
    validation: { status: "pass" },
    proof: { releaseStatus: "certified", completeness: 100 },
  },

  // BOUNDARY / PACKS
  {
    id: "bound:security-offline-perimeter",
    family: "Boundary",
    label: "Boundary: Zero-Trust Perimeter",
    title: "Zero-Network Sandboxed Client Perimeter",
    summary: "Boundary isolating browser views from any external telemetry trackers.",
    description: "Enforces that the workspace client never executes fetch calls or telemetry leaks to uncertified origins.",
    status: "active",
    tier: "T1",
    origin: "security-pack",
    originKind: "extension-pack",
  },
];

const coreEdges: LineageEdge[] = [
  // ADR to Spec
  { from: "adr:001-offline-portability", to: "spec:lineage-payload-v2", type: "defines", status: "active", originKind: "direct" },
  { from: "adr:002-deterministic-layering", to: "spec:lineage-payload-v2", type: "defines", status: "active", originKind: "direct" },

  // Spec to Features
  { from: "spec:lineage-payload-v2", to: "feat:portable-lineage-export", type: "implements", status: "active", originKind: "direct" },
  { from: "spec:lineage-payload-v2", to: "feat:top-down-engine", type: "implements", status: "active", originKind: "direct" },

  // Features to Claims
  { from: "feat:portable-lineage-export", to: "claim:supports-offline-standalone", type: "justifies", status: "active", originKind: "direct" },
  { from: "feat:top-down-engine", to: "claim:provable-visual-lineage", type: "justifies", status: "active", originKind: "direct" },
  { from: "feat:top-down-engine", to: "claim:high-performance-rendering", type: "justifies", status: "active", originKind: "direct" },

  // Claims to Tests
  { from: "claim:supports-offline-standalone", to: "test:standalone-integrity-checks", type: "verified_by", status: "active", originKind: "direct" },
  { from: "claim:provable-visual-lineage", to: "test:layout-rank-alignment", type: "verified_by", status: "active", originKind: "direct" },
  { from: "claim:high-performance-rendering", to: "test:layout-rank-alignment", type: "verified_by", status: "active", originKind: "direct" },

  // Tests to Evidence
  { from: "test:standalone-integrity-checks", to: "ev:standalone-html-hash-signatures", type: "proves", status: "active", originKind: "direct" },
  { from: "test:layout-rank-alignment", to: "ev:visual-regression-artifacts", type: "proves", status: "active", originKind: "direct" },

  // Evidence to Release
  { from: "ev:standalone-html-hash-signatures", to: "rel:v2.0.0-gold-compliance", type: "certifies", status: "active", originKind: "direct" },
  { from: "ev:visual-regression-artifacts", to: "rel:v2.0.0-gold-compliance", type: "certifies", status: "active", originKind: "direct" },

  // Boundaries & packs relationships
  { from: "bound:security-offline-perimeter", to: "claim:supports-offline-standalone", type: "governs", status: "active", originKind: "derived" },
  { from: "bound:security-offline-perimeter", to: "claim:zero-telemetry-isolation", type: "governs", status: "active", originKind: "derived" },
];

export const mockCoreRegistry: LineagePayload = {
  schemaVersion: "2.4.0",
  generatedAt: "2026-06-21T21:00:00-07:00",
  generator: {
    name: "ssot-core-compiler",
    version: "2.4.0",
    command: "ssot graph lineage . --output .ssot/graphs/registry.lineage.html",
  },
  registry: {
    path: "./.ssot/registry",
    repoRoot: "/workspace/ssot-repo",
    schemaVersion: "2.4.0",
    validationStatus: "valid",
  },
  package: {
    id: "packages/ssot-lineage-graph",
    name: "@ssot-registry/lineage-graph",
    version: "2.4.0",
    kind: "React Widget Library",
    repositoryUrl: "https://github.com/ssot-registry/lineage-graph",
    canonicalUrl: "https://ssot.dev/packages/lineage-graph",
  },
  nodes: coreNodes,
  edges: coreEdges,
  groups: [
    {
      id: "group:offline-capabilities",
      kind: "boundary",
      label: "Zero-Network Standalone Target",
      nodeIds: ["adr:001-offline-portability", "spec:lineage-payload-v2", "feat:portable-lineage-export", "claim:supports-offline-standalone", "test:standalone-integrity-checks", "ev:standalone-html-hash-signatures"],
      summary: "Contains all elements guaranteeing full offline operations.",
    },
    {
      id: "group:layout-and-lineage",
      kind: "boundary",
      label: "Top-Down Presentation Target",
      nodeIds: ["adr:002-deterministic-layering", "feat:top-down-engine", "claim:provable-visual-lineage", "test:layout-rank-alignment", "ev:visual-regression-artifacts"],
      summary: "Contains elements standardizing horizontal family layers.",
    },
  ],
  summaries: generateSummaries(coreNodes, coreEdges),
};


// ==========================================
// DATASET 2: VALIDATION DRIFT & BLOCKED RELEASE SCENARIO
// ==========================================
// This dataset represents a realistic failure state!
// It is incredibly instructive for developers and compliance managers.
const driftNodes: LineageNode[] = [
  {
    id: "adr:004-dynamic-reposition",
    family: "ADR",
    label: "ADR-004: Interactive Repositioning",
    title: "User-initiated Canvas Node Drag and Repositioning",
    summary: "Permit manual click-and-drag coordinates saving in local browsers.",
    description: "Ensures heavy layout clutter can be cleared up by hand, storing the new x/y parameters permanently inside local viewport cache states.",
    status: "active",
    tier: "T2",
    origin: "repo-local-specs",
    originKind: "repo-local",
    validation: { status: "pass" },
  },
  {
    id: "spec:canvas-interaction-v1",
    family: "SPEC",
    label: "SPEC: Drag & Drop Contract",
    title: "Interactive Canvas Pan Zoom Spec Schema",
    summary: "Details mouse and touch interactive coordinate updates.",
    status: "active",
    tier: "T2",
    origin: "repo-local-impl",
    originKind: "repo-local",
    validation: { status: "pass" },
  },
  {
    id: "feat:canvas-drag-and-drop",
    family: "Feature",
    label: "Feat: Desktop Node Dragger",
    title: "Interactive Drag-and-Drop Node Repositions",
    summary: "Binds mouse gestures to coordinate positions in state machines.",
    description: "Uses standard pointer events with Framer Motion triggers to recalculate adjacent connection curves relative to drag actions.",
    status: "experimental",
    tier: "T2",
    origin: "repo-local-impl",
    originKind: "generated",
    path: "packages/viewer/drag.ts",
    validation: { status: "pass" },
  },
  {
    id: "claim:drag-any-node-fluidly",
    family: "Claim",
    label: "Claim: Fluid 60fps Free Positioning",
    title: "Draggable Nodes Redraw Connection Line Curves Smoothly",
    summary: "Requires adjacent coordinates recalculate at high performance during drags.",
    description: "Allows rendering to occur at 60fps without choking or causing browser lock-ups on multiple layers.",
    status: "active",
    tier: "T2",
    origin: "repo-local-impl",
    originKind: "repo-local",
    validation: {
      status: "warn",
      issues: ["Linked tests have pending/failing statuses", "Missing evidence document approval hash"],
    },
    proof: { claimTier: "Strict Compliance", testStatus: "failed", evidenceStatus: "missing", completeness: 40 },
  },
  {
    id: "test:pointer-drag-velocity",
    family: "Test",
    label: "Test: Drag Velocity & FPS benchmarks",
    title: "Benchmarking FPS Refresh Redraw Cadence during Gesture Hold",
    summary: "Ensures UI transitions remain high speed on 4K resolutions.",
    description: "Runs simulations pushing 800 parallel nodes. Fails if average framerate logs dip under 45 FPS.",
    status: "deprecated",
    tier: "T3",
    origin: "repo-local-impl",
    originKind: "generated",
    path: "packages/viewer/tests/fps-drag.test.ts",
    validation: { status: "fail", issues: ["Test suite execution timed out consistently after 5000ms"] },
    proof: { testStatus: "failed" },
  },
  {
    id: "ev:fps-benchmark-audit-logs",
    family: "Evidence",
    label: "Evidence: Performance Check Logs",
    title: "FPS Stress Benchmarking Performance Execution Logs",
    summary: "Automated output logs verifying average ticks per frame.",
    description: "MISSING/STALE! The test is currently disabled in continuous integration pipelines due to local GPU rendering timeouts.",
    status: "unverified",
    tier: "T3",
    origin: "ci-logs",
    originKind: "unknown",
    validation: { status: "fail", issues: ["File not found at configured repository path: packages/viewer/build/fps-audit.log"] },
    proof: { evidenceStatus: "missing" },
  },
  {
    id: "rel:v2.1.0-unstable-drag",
    family: "Release",
    label: "Release: v2.1.0-beta (Blocked)",
    title: "SSOT Unstable Interactivity Release v2.1.0-beta",
    summary: "A milestone release planned to ship the canvas repositioning package.",
    description: "RELEASE BLOCKED! Contains failing integrity benchmarks and incomplete path validations.",
    status: "experimental",
    tier: "T2",
    origin: "release-registry",
    originKind: "repo-local",
    path: "releases/v2.1.0-beta.json",
    lifecycle: { stage: "Pre-release", state: "Blocked" },
    validation: {
      status: "fail",
      issues: [
        "Blocker issue: Blocker #703 is active inside client workspace",
        "At-Risk Proof Chain: claim:drag-any-node-fluidly lacks validated Test outcomes",
        "Evidence drift: ev:fps-benchmark-audit-logs is missing signed digests",
      ],
    },
    proof: { releaseStatus: "blocked", completeness: 55 },
  },
  {
    id: "issue:fps-drop-on-safari",
    family: "Issue",
    label: "Issue #703: Safari Redraw Choke",
    title: "Issue #703: CSS border-radius composite clips cause repaint loops",
    summary: "Critical visual lag observed on Safari 17.2 when dragging rounded circular svg groups.",
    description: "Causes catastrophic render loop painting overhead. Classified as a critical release blocker for T2 claims.",
    status: "active",
    tier: "T1",
    origin: "github-issues",
    originKind: "repo-local",
    validation: { status: "warn", issues: ["Active issue marked as Block-Release"] },
    metrics: { blockerCount: 1 },
  },
  {
    id: "risk:uncapped-drag-bounds",
    family: "Risk",
    label: "Risk: Viewport Coordinate Escape",
    title: "Nodes Dragged Out of Infinite Canvas Bounds",
    summary: "Allows items to escape bounding boxes, resulting in orphan positions.",
    description: "No boundary restraint exists on current canvas dragging coordinate calculation formulas, leading to missing node visual glitches.",
    status: "active",
    tier: "T2",
    origin: "repo-local-yaml",
    originKind: "repo-local",
  },
];

const driftEdges: LineageEdge[] = [
  { from: "adr:004-dynamic-reposition", to: "spec:canvas-interaction-v1", type: "defines", status: "active", originKind: "direct" },
  { from: "spec:canvas-interaction-v1", to: "feat:canvas-drag-and-drop", type: "implements", status: "active", originKind: "direct" },
  { from: "feat:canvas-drag-and-drop", to: "claim:drag-any-node-fluidly", type: "justifies", status: "active", originKind: "direct" },

  // STALE / FAILING LINK
  {
    from: "claim:drag-any-node-fluidly",
    to: "test:pointer-drag-velocity",
    type: "verified_by",
    status: "stale",
    originKind: "direct",
    proof: { required: true, satisfied: false, blocker: true, reason: "Speed benchmark tests are failing execution constraints" },
  },
  {
    from: "test:pointer-drag-velocity",
    to: "ev:fps-benchmark-audit-logs",
    type: "proves",
    status: "stale",
    originKind: "direct",
    proof: { required: true, satisfied: false, blocker: true, reason: "Evidence log file is missing or contains corrupt digest matching" },
  },

  // BLOCKED release link
  {
    from: "ev:fps-benchmark-audit-logs",
    to: "rel:v2.1.0-unstable-drag",
    type: "certifies",
    status: "missing",
    originKind: "inferred",
    proof: { required: true, satisfied: false, blocker: true, reason: "Release-blocking check failed: Missing signed performance verification" },
  },

  // Concerns
  { from: "issue:fps-drop-on-safari", to: "rel:v2.1.0-unstable-drag", type: "blocks", status: "active", originKind: "direct", proof: { blocker: true } },
  { from: "risk:uncapped-drag-bounds", to: "feat:canvas-drag-and-drop", type: "threatens", status: "active", originKind: "direct" },
];

export const mockDriftRegistry: LineagePayload = {
  schemaVersion: "2.4.0",
  generatedAt: "2026-06-21T22:15:00-07:00",
  generator: {
    name: "ssot-core-compiler",
    version: "2.4.0",
    command: "ssot graph lineage . --output .ssot/graphs/registry.lineage.html",
  },
  registry: {
    path: "./.ssot/registry",
    repoRoot: "/workspace/ssot-repo-drift",
    schemaVersion: "2.4.0",
    validationStatus: "invalid",
  },
  package: {
    id: "packages/ssot-lineage-graph",
    name: "@ssot-registry/lineage-graph",
    version: "2.4.1-beta",
    kind: "React Widget Library",
    repositoryUrl: "https://github.com/ssot-registry/lineage-graph",
  },
  nodes: driftNodes,
  edges: driftEdges,
  summaries: generateSummaries(driftNodes, driftEdges),
};


// ==========================================
// DATASET 3: LARGE-SCALE COMPACT PORTFOLIO REGISTRY (100+ nodes)
// ==========================================
// Generates a clean procedural tree/network with 105 total elements
// designed for visual stress testing and smooth performance layout checks.
export function createLargeRegistry(): LineagePayload {
  const nodes: LineageNode[] = [];
  const edges: LineageEdge[] = [];

  // 4 Core ADRs
  for (let i = 1; i <= 6; i++) {
    nodes.push({
      id: `adr:00${i}-large-arch`,
      family: "ADR",
      label: `ADR-00${i}: Core Architecture Specification`,
      title: `Decisions Policy and Design Standard ${i}`,
      summary: `Defines critical systemic constraints on micro-assembly standard layer ${i}.`,
      description: `In-depth requirement contract and governance mandates layout guidelines. Ensures compliance is mathematically provable.`,
      status: "active",
      tier: "T1",
      origin: "upstream-standards-pack",
      originKind: i % 2 === 0 ? "ssot-origin" : "ssot-core",
      validation: { status: "pass" },
    });
  }

  // 10 SPECS
  for (let s = 1; s <= 10; s++) {
    const parentAdr = `adr:00${(s % 6) + 1}-large-arch`;
    nodes.push({
      id: `spec:api-contract-s${s}`,
      family: "SPEC",
      label: `SPEC: API Contract Layer ${s}`,
      title: `SSOT Registry JSON Contract Spec ${s}`,
      summary: `Specification endpoints model defining contract structures for schema v${s}.`,
      status: "active",
      tier: "T1",
      origin: "extension-pack-iso26262",
      originKind: "extension-pack",
      validation: { status: "pass" },
    });
    // Edge
    edges.push({
      from: parentAdr,
      to: `spec:api-contract-s${s}`,
      type: "defines",
      status: "active",
    });
  }

  // 20 Features
  for (let f = 1; f <= 20; f++) {
    const parentSpec = `spec:api-contract-s${(f % 10) + 1}`;
    nodes.push({
      id: `feat:functional-module-f${f}`,
      family: "Feature",
      label: `Feat: Modular System Controller ${f}`,
      title: `SSOT Orchestrated Functional Module Component ${f}`,
      summary: `Provides atomic component feature services in pipeline category ${f}.`,
      status: f % 4 === 0 ? "experimental" : "certified",
      tier: "T2",
      origin: f % 2 === 0 ? "local-development" : "ssot-pack-provider",
      originKind: f % 2 === 0 ? "repo-local" : "extension-pack",
    });
    edges.push({
      from: parentSpec,
      to: `feat:functional-module-f${f}`,
      type: "implements",
      status: "active",
    });
  }

  // 20 Claims
  for (let c = 1; c <= 20; c++) {
    const parentFeat = `feat:functional-module-f${c}`;
    nodes.push({
      id: `claim:operational-guarantee-c${c}`,
      family: "Claim",
      label: `Claim: Guaranteed SLA Integrity ${c}`,
      title: `Verified Governance Claim Assertion Statement ${c}`,
      summary: `Strict architectural check checking that no unauthorized calls breach perimeter boundary ${c}.`,
      status: "active",
      tier: `T${c % 4}`,
      originKind: "repo-local",
      proof: {
        claimTier: "Standard Compliance",
        testStatus: c % 7 === 0 ? "failed" : "passed",
        evidenceStatus: c % 8 === 0 ? "missing" : "signed",
        completeness: c % 7 === 0 ? 30 : 100,
      },
    });
    edges.push({
      from: parentFeat,
      to: `claim:operational-guarantee-c${c}`,
      type: "justifies",
      status: "active",
    });
  }

  // 20 Tests
  for (let t = 1; t <= 20; t++) {
    const parentClaim = `claim:operational-guarantee-c${t}`;
    nodes.push({
      id: `test:verification-suite-t${t}`,
      family: "Test",
      label: `Test: Suite Validation Execution ${t}`,
      title: `Unit Test Runner Benchmark Assertion Profile ${t}`,
      summary: `Executes verification tests matching criteria mapping #10${t} checks.`,
      status: "active",
      tier: "T2",
      originKind: "repo-local",
      proof: { testStatus: t % 7 === 0 ? "failed" : "passed" },
    });
    edges.push({
      from: parentClaim,
      to: `test:verification-suite-t${t}`,
      type: "verified_by",
      status: t % 7 === 0 ? "stale" : "active",
    });
  }

  // 20 Evidences
  for (let e = 1; e <= 20; e++) {
    const parentTest = `test:verification-suite-t${e}`;
    nodes.push({
      id: `ev:compliance-digest-e${e}`,
      family: "Evidence",
      label: `Evidence: Signed Cryptographic Stamp ${e}`,
      title: `CI Build Audit Ledger Hash Certificate Output ${e}`,
      summary: `Cryptographic digest recorded in remote verification servers.`,
      status: "active",
      tier: "T1",
      originKind: "generated",
      proof: { evidenceStatus: e % 8 === 0 ? "missing" : "signed" },
    });
    edges.push({
      from: parentTest,
      to: `ev:compliance-digest-e${e}`,
      type: "proves",
      status: e % 8 === 0 ? "missing" : "active",
    });
  }

  // 4 Releases
  for (let r = 1; r <= 4; r++) {
    nodes.push({
      id: `rel:version-v${r}.0-gold`,
      family: "Release",
      label: `Release: Production Version v${r}.0-stable`,
      title: `SSOT Certified Mainline Compliance Milestone Version v${r}.0`,
      summary: `Official certified workspace release. Matches ISO compliance guidelines.`,
      status: r === 4 ? "experimental" : "certified",
      tier: "T1",
      originKind: "repo-local",
      path: `releases/v${r}.0.0.json`,
      proof: {
        completeness: r === 4 ? 80 : 100,
        releaseStatus: r === 4 ? "pending" : "certified",
      },
    });

    // Link the last 5 evidence files to this release
    const evOffset = (r - 1) * 5;
    for (let re = 1; re <= 5; re++) {
      const prevEv = `ev:compliance-digest-e${evOffset + re}`;
      edges.push({
        from: prevEv,
        to: `rel:version-v${r}.0-gold`,
        type: "certifies",
        status: "active",
      });
    }
  }

  return {
    schemaVersion: "2.4.0",
    generatedAt: "2026-06-21T23:30:00-07:00",
    generator: {
      name: "ssot-load-tester",
      version: "2.4.0",
      command: "ssot graph export --sample large-compliance-model",
    },
    registry: {
      path: "./.ssot/stress-test",
      repoRoot: "/workspace/ssot-large-stress-repo",
      schemaVersion: "2.4.0",
      validationStatus: "valid",
    },
    package: {
      id: "packages/ssot-enterprise-graph",
      name: "@ssot-enterprise/monorepo-registry",
      version: "1.0.0-gold",
      kind: "Corporate Infrastructure Workspace",
    },
    nodes,
    edges,
    summaries: generateSummaries(nodes, edges),
  };
}

// ==========================================
// DATASET 3: HYPER_SCALE COMPLIANCE STRESS_TEST (1,300+ NODES, 1,500+ EDGES)
// ==========================================
export function createSuperLargeRegistry(): LineagePayload {
  const nodes: LineageNode[] = [];
  const edges: LineageEdge[] = [];

  // 1. 30 Architecture Decision Records (ADRs)
  for (let i = 1; i <= 30; i++) {
    nodes.push({
      id: `adr:00${i}-hyper-scale`,
      family: "ADR",
      label: `ADR-0${i}: Global System Architecture Spec`,
      title: `Corporate Governance Standard Decision ${i}`,
      summary: `Decisions and architectural standards under global policy section ${i}.`,
      description: `Establishes strict mathematical validation rules and structure constraints for subsystem section ${i}.`,
      status: "active",
      tier: "T1",
      origin: "corporate-standards-suite",
      originKind: i % 2 === 0 ? "ssot-origin" : "ssot-core",
      validation: { status: "pass" },
    });
  }

  // 2. 100 Specifications
  for (let s = 1; s <= 100; s++) {
    const parentAdr = `adr:00${(s % 30) + 1}-hyper-scale`;
    nodes.push({
      id: `spec:hyper-api-contract-s${s}`,
      family: "SPEC",
      label: `SPEC: API Contract v${s}`,
      title: `Service Endpoints Specification Document ${s}`,
      summary: `Details strict structural request/response validation schema contracts.`,
      status: "active",
      tier: "T1",
      origin: "compliance-pack-iso26262",
      originKind: "extension-pack",
      validation: { status: "pass" },
    });
    // Edge
    edges.push({
      from: parentAdr,
      to: `spec:hyper-api-contract-s${s}`,
      type: "defines",
      status: "active",
    });
  }

  // 3. 250 Features
  for (let f = 1; f <= 250; f++) {
    const parentSpec = `spec:hyper-api-contract-s${(f % 100) + 1}`;
    nodes.push({
      id: `feat:hyper-module-f${f}`,
      family: "Feature",
      label: `Feat: Micro-Controller ${f}`,
      title: `Orchestrated Pipeline Control Feature Component ${f}`,
      summary: `Durable stateful processor element responsible for execution path category ${f}.`,
      status: f % 12 === 0 ? "experimental" : "certified",
      tier: "T2",
      origin: "system-local-repositories",
      originKind: "repo-local",
    });
    // Edge
    edges.push({
      from: parentSpec,
      to: `feat:hyper-module-f${f}`,
      type: "implements",
      status: "active",
    });
  }

  // 4. 300 Claims
  for (let c = 1; c <= 300; c++) {
    const parentFeat = `feat:hyper-module-f${(c % 250) + 1}`;
    const claimPass = c % 45 !== 0;
    nodes.push({
      id: `claim:hyper-guarantee-c${c}`,
      family: "Claim",
      label: `Claim: SLA Target SLA-${c}`,
      title: `Corporate Compliance Security SLA Claim Statement ${c}`,
      summary: `Secures data processing isolation boundary constraints in subsystem section ${c}.`,
      status: "active",
      tier: `T${(c % 4) + 1}`,
      originKind: "repo-local",
      proof: {
        claimTier: "High Core Assurance",
        testStatus: claimPass ? "passed" : "failed",
        evidenceStatus: c % 50 === 0 ? "missing" : "signed",
        completeness: claimPass ? 100 : 45,
      },
    });
    // Edge
    edges.push({
      from: parentFeat,
      to: `claim:hyper-guarantee-c${c}`,
      type: "justifies",
      status: "active",
    });
  }

  // 5. 300 Validation Test Suites
  for (let t = 1; t <= 300; t++) {
    const parentClaim = `claim:hyper-guarantee-c${t}`;
    const testStatus = t % 45 === 0 ? "failed" : "passed";
    nodes.push({
      id: `test:hyper-test-suite-t${t}`,
      family: "Test",
      label: `Test: Automated Assertions #20${t}`,
      title: `CI Runner Regression Test Assertion Execution Bundle ${t}`,
      summary: `Automates compliance assertion tests on state transitions matching scenario #${t}.`,
      status: "active",
      tier: "T2",
      originKind: "repo-local",
      proof: { testStatus },
    });
    // Edge
    edges.push({
      from: parentClaim,
      to: `test:hyper-test-suite-t${t}`,
      type: "verified_by",
      status: testStatus === "failed" ? "stale" : "active",
    });
  }

  // 6. 300 Signed Evidences
  for (let e = 1; e <= 300; e++) {
    const parentTest = `test:hyper-test-suite-t${e}`;
    const evidenceMissing = e % 50 === 0;
    nodes.push({
      id: `ev:hyper-digest-e${e}`,
      family: "Evidence",
      label: `Evidence: Cryptographic Ledger Stamp ${e}`,
      title: `CI Pipeline Vault Notary Audit Log Hash ${e}`,
      summary: `Unmodifiable secure verification payload registered in cloud telemetry servers.`,
      status: "active",
      tier: "T1",
      originKind: "generated",
      proof: { evidenceStatus: evidenceMissing ? "missing" : "signed" },
    });
    // Edge
    edges.push({
      from: parentTest,
      to: `ev:hyper-digest-e${e}`,
      type: "proves",
      status: evidenceMissing ? "missing" : "active",
    });
  }

  // 7. 20 Production Releases
  for (let r = 1; r <= 20; r++) {
    const isPending = r === 20;
    nodes.push({
      id: `rel:hyper-version-v${r}.0`,
      family: "Release",
      label: `Release: Production v${r}.0-stable`,
      title: `SSOT Certified Mainline Milestone Release Version v${r}.0`,
      summary: `Mainline release certifying ISO guidelines compliance for global region ${r}.`,
      status: isPending ? "experimental" : "certified",
      tier: "T1",
      originKind: "repo-local",
      path: `releases/v${r}.0.0-final.json`,
      proof: {
        completeness: isPending ? 72 : 100,
        releaseStatus: isPending ? "pending" : "certified",
      },
    });

    // Link a slice of 10 evidence stamps to each release milestone (200 links total)
    const evStart = (r - 1) * 10;
    for (let re = 1; re <= 10; re++) {
      const prevEv = `ev:hyper-digest-e${evStart + re}`;
      edges.push({
        from: prevEv,
        to: `rel:hyper-version-v${r}.0`,
        type: "certifies",
        status: "active",
      });
    }
  }

  return {
    schemaVersion: "3.2.0",
    generatedAt: "2026-06-22T00:15:00-07:00",
    generator: {
      name: "ssot-hyper-scale-load-tester",
      version: "3.2.0",
      command: "ssot graph export --sample hyper-massive-compliance-model",
    },
    registry: {
      path: "./.ssot/hyper-scale",
      repoRoot: "/workspace/ssot-massive-enterprise-monorepo",
      schemaVersion: "3.2.0",
      validationStatus: "valid",
    },
    package: {
      id: "packages/ssot-massive-enterprise-graph",
      name: "@ssot-enterprise/massive-registry",
      version: "3.0.0-release",
      kind: "Corporate HyperScale Monorepo Infrastructure",
    },
    nodes,
    edges,
    summaries: generateSummaries(nodes, edges),
  };
}

// ==========================================
// DATASET 4: MEGASCALE CORE STRESS TEST (100k+ NODES, 1M+ EDGES)
// ==========================================
export function createMegaScaleRegistry(): LineagePayload {
  const nodes: LineageNode[] = [];
  const edges: LineageEdge[] = [];

  const numADR = 10000;
  const numSPEC = 15000;
  const numFeat = 30000;
  const numClaim = 25000;
  const numTest = 10000;
  const numEv = 10000;
  const numRel = 500;

  // 1. Generate ADRs (T1)
  for (let i = 1; i <= numADR; i++) {
    nodes.push({
      id: `adr:mega-${i}`,
      family: "ADR",
      label: `ADR-${i}: Architecture Decision`,
      title: `System Design Mandate Statement #${i}`,
      summary: `SSOT specification governance regulations under design module category id ${i}.`,
      status: "active",
      tier: "T1",
      originKind: "ssot-core",
    });
  }

  // 2. Generate SPECs
  for (let i = 1; i <= numSPEC; i++) {
    nodes.push({
      id: `spec:mega-${i}`,
      family: "SPEC",
      label: `SPEC: Component Contract v${i}`,
      title: `RESTful Interface Protocol Definition Statement ${i}`,
      summary: `Describes serialization layers, data mapping structures, and downstream execution limits.`,
      status: "active",
      tier: "T1",
      originKind: "extension-pack",
    });
  }

  // 3. Generate Features
  for (let i = 1; i <= numFeat; i++) {
    nodes.push({
      id: `feat:mega-${i}`,
      family: "Feature",
      label: `Feat: Module Unit ${i}`,
      title: `Orchestrated Pipeline Execution Worker Runner component #${i}`,
      summary: `Maintains sub-second execution threads, high concurrency pools, and reliable local logging paths.`,
      status: "certified",
      tier: "T2",
      originKind: "repo-local",
    });
  }

  // 4. Generate Claims
  for (let i = 1; i <= numClaim; i++) {
    nodes.push({
      id: `claim:mega-${i}`,
      family: "Claim",
      label: `Claim: Isolation SLA Target #${i}`,
      title: `Security Compliance Isolation SLA Clause Requirement Statement #${i}`,
      summary: `Enforces strict boundaries, sandbox variables, and secure token checks in database row levels.`,
      status: "active",
      tier: "T3",
      originKind: "repo-local",
      proof: {
        claimTier: "High Core Assurance",
        testStatus: i % 230 === 0 ? "failed" : "passed",
        evidenceStatus: i % 550 === 0 ? "missing" : "signed",
        completeness: i % 230 === 0 ? 45 : 100,
      },
    });
  }

  // 5. Generate Tests
  for (let i = 1; i <= numTest; i++) {
    nodes.push({
      id: `test:mega-${i}`,
      family: "Test",
      label: `Test: Suite Regression #${i}`,
      title: `Automated Pipeline Regression Verification Runner Group #${i}`,
      summary: `Verifies data integrity across parallel stream batches under extreme load states.`,
      status: "active",
      tier: "T3",
      originKind: "repo-local",
    });
  }

  // 6. Generate Evidences
  for (let i = 1; i <= numEv; i++) {
    nodes.push({
      id: `ev:mega-${i}`,
      family: "Evidence",
      label: `Evidence: Hash Seal Log v${i}`,
      title: `Unmodifiable Cryptographic Ledger Verification Stamp ${i}`,
      summary: `Signed by pipeline authority vault during execution checklist confirmation steps.`,
      status: "active",
      tier: "T1",
      originKind: "generated",
    });
  }

  // 7. Generate Releases
  for (let i = 1; i <= numRel; i++) {
    nodes.push({
      id: `rel:mega-${i}`,
      family: "Release",
      label: `Release: Prod Milestone Version v${i}.0`,
      title: `Monorepo Mainline Master Branch Milestone Version v${i}.0`,
      summary: `Officially tagged build and certified release container running in production zones.`,
      status: "certified",
      tier: "T1",
      originKind: "repo-local",
    });
  }

  // Define structured, highly connected backbones (90.5k edges total)

  // 1. SPEC to ADR links (15k)
  for (let i = 1; i <= numSPEC; i++) {
    edges.push({
      from: `adr:mega-${(i % numADR) + 1}`,
      to: `spec:mega-${i}`,
      type: "defines",
      status: "active",
    });
  }

  // 2. Feature to SPEC links (30k)
  for (let i = 1; i <= numFeat; i++) {
    edges.push({
      from: `spec:mega-${(i % numSPEC) + 1}`,
      to: `feat:mega-${i}`,
      type: "implements",
      status: "active",
    });
  }

  // 3. Claim to Feature links (25k)
  for (let i = 1; i <= numClaim; i++) {
    edges.push({
      from: `feat:mega-${(i % numFeat) + 1}`,
      to: `claim:mega-${i}`,
      type: "justifies",
      status: "active",
    });
  }

  // 4. Test to Claim links (10k)
  for (let i = 1; i <= numTest; i++) {
    edges.push({
      from: `claim:mega-${(i % numClaim) + 1}`,
      to: `test:mega-${i}`,
      type: "verified_by",
      status: "active",
    });
  }

  // 5. Evidence to Test links (10k)
  for (let i = 1; i <= numEv; i++) {
    edges.push({
      from: `test:mega-${(i % numTest) + 1}`,
      to: `ev:mega-${i}`,
      type: "proves",
      status: "active",
    });
  }

  // 6. Release milestones (500)
  for (let i = 1; i <= numRel; i++) {
    edges.push({
      from: `ev:mega-${(i % numEv) + 1}`,
      to: `rel:mega-${i}`,
      type: "certifies",
      status: "active",
    });
  }

  // Generate dense cross-cutting connectivity to make exactly 1,000,000 edges
  const currentEdgeCount = edges.length;
  const targetEdgeCount = 1000000;
  const gap = targetEdgeCount - currentEdgeCount;

  for (let step = 0; step < gap; step++) {
    const selector = step % 3;
    if (selector === 0) {
      const featA = (step % numFeat) + 1;
      const featB = ((step + 123) % numFeat) + 1;
      edges.push({
        from: `feat:mega-${featA}`,
        to: `feat:mega-${featB}`,
        type: "depends_on",
        status: "active",
      });
    } else if (selector === 1) {
      const testId = (step % numTest) + 1;
      const featId = ((step + 456) % numFeat) + 1;
      edges.push({
        from: `feat:mega-${featId}`,
        to: `test:mega-${testId}`,
        type: "verified_by",
        status: "active",
      });
    } else {
      const claimId = (step % numClaim) + 1;
      const adrId = ((step + 789) % numADR) + 1;
      edges.push({
        from: `adr:mega-${adrId}`,
        to: `claim:mega-${claimId}`,
        type: "justifies",
        status: "active",
      });
    }
  }

  return {
    schemaVersion: "3.2.0",
    generatedAt: "2026-06-22T01:00:00-07:00",
    generator: {
      name: "ssot-megascale-stresstester",
      version: "3.2.0",
      command: "ssot graph export --sample massive-enterprise-megascale",
    },
    registry: {
      path: "./.ssot/megascale",
      repoRoot: "/workspace/ssot-enterprise-megascale-monorepo",
      schemaVersion: "3.2.0",
      validationStatus: "valid",
    },
    package: {
      id: "packages/ssot-enterprise-megascale-graph",
      name: "@ssot-enterprise/megascale-registry",
      version: "3.0.0-release",
      kind: "Corporate MegaScale Monorepo Infrastructure (100k Nodes, 1M Edges)",
    },
    nodes,
    edges,
    summaries: generateSummaries(nodes, edges),
  };
}
