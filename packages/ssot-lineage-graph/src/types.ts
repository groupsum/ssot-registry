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
  status?: string;
  tier?: string;
  origin?: string;
  path?: string;
  degree?: number;
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
}

export interface LineagePayload {
  package?: {
    id?: string;
    name?: string;
    version?: string;
    kind?: string;
  };
  nodes: LineageNode[];
  edges: LineageEdge[];
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
