# Enhanced SSOT Lineage Graph React Component Brief

Audience: product, design, frontend engineering, Python/CLI engineering, technical writing, DevRel, copywriting.

Primary implementation area: `packages/ssot-lineage-graph`

Primary data source: `pkgs/ssot-core/src/ssot_registry/api/graph.py::_lineage_payload()`

Primary user-facing surfaces:

- `@ssot-registry/lineage-graph` React package
- `ssot graph lineage <path> --output <file.html>` standalone offline HTML
- product portfolio website pages that embed or describe SSOT lineage behavior
- DevRel demos that generate graphs from real repositories with `uv run ssot graph lineage ...`

## Executive Summary

The enhanced lineage graph should become the canonical visual workspace for explaining how an SSOT-governed repository proves scope, governance, implementation readiness, release certification, and publication lineage. It should remain a portable React component that can be embedded in the product portfolio website, internal docs, local static artifacts, and CLI-generated standalone HTML without requiring network access at runtime.

The current package already provides a strong base: a reusable React viewer, a canvas graph, network and top-down lineage modes, family filters, search, connected edge inspection, selection/focus separation, PNG/SVG export, and standalone HTML generation. The enhancement should build on that instead of replacing it. The core work is to enrich the payload contract, add domain-aware graph modes, expose a clearer diagnostic inspector, support larger and more complex registries, and make the component excellent for communication across developer, technical writer, and decision-maker audiences.

The component must not become a marketing infographic. It is an operational graph workspace. It should answer concrete questions:

- Which ADR, SPEC, feature, claim, test, evidence, boundary, profile, release, issue, and risk entities are connected?
- Which relationships are direct, derived, inferred, missing, stale, or release-blocking?
- Which ADR/SPEC origins are repo-local versus upstream, canonical, generated, or extension-pack supplied?
- Which governance packs and `ssot-pack-contracts` are involved in a feature or release proof chain?
- Which proof chain supports a claim or release, and where does it break?
- Which node or edge should an engineer inspect next?
- What can copywriting, technical writing, and DevRel safely say based on visible proof?

## Current Repo-Grounded Baseline

The current React package is `@ssot-registry/lineage-graph` in `packages/ssot-lineage-graph`.

Current public API:

- `LineageGraph`
- `LineageGraphApp`
- `createStandaloneHtml`
- exported TypeScript types

Current payload shape:

- `LineagePayload.package`: optional package context with `id`, `name`, `version`, and `kind`
- `LineagePayload.nodes`: graph nodes with `id`, `family`, optional `label`, `status`, `tier`, `origin`, `path`, `degree`, and layout fields
- `LineagePayload.edges`: graph edges with `from`, `to`, optional `type`
- `LineagePayload.summary`: arbitrary summary record

Current graph behavior:

- network layout for visible graph subsets
- deterministic top-down lineage layout
- search and depth expansion
- family filters
- edge-type filter
- node limit controls
- x/y lineage scale controls
- edge opacity, width, and ribbon culling controls
- force layout controls
- selection, focus, connected edge inspection
- empty-space panning, node dragging, wheel zoom, finite fit, PNG export, SVG export
- collapsible left and right sidebars

Current packaging constraints:

- The React package owns rendering, interaction, layout controls, and standalone app behavior.
- `_lineage_payload()` in `ssot-core` is the canonical payload producer.
- Built assets are vendored into `pkgs/ssot-core/src/ssot_registry/assets/lineage_graph`.
- PyPI users must be able to generate and open lineage HTML without Node, npm, a CDN, or network access.

## Product Goal

Create a lineage graph component that makes SSOT governance legible at repository, package, pack, boundary, feature, release, and proof-chain levels.

The component should help four groups do different jobs from the same source of truth:

- Developers: inspect graph links, missing proof, stale edges, dependency direction, and implementation targets.
- Technical writers: understand entity relationships and document what is actually supported.
- Copywriters: extract truthful product claims without overstating current support.
- DevRel: demo the lifecycle from ADR/SPEC origins through packs, features, tests, evidence, release certification, and publication.

The component should also act as a product proof surface for the portfolio website: instead of saying SSOT has governance, it should show a navigable graph of governance.

## Non-Goals

