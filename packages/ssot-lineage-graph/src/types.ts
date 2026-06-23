export type LineageFamily =
  | "ADR"
  | "Boundary"
  | "Claim"
  | "Evidence"
  | "Feature"
  | "Issue"
  | "Profile"
  | "Release"
  | "Risk"
  | "Spec"
  | "SPEC"
  | "Test"
  | string;

export type LayoutMode = "network" | "lineage";
export type RendererPreference = "auto" | "webgl" | "canvas";
export type RendererMode = "webgl" | "canvas";
export type DepthSetting = "1" | "2" | "3" | "max";

export interface LineageNode {
  id: string;
  family: LineageFamily;
  label?: string;
  title?: string;
  summary?: string;
  description?: string;
  status?: string;
  lifecycle?: {
    stage?: string;
    state?: string;
    promotedAt?: string;
    certifiedAt?: string;
    publishedAt?: string;
  };
  tier?: string;
  origin?: string;
  originKind?: string;
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
    testStatus?: string;
    evidenceStatus?: string;
    releaseStatus?: string;
    completeness?: number;
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
    kind?: string;
  }>;
  x?: number;
  y?: number;
  vx?: number;
  vy?: number;
  pinned?: boolean;
}

export interface LineageEdge {
  from: string;
  to: string;
  type?: string;
  label?: string;
  direction?: "forward" | "reverse" | "bidirectional";
  status?: "active" | "planned" | "deprecated" | "stale" | "missing" | "invalid" | "unknown";
  originKind?: string;
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
    kind?: string;
  };
}

export interface LineageGroup {
  id: string;
  kind: string;
  label: string;
  nodeIds: string[];
  status?: string;
  originKind?: string;
  summary?: string;
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
  summaries?: Record<string, unknown>;
  summary?: Record<string, unknown>;
}

export interface SelectionState {
  selectedNodeId: string | null;
  selectedEdgeIndex: number | null;
  focusNodeId: string | null;
}

export interface RendererOptions {
  renderer?: RendererPreference;
  layoutMode?: LayoutMode;
  initialDepth?: DepthSetting;
  initialNodeLimit?: number | "all";
  forceCutoff?: number;
  forceStrength?: number;
  repulsionStrength?: number;
  edgeOpacity?: number;
  edgeWidth?: number;
  ribbonCulling?: "off" | "light" | "strong";
}

export interface LineageGraphProps {
  payload: LineagePayload;
  options?: RendererOptions;
  className?: string;
  onSelectionChange?: (selection: SelectionState) => void;
}

export interface ViewportState {
  x: number;
  y: number;
  zoom: number;
}

export interface PositionedNode extends Required<Pick<LineageNode, "id" | "family">> {
  label: string;
  status: string;
  tier: string;
  origin: string;
  path: string;
  degree: number;
  x: number;
  y: number;
  vx: number;
  vy: number;
  pinned: boolean;
}

export interface StandaloneHtmlOptions {
  title?: string;
  script?: string;
  style?: string;
  rootId?: string;
}
