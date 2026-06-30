/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

export type GraphViewMode =
  | "network"
  | "lineage"
  | "proof"
  | "release"
  | "origins"
  | "packs"
  | "validation"
  | "flow-force";

export type OriginKind =
  | "ssot-core"
  | "ssot-origin"
  | "repo-local"
  | "extension-pack"
  | "generated"
  | "unknown"
  | string;

export type LineageFamily =
  | "ADR"
  | "Spec"
  | "SPEC"
  | "Feature"
  | "Claim"
  | "Test"
  | "Evidence"
  | "Boundary"
  | "Profile"
  | "Release"
  | "Risk"
  | "Issue"
  | string;

export interface LineageNode {
  id: string;
  family: LineageFamily;
  label?: string;
  title?: string;
  summary?: string;
  description?: string;
  body?: string;
  status?: string; // e.g., "active", "planned", "certified", "deprecated", "experimental"
  lifecycle?: {
    stage?: string;
    state?: string;
    promotedAt?: string;
    certifiedAt?: string;
    publishedAt?: string;
  };
  tier?: string; // e.g., "Tier 1", "Tier 2", "Tier 3"
  origin?: string; // e.g., "core-rules", "local-repo", "pci-dss-pack"
  originKind?: OriginKind;
  originRef?: string;
  source?: {
    path?: string;
    line?: number;
    url?: string;
    documentId?: string;
  };
  path?: string;
  degree?: number;
  tags?: string[];
  packs?: string[];
  governancePacks?: string[];
  contractPacks?: string[];
  boundaries?: string[];
  releases?: string[];
  profiles?: string[];
  validation?: {
    status?: "pass" | "warn" | "fail" | "unknown";
    issues?: string[];
    lastCheckedAt?: string;
  };
  proof?: {
    claimTier?: string;
    testStatus?: string; // "passed" | "failed" | "pending" | "missing"
    evidenceStatus?: string; // "signed" | "missing" | "unverified"
    releaseStatus?: string; // "certified" | "blocked" | "pending"
    completeness?: number; // 0 to 100
  };
  metrics?: {
    upstreamCount?: number;
    downstreamCount?: number;
    blockerCount?: number;
    staleEdgeCount?: number;
  };
  links?: Array<{
    label: string;
    href: string;
    kind?: "source" | "docs" | "website" | "issue" | "release" | "external" | string;
  }>;
}

export interface LineageEdge {
  from: string;
  to: string;
  type?: string; // e.g., "implements", "verifies", "proves", "depends_on"
  label?: string;
  direction?: "forward" | "reverse" | "bidirectional";
  status?: "active" | "planned" | "deprecated" | "stale" | "missing" | "invalid" | "unknown" | string;
  originKind?: "direct" | "derived" | "inferred" | "generated" | "unknown" | string;
  strength?: number;
  tier?: string;
  source?: {
    path?: string;
    line?: number;
    field?: string;
    url?: string;
  };
  proof?: {
    required?: boolean;
    satisfied?: boolean;
    blocker?: boolean;
    reason?: string;
  };
  pack?: {
    id?: string;
    kind?: "governance-pack" | "pack-contract" | "extension-pack" | string;
  };
}

export interface LineageGroup {
  id: string;
  kind: "boundary" | "release" | "profile" | "package" | "governance-pack" | "pack-contract" | "origin" | string;
  label: string;
  nodeIds: string[];
  status?: string;
  originKind?: string;
  summary?: string;
}

export interface LineageSummaries {
  counts?: {
    nodes?: number;
    edges?: number;
    families?: Record<string, number>;
    statuses?: Record<string, number>;
    origins?: Record<string, number>;
    tiers?: Record<string, number>;
  };
  proof?: {
    completeChains?: number;
    incompleteChains?: number;
    blockedReleases?: number;
    missingEvidence?: number;
    missingTests?: number;
  };
  packs?: {
    governancePacks?: number;
    contractPacks?: number;
    extensionPacks?: number;
  };
  hotspots?: Array<{
    nodeId: string;
    reason: string;
    score?: number;
  }>;
}

export interface LineagePayload {
  schemaVersion?: string;
  generatedAt?: string;
  generator?: {
    name?: string;
    version?: string;
    command?: string;
  };
  registry?: {
    path?: string;
    repoRoot?: string;
    schemaVersion?: string;
    validationStatus?: "valid" | "invalid" | "unknown";
  };
  package?: {
    id?: string;
    name?: string;
    version?: string;
    kind?: string;
    repositoryUrl?: string;
    canonicalUrl?: string;
  };
  nodes: LineageNode[];
  edges: LineageEdge[];
  groups?: LineageGroup[];
  summaries?: LineageSummaries;
  summary?: Record<string, unknown>;
}

export interface GraphFilters {
  search: string;
  families: Set<LineageFamily>;
  statuses: Set<string>;
  originKinds: Set<OriginKind>;
  tiers: Set<string>;
  packs: Set<string>;
  validationStatuses: Set<string>;
  edgeTypes: Set<string>;
}

export interface GraphSelection {
  selectedNodeId: string | null;
  selectedEdgeId: string | null;
  focusNodeId: string | null;
  focusHistory: string[];
  collapsedNodeIds: Set<string>; // For tree-style recursive collapse
}

export interface ViewSettings {
  showLabels: boolean;
  edgeWidth: number;
  edgeOpacity: number;
  showMinimap: boolean;
  theme: "light" | "steel-dark";
}

export interface Position {
  x: number;
  y: number;
  vx?: number;
  vy?: number;
  fx?: number | null;
  fy?: number | null;
  iy?: number;
}

export type NodePositions = Record<string, Position>;