- Do not replace the Python SSOT registry parser or validator in React.
- Do not make the graph depend on live network calls.
- Do not require React Router inside the reusable graph package.
- Do not show raw JSON payloads in normal user-facing panels.
- Do not build a decorative graph that hides edges or proof details.
- Do not claim graph facts that are not present in the payload.
- Do not turn the public product website into a page-count brag. Large matrix/corpus generation should be implementation infrastructure, not marketing copy.

## Core UX Principles

1. Make proof visible before decoration.

   The graph must prioritize readable nodes, visible edges, useful filtering, clear status, and fast inspection. Visual polish matters, but the graph is successful only if users can trace relationships.

2. Separate graph navigation from graph explanation.

   The canvas is for spatial exploration. Sidebars and inspectors are for meaning, status, provenance, and next actions.

3. Treat selection, focus, filters, and route state as separate concepts.

   A selected node is the current inspected entity. A focused node is the traversal center. Filters define the visible universe. Route or share state should serialize the view without changing the payload.

4. Preserve offline portability.

   The same graph experience should work from local standalone HTML generated by `ssot graph lineage`, from npm package embedding, and from a product website route.

5. Make the graph useful at small and large sizes.

   A 50-node demo and a 10,000-node registry require different defaults, labels, culling, search, grouping, and performance strategies.

## Target Audiences And Primary Jobs

### Developer

Developer jobs:

- Find everything connected to a feature, test, release, boundary, or ADR.
- Verify whether a claim has tests and evidence.
- See whether release certification is blocked by missing or stale proof.
- Understand which pack or origin supplied a governance rule or document.
- Inspect edge direction and relationship type without reading registry files first.

Developer language:

- "Focus feature"
- "Show proof chain"
- "Show blockers"
- "Open source path"
- "Copy entity id"
- "Trace to release"
- "Trace to ADR/SPEC"

### Technical Writer

Technical writer jobs:

- Understand which concepts are canonical and which are repo-local.
- Determine whether docs should describe a feature as planned, active, certified, deprecated, or experimental.
- See how ADRs, SPECs, packs, and release artifacts connect.
- Extract a stable glossary of SSOT entity families and relationship types.

Technical writer language:

- "Canonical origin"
- "Repo-local extension"
- "Governance pack"
- "Pack contract"
- "Proof chain"
- "Release evidence"

### Copywriter

Copywriter jobs:

- Identify safe product claims supported by graph relationships.
- Avoid overclaiming unsupported automation, publication, or certification.
- Understand the highest-value visual story for product pages.
- Translate governance mechanics into clear product benefits.

Copywriter language:

- "Trace decisions to releases"
- "See proof behind every claim"
- "Governed package portfolios"
- "Portable registry intelligence"

### DevRel

DevRel jobs:

- Generate a real graph from a sample repository.
- Demonstrate ADR-to-release lineage with one command.
- Show governance packs and pack contracts as reusable building blocks.
- Export graph images for talks, docs, and READMEs.
- Share standalone HTML without requiring a hosted app.

DevRel language:

- `uv run ssot graph lineage . --output .ssot/graphs/registry.lineage.html`
- `uv run ssot graph export . --format json --output .ssot/graphs/registry.graph.json`
- `pip install ssot-registry`
- `uv tool install ssot-registry`

## Required Component Surfaces

### `LineageGraph`

Low-level graph canvas/workspace component.

Responsibilities:

- accept a `LineagePayload`
- accept view/rendering options
- render the graph
- expose selection changes
- support programmatic focus and visible-state updates
- stay embeddable in custom shells

This component should remain the right choice for product website pages that already provide their own layout, navigation, SEO metadata, and surrounding copy.

### `LineageGraphApp`

Full graph application shell.

Responsibilities:

- include package summary
- include filters and search
- include layout controls
- include family legend
- include selected node inspector
- include connected edge inspector
- include export controls
- include diagnostics panels
- support standalone HTML usage

This component should remain the right choice for CLI-generated HTML and demos.

### `createStandaloneHtml`

Offline HTML generator.

Responsibilities:

- embed payload safely
- embed vendored JavaScript and CSS when called from Python
- require no CDN or runtime network access
- preserve title/root-id options
- remain robust with large payloads

Enhancement target:

- include optional view-state bootstrap data
- include optional generated-at metadata
- include optional structured summary metadata for non-graph contexts
- keep payload escaping safe for HTML/script contexts

### Optional New Helper: `createLineageViewState`

