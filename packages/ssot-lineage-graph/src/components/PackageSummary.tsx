import React from "react";
import type { LineagePayload } from "../types";
import { Section } from "../subcomponents/Section";
import { StatCard } from "../subcomponents/StatCard";

export function PackageSummary({ payload, packageText }: { payload: LineagePayload; packageText: string }): React.ReactElement {
  return (
    <Section>
      <h1 className="ssot-app-title">SSOT Lineage Graph</h1>
      <div className="ssot-muted">{packageText}</div>
      <div className="ssot-stats">
        <StatCard value={payload.summary?.nodeCount ?? payload.nodes.length} label="nodes" />
        <StatCard value={payload.summary?.edgeCount ?? payload.edges.length} label="edges" />
      </div>
    </Section>
  );
}
