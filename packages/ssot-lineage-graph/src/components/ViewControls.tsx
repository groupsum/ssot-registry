import React from "react";
import type { DepthSetting, LayoutMode } from "../types";

interface ViewControlsProps {
  mode: LayoutMode;
  setMode: (mode: LayoutMode) => void;
  depth: DepthSetting;
  setDepth: (depth: DepthSetting) => void;
  nodeLimit: number | "all";
  setNodeLimit: (limit: number | "all") => void;
  edgeType: string;
  setEdgeType: (edgeType: string) => void;
  edgeTypes: string[];
  search: string;
  setSearch: (search: string) => void;
  xScaleExponent: number;
  setXScaleExponent: (value: number) => void;
  yScaleExponent: number;
  setYScaleExponent: (value: number) => void;
  edgeOpacity: number;
  setEdgeOpacity: (value: number) => void;
  edgeWidth: number;
  setEdgeWidth: (value: number) => void;
  ribbonCulling: "off" | "light" | "strong";
  setRibbonCulling: (value: "off" | "light" | "strong") => void;
  forceCutoff: number;
  setForceCutoff: (value: number) => void;
  forceStrength: number;
  setForceStrength: (value: number) => void;
  repulsionStrength: number;
  setRepulsionStrength: (value: number) => void;
}

export function ViewControls(props: ViewControlsProps): React.ReactElement {
  return (
    <>
      <label>Search</label>
      <input value={props.search} placeholder="id, title, family" onChange={(event) => props.setSearch(event.target.value)} />
      <div className="ssot-row">
        <div>
          <label>Mode</label>
          <select value={props.mode} onChange={(event) => props.setMode(event.target.value as LayoutMode)}>
            <option value="network">Network</option>
            <option value="lineage">Top-down lineage</option>
          </select>
        </div>
        <div>
          <label>Edge Type</label>
          <select value={props.edgeType} onChange={(event) => props.setEdgeType(event.target.value)}>
            <option value="">All</option>
            {props.edgeTypes.map((type) => (
              <option key={type} value={type}>
                {type}
              </option>
            ))}
          </select>
        </div>
      </div>
      <div className="ssot-row">
        <div>
          <label>Depth</label>
          <select value={props.depth} onChange={(event) => props.setDepth(event.target.value as DepthSetting)}>
            <option value="1">1 hop</option>
            <option value="2">2 hops</option>
            <option value="3">3 hops</option>
            <option value="max">Maximum</option>
          </select>
        </div>
        <div>
          <label>Node Limit</label>
          <select value={props.nodeLimit} onChange={(event) => props.setNodeLimit(event.target.value === "all" ? "all" : Number(event.target.value))}>
            <option value={250}>250</option>
            <option value={1000}>1000</option>
            <option value={5000}>5000</option>
            <option value="all">All</option>
          </select>
        </div>
      </div>
      <div className="ssot-row">
        <div>
          <label>X Scale</label>
          <input type="range" min="-1" max="3" step="0.05" value={props.xScaleExponent} onChange={(event) => props.setXScaleExponent(Number(event.target.value))} />
        </div>
        <div>
          <label>Y Scale</label>
          <input type="range" min="-1" max="3" step="0.05" value={props.yScaleExponent} onChange={(event) => props.setYScaleExponent(Number(event.target.value))} />
        </div>
      </div>
      <div className="ssot-muted">
        x {Math.pow(10, props.xScaleExponent).toFixed(2)}x / y {Math.pow(10, props.yScaleExponent).toFixed(2)}x
      </div>
      <div className="ssot-row">
        <div>
          <label>Ribbon Culling</label>
          <select value={props.ribbonCulling} onChange={(event) => props.setRibbonCulling(event.target.value as "off" | "light" | "strong")}>
            <option value="light">Light</option>
            <option value="strong">Strong</option>
            <option value="off">Off</option>
          </select>
        </div>
        <div>
          <label>Force Cutoff</label>
          <input min={100} max={10000} step={100} type="range" value={props.forceCutoff} onChange={(event) => props.setForceCutoff(Number(event.target.value))} />
        </div>
      </div>
      <div className="ssot-muted">Barnes-Hut Force is active in network mode up to {props.forceCutoff} visible nodes.</div>
      <div className="ssot-row">
        <div>
          <label>Force Strength</label>
          <input min={0} max={3} step={0.05} type="range" value={props.forceStrength} onChange={(event) => props.setForceStrength(Number(event.target.value))} />
        </div>
        <div>
          <label>Repulsion</label>
          <input min={0} max={4} step={0.05} type="range" value={props.repulsionStrength} onChange={(event) => props.setRepulsionStrength(Number(event.target.value))} />
        </div>
      </div>
      <div className="ssot-muted">
        force {props.forceStrength.toFixed(2)}x / repulsion {props.repulsionStrength.toFixed(2)}x
      </div>
      <div className="ssot-row">
        <div>
          <label>Edge Opacity</label>
          <input min={0.05} max={1} step={0.05} type="range" value={props.edgeOpacity} onChange={(event) => props.setEdgeOpacity(Number(event.target.value))} />
        </div>
        <div>
          <label>Edge Width</label>
          <input min={0.5} max={8} step={0.25} type="range" value={props.edgeWidth} onChange={(event) => props.setEdgeWidth(Number(event.target.value))} />
        </div>
      </div>
    </>
  );
}