Purpose:

- normalize URL/search params or saved state into graph view options
- make website deep links and standalone permalinks consistent
- keep route parsing outside the canvas component

Possible API:

```ts
type LineageViewState = {
  mode?: "network" | "lineage" | "proof" | "release" | "origins" | "packs";
  selectedNodeId?: string | null;
  focusNodeId?: string | null;
  search?: string;
  families?: string[];
  edgeTypes?: string[];
  origins?: string[];
  statuses?: string[];
  tiers?: string[];
  depth?: "1" | "2" | "3" | "max";
  nodeLimit?: number | "all";
};
```

This helper should be optional and backward compatible. Existing consumers should not need to adopt it.

## Payload Contract Enhancement

The existing payload must remain valid. Add optional fields rather than replacing required fields.

### Payload Metadata

Recommended additions:

```ts
interface LineagePayload {
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
```

Rationale:

- `schemaVersion` lets React safely branch on optional capabilities.
- `generatedAt` helps users judge freshness.
- `generator` helps DevRel and support reproduce artifacts.
- `registry.validationStatus` makes validation state visible without re-running Python.
- package URLs help website integrations generate canonical graph pages.

### Node Enhancement

Recommended additions:

```ts
interface LineageNode {
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
  originKind?: "ssot-core" | "ssot-origin" | "repo-local" | "extension-pack" | "generated" | "unknown" | string;
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
    kind?: "source" | "docs" | "website" | "issue" | "release" | "external" | string;
  }>;
}
```

Required origin distinction:

- `ssot-core`: canonical entities, validators, or schema-owned governance from the core registry implementation.
- `ssot-origin`: upstream canonical origin material that should be treated as inherited source-of-truth context.
- `repo-local`: project-specific ADRs, SPECs, features, tests, claims, evidence, boundaries, releases, issues, or risks.
- `extension-pack`: reusable pack-supplied governance, templates, policies, contracts, or metadata.
- `generated`: generated entity or generated view material derived from other source records.
- `unknown`: legacy payload or insufficient origin metadata.

This distinction should be displayed directly in the inspector and available as a filter. Do not collapse origins into a single free-text string when the payload can provide structured origin kind.

### Edge Enhancement

Recommended additions:

```ts
interface LineageEdge {
  from: string;
  to: string;
  type?: string;
  label?: string;
  direction?: "forward" | "reverse" | "bidirectional";
  status?: "active" | "planned" | "deprecated" | "stale" | "missing" | "invalid" | "unknown";
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
```

Edge display rules:

- Direct edges should be visually stronger than inferred edges.
- Missing or invalid proof edges should be visible, not hidden.
- Stale/deprecated edges should remain inspectable with reduced emphasis.
- Direction should be readable in the connected edge panel even if the canvas uses undirected depth traversal.
- Edge type labels should be human-readable in panels and compact on-canvas.

### Group Enhancement

Groups are optional and should support higher-level views without forcing every consumer to pre-cluster nodes.

```ts
interface LineageGroup {
  id: string;
  kind: "boundary" | "release" | "profile" | "package" | "governance-pack" | "pack-contract" | "origin" | string;
  label: string;
  nodeIds: string[];
  status?: string;
  originKind?: string;
  summary?: string;
}
```

Group use cases:

- collapse all nodes in a governance pack
- show a release envelope around claims, tests, evidence, and features
- show a boundary envelope around scoped features
- show repo-local versus upstream origin clusters
- show package or corpus groupings on product portfolio routes

### Summaries Enhancement

Recommended summary object:

```ts
interface LineageSummaries {
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
```

Keep the existing `summary?: Record<string, unknown>` for backward compatibility. New UI should prefer structured `summaries` when available and gracefully fall back to `summary`.

## Required Graph Modes

### Network Mode

Purpose:

- Explore all visible graph families using force layout.

Requirements:

- Keep current behavior: every visible family can participate.
- Do not special-case ADRs, specs, features, claims, tests, evidence, boundaries, profiles, releases, issues, or risks out of force behavior.
- Use visible edge and node limits to protect performance.
- Show performance/readability guidance when the graph exceeds recommended thresholds.

### Top-Down Lineage Mode

Purpose:

- Show deterministic left-to-right or top-to-bottom lineage by family rank.

Requirements:

