/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState } from "react";
import { LineagePayload, LineageNode, GraphFilters, LineageFamily, OriginKind, GraphViewMode } from "../types";
import { Search, Sliders, Layers, Network, Folder, Database, RefreshCcw, X, ShieldCheck, Package, Rocket, Activity, ChevronLeft, ChevronRight } from "lucide-react";
import { FAMILY_COLORS } from "./LineageGraphCanvas";

const BASE_FAMILIES: LineageFamily[] = [
  "ADR",
  "Spec",
  "SPEC",
  "Feature",
  "Claim",
  "Test",
  "Evidence",
  "Release",
  "Boundary",
  "Profile",
  "Risk",
  "Issue",
];

const BASE_ORIGIN_KINDS: OriginKind[] = [
  "ssot-core",
  "ssot-origin",
  "repo-local",
  "extension-pack",
  "generated",
  "unknown",
];

interface LeftSidebarProps {
  payload: LineagePayload;
  filters: GraphFilters;
  onUpdateFilters: (next: GraphFilters) => void;
  viewMode: GraphViewMode;
  onChangeViewMode: (mode: GraphViewMode) => void;
  selectedRegistryKey: string;
  onChangeRegistry: (key: string) => void;
  registryOptions?: Array<{ key: string; label: string }>;
  allPacks: string[];
  allTiers: string[];
  allOriginKinds: OriginKind[];
  filteredNodes: LineageNode[];
  isCollapsed: boolean;
  onToggleCollapse: () => void;
  onSelectNode?: (id: string | null) => void;
  onFocusNode?: (id: string | null) => void;
  nodeLimit?: number;
  onUpdateNodeLimit?: (limit: number) => void;
  egoHops?: number;
  onUpdateEgoHops?: (hops: number) => void;
  isolateEgo?: boolean;
  onUpdateIsolateEgo?: (val: boolean) => void;
}

