import React, { useMemo, useState } from "react";
import { ConnectedEdgesPanel } from "../components/ConnectedEdgesPanel";
import { FamilyFilters } from "../components/FamilyFilters";
import { Legend } from "../components/Legend";
import { LineageGraph } from "../LineageGraph";
import { PackageSummary } from "../components/PackageSummary";
import { ResultsList } from "../components/ResultsList";
import { SelectedNodePanel } from "../components/SelectedNodePanel";
import { ViewControls } from "../components/ViewControls";
import { KeyValue } from "../subcomponents/KeyValue";
import { Section } from "../subcomponents/Section";
import "../styles.css";
import type { DepthSetting, LayoutMode, LineagePayload, SelectionState } from "../types";

export function LineageGraphApp({ payload }: { payload: LineagePayload }): React.ReactElement {
  const families = useMemo(() => [...new Set(payload.nodes.map((node) => node.family))].sort(), [payload.nodes]);
  const edgeTypes = useMemo(() => [...new Set(payload.edges.map((edge) => edge.type || "RELATED"))].sort(), [payload.edges]);
  const [mode, setMode] = useState<LayoutMode>("network");
  const [depth, setDepth] = useState<DepthSetting>("1");
  const [nodeLimit, setNodeLimit] = useState<number | "all">(250);
  const [edgeType, setEdgeType] = useState("");
  const [search, setSearch] = useState("");
  const [centerId, setCenterId] = useState<string | null>(null);
  const [selection, setSelection] = useState<SelectionState>({ selectedNodeId: null, selectedEdgeIndex: null, focusNodeId: null });
  const [familyVisible, setFamilyVisible] = useState<Record<string, boolean>>(() =>
    Object.fromEntries(families.map((family) => [family, true])),
  );
  const [xScaleExponent, setXScaleExponent] = useState(0);
  const [yScaleExponent, setYScaleExponent] = useState(0);
  const [edgeOpacity, setEdgeOpacity] = useState(0.92);
  const [edgeWidth, setEdgeWidth] = useState(2.25);
  const [ribbonCulling, setRibbonCulling] = useState<"off" | "light" | "strong">("light");
  const [forceCutoff, setForceCutoff] = useState(10000);
  const [forceStrength, setForceStrength] = useState(1);
  const [repulsionStrength, setRepulsionStrength] = useState(1);
  const [leftSidebarCollapsed, setLeftSidebarCollapsed] = useState(false);
  const [rightSidebarCollapsed, setRightSidebarCollapsed] = useState(false);

  const selectedNode = payload.nodes.find((node) => node.id === selection.selectedNodeId);
  const connectedEdges = selection.selectedNodeId
    ? payload.edges.filter((edge) => edge.from === selection.selectedNodeId || edge.to === selection.selectedNodeId)
    : [];
  const packageText =
    [payload.package?.name, payload.package?.version, payload.package?.kind].filter(Boolean).join(" | ") ||
    payload.package?.id ||
    "Package context unavailable";
  const appClassName = [
    "ssot-lineage-app",
    leftSidebarCollapsed ? "ssot-lineage-app-left-collapsed" : "",
    rightSidebarCollapsed ? "ssot-lineage-app-right-collapsed" : "",
  ]
    .filter(Boolean)
    .join(" ");
  const leftSidebarClassName = ["ssot-sidebar", "ssot-sidebar-left", leftSidebarCollapsed ? "ssot-sidebar-collapsed" : ""]
    .filter(Boolean)
    .join(" ");
  const rightSidebarClassName = [
    "ssot-sidebar",
    "ssot-sidebar-right",
    "detail",
    rightSidebarCollapsed ? "ssot-sidebar-collapsed" : "",
  ]
    .filter(Boolean)
    .join(" ");

  return (
    <div className={appClassName}>
      <aside className={leftSidebarClassName} aria-label="Lineage graph controls">
        <div className="ssot-sidebar-toggle-row">
          <button
            type="button"
            className="ssot-sidebar-toggle ssot-sidebar-toggle-left"
            aria-expanded={!leftSidebarCollapsed}
            aria-label={leftSidebarCollapsed ? "Expand left sidebar" : "Collapse left sidebar"}
            title={leftSidebarCollapsed ? "Expand controls" : "Collapse controls"}
            onClick={() => setLeftSidebarCollapsed((collapsed) => !collapsed)}
          >
            {leftSidebarCollapsed ? ">" : "<"}
          </button>
        </div>
        {!leftSidebarCollapsed ? (
          <>
            <PackageSummary payload={payload} packageText={packageText} />
            <Section title="View" collapsible>
              <ViewControls
                mode={mode}
                setMode={setMode}
                depth={depth}
                setDepth={setDepth}
                nodeLimit={nodeLimit}
                setNodeLimit={setNodeLimit}
                edgeType={edgeType}
                setEdgeType={setEdgeType}
                edgeTypes={edgeTypes}
                search={search}
                setSearch={setSearch}
                xScaleExponent={xScaleExponent}
                setXScaleExponent={setXScaleExponent}
                yScaleExponent={yScaleExponent}
                setYScaleExponent={setYScaleExponent}
                edgeOpacity={edgeOpacity}
                setEdgeOpacity={setEdgeOpacity}
                edgeWidth={edgeWidth}
                setEdgeWidth={setEdgeWidth}
                ribbonCulling={ribbonCulling}
                setRibbonCulling={setRibbonCulling}
                forceCutoff={forceCutoff}
                setForceCutoff={setForceCutoff}
                forceStrength={forceStrength}
                setForceStrength={setForceStrength}
                repulsionStrength={repulsionStrength}
                setRepulsionStrength={setRepulsionStrength}
              />
            </Section>
            <Section title="Families" collapsible>
              <FamilyFilters families={families} familyVisible={familyVisible} setFamilyVisible={setFamilyVisible} />
            </Section>
            <Section title="Results" className="ssot-results-section" collapsible>
              <ResultsList nodes={payload.nodes} search={search} selection={selection} setSelection={setSelection} />
            </Section>
          </>
        ) : null}
      </aside>
      <LineageGraph
        payload={payload}
        options={{
          mode,
          depth,
          nodeLimit,
          edgeType,
          search,
          familyVisible,
          centerId,
          renderer: "auto",
          xScale: Math.pow(10, xScaleExponent),
          yScale: Math.pow(10, yScaleExponent),
          edgeOpacity,
          edgeWidth,
          ribbonCulling,
          forceCutoff,
          forceStrength,
          repulsionStrength,
          selectedNodeId: selection.selectedNodeId,
          selectedEdgeIndex: selection.selectedEdgeIndex,
        }}
        onSelectionChange={setSelection}
      />
      <aside className={rightSidebarClassName} aria-label="Lineage graph details">
        <div className="ssot-sidebar-toggle-row">
          <button
            type="button"
            className="ssot-sidebar-toggle ssot-sidebar-toggle-right"
            aria-expanded={!rightSidebarCollapsed}
            aria-label={rightSidebarCollapsed ? "Expand right sidebar" : "Collapse right sidebar"}
            title={rightSidebarCollapsed ? "Expand details" : "Collapse details"}
            onClick={() => setRightSidebarCollapsed((collapsed) => !collapsed)}
          >
            {rightSidebarCollapsed ? "<" : ">"}
          </button>
        </div>
        {!rightSidebarCollapsed ? (
          <>
            <Section title="Selected Node" collapsible>
              <SelectedNodePanel selectedNode={selectedNode} centerId={centerId} setCenterId={setCenterId} setSelection={setSelection} />
            </Section>
            <Section title="Connected Edges" collapsible>
              <ConnectedEdgesPanel
                connectedEdges={connectedEdges}
                selectedNodeId={selection.selectedNodeId}
                centerId={centerId}
                setCenterId={setCenterId}
                setSelection={setSelection}
              />
            </Section>
            <Section title="Summary" collapsible defaultOpen={false}>
              <KeyValue record={payload.summary || { nodeCount: payload.nodes.length, edgeCount: payload.edges.length }} />
            </Section>
            <Section title="Legend" collapsible defaultOpen={false}>
              <Legend families={families} />
            </Section>
          </>
        ) : null}
      </aside>
    </div>
  );
}