- Preserve deterministic ordering.
- Honor x/y scale controls.
- Left-align nodes within each layer.
- Keep edge ribbons visible at defaults.
- Make edge type and family filters work exactly as in network mode.

### Proof Chain Mode

Purpose:

- Show whether a claim, feature, or release has a complete proof chain.

Recommended default path:

`ADR/SPEC -> Feature -> Claim -> Test -> Evidence -> Release`

Requirements:

- Emphasize required proof edges.
- Mark missing or unsatisfied proof links.
- Show claim tier, test status, evidence status, and release status.
- Support "Trace upstream" and "Trace downstream" from selected nodes.
- Make incomplete proof chains obvious in the inspector.

### Release Boundary Mode

Purpose:

- Explain release certification and boundary closure.

Requirements:

- Group or frame nodes by release and boundary.
- Highlight release-blocking issues and risks.
- Show which features are included, excluded, planned, frozen, certified, promoted, or published.
- Support filtering by release id and boundary id.

### Origin Mode

Purpose:

- Discern between ADR/SPEC/entity origins.

Requirements:

- Visually distinguish `ssot-core`, `ssot-origin`, `repo-local`, `extension-pack`, `generated`, and `unknown`.
- Provide origin filter chips.
- Show origin in node cards, tooltips, inspector summary, and exported legends.
- Let technical writers identify whether a document is canonical, inherited, local, pack-provided, or generated.

### Packs And Contracts Mode

Purpose:

- Present `ssot-pack-contracts` and governance packs as first-class product surfaces.

Requirements:

- Show governance packs, contract packs, and extension packs as groups or lenses.
- Trace pack-provided rules to affected ADRs, SPECs, features, claims, tests, evidence, releases, and boundaries.
- Make pack membership visible on selected node details.
- Support pack-level filters and group collapse.
- Use plain labels such as "Governance Pack", "Pack Contract", and "Extension Pack" rather than internal-only identifiers.

### Validation Drift Mode

Purpose:

- Help maintainers identify stale, invalid, missing, or at-risk graph relationships.

Requirements:

- Surface validation warnings and failures from payload metadata.
- Highlight stale edges and invalid links without hiding them.
- Rank hotspots by blocker count, missing proof, or stale edge count.
- Provide a compact "Next inspection targets" list.

## Interaction Requirements

### Search

Search should match:

- id
- label/title
- summary/description
- family
- status
- origin
- origin kind
- path
- pack id
- boundary id
- release id
- edge type when searching from connected-edge context

Search should support:

- keyboard focus shortcut from host app if provided
- clear button
- exact id match boost
- highlighted matched terms in result rows
- empty-state copy that explains whether filters are hiding matches

### Filtering

Required filters:

- family
- edge type
- status
- origin kind
- tier
- release
- boundary
- profile
- pack
- validation status
- proof status

Filter behavior:

- Filters must be composable.
- The UI should show active filter count.
- Users should be able to clear all filters.
- Empty states should explain which filters are active.
- Family filters should remain visible even when no nodes of that family are currently visible because of other filters.

### Selection And Focus

Selection:

- clicking a node selects it
- selecting a result row selects the node
- selected node remains visible if possible
- selected node details update immediately

Focus:

- focusing a node changes traversal center
- focus should be explicit and reversible
- focus should not silently clear filters
- focused node should be visibly different from selected node

History:

- maintain a focus trail
- allow back/forward through focus history inside the component
- support copying a link or serialized state for the current view

### Canvas Navigation

Required:

- pan
- zoom
- fit to view
- zoom in
- zoom out
- reset to 100 percent
- double-click fit or focus behavior, depending on mode
- node dragging
- pinned node state
- finite viewport math at extreme zoom

Nice-to-have:

- minimap
- lasso selection
- box zoom
- keyboard pan/zoom
- "locate selected" button

### Inspector

The right-side inspector should use structured sections instead of raw JSON.

Recommended sections:

- Summary
- Status
- Origin
- Source
- Proof
- Packs
- Release And Boundary
- Connected Edges
- Validation
- Links
- Copy IDs

Summary fields:

- id
- family
- label/title
- status
- tier
- degree
- origin kind
- origin ref

Source fields:

- path
- line
- document id
- source URL when available

Proof fields:

- claim tier
- required tests
- linked tests
- evidence status
- release certification status
- blockers