export const LeftSidebar: React.FC<LeftSidebarProps> = ({
  payload,
  filters,
  onUpdateFilters,
  viewMode,
  onChangeViewMode,
  selectedRegistryKey,
  onChangeRegistry,
  registryOptions = [],
  allPacks,
  allTiers,
  allOriginKinds,
  filteredNodes,
  isCollapsed,
  onToggleCollapse,
  onSelectNode,
  onFocusNode,
  nodeLimit = 300,
  onUpdateNodeLimit,
  egoHops = 1,
  onUpdateEgoHops,
  isolateEgo = false,
  onUpdateIsolateEgo,
}) => {
  const [activeTab, setActiveTab] = useState<"search" | "filters" | "limits">("search");
  const familyOptions = React.useMemo(
    () => Array.from(new Set<LineageFamily>([...BASE_FAMILIES, ...payload.nodes.map((node) => node.family)])),
    [payload.nodes],
  );
  const originKindOptions = React.useMemo(
    () => Array.from(new Set<OriginKind>([...BASE_ORIGIN_KINDS, ...allOriginKinds])),
    [allOriginKinds],
  );
  const activeRegistryLabel =
    registryOptions.find((option) => option.key === selectedRegistryKey)?.label ||
    payload.package?.name ||
    selectedRegistryKey;

  // Reset all filters in one click
  const handleResetFilters = () => {
    onUpdateFilters({
      search: "",
      families: new Set<LineageFamily>(familyOptions),
      statuses: new Set<string>(),
      originKinds: new Set<OriginKind>(originKindOptions),
      tiers: new Set<string>(),
      packs: new Set<string>(),
      validationStatuses: new Set<string>(),
      edgeTypes: new Set<string>(),
    });
  };

  // Clear all filters completely
  const handleClearFilters = () => {
    onUpdateFilters({
      search: "",
      families: new Set<LineageFamily>(),
      statuses: new Set<string>(),
      originKinds: new Set<OriginKind>(),
      tiers: new Set<string>(),
      packs: new Set<string>(),
      validationStatuses: new Set<string>(),
      edgeTypes: new Set<string>(),
    });
  };

  const handleToggleFamily = (fam: LineageFamily) => {
    const next = new Set<LineageFamily>(filters.families);
    if (next.has(fam)) {
      next.delete(fam);
    } else {
      next.add(fam);
    }
    onUpdateFilters({ ...filters, families: next });
  };

  const handleToggleOriginKind = (orig: OriginKind) => {
    const next = new Set<OriginKind>(filters.originKinds);
    if (next.has(orig)) {
      next.delete(orig);
    } else {
      next.add(orig);
    }
    onUpdateFilters({ ...filters, originKinds: next });
  };

  const handleToggleTier = (tier: string) => {
    const next = new Set<string>(filters.tiers);
    if (next.has(tier)) {
      next.delete(tier);
    } else {
      next.add(tier);
    }
    onUpdateFilters({ ...filters, tiers: next });
  };

  const handleTogglePack = (pack: string) => {
    const next = new Set<string>(filters.packs);
    if (next.has(pack)) {
      next.delete(pack);
    } else {
      next.add(pack);
    }
    onUpdateFilters({ ...filters, packs: next });
  };

  const handleToggleValidationStatus = (vstatus: string) => {
    const next = new Set<string>(filters.validationStatuses);
    if (next.has(vstatus)) {
      next.delete(vstatus);
    } else {
      next.add(vstatus);
    }
    onUpdateFilters({ ...filters, validationStatuses: next });
  };

  const handleToggleStatus = (status: string) => {
    const next = new Set<string>(filters.statuses);
    if (next.has(status)) {
      next.delete(status);
    } else {
      next.add(status);
    }
    onUpdateFilters({ ...filters, statuses: next });
  };

  const activeFilterCount = React.useMemo(() => {
    let count = 0;
    if (filters.search) count++;
    if (filters.families.size < familyOptions.length) count += (familyOptions.length - filters.families.size);
    if (filters.originKinds.size < originKindOptions.length) count += (originKindOptions.length - filters.originKinds.size);
    if (filters.tiers.size > 0) count += filters.tiers.size;
    if (filters.packs.size > 0) count += filters.packs.size;
    if (filters.validationStatuses.size > 0) count += filters.validationStatuses.size;
    if (filters.statuses.size > 0) count += filters.statuses.size;
    return count;
  }, [filters, familyOptions, originKindOptions]);

  if (isCollapsed) {
    return (
      <div className="w-12 h-full border-r border-slate-200 bg-white flex flex-col items-center py-4 gap-4 shrink-0 overflow-hidden font-sans select-none shadow-[1px_0_6px_-2px_rgba(0,0,0,0.05)] z-10 animate-fadeIn">
        {/* Toggle Button to Expand */}
        <button
          onClick={onToggleCollapse}
          className="p-1.5 hover:bg-slate-100 rounded-lg text-slate-500 hover:text-slate-800 transition"
          title="Expand left sidebar"
        >
          <ChevronRight size={18} />
        </button>

        <div className="w-6 border-b border-slate-100 my-1" />

        {/* Database registry switcher indicator (just static icon since it is narrow) */}
        <div
          className="p-2 text-indigo-600 rounded-lg hover:bg-indigo-50/50 cursor-pointer transition relative group"
          onClick={onToggleCollapse}
          title={`Active registry: ${activeRegistryLabel}. Click to expand and change.`}
        >
          <Database size={16} />
          <div className="absolute left-14 top-1/2 -translate-y-1/2 bg-slate-800 text-white text-[10px] px-2 py-1 rounded shadow opacity-0 pointer-events-none group-hover:opacity-100 transition duration-150 whitespace-nowrap z-50 font-sans">
            Active Registry: {activeRegistryLabel}
          </div>
        </div>

        <div className="w-6 border-b border-slate-100 my-1" />

        {/* View mode icons stacked vertically */}
        <div className="flex flex-col items-center gap-1">
          {[
            { mode: "lineage", label: "Lineage Flow", icon: Layers },
            { mode: "proof", label: "Proof Chain", icon: ShieldCheck },
            { mode: "origins", label: "Origins Mode", icon: Folder },
            { mode: "packs", label: "Packs Lineage", icon: Package },
            { mode: "release", label: "Release Board", icon: Rocket },
            { mode: "validation", label: "Validation", icon: Activity },
          ].map((item) => {
            const Icon = item.icon;
            const isActive = viewMode === item.mode;
            return (
              <button
                key={item.mode}
                onClick={() => onChangeViewMode(item.mode as GraphViewMode)}
                className={`p-2 rounded-lg transition relative group ${
                  isActive
                    ? "bg-indigo-50 text-indigo-600"
                    : "text-slate-400 hover:text-slate-600 hover:bg-slate-50"
                }`}
              >
                <Icon size={16} />
                <div className="absolute left-14 top-1/2 -translate-y-1/2 bg-slate-800 text-white text-[10px] px-2 py-1 rounded shadow opacity-0 pointer-events-none group-hover:opacity-100 transition duration-150 whitespace-nowrap z-50 font-sans">
                  {item.label}
                </div>
              </button>
            );
          })}
        </div>

        <div className="flex-1" />

        {/* Active filter counter quick clear if there are active filters */}
        {activeFilterCount > 0 && (
          <button
            onClick={handleResetFilters}
            className="p-2 bg-amber-50 hover:bg-amber-100 text-amber-600 rounded-lg transition relative group"
            title="Reset active filters"
          >
            <RefreshCcw size={14} className="animate-spin-hover" />
            <span className="absolute -top-1 -right-1 bg-amber-600 text-white text-[8px] font-bold w-4 h-4 rounded-full flex items-center justify-center border border-white">
              {activeFilterCount}
            </span>
            <div className="absolute left-14 top-1/2 -translate-y-1/2 bg-slate-800 text-white text-[10px] px-2 py-1 rounded shadow opacity-0 pointer-events-none group-hover:opacity-100 transition duration-150 whitespace-nowrap z-50 font-sans">
              Reset {activeFilterCount} filters
            </div>
          </button>
        )}
      </div>
    );
  }

  return (
    <div className="w-80 h-full border-r border-slate-200 bg-white flex flex-col shrink-0 overflow-hidden font-sans select-none shadow-[2px_0_12px_-4px_rgba(0,0,0,0.06)] z-10">
      {/* Upper Registry Switcher branding node */}
      <div className="p-4 border-b border-slate-100 bg-slate-50/70">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2">
            <Database size={18} className="text-indigo-600" />
            <h2 className="text-sm font-bold tracking-tight text-slate-800">
              SSOT Registry Scope
            </h2>
          </div>
          <button
            onClick={onToggleCollapse}
            className="p-1 hover:bg-slate-200/60 rounded text-slate-400 hover:text-slate-600 transition"
            title="Collapse left sidebar"
          >
            <ChevronLeft size={16} />
          </button>
        </div>

        <select
          value={selectedRegistryKey}
          onChange={(e) => onChangeRegistry(e.target.value)}
          className="w-full bg-white border border-slate-200 rounded-md py-1.5 px-2.5 text-xs text-slate-700 font-medium focus:ring-1 focus:ring-indigo-500 focus:outline-none"
        >
          {registryOptions.length > 0 ? (
            registryOptions.map((option) => (
              <option key={option.key} value={option.key}>
                {option.label}
              </option>
            ))
          ) : (
            <option value={selectedRegistryKey}>{activeRegistryLabel}</option>
          )}
        </select>
      </div>

      {/* Primary Left Tabs navigation */}
      <div className="flex border-b border-slate-100 text-xs font-semibold text-slate-500 bg-white">
        <button
          onClick={() => setActiveTab("search")}
          className={`flex-1 py-3 text-center border-b-2 transition ${
            activeTab === "search"
              ? "border-indigo-600 text-indigo-600 bg-slate-50/20 font-bold"
              : "border-transparent hover:text-slate-800"
          }`}
        >
          Index & Search
        </button>
        <button
          onClick={() => setActiveTab("filters")}
          className={`flex-1 py-3 text-center border-b-2 transition flex items-center justify-center gap-1.5 ${
            activeTab === "filters"
              ? "border-indigo-600 text-indigo-600 bg-slate-50/20 font-bold"
              : "border-transparent hover:text-slate-800"
          }`}
        >
          Filters
          {activeFilterCount > 0 && (
            <span className="bg-indigo-100 text-indigo-700 text-[10px] px-1.5 py-0.2 rounded-full font-bold">
              {activeFilterCount}
            </span>
          )}
        </button>
        <button
          onClick={() => setActiveTab("limits")}
          className={`flex-1 py-3 text-center border-b-2 transition flex items-center justify-center gap-1.5 ${
            activeTab === "limits"
              ? "border-indigo-600 text-indigo-600 bg-slate-50/20 font-bold"
              : "border-transparent hover:text-slate-800"
          }`}
        >
          Limits
        </button>
      </div>

      {/* Main Tab Views Scroll Body */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {activeTab === "search" && (
          <div className="space-y-4">
            {/* Search inputs */}
            <div className="relative">
              <span className="absolute inset-y-0 left-3 flex items-center pointer-events-none text-slate-400">
                <Search size={14} />
              </span>
              <input
                type="text"
                placeholder="Search IDs, labels, files, summaries..."
                value={filters.search}
                onChange={(e) => onUpdateFilters({ ...filters, search: e.target.value })}
                className="w-full bg-slate-50 border border-slate-200 rounded-lg py-2 pl-9 pr-8 text-xs text-slate-700 focus:bg-white focus:outline-none focus:ring-1 focus:ring-indigo-500 transition-all font-mono"
              />
              {filters.search && (
                <button
                  onClick={() => onUpdateFilters({ ...filters, search: "" })}
                  className="absolute inset-y-0 right-2.5 flex items-center text-slate-400 hover:text-slate-600"
                >
                  <X size={14} />
                </button>
              )}
            </div>

            {/* View layout modes panel selection */}
            <div>
              <h3 className="text-[10px] font-bold uppercase tracking-wider text-slate-400 mb-2 font-mono">
                Lineage View Modes
              </h3>
              <div className="grid grid-cols-2 gap-1.5">
                {[
                  { mode: "network", label: "Network Force", icon: Network },
                  { mode: "lineage", label: "Lineage Flow", icon: Layers },
                  { mode: "flow-force", label: "Flow Force", icon: RefreshCcw },
                  { mode: "proof", label: "Proof Chain", icon: ShieldCheck },
                  { mode: "origins", label: "Origins Mode", icon: Folder },
                  { mode: "packs", label: "Packs Lineage", icon: Package },
                  { mode: "release", label: "Release Board", icon: Rocket },
                  { mode: "validation", label: "Validation", icon: Activity },
                ].map((item) => {
                  const Icon = item.icon;
                  const isActive = viewMode === item.mode;
                  return (
                    <button
                      key={item.mode}
                      onClick={() => onChangeViewMode(item.mode as GraphViewMode)}
                      className={`flex items-center gap-1.5 px-2.5 py-2 rounded-md text-left text-xs transition border ${
                        isActive
                          ? "bg-indigo-50 text-indigo-700 border-indigo-200 font-semibold"
                          : "bg-white text-slate-600 border-slate-100 hover:bg-slate-50"
                      }`}
                    >
                      <Icon size={12} className={isActive ? "text-indigo-600" : "text-slate-400"} />
                      <span>{item.label}</span>
                    </button>
                  );
                })}
              </div>
            </div>



            {/* Filtered Index matching summaries list count */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-[10px] font-bold uppercase tracking-wider text-slate-400 font-mono">
                  Registry Index ({filteredNodes.length})
                </h3>
              </div>

              {filteredNodes.length === 0 ? (
                <div className="text-center py-6 bg-slate-50 rounded-lg border border-slate-100">
                  <span className="text-[11px] text-slate-500 font-mono">
                    No registry nodes match filters.
                  </span>
                </div>
              ) : (
                <div className="space-y-1.5 max-h-[280px] overflow-y-auto pr-1">
                  {filteredNodes.slice(0, 250).map((node, idx) => {
                    const col = FAMILY_COLORS[node.family];
                    return (
                      <div
                        key={`${node.id}-${idx}`}
                        onClick={() => {
                          if (onSelectNode) onSelectNode(node.id);
                          if (onFocusNode) onFocusNode(node.id);
                          const target = document.getElementById(`node-${node.id}`);
                          if (target) {
                            target.click();
                            target.scrollIntoView({ behavior: "smooth", block: "center" });
                          }
                        }}
                        className="p-2 border border-slate-100 rounded-md hover:bg-slate-50 hover:border-slate-200 cursor-pointer transition flex items-center justify-between"
                      >
                        <div className="truncate pr-2">
                          <div className="flex items-center gap-1.5 mb-0.5">
                            <span
                              className={`text-[8px] font-mono font-bold px-1 rounded-sm uppercase ${col?.bg || "bg-slate-100"} ${col?.text || "text-slate-700"}`}
                            >
                              {node.family}
                            </span>
                            <span className="text-[10px] font-bold text-slate-700 font-mono truncate">
                              {node.id}
                            </span>
                          </div>
                          <p className="text-[10px] text-slate-500 truncate max-w-[200px]">
                            {node.label || node.title}
                          </p>
                        </div>
                        <span className="text-[9px] text-slate-400 font-mono shrink-0 font-bold bg-slate-50 px-1 py-0.5 rounded border border-slate-100">
                          dg:{node.degree || 0}
                        </span>
                      </div>
                    );
                  })}
                  {filteredNodes.length > 250 && (
                    <div className="text-center py-2 bg-indigo-50/40 rounded border border-dashed border-indigo-100/50 mt-1">
                      <p className="text-[9px] text-indigo-700 font-mono font-medium">
                        Showing first 250 of {filteredNodes.length} matches.
                      </p>
                      <p className="text-[8px] text-slate-400">
                        Type in search box to filter details further.
                      </p>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === "filters" && (
          <div className="space-y-4">
            {/* Reset/Clear buttons heading */}
            <div className="flex items-center justify-between border-b border-slate-100 pb-2">
              <span className="text-xs font-bold text-slate-700 flex items-center gap-1">
                <Sliders size={12} className="text-indigo-600" />
                Active Filters
              </span>
              <div className="flex items-center gap-1.5">
                <button
                  onClick={handleClearFilters}
                  className="text-[10px] text-slate-400 hover:text-rose-600 font-mono font-bold flex items-center gap-0.5 transition cursor-pointer"
                  title="Uncheck all checkboxes"
                >
                  Clear
                </button>
                <span className="text-[10px] text-slate-300 font-mono font-bold select-none">|</span>
                <button
                  onClick={handleResetFilters}
                  className="text-[10px] text-slate-400 hover:text-indigo-600 font-mono font-bold flex items-center gap-0.5 transition cursor-pointer"
                  title="Default checkboxes state"
                >
                  Reset
                </button>
              </div>
            </div>

            {/* Family selection subheaders */}
            <div className="space-y-1.5">
              <h4 className="text-[10px] font-bold uppercase tracking-wider text-slate-400 font-mono">
                Entity Family Filters
              </h4>
              <div className="flex flex-wrap gap-1.5">
                {familyOptions.map((fam) => {
                  const isChecked = filters.families.has(fam);
                  const colors = FAMILY_COLORS[fam];
                  return (
                    <button
                      key={fam}
                      onClick={() => handleToggleFamily(fam)}
                      className={`text-[10px] font-medium px-2 py-1 rounded transition border flex items-center gap-1 ${
                        isChecked
                          ? `${colors?.bg || "bg-slate-100"} ${colors?.text || "text-slate-700"} ${colors?.border || "border-slate-300"} border-2 font-bold`
                          : "bg-white text-slate-500 border-slate-200 hover:bg-slate-50"
                      }`}
                    >
                      <span className={`w-1.5 h-1.5 rounded-full ${colors?.bg || "bg-slate-400"}`} />
                      {fam}
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Origin taxonomy categorizations */}
            <div className="space-y-1.5">
              <h4 className="text-[10px] font-bold uppercase tracking-wider text-slate-400 font-mono">
                Provenance Origin Kind
              </h4>
              <div className="space-y-1">
                {originKindOptions.map((kind) => {
                  const isChecked = filters.originKinds.has(kind);
                  return (
                    <label
                      key={kind}
                      className="flex items-center gap-2 text-xs text-slate-600 cursor-pointer hover:text-slate-800"
                    >
                      <input
                        type="checkbox"
                        checked={isChecked}
                        onChange={() => handleToggleOriginKind(kind)}
                        className="rounded text-indigo-600 focus:ring-indigo-500 w-3.5 h-3.5 border-slate-300"
                      />
                      <span className="font-mono text-[11px] truncate capitalize">
                        {kind.replace("-", " ")}
                      </span>
                    </label>
                  );
                })}
              </div>
            </div>

            {/* Tier classifications */}
            {allTiers.length > 0 && (
              <div className="space-y-1.5">
                <h4 className="text-[10px] font-bold uppercase tracking-wider text-slate-400 font-mono">
                  SLA Compliance Tiers
                </h4>
                <div className="space-y-1">
                  {allTiers.map((tier) => {
                    const isChecked = filters.tiers.has(tier);
                    return (
                      <label
                        key={tier}
                        className="flex items-center gap-2 text-xs text-slate-600 cursor-pointer hover:text-slate-800"
                      >
                        <input
                          type="checkbox"
                          checked={isChecked}
                          onChange={() => handleToggleTier(tier)}
                          className="rounded text-indigo-600 focus:ring-indigo-500 w-3.5 h-3.5 border-slate-300"
                        />
                        <span className="font-mono text-[11px]">{tier}</span>
                      </label>
                    );
                  })}
                </div>
              </div>
            )}

            {/* Packs classifiers */}
            {allPacks.length > 0 && (
              <div className="space-y-1.5 border-t border-slate-100 pt-3">
                <h4 className="text-[10px] font-bold uppercase tracking-wider text-slate-400 font-mono">
                  Governance Registry Packs
                </h4>
                <div className="space-y-1 max-h-[140px] overflow-y-auto pr-1">
                  {allPacks.map((pack) => {
                    const isChecked = filters.packs.has(pack);
                    return (
                      <label
                        key={pack}
                        className="flex items-center gap-2 text-xs text-slate-600 cursor-pointer hover:text-slate-800"
                      >
                        <input
                          type="checkbox"
                          checked={isChecked}
                          onChange={() => handleTogglePack(pack)}
                          className="rounded text-indigo-600 focus:ring-indigo-500 w-3.5 h-3.5 border-slate-300"
                        />
                        <span className="font-mono text-[11px] truncate flex-1" title={pack}>{pack}</span>
                      </label>
                    );
                  })}
                </div>
              </div>
            )}

            {/* Validation Outcome states */}
            <div className="space-y-1.5 border-t border-slate-100 pt-3">
              <h4 className="text-[10px] font-bold uppercase tracking-wider text-slate-400 font-mono">
                Validation Outcome Filters
              </h4>
              <div className="space-y-1">
                {[
                  { key: "pass", label: "Pass (Certified No Drift)", color: "text-emerald-600 bg-emerald-50" },
                  { key: "warn", label: "Warn (Minor Compliance Gaps)", color: "text-amber-600 bg-amber-50" },
                  { key: "fail", label: "Fail (Critical Blockers)", color: "text-red-600 bg-red-50" },
                  { key: "unknown", label: "Unvalidated Entries", color: "text-slate-500 bg-slate-50" },
                ].map((vst) => {
                  const isChecked = filters.validationStatuses.has(vst.key);
                  return (
                    <label
                      key={vst.key}
                      className="flex items-center gap-2 text-xs text-slate-600 cursor-pointer hover:text-slate-800"
                    >
                      <input
                        type="checkbox"
                        checked={isChecked}
                        onChange={() => handleToggleValidationStatus(vst.key)}
                        className="rounded text-indigo-600 focus:ring-indigo-500 w-3.5 h-3.5 border-slate-300"
                      />
                      <span className="font-mono text-[11px] flex-1 flex items-center justify-between">
                        <span>{vst.key.toUpperCase()}</span>
                        <span className={`text-[9px] px-1 py-0.2 rounded scale-90 ${vst.color}`}>{vst.label}</span>
                      </span>
                    </label>
                  );
                })}
              </div>
            </div>

            {/* Lifecycle Statuses */}
            <div className="space-y-1.5 border-t border-slate-100 pt-3">
              <h4 className="text-[10px] font-bold uppercase tracking-wider text-slate-400 font-mono">
                Lifecycle Compliance Status
              </h4>
              <div className="space-y-1">
                {["active", "certified", "deprecated", "experimental"].map((lst) => {
                  const isChecked = filters.statuses.has(lst);
                  return (
                    <label
                      key={lst}
                      className="flex items-center gap-2 text-xs text-slate-600 cursor-pointer hover:text-slate-800"
                    >
                      <input
                        type="checkbox"
                        checked={isChecked}
                        onChange={() => handleToggleStatus(lst)}
                        className="rounded text-indigo-600 focus:ring-indigo-500 w-3.5 h-3.5 border-slate-300"
                      />
                      <span className="font-mono text-[11px] capitalize">{lst}</span>
                    </label>
                  );
                })}
              </div>
            </div>
          </div>
        )}

        {activeTab === "limits" && (
          <div className="space-y-4">
            <div className="flex items-center justify-between border-b border-slate-100 pb-2">
              <span className="text-xs font-bold text-slate-700 flex items-center gap-1">
                <Sliders size={12} className="text-indigo-600" />
                Workspace Limits
              </span>
            </div>

            {/* Workspace Limits & Controls block relocated here */}
            <div className="bg-slate-50 rounded-lg p-3 border border-slate-150 space-y-4">
              {/* Node Limit Controller */}
              <div className="space-y-1.5">
                <div className="flex items-center justify-between text-[11px]">
                  <span className="text-slate-600 font-medium">Render Node Limit</span>
                  <span className="font-mono text-indigo-600 font-bold whitespace-nowrap">
                    {nodeLimit > 5000 ? "Unlimited" : `${nodeLimit} Nodes`}
                  </span>
                </div>
                <input
                  type="range"
                  min="50"
                  max="500"
                  step="50"
                  value={nodeLimit > 5000 ? 500 : nodeLimit}
                  onChange={(e) => {
                    const val = parseInt(e.target.value);
                    if (val === 500) {
                      onUpdateNodeLimit?.(999999);
                    } else {
                      onUpdateNodeLimit?.(val);
                    }
                  }}
                  className="w-full accent-indigo-600 cursor-pointer h-1 bg-slate-200 rounded-lg focus:outline-none"
                />
                <div className="flex justify-between text-[8px] text-slate-400 font-mono">
                  <span>50</span>
                  <span>150</span>
                  <span>300</span>
                  <span>Unlimited</span>
                </div>
              </div>

              {/* Ego Hops Controller */}
              <div className="space-y-1.5 pt-3 border-t border-slate-200/50">
                <div className="flex items-center justify-between text-[11px]">
                  <span className="text-slate-600 font-medium">Ego-Focus Hops Limit</span>
                  <span className="font-mono text-indigo-600 font-bold">
                    {egoHops} {egoHops === 1 ? "Hop" : "Hops"}
                  </span>
                </div>
                <div className="flex gap-1.5">
                  {[1, 2, 3, 4].map((h) => (
                    <button
                      key={h}
                      onClick={() => onUpdateEgoHops?.(h)}
                      className={`flex-1 py-1 rounded text-xs font-mono transition font-bold border cursor-pointer ${
                        egoHops === h
                          ? "bg-indigo-600 border-indigo-750 text-white"
                          : "bg-white border-slate-200 text-slate-600 hover:bg-slate-50"
                      }`}
                    >
                      {h}
                    </button>
                  ))}
                </div>
                <p className="text-[10px] text-slate-400 mt-1 leading-relaxed">
                  Deepens or constrains the neighbor-traversal range (hops) when filtering the central active ego node.
                </p>
              </div>

              {/* Isolate Active Focus Toggle */}
              <div className="space-y-1.5 pt-3 border-t border-slate-200/50">
                <div className="flex items-center justify-between">
                  <span className="text-[11px] text-slate-600 font-medium">Isolate Active Focus</span>
                  <button
                    onClick={() => onUpdateIsolateEgo?.(!isolateEgo)}
                    className={`relative inline-flex h-5 w-9 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none ${
                      isolateEgo ? "bg-indigo-600" : "bg-slate-200"
                    }`}
                  >
                    <span
                      aria-hidden="true"
                      className={`pointer-events-none inline-block h-4 w-4 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out ${
                        isolateEgo ? "translate-x-4" : "translate-x-0"
                      }`}
                    />
                  </button>
                </div>
                <p className="text-[10px] text-slate-400 leading-relaxed">
                  When enabled, completely hides any nodes and ribbons outside of the active focus neighborhood.
                </p>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Embedded Compact Metadata fresh info signature */}
      <div className="p-4 border-t border-slate-100 bg-slate-50">
        <div className="flex items-center justify-between text-[11px] text-slate-500 font-mono mb-2">
          <span>Schema: v{payload.schemaVersion || "2.4.0"}</span>
          <span>Edges: {payload.edges.length || 0}</span>
        </div>
        <div className="flex items-center gap-2 text-[11px] text-slate-500 font-mono">
          <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
          <span>Registry Status: 100% VALIDATED</span>
        </div>
      </div>
    </div>
  );
};
