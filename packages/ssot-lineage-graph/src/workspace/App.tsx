/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import { useState, useEffect } from "react";
import { LineageGraphApp } from "./components/LineageGraphApp";
import { 
  mockCoreRegistry, 
  mockDriftRegistry, 
  createLargeRegistry, 
  createSuperLargeRegistry 
} from "./utils/mockData";
import { LineagePayload, LineageNode, LineageEdge } from "./types";
import { computeGraphIndices } from "./utils/graphHelpers";
import { loadDatasetFromCache, saveDatasetToCache } from "./utils/indexedDbHelper";
import { Zap, Layers, RefreshCw, AlertCircle, Database } from "lucide-react";

export default function App() {
  const [registryKey, setRegistryKey] = useState<string>("canonical");
  const [payload, setPayload] = useState<LineagePayload>(mockCoreRegistry);
  const [precomputedIndices, setPrecomputedIndices] = useState<any>(() => computeGraphIndices(mockCoreRegistry));
  
  // Loading and progressive tracking states
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [loadingStatus, setLoadingStatus] = useState<string>("");
  const [loadingPercent, setLoadingPercent] = useState<number>(0);
  const [stats, setStats] = useState({ nodes: 0, edges: 0 });

  useEffect(() => {
    let isCurrent = true;

    // Fast local mapper
    const fastComputeIndices = (nodesList: LineageNode[], edgesList: LineageEdge[]) => {
      const nodeMap = new Map<string, LineageNode>();
      nodesList.forEach((n) => nodeMap.set(n.id, n));

      const incoming = new Map<string, string[]>();
      const outgoing = new Map<string, string[]>();
      const edgeMap = new Map<string, LineageEdge[]>();

      edgesList.forEach((edge) => {
        const fromList = outgoing.get(edge.from) || [];
        fromList.push(edge.to);
        outgoing.set(edge.from, fromList);

        const toList = incoming.get(edge.to) || [];
        toList.push(edge.from);
        incoming.set(edge.to, toList);

        const nodeFromEdges = edgeMap.get(edge.from) || [];
        nodeFromEdges.push(edge);
        edgeMap.set(edge.from, nodeFromEdges);

        const nodeToEdges = edgeMap.get(edge.to) || [];
        nodeToEdges.push(edge);
        edgeMap.set(edge.to, nodeToEdges);
      });

      return { nodeMap, incoming, outgoing, edgeMap };
    };

    async function loadDataset() {
      if (registryKey === "canonical") {
        setIsLoading(false);
        setPayload(mockCoreRegistry);
        setPrecomputedIndices(fastComputeIndices(mockCoreRegistry.nodes, mockCoreRegistry.edges));
        return;
      }
      if (registryKey === "drift") {
        setIsLoading(false);
        setPayload(mockDriftRegistry);
        setPrecomputedIndices(fastComputeIndices(mockDriftRegistry.nodes, mockDriftRegistry.edges));
        return;
      }

      setIsLoading(true);
      setLoadingPercent(0);
      setStats({ nodes: 0, edges: 0 });

      if (registryKey === "large") {
        setLoadingStatus("Generating Enterprise Monorepo dataset (100+ Nodes)...");
        setLoadingPercent(30);
        await new Promise(r => setTimeout(r, 60));
        if (!isCurrent) return;

        const largeRegistry = createLargeRegistry();
        setStats({ nodes: largeRegistry.nodes.length, edges: largeRegistry.edges.length });
        setLoadingPercent(70);
        setLoadingStatus("Forming adjacency matrices for large hierarchy...");
        await new Promise(r => setTimeout(r, 40));
        if (!isCurrent) return;

        const inds = fastComputeIndices(largeRegistry.nodes, largeRegistry.edges);
        setPayload(largeRegistry);
        setPrecomputedIndices(inds);
        setIsLoading(false);
      } 
      else if (registryKey === "superLarge") {
        setLoadingStatus("Structuring HyperScale Stress Test dataset (1,300+ Nodes)...");
        setLoadingPercent(20);
        await new Promise(r => setTimeout(r, 100));
        if (!isCurrent) return;

        const superLarge = createSuperLargeRegistry();
        setStats({ nodes: superLarge.nodes.length, edges: superLarge.edges.length });
        setLoadingPercent(60);
        setLoadingStatus("Processing relational connection tables...");
        await new Promise(r => setTimeout(r, 80));
        if (!isCurrent) return;

        const inds = fastComputeIndices(superLarge.nodes, superLarge.edges);
        setPayload(superLarge);
        setPrecomputedIndices(inds);
        setIsLoading(false);
      } 
      else if (registryKey === "megaScale") {
        // High-Performance IndexedDB Offloading: Check cache first to avoid main-thread allocation and parsing lag!
        try {
          const cached = await loadDatasetFromCache("megaScale", (status, percent) => {
            setLoadingStatus(status);
            setLoadingPercent(percent);
          });
          if (cached && isCurrent) {
            setPayload(cached.payload);
            setPrecomputedIndices(cached.precomputedIndices);
            setStats({ nodes: cached.payload.nodes.length, edges: cached.payload.edges.length });
            setIsLoading(false);
            return;
          }
        } catch (err) {
          console.warn("[IndexedDB Cache] Could not load from IndexedDB, falling back to progressive generation:", err);
        }

        // Cache miss: run progressive chunked generator for MegaScale! (100,500 Nodes, 1,000,000 Edges)
        setLoadingStatus("Allocating progressive memory slots for target dataset...");
        setLoadingPercent(5);
        await new Promise(r => setTimeout(r, 100));
        if (!isCurrent) return;

        const nodes: LineageNode[] = [];
        const edges: LineageEdge[] = [];

        const numADR = 10000;
        const numSPEC = 15000;
        const numFeat = 30000;
        const numClaim = 25000;
        const numTest = 10000;
        const numEv = 10000;
        const numRel = 500;

        // Step 1: ADR nodes (10,000)
        setLoadingStatus("Creating architectural design decisions (ADR-001 to ADR-10000)...");
        setLoadingPercent(10);
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
          if (i % 2500 === 0) {
            setStats({ nodes: nodes.length, edges: 0 });
            await new Promise(r => setTimeout(r, 0));
            if (!isCurrent) return;
          }
        }
        setStats({ nodes: nodes.length, edges: 0 });

        // Step 2: SPEC nodes (15,000)
        setLoadingStatus("Compiling component contract specifications (SPEC-001 to SPEC-15000)...");
        setLoadingPercent(18);
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
          if (i % 2500 === 0) {
            setStats({ nodes: nodes.length, edges: 0 });
            await new Promise(r => setTimeout(r, 0));
            if (!isCurrent) return;
          }
        }
        setStats({ nodes: nodes.length, edges: 0 });

        // Step 3: Feature nodes (30,000)
        setLoadingStatus("Synthesizing orchestrator module features (T2, 30,000 Nodes)...");
        setLoadingPercent(26);
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
          if (i % 5000 === 0) {
            setStats({ nodes: nodes.length, edges: 0 });
            await new Promise(r => setTimeout(r, 0));
            if (!isCurrent) return;
          }
        }
        setStats({ nodes: nodes.length, edges: 0 });

        // Step 4: Claim nodes (25,000)
        setLoadingStatus("Modeling sandbox compliance claims & SLAs (T3, 25,000 Nodes)...");
        setLoadingPercent(35);
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
          if (i % 5000 === 0) {
            setStats({ nodes: nodes.length, edges: 0 });
            await new Promise(r => setTimeout(r, 0));
            if (!isCurrent) return;
          }
        }
        setStats({ nodes: nodes.length, edges: 0 });

        // Step 5: Test, Evidence, and Release nodes
        setLoadingStatus("Mapping automated regression suites, seals, and milestone tags...");
        setLoadingPercent(45);
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
          if (i % 5000 === 0) {
            setStats({ nodes: nodes.length, edges: 0 });
            await new Promise(r => setTimeout(r, 0));
            if (!isCurrent) return;
          }
        }
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
          if (i % 5000 === 0) {
            setStats({ nodes: nodes.length, edges: 0 });
            await new Promise(r => setTimeout(r, 0));
            if (!isCurrent) return;
          }
        }
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
        setStats({ nodes: nodes.length, edges: 0 });
        await new Promise(r => setTimeout(r, 10));
        if (!isCurrent) return;

        // Step 6: Backbone edges (90,500 edges)
        setLoadingStatus("Constructing primary backbone hierarchic lineage connections (90.5k)...");
        setLoadingPercent(52);

        for (let i = 1; i <= numSPEC; i++) {
          edges.push({
            from: `adr:mega-${(i % numADR) + 1}`,
            to: `spec:mega-${i}`,
            type: "defines",
            status: "active",
          });
        }
        await new Promise(r => setTimeout(r, 5));
        if (!isCurrent) return;

        for (let i = 1; i <= numFeat; i++) {
          edges.push({
            from: `spec:mega-${(i % numSPEC) + 1}`,
            to: `feat:mega-${i}`,
            type: "implements",
            status: "active",
          });
        }
        await new Promise(r => setTimeout(r, 5));
        if (!isCurrent) return;

        for (let i = 1; i <= numClaim; i++) {
          edges.push({
            from: `feat:mega-${(i % numFeat) + 1}`,
            to: `claim:mega-${i}`,
            type: "justifies",
            status: "active",
          });
        }
        await new Promise(r => setTimeout(r, 5));
        if (!isCurrent) return;

        for (let i = 1; i <= numTest; i++) {
          edges.push({
            from: `claim:mega-${(i % numClaim) + 1}`,
            to: `test:mega-${i}`,
            type: "verified_by",
            status: "active",
          });
        }
        await new Promise(r => setTimeout(r, 5));
        if (!isCurrent) return;

        for (let i = 1; i <= numEv; i++) {
          edges.push({
            from: `test:mega-${(i % numTest) + 1}`,
            to: `ev:mega-${i}`,
            type: "proves",
            status: "active",
          });
        }
        await new Promise(r => setTimeout(r, 5));
        if (!isCurrent) return;

        for (let i = 1; i <= numRel; i++) {
          edges.push({
            from: `ev:mega-${(i % numEv) + 1}`,
            to: `rel:mega-${i}`,
            type: "certifies",
            status: "active",
          });
        }

        setStats({ nodes: nodes.length, edges: edges.length });
        await new Promise(r => setTimeout(r, 10));
        if (!isCurrent) return;

        // Step 7: Dense cross-dependency ties (generating remaining to hit exactly 1,000,000 edges)
        const targetEdgeCount = 1000000;
        const gap = targetEdgeCount - edges.length;
        
        setLoadingStatus("Synthesizing non-linear dependency lattice mesh...");
        setLoadingPercent(60);

        const edgeChunks = 40;
        const chunkSize = Math.ceil(gap / edgeChunks);

        for (let k = 0; k < edgeChunks; k++) {
          const startingIndex = k * chunkSize;
          const endingIndex = Math.min(gap, startingIndex + chunkSize);

          setLoadingStatus(`Welding cross-cutting dependency ties: ${Math.round(edges.length + chunkSize)} / 1,000,000...`);
          setLoadingPercent(60 + Math.round((k / edgeChunks) * 22));

          for (let step = startingIndex; step < endingIndex; step++) {
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

          setStats({ nodes: nodes.length, edges: edges.length });
          await new Promise(r => setTimeout(r, 0));
          if (!isCurrent) return;
        }

        // Step 8: Build indices on background thread to avoid blockages
        setLoadingStatus("Populating high-performance lineage maps...");
        setLoadingPercent(84);
        await new Promise(r => setTimeout(r, 10));
        if (!isCurrent) return;

        // Inline lightweight summary computation for megaScale
        const families: Record<string, number> = {
          ADR: numADR,
          SPEC: numSPEC,
          Feature: numFeat,
          Claim: numClaim,
          Test: numTest,
          Evidence: numEv,
          Release: numRel,
        };
        const statuses: Record<string, number> = {
          active: numADR + numSPEC + numClaim + numTest + numEv,
          certified: numFeat + numRel,
        };
        const origins: Record<string, number> = {
          "ssot-core": numADR,
          "extension-pack": numSPEC,
          "repo-local": numFeat + numClaim + numTest + numRel,
          generated: numEv,
        };
        const tiers: Record<string, number> = {
          T1: numADR + numSPEC + numEv + numRel,
          T2: numFeat,
          T3: Math.floor((numClaim + numTest) * 0.75),
          T4: Math.floor((numClaim + numTest) * 0.25),
        };

        const summaries = {
          counts: {
            nodes: nodes.length,
            edges: edges.length,
            families,
            statuses,
            origins,
            tiers,
          },
          proof: {
            completeChains: 24890,
            incompleteChains: 110,
            blockedReleases: 0,
            missingEvidence: 18,
            missingTests: 43,
          },
          packs: {
            governancePacks: 45,
            contractPacks: 112,
            extensionPacks: 85,
          },
          hotspots: [
            { nodeId: "claim:mega-1200", reason: "Multiple critical downstream tests dependent on single certificate", score: 88 },
            { nodeId: "spec:mega-50", reason: "Highly connected hub representing specifications core format", score: 94 },
          ],
        };

        const uniqueNodes: LineageNode[] = [];
        const seenNodeIds = new Set<string>();
        nodes.forEach((n) => {
          if (!seenNodeIds.has(n.id)) {
            seenNodeIds.add(n.id);
            uniqueNodes.push(n);
          }
        });

        const finishedPayload: LineagePayload = {
          schemaVersion: "3.2.0",
          generatedAt: new Date().toISOString(),
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
          nodes: uniqueNodes,
          edges,
          summaries,
         };

        // Run multi-phase async indices builder
        const nodeMap = new Map<string, LineageNode>();
        uniqueNodes.forEach((n) => nodeMap.set(n.id, n));

        const incoming = new Map<string, string[]>();
        const outgoing = new Map<string, string[]>();
        const edgeMap = new Map<string, LineageEdge[]>();

        const edgeChunkSize = 40000;
        const totalEdgesCount = edges.length;

        for (let idx = 0; idx < totalEdgesCount; idx += edgeChunkSize) {
          const chunkLimit = Math.min(totalEdgesCount, idx + edgeChunkSize);
          setLoadingStatus(`Compiling relational index maps: ${chunkLimit} / 1,000,000...`);
          setLoadingPercent(85 + Math.round((idx / totalEdgesCount) * 12));

          for (let i = idx; i < chunkLimit; i++) {
            const edge = edges[i];
            const fromList = outgoing.get(edge.from) || [];
            fromList.push(edge.to);
            outgoing.set(edge.from, fromList);

            const toList = incoming.get(edge.to) || [];
            toList.push(edge.from);
            incoming.set(edge.to, toList);

            const nodeFromEdges = edgeMap.get(edge.from) || [];
            nodeFromEdges.push(edge);
            edgeMap.set(edge.from, nodeFromEdges);

            const nodeToEdges = edgeMap.get(edge.to) || [];
            nodeToEdges.push(edge);
            edgeMap.set(edge.to, nodeToEdges);
          }

          await new Promise(r => setTimeout(r, 0));
          if (!isCurrent) return;
        }

        setLoadingStatus("Polishing system layouts & active indicators...");
        setLoadingPercent(98);
        await new Promise(r => setTimeout(r, 100));
        if (!isCurrent) return;

        setPayload(finishedPayload);
        const indexResult = { nodeMap, incoming, outgoing, edgeMap };
        setPrecomputedIndices(indexResult);
        setIsLoading(false);

        // Persistent Cache: Store the compiled megascale data in background IndexedDB
        setTimeout(async () => {
          try {
            await saveDatasetToCache("megaScale", finishedPayload, indexResult);
          } catch (err) {
            console.error("[IndexedDB Cache Save Error]", err);
          }
        }, 300);
      }
    }

    loadDataset();

    return () => {
      isCurrent = false;
    };
  }, [registryKey]);

  return (
    <div className="w-screen h-screen relative bg-slate-900 overflow-hidden font-sans select-none">
      {isLoading ? (
        <div id="loader-overlay" className="absolute inset-0 z-50 flex flex-col items-center justify-center bg-slate-950/95 p-6 md:p-12 text-slate-100">
          <div className="w-full max-w-lg bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl p-6 md:p-8 flex flex-col items-center">
            
            <div className="relative mb-6">
              <div className="w-16 h-16 rounded-full border-4 border-indigo-500/20 border-t-indigo-500 animate-spin flex items-center justify-center" />
              <Database className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 text-indigo-400 animate-pulse" size={24} />
            </div>

            <h2 className="text-xl md:text-2xl font-bold font-sans tracking-tight text-white text-center mb-1">
              {registryKey === "megaScale" ? "MegaScale Stress Test Loader" : "Loading Dataset Registry"}
            </h2>
            <p className="text-xs text-slate-400 font-mono text-center mb-6">
              Processing structured compliance dependencies...
            </p>

            {/* Micro progress bar */}
            <div className="w-full bg-slate-850 h-2 bg-slate-800 rounded-full overflow-hidden mb-3 relative">
              <div 
                className="h-full bg-gradient-to-r from-indigo-500 via-indigo-600 to-indigo-400 rounded-full transition-all duration-300 ease-out"
                style={{ width: `${loadingPercent}%` }}
              />
            </div>

            <div className="w-full flex justify-between text-[10px] font-mono text-slate-400 mb-8 px-1">
              <span>{loadingStatus}</span>
              <span className="font-bold text-indigo-400">{loadingPercent}%</span>
            </div>

            <div className="w-full mt-4 border-t border-slate-800 pt-5 grid grid-cols-2 gap-4 text-center">
              <div className="bg-slate-950/40 border border-slate-800/40 rounded-xl p-3 flex flex-col items-center">
                <span className="text-[10px] uppercase font-mono text-slate-400 mb-0.5">Procedural Nodes</span>
                <span className="text-lg md:text-xl font-bold text-slate-200 tracking-tight font-mono">
                  {stats.nodes > 0 ? stats.nodes.toLocaleString() : "Allocating..."}
                </span>
              </div>
              <div className="bg-slate-950/40 border border-slate-800/40 rounded-xl p-3 flex flex-col items-center">
                <span className="text-[10px] uppercase font-mono text-slate-400 mb-0.5">Connected Edges</span>
                <span className="text-lg md:text-xl font-bold text-slate-200 tracking-tight font-mono">
                  {stats.edges > 0 ? stats.edges.toLocaleString() : "Allocating..."}
                </span>
              </div>
            </div>

            <p className="text-[9px] text-slate-500 text-center mt-6 flex items-center gap-1">
              <Zap size={10} className="text-indigo-400" />
              Main thread responsive. Multi-phase chunking active.
            </p>

          </div>
        </div>
      ) : null}

      <div className="w-full h-full">
        <LineageGraphApp
          payload={payload}
          selectedRegistryKey={registryKey}
          onChangeRegistry={setRegistryKey}
          precomputedIndices={precomputedIndices}
        />
      </div>
    </div>
  );
}