Packs fields:

- governance packs
- pack contracts
- extension packs

Connected edge grouping:

- incoming
- outgoing
- bidirectional
- missing/invalid
- proof-required
- pack-supplied

### Results List

Enhance current results list into a fast graph index.

Required:

- virtualize or window when result count is large
- show family, id, label, status, origin kind, degree
- show why a result matched when search is active
- support select and focus actions
- support sorting by relevance, family, status, degree, origin, blocker count

### Legend

Legend should cover more than family colors.

Required legend dimensions:

- family color
- origin style
- edge status style
- direct versus inferred edge style
- proof-required edge style
- missing/invalid edge style
- selected versus focused node style
- group/envelope style

## Visual Design Direction

The visual language should be dense, operational, and trustworthy.

Layout:

- full-height workspace
- collapsible left controls
- central graph canvas
- collapsible right inspector
- no card-inside-card composition
- scrollable sidebars with stable widths
- compact toolbar above or inside canvas

Color:

- retain family color distinction
- add non-color signals for status and origin
- avoid one-note palettes
- preserve high contrast for edges and selected states
- ensure missing/invalid proof is visible for color-blind users

Typography:

- compact labels
- labels visible at practical zoom levels
- no viewport-width font scaling
- no negative letter spacing
- truncate long ids with middle ellipsis in panels only, not in copied values

Canvas:

- nodes should remain visible against the background at default zoom
- edges should remain visible at default opacity/width
- selected and focused nodes should have distinct outlines
- group envelopes should not obscure edges

Responsive behavior:

- desktop: three-pane workspace
- tablet: collapsible sidebars with canvas priority
- mobile: search/results and inspector become primary; graph remains available but not the only navigation method

## Accessibility Requirements

Minimum:

- keyboard access for controls, filters, results, inspector actions, and export actions
- visible focus states
- semantic buttons and native controls where possible
- ARIA labels for canvas controls
- accessible text equivalents for selected node and connected edges
- reduced-motion support for layout animation
- high-contrast-compatible selected/focused/missing states

Advanced:

- graph summary announced as text
- keyboard traversal of connected edges
- "list mode" for users who cannot use canvas navigation
- exportable text summary of selected proof chain

## Performance Requirements

Baseline targets:

- 1,000 nodes and 5,000 edges should feel immediate on a modern laptop.
- 5,000 nodes and 25,000 edges should remain navigable with culling and labels reduced.
- 10,000 nodes and 50,000 edges should load with clear progressive rendering, limits, and guidance.

Implementation recommendations:

- Keep payload normalization memoized.
- Compute degree, adjacency, filters, and search indexes once per payload or filter revision.
- Use typed arrays or compact structures for hot layout paths where useful.
- Keep force layout bounded by cutoff and visible set.
- Consider Web Worker layout for high-volume graphs.
- Consider OffscreenCanvas where supported.
- Be honest about renderer names: if WebGL is advertised, implement WebGL; otherwise report canvas accurately.
- Avoid adding large runtime dependencies unless they materially improve performance and remain portable.

High-volume behavior:

- default to aggregate/grouped views when payload is very large
- show visible-node and visible-edge counts
- explain when node limits are hiding graph data
- let users switch from "all" to sampled or focused views
- never silently drop selected or focused nodes

## Website Integration Requirements

The product portfolio website can embed this component, but the reusable graph package should not own the whole website routing layer.

Website adapter responsibilities:

- React Router routes
- canonical URLs
- canonical slugs
- route metadata
- JSON-LD emission
- structured-data graph pages
- `llms.txt`, `robots.txt`, `sitemap.xml`, and nested sitemap generation
- SEO/AEO/AiEO scoring gates
- matrix/corpus page generation infrastructure

Graph package responsibilities:

- provide embeddable components
- provide stable payload and view-state types
- provide accessible graph summaries
- expose summary data that a host can use for structured data
- avoid hard-coding website routes

Recommended website routes:

- `/portfolio/lineage-graph`
- `/portfolio/lineage-graph/governance-packs`
- `/portfolio/lineage-graph/pack-contracts`
- `/portfolio/lineage-graph/proof-chains`
- `/portfolio/lineage-graph/releases`
- `/portfolio/lineage-graph/origins`

Recommended canonical slug rules:

