import React from "react";
import { LineageGraphApp as WorkspaceLineageGraphApp } from "../workspace/components/LineageGraphApp";
import "../styles.css";
import "../workspace/index.css";
import type { LineagePayload } from "../types";

interface LineageGraphAppProps {
  payload: LineagePayload;
  selectedRegistryKey?: string;
  onChangeRegistry?: (key: string) => void;
  registryOptions?: Array<{ key: string; label: string }>;
  defaultMode?: "network" | "lineage" | "proof" | "release" | "origins" | "packs" | "validation";
  theme?: "light" | "steel-dark";
  showDocumentation?: boolean;
}

export function LineageGraphApp(props: LineageGraphAppProps): React.ReactElement {
  return <WorkspaceLineageGraphApp {...props} />;
}