- lowercase
- hyphen-separated
- stable family names
- entity ids URL-encoded only when used as query or route parameters
- no route that claims a fixed public page count

Example share URL pattern:

```text
/portfolio/lineage-graph?mode=proof&focus=feat:portable-lineage-export&depth=max&origin=repo-local
```

## Structured Data And AI Discovery

The component should expose structured summaries that host pages can translate into JSON-LD. The graph component itself may offer a helper, but the website should own final route-level JSON-LD emission.

Recommended host-level schema concepts:

- `SoftwareApplication` for SSOT Registry
- `SoftwareSourceCode` for source-backed examples
- `TechArticle` for explanatory graph pages
- `Dataset` for lineage payload snapshots
- `DefinedTermSet` for entity families and edge types
- `HowTo` for generating a lineage graph with uv or pip workflows
- `FAQPage` for AEO pages when real questions and answers exist

Recommended graph summary fields for structured-data adapters:

- package name/version/kind
- graph generated timestamp
- node counts by family
- proof chain completeness
- origin counts
- governance pack counts
- pack contract counts
- release certification counts

Rules:

- Do not expose full private registry payloads in public JSON-LD.
- Do not emit source paths publicly unless the repository is public and paths are intended to be indexed.
- Do not claim validation success unless payload metadata says validation passed.
- Keep AI-facing summaries consistent with visible page content.

## Copy And Content Guidance

Safe product claims when backed by payload and UI:

- "Trace ADRs, SPECs, features, claims, tests, evidence, boundaries, profiles, risks, issues, and releases in one graph."
- "Generate a portable lineage graph from an SSOT registry."
- "Inspect proof chains from decision records through release evidence."
- "Distinguish repo-local records from upstream, canonical, generated, and pack-supplied origins."
- "Use governance packs and pack contracts as visible graph dimensions."

Claims to avoid unless separately implemented and verified:

- "Automatic compliance certification for every repository."
- "Complete proof for every claim."
- "Real-time registry monitoring."
- "3840 public pages."
- "WebGL renderer" if the actual renderer is still canvas.
- "10/10 SEO/AEO/AiEO" unless measured by the website's own gates.

Preferred terms:

- "lineage graph"
- "proof chain"
- "governance pack"
- "pack contract"
- "origin"
- "release certification"
- "portable standalone HTML"
- "registry payload"
- "canonical source of truth"

## DevRel Demo Requirements

The enhanced component should support a demo flow that starts from a real repository and ends in a shareable artifact.

Primary uv flow:

```powershell
uv run ssot graph lineage . --output .ssot\graphs\registry.lineage.html
```

Primary pip/tool flow:

```powershell
pip install ssot-registry
ssot graph lineage . --output .ssot\graphs\registry.lineage.html
```

Optional uv tool flow:

```powershell
uv tool install ssot-registry
ssot graph lineage . --output .ssot\graphs\registry.lineage.html
```

Demo narrative:

1. Generate the graph.
2. Search for a feature or release.
3. Focus the node.
4. Switch to proof chain mode.
5. Show connected claims, tests, and evidence.
6. Switch to origin mode.
7. Show which records are repo-local, canonical, generated, or pack-supplied.
8. Switch to packs/contracts mode.
9. Show governance packs and pack contracts.
10. Export PNG/SVG or share standalone HTML.

## Engineering Implementation Plan

### Phase 0: Contract Preservation

Goals:

- preserve existing public exports
- preserve existing payload compatibility
- document current renderer truth
- prevent regressions in standalone HTML

Tasks:

- add type tests for existing payloads
- add compatibility fixtures for legacy payloads
- ensure existing standalone HTML tests still pass
- decide whether `renderer: "webgl"` means real WebGL or should be reported as canvas until implemented

Acceptance criteria:

- existing consumers using `LineageGraphApp payload={payload}` continue to work
- `createStandaloneHtml(payload)` still emits self-contained HTML
- no runtime network dependency is introduced

### Phase 1: Payload vNext

Goals:

- add optional structured metadata
- support origins, packs, proof, validation, and summaries
- keep `_lineage_payload()` canonical

Tasks:

- extend TypeScript interfaces with optional fields
- update Python `_lineage_payload()` to emit optional fields when available
- add fixtures that include `originKind`, `proof`, `validation`, `packs`, `groups`, and `summaries`
- update summary panels to prefer structured `summaries` but fall back to existing `summary`

Acceptance criteria:

- old payload fixtures render unchanged
- new payload fixtures expose origin, proof, validation, and pack data in panels
- Python unit tests verify payload shape

### Phase 2: Domain-Aware Modes

Goals:

- add proof chain mode
- add release boundary mode
- add origin mode
- add packs/contracts mode
- add validation drift mode

Tasks:

- define mode-specific default filters and layout hints
- add mode switch UI without crowding the existing View panel
- add edge and node styling rules per mode
- add inspector sections per mode
- add mode-specific empty states

Acceptance criteria:

- each mode answers a distinct user question
- switching modes preserves selected node when possible
- modes work in standalone HTML and package embedding

### Phase 3: Inspector And Index

Goals:

- make selected node details useful for technical and non-technical audiences
- improve search/result navigation
- avoid raw JSON panels

Tasks:

- add structured inspector sections
- group connected edges by direction/status/type
- add copy-id and copy-link actions
- add result sorting
- add match highlighting
- virtualize results for large payloads

Acceptance criteria:

- users can inspect provenance, proof, packs, source, validation, and connected edges without opening raw files
- results remain usable with thousands of nodes
- keyboard users can select and focus nodes from results

### Phase 4: Layout And Performance

Goals:

- keep graph usable at high volume
- improve force and lineage readability
- introduce group/envelope rendering

Tasks:

- build adjacency/search indexes
- optimize visible graph calculation
- add large-graph guidance
- add group envelope rendering
- evaluate Web Worker layout
- evaluate minimap
- test extreme zoom and fit behavior

Acceptance criteria:

- selected/focused nodes are never silently dropped
- graph remains responsive under agreed high-volume fixtures
- edges remain visible at defaults

### Phase 5: Website Adapter And Content Hooks

Goals:

- make the component easy to embed in the product portfolio website
- support canonical graph routes and structured data without coupling the package to routing

Tasks:

- document recommended website adapter props
- expose structured graph summary helpers if needed
- define canonical route/query state format
- provide sample route copy blocks for copywriter and technical writer teams
- provide DevRel demo snippets

Acceptance criteria:

- website can embed the component with React Router route state
- website can generate JSON-LD from safe graph summaries
- copywriter and DevRel teams can describe lineage graph capabilities without overclaiming

## Component Architecture Recommendation

Recommended internal structure:

```text
LineageGraphApp
  LineageGraphProvider
    LineageShell
      LeftSidebar
        PackageSummary
        ViewModeControl
        SearchControl
        FilterPanel
        ResultsIndex
      GraphWorkspace
        GraphToolbar
        LineageGraphCanvas
        Minimap
        PerformanceBadge
      RightInspector
        SelectedNodeSummary
        ProofPanel
        OriginPanel
        PacksPanel
        ReleaseBoundaryPanel
        ConnectedEdgesPanel
        ValidationPanel
        LinksPanel
        LegendPanel
```

Provider responsibilities:

- normalized payload
- indexes
- filters
- selected node
- focused node
- mode
- viewport state
- serialized view state

Canvas responsibilities:

- draw nodes, edges, labels, groups, selections, focus rings
- handle pan/zoom/drag
- emit selection
- expose export surfaces

Inspector responsibilities:

- render domain meaning
- provide actions
- avoid graph layout logic

Filter/index responsibilities:

- compute visible universe
- expose result counts
- explain empty states

## State Model

Recommended state groups:

```ts
type GraphViewMode = "network" | "lineage" | "proof" | "release" | "origins" | "packs" | "validation";

type GraphFilters = {
  families: Set<string>;
  edgeTypes: Set<string>;
  statuses: Set<string>;
  originKinds: Set<string>;
  tiers: Set<string>;
  releases: Set<string>;
  boundaries: Set<string>;
  profiles: Set<string>;
  packs: Set<string>;
  validationStatuses: Set<string>;
  proofStatuses: Set<string>;
};

type GraphSelection = {
  selectedNodeId: string | null;
  selectedEdgeId: string | null;
  focusNodeId: string | null;
  focusHistory: string[];
};
```

Rules:

- State must be serializable for share links.
- State should not mutate the original payload.
- Pinned node positions may be stored separately from payload unless explicitly exported.
- View state should degrade gracefully when a node id is missing from a later payload.

## Testing Requirements

Package-level tests:

- payload backward compatibility
- payload vNext fields render
- standalone HTML remains offline
- search matches new fields
- filters compose correctly
- selected/focused nodes stay visible
- proof mode highlights missing proof
- origin mode distinguishes origin kinds
- packs/contracts mode displays governance packs and pack contracts
- release boundary mode groups release/boundary records
- validation drift mode surfaces invalid/stale/missing links
- no raw JSON appears in user-facing panels
- edge visibility remains above threshold at defaults
- PNG/SVG exports still work

Python/CLI tests:

- `_lineage_payload()` emits compatible payloads
- `_lineage_payload()` emits optional vNext fields when registry data exists
- `ssot graph lineage` writes self-contained HTML
- graph viewer parity tests assert UI strings and offline behavior
- high-volume fixtures validate performance fallbacks

Recommended commands:

```powershell
npm run build:lineage-graph
npm run test:lineage-graph
npm run verify:lineage-graph-vendor
uv run pytest tests\unit\test_graph_export.py tests\integration\test_cli_graph.py tests\ssot_scaffold\test_graph_lineage_viewer_parity.py
```

If CLI parser surfaces change, regenerate the CLI surface manifest according to the repo's existing test workflow.

## Documentation Deliverables

Technical writer deliverables:

- lineage graph concept page
- payload schema reference
- graph modes reference
- origin taxonomy reference
- governance packs and pack contracts reference
- standalone HTML generation guide
- troubleshooting guide for large graphs

Copywriter deliverables:

- concise product page description
- proof-chain value proposition
- governance-pack value proposition
- pack-contract value proposition
- origin/provenance value proposition
- short demo captions for graph screenshots

DevRel deliverables:

- uv quickstart
- pip quickstart
- sample repository walkthrough
- demo script for ADR-to-release proof chain
- PNG/SVG export examples
- standalone HTML sharing guidance

Engineering deliverables:

- TypeScript payload vNext types
- Python payload emission update
- component mode implementation
- test fixtures
- high-volume proof fixture
- website adapter notes
- generated standalone artifact for review

## Definition Of Done

The enhanced lineage graph is done when:

- existing `@ssot-registry/lineage-graph` consumers remain compatible
- `ssot graph lineage` still emits offline standalone HTML
- the graph supports network, top-down lineage, proof chain, release boundary, origin, packs/contracts, and validation drift modes
- ADR/SPEC/entity origins are structurally represented and visually distinguishable
- governance packs and `ssot-pack-contracts` are first-class visible graph concepts
- selected node inspection exposes summary, origin, source, proof, packs, release/boundary, validation, and connected edge details
- the component works for small demo graphs and high-volume registries with clear performance behavior
- website teams can embed the component without coupling the package to React Router
- SEO/AEO/AiEO teams can use safe structured summaries without exposing private raw payloads
- DevRel can generate, demo, and export a graph using uv and pip workflows
- package, CLI, and parity tests pass

## Open Decisions

1. Should the package implement a real WebGL renderer, or should renderer reporting be corrected to canvas until WebGL exists?
2. Should proof chain mode be hard-coded by SSOT family order or driven by payload-provided edge semantics?
3. Should group/envelope rendering be computed in Python, React, or both?
4. Which fields define a complete proof chain for each release tier?
5. Should standalone HTML support persistent local view state, or should it remain stateless except for embedded bootstrap state?
6. Should website JSON-LD helpers live in this package or in the product portfolio website package?
7. What is the maximum supported public payload size for website embedding versus local standalone HTML?
8. Which governance pack and `ssot-pack-contracts` identifiers are canonical enough to appear in public copy?

## Immediate Next Steps

1. Add payload vNext fixtures that include origins, proof fields, validation status, governance packs, and pack contracts.
2. Extend TypeScript types with optional fields while preserving existing payload compatibility.
3. Update `_lineage_payload()` to emit structured origin, proof, pack, and validation metadata where registry data already exists.
4. Add inspector sections for origin, proof, packs/contracts, validation, and release/boundary context.
5. Add proof chain and origin modes first, because they directly address the highest-value website and DevRel story.
6. Add packs/contracts mode next, because it turns governance packs and `ssot-pack-contracts` into visible product portfolio surfaces.
7. Run package and CLI parity tests, then regenerate a real standalone graph artifact for review.
