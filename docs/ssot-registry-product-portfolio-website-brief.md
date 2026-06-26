# SSOT Registry Product Portfolio Website Brief

Research date: 2026-06-22

Audience: copywriting, technical writing, and developer relations teams updating `ssot-registry.com`.

Scope: repo-grounded product and website brief based on the local `ssot-registry` and `ssot-registry-com` repositories. This brief is not a live-web audit and does not claim that the public site is currently deployed with the exact repo contents.

## Executive Summary

SSOT Registry is a governed software-assurance registry and toolchain. Its core public promise should be:

> SSOT Registry keeps decisions, specifications, features, tests, claims, evidence, frozen boundaries, and releases in one canonical registry so teams can validate, prove, certify, promote, and publish release state without reconstructing truth from tickets, docs, and CI logs.

The product portfolio website should present SSOT Registry as a practical developer and release-operations system, not as generic documentation tooling. The strongest story is a workflow:

1. Establish decision authority through ADRs and SPECs.
2. Create targetable feature and profile scope.
3. Link tests, claims, and evidence into a proof chain.
4. Freeze a boundary so release scope cannot silently drift.
5. Certify, promote, and publish a release against that frozen boundary.
6. Export reports, graphs, snapshots, and website/discovery content as derived projections.

The existing website repo already has a serious content system: Vite + React, MdWrk lander packages, a private `@ssot-registry/site-content-pack`, generated sitemap/discovery artifacts, `llms.txt`, structured-data graph, content audit, component traceability, and a 3,840-page generated corpus plan. The update should refine the product portfolio and cornerstone pages rather than rebuild the host.

The biggest immediate gaps are:

- The website content pack does not currently represent all product surfaces. It includes `ssot-registry`, `ssot-core`, `ssot-cli`, `ssot-conformance`, `ssot-pack-contracts`, `ssot-contracts`, `ssot-views`, `ssot-codegen`, and `ssot-tui`, but it omits `ssot-mcp` and the npm package `@ssot-registry/lineage-graph`.
- The website should not market "3,840 pages" as a value proposition. It should use the matrix and corpus plan to generate a broad content surface while presenting user-facing entry points as product, workflow, package, docs, learning, and reference paths.
- The root product README still has stale schema copy and badges for `0.7.0`, while the live `.ssot/registry.json` and package READMEs show schema `0.8.0`.
- The generated content corpus is broad, but some template language needs copy polish, especially singular/plural wording such as "Evidence matter" and repeated direct-answer phrasing.
- The current site navigation is compact: Features, Proof, Packages, FAQ. A product portfolio site should make Workflows, API/CLI Reference, Governance Packs, MCP/Automation, TUI Review, and Lineage Graph easier to find.
- The current website app uses direct path lookup in `src/App.tsx`; `react-router` is not present in `package.json`. The target site should be a true multi-page application using React Router, canonical slugs, canonical URLs, layout slots, route-level metadata, and generated route registration from the content pack.
- The current image asset plan defines prompts, but the website public asset folder does not contain those named content images. The product repo already has usable CLI/TUI screenshots and a technical marketing graphic that can be reused or linked.

## Stakeholder Requirements Added To This Brief

These are implementation requirements for the next website update, not optional copy preferences.

- Present `uv`-based operations and/or `pip` operations. Do not publish install guidance that only works for one Python package manager.
- Use the 3,840-page matrix and corpus plan as implementation infrastructure. Do not make the public site brag that it "has 3,840 pages."
- Generate and maintain `llms.txt`, `robots.txt`, `sitemap.xml`, nested sitemaps, a structured-data graph, and JSON-LD output.
- Build a true React multi-page app using React Router, canonical slugs, canonical URLs, layout slots, and route-level page metadata.
- Target 10/10 SEO, 10/10 AEO, and 10/10 AiEO quality gates.
- Discern ADR/SPEC origins instead of flattening `ssot-core`, `ssot-origin`, `repo-local`, and `extension-pack` documents into one public category.
- Present `ssot-pack-contracts` and governance packs as first-class portfolio content.

## Repositories Researched

### `ssot-registry`

Purpose: product/toolchain monorepo.

Key files inspected:

- `README.md`
- `pyproject.toml`
- `.ssot/registry.json`
- `pkgs/*/pyproject.toml`
- `pkgs/*/README.md`
- `pkgs/ssot-core/src/ssot_registry`
- `pkgs/ssot-cli/src/ssot_cli`
- `.github/workflows/prepare-release.yml`
- `.github/workflows/release.yml`
- `packages/ssot-lineage-graph/package.json`
- `packages/ssot-lineage-graph/README.md`
- `examples/README.md`
- `examples/formats-and-exports.md`
- `assets/`
- `pkgs/ssot-cli/assets/`
- `pkgs/ssot-tui/assets/`

### `ssot-registry-com`

Purpose: public product site host and content pack.

Key files inspected:

- `README.md`
- `package.json`
- `site.manifest.json`
- `src/App.tsx`
- `packages/site-content-pack/package.json`
- `packages/site-content-pack/README.md`
- `packages/site-content-pack/src/index.ts`
- `packages/site-content-pack/src/content/*.ts`
- `packages/site-content-pack/artifacts/content-plan.json`
- `packages/site-content-pack/artifacts/site-content-pack-audit.md`
- `packages/site-content-pack/artifacts/component-traceability-matrix.md`
- `public/content-index.json`
- `public/sitemap-tree.json`
- `public/structured-data-graph.json`
- `public/llms.txt`
- `public/robots.txt`
- `public/sitemap.xml`

## Verified Product Facts

Use these as the source facts for public content. Refresh counts before publication if they will appear on the live site.

- Product repo: `groupsum/ssot-registry`
- Website repo: `groupsum/ssot-registry-com`
- Public site host in manifest: `ssot-registry.com`
- Site kind: `mdwrk-lander`
- Website deployment model in manifest: self-hosted Docker behind nginx-proxy-manager, DNS through Namecheap via `npmctl`
- Canonical registry artifact: `.ssot/registry.json`
- Live registry schema in `.ssot/registry.json`: `0.8.0`
- Live repo registry counts from `.ssot/registry.json`:
  - ADRs: 90
  - Specs: 99
  - Features: 407
  - Profiles: 3
  - Tests: 355
  - Claims: 1,376
  - Evidence rows: 642
  - Issues: 19
  - Risks: 0
  - Boundaries: 27
  - Releases: 20
- Feature planning state:
  - Current: 367
  - Next: 29
  - Explicit: 9
  - Backlog: 2
- Feature implementation state:
  - Implemented: 405
  - Partial: 2
- Claim tiers:
  - T0: 407
  - T1: 383
  - T2: 425
  - T3: 161
- Release statuses:
  - Draft: 2
  - Candidate: 1
  - Certified: 3
  - Published: 14
- Python package support range: Python `>=3.10,<3.15`
- Most current Python packages use Apache-2.0 and "Development Status :: 3 - Alpha"
- Primary CLI executable to prefer in new docs: `ssot`
- Compatibility CLI aliases: `ssot-cli`, `ssot-registry`
- ADR origins in the current product registry:
  - `ssot-core`: 52 ADRs
  - `ssot-origin`: 38 ADRs
- SPEC origins in the current product registry:
  - `ssot-core`: 57 specs
  - `ssot-origin`: 42 specs
- Supported document origins in the model include `ssot-core`, `ssot-origin`, `repo-local`, and `extension-pack`.

## Install And Operation Guidance

Public docs and website examples should support both `uv` and `pip` paths. Use `uv` where the audience is a modern Python application team; use `python -m pip` where the audience is browsing PyPI, copying from package READMEs, or installing a command-line tool globally into an existing Python environment.

Recommended install examples:

```bash
uv add ssot-registry
python -m pip install ssot-registry
```

Optional surfaces:

```bash
uv add "ssot-registry[mcp]"
uv add "ssot-registry[tui]"
uv add "ssot-registry[all]"

python -m pip install "ssot-registry[mcp]"
python -m pip install "ssot-registry[tui]"
python -m pip install "ssot-registry[all]"
```

Focused package installs:

```bash
uv add ssot-cli
uv add ssot-core
uv add ssot-conformance
uv add ssot-contracts
uv add ssot-pack-contracts
uv add ssot-mcp
uv add ssot-tui

python -m pip install ssot-cli
python -m pip install ssot-core
python -m pip install ssot-conformance
python -m pip install ssot-contracts
python -m pip install ssot-pack-contracts
python -m pip install ssot-mcp
python -m pip install ssot-tui
```

Use `ssot` in workflow commands:

```bash
ssot init .
ssot validate .
ssot feature list .
ssot boundary freeze . --boundary-id <boundary-id>
ssot release certify . --release-id <release-id>
```

The compatibility names `ssot-cli` and `ssot-registry` can be mentioned once per reference page, but new tutorials should not lead with them.

## Core Positioning

### Primary Position

SSOT Registry is a governed single source of truth for software assurance and release readiness.

It gives engineering teams a canonical registry for decision records, specifications, feature scope, tests, claims, evidence, boundaries, and releases. The registry is machine-readable, validated, and exportable, so release reviewers and automation can inspect the same authority trail.

### Short Positioning Options

- "A governed release-readiness registry for software teams."
- "Canonical software assurance from ADR to published release."
- "One registry for scope, proof, and release authority."
- "Freeze scope. Prove claims. Certify releases."
- "Turn software assurance from scattered evidence into a validated registry."

### Homepage H1 Direction

For a product portfolio website, the first viewport should make the product name unmistakable. Recommended H1 pattern:

```text
SSOT Registry
```

Supporting headline:

```text
Ship from a registry that proves the release.
```

Supporting copy:

```text
SSOT Registry keeps ADRs, SPECs, features, claims, tests, evidence, frozen boundaries, and releases in one canonical `.ssot/registry.json` authority file so teams can validate scope and proof before release decisions depend on them.
```

### What It Replaces

The website should be explicit about the pain it solves:

- Release scope tracked in spreadsheets, tickets, or issue comments.
- Architecture decisions separated from implementation units.
- Claims about readiness that are not linked to tests and evidence.
- Release notes treated as authority instead of generated from authority.
- CI logs and proof artifacts that are hard to map back to features.
- Human review processes that cannot tell whether scope changed after certification.

### What It Is Not

Avoid positioning SSOT Registry as:

- A general knowledge base.
- A full project-management suite.
- A compliance certification authority.
- A security scanner.
- A replacement for CI.
- A generic documentation generator.
- A proprietary SaaS control plane.

It is a local, portable, repo-oriented authority model and toolchain. It can feed docs, sites, reports, graphs, and automation, but those outputs are derived projections.

## Messaging Pillars

### Pillar 1: Canonical Authority

Core message:

> `.ssot/registry.json` is the canonical machine-readable source of truth. ADR and SPEC JSON documents are canonical companions. Reports, Markdown, CSV, DOT graphs, SQLite exports, validation reports, snapshots, generated site pages, and discovery files are derived projections.

Copy angle:

- "The registry is the authority. Everything else is a view."
- "Derived pages and reports should be regenerated, not edited as competing truth."
- "Reviewers can inspect the same IDs and links that automation uses."

Technical proof:

- `ssot-core` owns registry load/save, validation, guards, graph builders, reports, snapshots, planning, evidence verification, and release gating.
- `ssot-views` owns derived reports and graph projections.
- The site content pack already encodes canonical-vs-derived editorial guidance.

### Pillar 2: Governed Entity Model

Core message:

> SSOT Registry models the entities that make software assurance reviewable: ADRs, SPECs, features, profiles, tests, claims, evidence, issues, risks, boundaries, and releases.

Plain-language explanation:

- ADRs explain why a decision was made.
- SPECs define the normative or operational contract.
- Features are targetable units of work.
- Profiles group reusable capability or deployment bundles.
- Tests are executable or procedural verification rows.
- Claims state what must be true.
- Evidence points to concrete artifacts supporting claims.
- Issues and risks track blockers or exposure.
- Boundaries freeze scope.
- Releases attest and publish against frozen scope.

Website implication:

- Do not explain these as isolated glossary terms only.
- Show the chain: ADR/SPEC -> feature/profile -> test/claim/evidence -> boundary -> release.

### ADR And SPEC Origin Model

Core message:

> ADRs and SPECs are not all the same kind of document. Their origin determines ownership, mutability, numbering, and how they should be described publicly.

Origin definitions for website and docs teams:

- `ssot-core`: core upstream documents owned by the SSOT core registry itself. These define the internal architecture and core governance rules of the SSOT Registry project.
- `ssot-origin`: public operator templates shipped from `ssot-contracts` for downstream synchronization. These are packaged SSOT-origin documents intended to seed or govern downstream repositories.
- `repo-local`: documents authored by an adopting repository in its own local range. These should be presented as local project decisions and requirements, not SSOT upstream canon.
- `extension-pack`: documents supplied by installable governance packs through the `ssot-pack-contracts` API. These must include pack source metadata and should be described as governed pack content.

Current repo evidence:

- This product repo currently contains `ssot-core` and `ssot-origin` ADR/SPEC rows.
- The model and validators also support `repo-local` and `extension-pack` origins for downstream repositories and governance packs.

Website implications:

- Do not say "SSOT Registry ADRs" when the real distinction is upstream core ADRs, public SSOT-origin templates, repo-local ADRs, or extension-pack ADRs.
- On governance-pack pages, explicitly use "extension-pack ADRs and SPECs" or "pack-sourced ADR/SPEC content."
- On quickstart pages, explain that adopting repos create `repo-local` ADRs and SPECs unless they are syncing packaged upstream or extension-pack content.
- On concept pages, make origin a visible filter or table column where ADRs/SPECs are shown.

### Pillar 3: Boundary and Release Separation

Core message:

> Boundaries freeze scope. Releases certify, promote, publish, or revoke against that frozen scope.

Why it matters:

- Without this distinction, releases look redundant.
- With this distinction, late scope changes cannot silently rewrite what was certified.

Recommended copy:

```text
A boundary freezes the feature and profile set a delivery unit will be judged against. A release references that frozen boundary, then carries the claims, evidence, certification, promotion, publication, or revocation state used for review.
```

### Pillar 4: Proof Chains

Core message:

> Claims should not stand alone. Claims need tests and evidence, and evidence should point to concrete artifacts.

Recommended copy:

```text
Claims say what should be true. Tests verify behavior. Evidence records the artifact that supports the claim. Certification checks that these links exist, match the required tier, and satisfy the frozen release scope.
```

Technical proof:

- `ssot claim evaluate`
- `ssot evidence verify`
- `ssot test run`
- `ssot boundary run-tests`
- `ssot release certify`

### Pillar 5: Operator Workflow

Core message:

> The product is most understandable when explained as an operating path, not as a package taxonomy.

Recommended workflow:

```text
ssot init .
ssot validate .
ssot adr sync .
ssot spec sync .
ssot feature list .
ssot test run .
ssot claim evaluate .
ssot evidence verify .
ssot boundary freeze .
ssot release certify .
ssot release promote .
ssot release publish .
```

Not every quickstart should ask a new user to perform release certification immediately. For the homepage, present the end-to-end path as the system's shape, then provide a smaller first-run:

```text
uv add ssot-registry
python -m pip install ssot-registry
ssot init .
ssot validate .
ssot feature list .
```

The site currently uses `uv add ssot-registry`. Keep `uv` for modern Python workflows, but include `python -m pip install ...` because the product README uses it and PyPI users expect it.

### Pillar 6: Portable Product Surfaces

Core message:

> SSOT Registry is a portfolio of interoperable packages, not one monolith.

Use a package chooser that starts with the user's job:

- "I need one install target." -> `ssot-registry`
- "I need CLI workflows." -> `ssot-cli`
- "I need Python APIs." -> `ssot-core`
- "I need reusable conformance checks." -> `ssot-conformance`
- "I need schemas and templates." -> `ssot-contracts`
- "I need governance-pack contracts." -> `ssot-pack-contracts`
- "I need derived reports or graph exports." -> `ssot-views`
- "I need generated contract metadata." -> `ssot-codegen`
- "I need Codex or MCP coordination." -> `ssot-mcp`
- "I need a terminal browser for review." -> `ssot-tui`
- "I need an embeddable lineage graph viewer." -> `@ssot-registry/lineage-graph`

## Product Portfolio Matrix

### `ssot-registry`

Current version in repo: `0.2.24`

Role:

- Umbrella Python distribution.
- Installs `ssot-core`, `ssot-cli`, `ssot-contracts`, and `ssot-pack-contracts`.
- Optional extras add MCP and TUI surfaces.

Install copy:

```bash
uv add ssot-registry
uv add "ssot-registry[mcp]"
uv add "ssot-registry[tui]"
uv add "ssot-registry[all]"

python -m pip install ssot-registry
python -m pip install "ssot-registry[mcp]"
python -m pip install "ssot-registry[tui]"
python -m pip install "ssot-registry[all]"
```

Best for:

- Teams that want one "install SSOT" target.
- Operators starting from the public product site.

Public message:

> Use `ssot-registry` when you want the full local operator bundle for registry initialization, validation, proof review, and release closure.

### `ssot-core`

Current version in repo: `0.2.24`

Role:

- Core Python runtime and import package.
- Owns the canonical `ssot_registry` module.
- Provides registry model, APIs, validators, guards, planning, evidence verification, graph export, report/snapshot generation, and release workflow operations.

Best for:

- Python applications embedding SSOT behavior.
- Tooling that needs to read, mutate, validate, or export registries without shelling out.

Public message:

> Use `ssot-core` when your application needs the same registry APIs and validation rules that the CLI uses.

### `ssot-cli`

Current version in repo: `0.1.18`

Role:

- Primary command-line distribution.
- Installs equivalent console scripts: `ssot`, `ssot-cli`, and `ssot-registry`.
- Implements the end-user command surface, structured output, and file-output conventions.

Best for:

- CI jobs.
- Local operators.
- Release workflows.
- DevRel tutorials.

Public message:

> Use `ssot-cli` when automation needs explicit commands for validation, linking, boundary freeze, proof checks, registry export, graph export, and release certification.

Commands to feature:

```bash
ssot validate .
ssot test run .
ssot claim evaluate .
ssot evidence verify .
ssot boundary freeze .
ssot release certify .
ssot registry export .
ssot graph export .
```

### `ssot-conformance`

Current version in repo: `0.2.24`

Role:

- Reusable conformance harness and pytest plugin.
- Provides portable case families for registry, document, ID, SPEC-to-ADR, feature-to-SPEC, proof-chain, and boundary/release concerns.
- Can emit machine-readable evidence output for later SSOT evidence ingestion and status synchronization.

Best for:

- Downstream repos adopting SSOT.
- Teams that need repeatable proof before evidence is trusted.

Public message:

> Use `ssot-conformance` when a repo needs portable checks that can become evidence for governed claims.

### `ssot-contracts`

Current version in repo: `0.2.24`

Role:

- Canonical artifact package.
- Ships schemas, registry templates, packaged ADR/SPEC manifests, and generated Python metadata.

Best for:

- Tooling that needs stable schema and template resources without the full CLI.
- Internal packages that consume canonical contract metadata.

Public message:

> Use `ssot-contracts` when you need packaged schemas, registry templates, and generated contract metadata.

Representative artifacts:

- `registry.schema.json`
- `validation.report.schema.json`
- `certification.report.schema.json`
- `graph.export.schema.json`
- `boundary.snapshot.schema.json`
- `release.snapshot.schema.json`
- `published.snapshot.schema.json`

### `ssot-pack-contracts`

Current version in repo: `0.2.23`

Role:

- Shared contract layer for installable SSOT governance packs.
- Defines pack identity, compatibility, trust metadata, document manifests, document readers, and fail-closed validation.

Best for:

- Governance-pack authors.
- Repos importing governed ADR/SPEC content into reserved ranges.

Public message:

> Use `ssot-pack-contracts` when external governance packs need a stable API for declaring trusted ADR and SPEC resources.

Important nuance:

- Governance packs are not loose documentation bundles.
- They expose metadata and manifests that `ssot pack inspect`, `ssot pack preflight`, and `ssot pack sync` can evaluate before registry mutation.

### Governance Packs

Role:

- Installable packages that ship governed ADR and SPEC content through the `ssot-pack-contracts` API.
- Provide pack identity, compatibility, trust metadata, document manifests, packaged resources, source metadata, and reserved-range behavior.
- Let downstream repos import governed content without copying loose documents or bypassing registry validation.

Current examples named by `ssot-pack-contracts` README:

- `seo-aeo-aieo-governance-pack`
- `cache-freshness-governance-pack`
- `digital-signature-governance-pack`

Public message:

> Governance packs are installable policy and decision packs. SSOT Registry can inspect, preflight, and sync their declared ADR/SPEC documents into governed registry ranges while preserving source, origin, trust, and compatibility metadata.

Commands to feature:

```bash
ssot pack inspect <import-package>
ssot pack preflight . <import-package>
ssot pack sync . <import-package> --trust --yes
```

Copy requirements:

- Always connect governance packs to `ssot-pack-contracts`.
- Explain that extension-pack documents are origin-aware and should preserve `source_pack_id`, `source_package_name`, `source_document_kind`, and `source_document_id`.
- Explain that pack sync must preflight compatibility before mutation.
- Explain that pack trust is explicit and should not be implied.
- Explain that imported documents are governed ADR/SPEC material, not ordinary blog posts or free-form docs.

### `ssot-views`

Current version in repo: `0.2.24`

Role:

- Derived report and graph projection library.
- Builds validation reports, certification reports, summaries, graph JSON, and graph DOT.

Best for:

- Teams building reporting, analysis, or export tooling around SSOT registries.

Public message:

> Use `ssot-views` when you need reusable derived reports or graph exports while keeping `.ssot/registry.json` authoritative.

### `ssot-codegen`

Current version in repo: `0.2.24`

Role:

- Development-time generator package.
- Regenerates Python-side metadata artifacts derived from `ssot-contracts`.

Best for:

- Maintainers of the SSOT workspace.
- Release tooling that regenerates contract indexes, CLI metadata, TUI metadata, and generated constants.

Public message:

> Use `ssot-codegen` when maintaining SSOT package metadata and generated contract artifacts. Most application users do not need it directly.

### `ssot-mcp`

Current version in repo: `0.1.6`

Current website gap:

- Missing from `packages/site-content-pack/src/content/packages.ts`.

Role:

- Optional Model Context Protocol server.
- Lets MCP-capable clients coordinate registry mutations, pull-worker campaigns, leases, worker events, and campaign state through tools backed by `ssot-core`.

Best for:

- Codex or other MCP-capable clients.
- Worker campaigns that pull scoped maturation slices.
- Teams that want registry mutation through validated tools instead of hand-editing `.ssot/registry.json`.

Public message:

> Use `ssot-mcp` when Codex or another MCP client should coordinate SSOT registry work through validated tools, mirrored CLI command paths, and pull-worker campaign state.

Avoid overclaiming:

- Do not say MCP is required for ordinary SSOT workflows.
- Do not say MCP tools have independent authority outside the registry validation model.
- Do not imply autonomous agents should hand-edit registry JSON.

### `ssot-tui`

Current version in repo: `0.1.18`

Role:

- Textual terminal UI for browsing SSOT registries.
- Read-oriented, browser-first, with safe workflow bridges.

Best for:

- Reviewers who need to inspect registry relationships.
- Operators who prefer terminal navigation over JSON scanning.

Public message:

> Use `ssot-tui` when reviewers need a keyboard-first terminal browser for registry sections, entity details, validation state, and linked resources.

Avoid overclaiming:

- The current implementation does not claim full CRUD parity with the CLI.

### `@ssot-registry/lineage-graph`

Current version in repo: `0.2.24-dev.1`

Current website gap:

- Missing from `packages/site-content-pack/src/content/packages.ts`.

Role:

- Portable React viewer for SSOT lineage graph payloads.
- Exports `LineageGraphApp`.
- Exports `createStandaloneHtml(payload)`, used by Python `ssot-registry graph lineage` to emit an offline HTML artifact.

Best for:

- Embedding registry lineage views in product docs or developer tooling.
- Generating offline HTML review artifacts.

Public message:

> Use `@ssot-registry/lineage-graph` when registry relationships need to be inspected visually in a React app or exported as an offline HTML lineage artifact.

## Recommended Website Information Architecture

The site should stay generated and content-pack driven, but the first-level product story should be less taxonomy-heavy.

Recommended top navigation:

1. Product
2. Workflows
3. Packages
4. Docs
5. Learn
6. GitHub

Recommended homepage sections:

1. Hero: product name, release-readiness value proposition, install and workflow CTAs.
2. First five minutes: install, initialize/validate, inspect records.
3. What it replaces: spreadsheets, unlinked docs, unreviewable proof, CI archaeology.
4. Canonical model: `.ssot/registry.json` plus ADR/SPEC companions.
5. Proof chain: claim -> test -> evidence.
6. Boundary vs release: freeze scope before certifying release state.
7. Product portfolio: package chooser by job.
8. Operator workflows: decision-to-scope, scope-to-freeze, proof-to-certify, promote-to-publish.
9. Automation surfaces: CLI, Python API, MCP, TUI, lineage graph.
10. Governance packs: inspect, preflight, sync.
11. Learn and reference: examples, API/CLI reference, FAQ, glossary.
12. Proof and artifacts: screenshots, graph exports, release snapshots, validation reports.

Recommended cornerstone pages:

- `/product/` or `/`
  - What SSOT Registry is.
  - The release-readiness workflow.
  - The package portfolio.
- `/workflows/`
  - Decision to scope.
  - Scope to freeze.
  - Proof to certify.
  - Promote to publish.
- `/packages/`
  - Package chooser.
  - Install options.
  - Python and npm surfaces.
- `/packages/ssot-mcp/`
  - MCP use cases and limits.
- `/packages/lineage-graph/`
  - React viewer and offline HTML artifact.
- `/proof-model/`
  - Claims, tests, evidence, tiers, verification.
- `/boundary-release/`
  - Boundary vs release.
- `/governance-packs/`
  - `ssot-pack-contracts`, pack metadata, trust, reserved ranges.
- `/cli/`
  - Primary commands, output formats, file output.
- `/python-api/`
  - `ssot_registry.api` examples.
- `/tui/`
  - Reviewer-focused terminal browsing.
- `/learn/`
  - Quickstart, tutorials, release-readiness exercises.

## Current Website Content System

The website repo currently owns:

- Host app: `src/App.tsx`
- Product/content source: `packages/site-content-pack/src/index.ts`
- Package content: `packages/site-content-pack/src/content/packages.ts`
- API content: `packages/site-content-pack/src/content/apis.ts`
- Audiences: `packages/site-content-pack/src/content/audiences.ts`
- Subjects: `packages/site-content-pack/src/content/subjects.ts`
- Sections: `packages/site-content-pack/src/content/sections.ts`
- Page planning: `packages/site-content-pack/src/content/page-plan.ts`
- Page generation: `packages/site-content-pack/src/content/page-corpus.ts`
- Editorial guidance and image prompts: `packages/site-content-pack/src/content/editorial-guidance.ts`
- Audit source: `packages/site-content-pack/src/content/site-content-audit.ts`
- Component traceability: `packages/site-content-pack/src/content/component-traceability.ts`
- Structured data declarations: `packages/site-content-pack/src/content/structured-data.ts`

The content pack currently generates:

- 3,840 detail page plans.
- 12 section index pages.
- A public content index with 3,854 pages.
- `sitemap.xml`
- `sitemap-tree.json`
- `semantic-index.json`
- `structured-data-graph.json`
- `llms.txt`
- `llms-full.txt`
- `robots.txt`

The corpus formula is:

```text
12 sections * 20 subject areas * 4 intents * 4 audiences = 3840 pages
```

Public positioning rule:

- The corpus formula is an internal production and coverage mechanism.
- The public website should not advertise "3,840 pages" as a product benefit.
- The public website should advertise the outcomes made possible by the matrix: complete coverage, canonical slugs, consistent structured data, answer-ready content, workflow paths, package pages, and machine-readable discovery artifacts.

Current section model:

- Features
- Proofs
- Packages
- Packs
- FAQ / QA
- Courses
- Lessons
- Certifications
- API Reference
- Workflows
- Comparisons
- Glossary

Current subject areas:

- ADRs
- Specifications
- Features
- Claims
- Tests
- Evidence
- Boundaries
- Profiles
- Risks
- Issues
- Releases
- Certification
- Promotion
- Publication
- CLI workflows
- Registry schemas
- Conformance
- ADR and SPEC sync
- Graph exports
- Operator guides

Current audiences:

- Developer
- Architect
- Release manager
- Vibe coder

Recommendation:

- Keep the generated corpus but manually strengthen the homepage and section index pages.
- Consider changing "Vibe coder" to "AI-assisted developer" or "AI-assisted builder" for a more professional product portfolio tone, unless the brand intentionally wants the colloquial label.
- Add or replace subject areas so the product surfaces are represented:
  - MCP coordination
  - Lineage graph
  - Governance packs
  - Python API
  - TUI review
  - Release snapshots
  - Validation reports

## Website Architecture Requirements

The current `src/App.tsx` resolves the current page by reading `window.location.pathname`, normalizing it, and finding a matching page in `ssotRegistrySite.pages`. That is a workable static lookup, but the target product portfolio website should be a true React multi-page app.

Required architecture:

- Add React Router, for example `react-router` / `react-router-dom`, and register generated routes from the content pack.
- Preserve canonical slugs from content plans as route paths.
- Emit canonical URLs from the product canonical root plus normalized slug.
- Use route-level metadata for title, description, canonical URL, breadcrumbs, structured-data nodes, and discovery indexes.
- Provide layout slots for hero, body sections, package cards, proof matrices, related APIs, related packages, FAQs, breadcrumbs, side navigation, and footer CTAs.
- Keep generated page data in the content pack rather than hard-coding route bodies in `src/App.tsx`.
- Support section index routes and detail routes as first-class pages.
- Add route-level 404 behavior for unknown slugs.
- Keep generated pages directly addressable by URL and crawlable after build/deploy.

Recommended implementation direction:

```text
content pack pages -> route manifest -> React Router route objects -> LanderPage with named slots -> JSON-LD/head metadata emitter -> discovery artifact generators
```

Minimum route contract:

- `slug`
- `canonicalUrl`
- `title`
- `description`
- `h1`
- `intro`
- `sections`
- `schema`
- `breadcrumbs`
- `relatedPackages`
- `relatedApis`
- `updatedAt` or deterministic generated timestamp policy

The app should keep the MdWrk renderer stack, but route ownership should move from manual path lookup to route objects generated from canonical content data.

## Discovery And Machine-Readable Requirements

Required files and surfaces:

- `robots.txt`
- Root `sitemap.xml`
- Nested sitemap indexes or child sitemap files for major content groups.
- `llms.txt`
- `llms-full.txt`
- `content-index.json`
- `semantic-index.json`
- `sitemap-tree.json`
- `structured-data-graph.json`
- Route-level JSON-LD output.
- Canonical URL tags.
- Open Graph and Twitter/social metadata for key pages.

Nested sitemap guidance:

- Keep a root `sitemap.xml` that either lists all page URLs or points to child sitemap files.
- For scale, prefer child sitemaps by section, such as:
  - `sitemap-content.xml`
  - `sitemap-features.xml`
  - `sitemap-proofs.xml`
  - `sitemap-packages.xml`
  - `sitemap-packs.xml`
  - `sitemap-api-reference.xml`
  - `sitemap-workflows.xml`
  - `sitemap-learn.xml`
- Reference the sitemap index from `robots.txt`.

JSON-LD requirements:

- Emit valid JSON-LD per route, not only a global structured-data graph artifact.
- Use `SoftwareApplication`, `SoftwareSourceCode`, `Product`, `WebPage`, `TechArticle`, `FAQPage`, `QAPage`, `HowTo`, `BreadcrumbList`, `ItemList`, `Dataset`, `ClaimReview`, `Course`, `CourseInstance`, `DefinedTerm`, and `DefinedTermSet` where appropriate.
- Package pages should emit software/product schema.
- Workflow pages should emit `HowTo` and `TechArticle`.
- FAQ and direct-answer pages should emit `FAQPage` or `QAPage`.
- Glossary pages should emit `DefinedTerm` or `DefinedTermSet`.
- Proof pages should emit `ClaimReview` and `Dataset` where the content is actually claim/evidence oriented.

Structured-data graph requirements:

- `structured-data-graph.json` should remain a crawlable, machine-readable inventory of route-level structured-data nodes.
- Node IDs should be stable and derived from canonical slugs.
- The graph should include page path, canonical URL, schema type, and source page.
- The graph should distinguish generated website schema nodes from SSOT registry entities. Do not imply that JSON-LD nodes are registry authority.

## SEO, AEO, And AiEO Quality Gates

The target is 10/10 across SEO, AEO, and AiEO. Treat that as a release gate for the website update.

### SEO 10/10 Criteria

- Every route has one canonical URL.
- Every route has a unique title and meta description.
- Every route has one clear H1.
- Slugs are canonical, lowercase, stable, and human-readable.
- Section index pages expose crawlable links to detail pages.
- Root and nested sitemaps are generated and referenced from `robots.txt`.
- Important package and workflow pages are no more than two clicks from the homepage.
- Package pages include install commands, repository links, package role, and related package links.
- No route presents duplicate generic copy as its only substantive content.
- Social metadata exists for homepage and key portfolio pages.

### AEO 10/10 Criteria

- Each concept, package, command, and workflow page begins with a direct answer.
- FAQ/Q&A pages answer one concrete question before expanding.
- Answers include operational next steps, not only definitions.
- Boundary/release, claim/test/evidence, canonical/derived, and ADR-origin distinctions are answerable in one or two paragraphs.
- Pages include "best for" and "not for" blocks where users are choosing packages or workflows.
- Generated content avoids circular explanations such as "Explain X and identify the next command-backed step" as visible copy.

### AiEO 10/10 Criteria

- `llms.txt` and `llms-full.txt` are regenerated from canonical page metadata.
- `semantic-index.json` includes stable page IDs, canonical URLs, summaries, topics, audiences, related packages, related APIs, and schema intents.
- Package and command facts are written in short, extractable sentences.
- Pages state whether a surface is core, optional, derived, read-oriented, or development-time.
- ADR/SPEC origin language is explicit enough for agents to avoid confusing upstream, repo-local, and extension-pack documents.
- Governance-pack content includes trust, origin, reservation, manifest, and sync semantics.
- AI/MCP language is bounded: MCP coordinates through validated tools and does not replace registry authority.

Recommended scorecard output:

```text
SEO: 10/10 only if canonical URLs, slugs, sitemap coverage, metadata uniqueness, and crawl paths are complete.
AEO: 10/10 only if direct answers, FAQs, comparison blocks, package chooser copy, and next actions are complete.
AiEO: 10/10 only if llms files, semantic index, structured-data graph, JSON-LD, and extractable operational facts are complete.
```

## File-Level Recommendations For Website Team

### `package.json`

Update required.

Actions:

- Add React Router dependencies if the team adopts the required routing model:

```bash
npm install react-router react-router-dom
```

- Keep MdWrk lander packages as the rendering layer.
- Add route/discovery validation scripts if they do not already exist.
- Keep `npm run build`, `npm run check`, and content-pack tests as release gates.

### `src/App.tsx`

Update required.

Actions:

- Replace manual `window.location.pathname` page lookup with React Router route registration.
- Generate route objects from `ssotRegistrySite.pages` or a route manifest exported by `@ssot-registry/site-content-pack`.
- Preserve `LanderPage` rendering, but pass route-resolved page data through layout slots.
- Add 404 and canonical redirect behavior for non-canonical slugs if needed.
- Ensure page-level metadata and JSON-LD can be emitted per route.

### `packages/site-content-pack/src/content/page-corpus.ts`

Update required.

Actions:

- Export a route manifest with canonical slugs, canonical URLs, breadcrumbs, metadata, and schema nodes.
- Keep the 3,840-page corpus as an implementation plan, but avoid public-facing copy that markets page count.
- Add route grouping metadata for nested sitemap generation.
- Add package/workflow priority metadata so key product pages are linked from hub pages and not buried in generated detail routes.

### `packages/site-content-pack/src/content/sitemap-tree.ts`

Update required.

Actions:

- Extend sitemap generation to support nested sitemap indexes or child sitemap files.
- Group sitemaps by section or content family.
- Ensure `robots.txt` references the root sitemap index.

### `packages/site-content-pack/src/content/structured-data.ts`

Update required.

Actions:

- Keep the structured-data type list, but ensure route-level JSON-LD emission maps each page to the correct schema nodes.
- Add validation for package pages, workflow pages, FAQ/Q&A pages, glossary pages, proof pages, and course/lesson pages.
- Ensure `structured-data-graph.json` remains an inventory and does not get mistaken for registry authority.

### `packages/site-content-pack/src/content/packages.ts`

Update required.

Actions:

- Add `ssot-mcp`.
- Add `@ssot-registry/lineage-graph`.
- Consider adding `ssot-mcp` between CLI and TUI, because it is an optional control-plane surface.
- Consider adding lineage graph as an npm package, separate from the Python package grid.
- Add both pip and uv install guidance where appropriate.
- Update package chooser copy to include MCP and lineage graph.

Suggested package details:

```text
ssot-mcp
Role: Optional MCP server for Codex and MCP-capable clients that coordinate registry mutations, worker campaigns, leases, and events through validated tools.
Install: uv add ssot-mcp; uv add "ssot-registry[mcp]"; python -m pip install ssot-mcp; python -m pip install "ssot-registry[mcp]"
Best for: agent-assisted registry workflows and pull-worker campaigns.
Proof point: Uses the same core registry mutation APIs as the CLI, validates before saving, and exposes mirrored CLI command paths.
Primary commands/tools: ssot-mcp --transport stdio --repo <path>; get_ssot_cli_surface; run_ssot_cli; claim_next_maturation_slice.

@ssot-registry/lineage-graph
Role: Portable React viewer for SSOT lineage graph payloads and offline HTML graph artifacts.
Install: npm install @ssot-registry/lineage-graph
Best for: embeddable graph review surfaces and standalone lineage artifacts.
Proof point: Used by Python graph lineage command to produce offline HTML.
Primary APIs: LineageGraphApp; createStandaloneHtml(payload); ssot graph lineage.
```

### `packages/site-content-pack/src/content/apis.ts`

Update recommended.

Actions:

- Add `ssot graph lineage`.
- Add `ssot registry sync-statuses`.
- Add `ssot feature certify-proof-graph` if it remains public in the current CLI surface.
- Make pack commands show required package argument in examples:
  - `ssot pack inspect <package>`
  - `ssot pack preflight <package>`
  - `ssot pack sync <package>`
- Add explicit output descriptions for graph lineage and status sync.

### `packages/site-content-pack/src/content/editorial-guidance.ts`

Update required.

Actions:

- Update `packageChooserCopy` to include `ssot-mcp` and `@ssot-registry/lineage-graph`.
- Add principle: "Do not overclaim release certification as external compliance certification."
- Add principle: "Describe TUI as read-oriented unless a future release adds full CRUD parity."
- Add principle: "Describe MCP as optional control-plane coordination, not the default path."
- Add asset notes pointing to existing repo assets:
  - `assets/ssot-registry-technical-marketing.png`
  - `pkgs/ssot-cli/assets/ssot-cli-help.png`
  - `pkgs/ssot-cli/assets/ssot-cli-boundary-help.png`
  - `pkgs/ssot-tui/assets/ssot-tui-browser.png`
  - `pkgs/ssot-tui/assets/ssot-tui-adrs.png`
  - `pkgs/ssot-tui/assets/ssot-tui-specs.png`
  - `pkgs/ssot-tui/assets/ssot-tui-validated.png`

### `packages/site-content-pack/src/content/subjects.ts`

Update recommended.

Actions:

- Add product-surface subjects or replace lower-value generated subjects.
- Strong additions:
  - MCP coordination
  - Lineage graph
  - Governance packs
  - Python API
  - TUI review
  - Release snapshots
  - Validation reports

Impact:

- Adding subjects increases generated page count. Replacing subjects preserves the 3,840-page formula.
- If the team wants stable page counts, replace weaker subjects rather than expanding the matrix.

### `packages/site-content-pack/src/content/audiences.ts`

Update optional but recommended.

Actions:

- Decide whether "Vibe coder" is acceptable public-site language.
- If not, replace with "AI-assisted developer" or "Builder".
- If retained, define it explicitly so generated copy does not sound casual in enterprise/product contexts.

### `packages/site-content-pack/src/content/page-plan.ts`

Update recommended.

Actions:

- Fix singular/plural grammar for generated subjects:
  - "Evidence matters" instead of "Evidence matter"
  - "Specifications matter" is fine
  - "Tests matter" is fine
  - "Certification matters" or "Certification workflows matter"
- Reduce repeated sentences such as "Explain X and identify the next command-backed SSOT Registry step."
- Add subject-specific verbs so generated descriptions feel less templated.
- Ensure generated answers do not imply every page is equally important.

### `packages/site-content-pack/src/index.ts`

Update required.

Actions:

- Add a homepage card for MCP/automation.
- Add a homepage card for lineage graph or visual review.
- Add a homepage card for governance packs if packs remain a core portfolio surface.
- Consider changing nav from:

```text
Features | Proof | Packages | FAQ
```

to:

```text
Product | Workflows | Packages | Docs | Learn
```

- Keep GitHub as the primary external CTA, but add an install/quickstart CTA in the first viewport.

### Generated Artifacts

Do not edit these directly:

- `public/content-index.json`
- `public/sitemap-tree.json`
- `public/semantic-index.json`
- `public/structured-data-graph.json`
- `public/llms.txt`
- `public/llms-full.txt`
- `public/sitemap.xml`
- `packages/site-content-pack/artifacts/content-plan.json`
- `packages/site-content-pack/artifacts/site-content-pack-audit.md`
- `packages/site-content-pack/artifacts/component-traceability-matrix.md`

Regenerate through existing scripts after content source changes:

```bash
npm --prefix packages/site-content-pack run test
npm run build
npm run check
```

## Copywriter Brief

### Tone

Use precise, practical, release-operator language.

Good:

- "validated registry"
- "frozen scope"
- "proof chain"
- "release readiness"
- "canonical authority"
- "derived projections"
- "repo-local workflow"
- "inspectable evidence"
- "command-backed review"

Avoid:

- "magical truth"
- "automatic compliance"
- "AI does your governance"
- "replaces all docs"
- "guarantees release quality"
- "one click certification"
- "enterprise-grade" unless backed by evidence and support commitments

### Hero Copy Options

Option A:

```text
SSOT Registry
Ship from a registry that proves the release.

Keep decisions, specs, features, tests, claims, evidence, frozen boundaries, and releases in one canonical `.ssot/registry.json` authority file.
```

Option B:

```text
SSOT Registry
One canonical record for release scope and proof.

Freeze delivery scope, verify claims with tests and evidence, certify releases, and publish reviewable authority snapshots from the same registry.
```

Option C:

```text
SSOT Registry
Governed software assurance for repo-local releases.

SSOT Registry turns scattered decisions, requirements, tests, evidence, and release state into a validated registry your team and automation can inspect.
```

### Subhead Options

- "Stop reconstructing release truth from issues, docs, spreadsheets, and CI logs."
- "Make scope, proof, and release state explicit before reviewers depend on them."
- "Keep the registry authoritative and regenerate reports, graphs, snapshots, and site pages from it."

### Value Proposition Blocks

Block 1: Canonical registry

```text
Keep governed software assurance entities in one machine-readable authority file. ADRs, SPECs, features, profiles, tests, claims, evidence, issues, risks, boundaries, and releases stay linked and inspectable.
```

Block 2: Proof-first releases

```text
Release certification is tied to frozen scope, claim tiers, tests, and evidence. If proof links are missing or evidence cannot be trusted, the workflow can fail closed before promotion.
```

Block 3: Developer-native operation

```text
Run SSOT from the command line, embed it through Python APIs, browse it in a terminal UI, coordinate it through MCP, or export graph and report projections for reviewers.
```

Block 4: Portfolio fit

```text
Install the bundle when you want the full operator path, or choose focused packages for core APIs, CLI workflows, conformance, contracts, views, codegen, MCP, TUI review, and lineage visualization.
```

### CTAs

Primary:

- Install SSOT Registry
- Start the release workflow
- Validate a registry

Secondary:

- View package portfolio
- Browse CLI reference
- Open GitHub
- Explore proof model
- See boundary vs release

Avoid vague CTAs:

- Learn more
- Get started now
- Unlock governance

## Technical Writer Brief

### Primary Docs To Create Or Strengthen

1. Quickstart
   - Install with pip and uv.
   - Initialize or validate a repo.
   - Explain `.ssot/registry.json`.
   - Show first useful commands.

2. Concepts
   - Canonical vs derived.
   - ADRs and SPECs as companion authority.
   - Features and profiles.
   - Claims, tests, evidence.
   - Boundaries vs releases.
   - Issues and risks.

3. Package chooser
   - One page per package.
   - Include install command, role, best fit, what it owns, what it does not own.

4. CLI reference
   - Prefer `ssot`.
   - Mention aliases.
   - Document global output flags.
   - Include command purpose, inputs, outputs, and failure behavior.

5. Release workflow guide
   - Decision to scope.
   - Scope to freeze.
   - Proof to certify.
   - Promote to publish.
   - Revoke or repair.

6. Governance pack guide
   - Explain pack metadata.
   - Explain trust and reserved ranges.
   - Show `ssot pack inspect`, `ssot pack preflight`, `ssot pack sync`.

7. MCP guide
   - Explain optional nature.
   - Show repo-pinned server and explicit repo mode.
   - Explain registry write authority.
   - Explain pull-worker campaigns without promising autonomous completion.

8. TUI guide
   - Explain read-oriented browser scope.
   - List supported interactions.
   - Use screenshots.

9. Lineage graph guide
   - Explain graph exports vs lineage viewer.
   - Show React usage.
   - Show offline HTML artifact generation.

10. Migration and schema guide
   - Current schema is `0.8.0`.
   - Explain upgrade reports.
   - Fix stale root README references to `0.7.0` before public reuse.

### Technical Accuracy Rules

- Use `ssot` in new docs; mention `ssot-registry` as compatibility alias.
- Say `.ssot/registry.json` is canonical.
- Say ADR/SPEC JSON companions are canonical companions.
- Say generated pages, Markdown, reports, snapshots, CSV, DOT, SQLite, and graph outputs are derived.
- Say release certification is an SSOT workflow state, not external compliance certification.
- Say `ssot-tui` is read-oriented unless its current implementation changes.
- Say `ssot-mcp` is optional and built on the same core registry APIs.
- Include Python version support: `>=3.10,<3.15`.
- Include package development status honestly if surfaced: alpha.

### Docs Acceptance Criteria

- Package inventory includes every Python and npm package in the current product repo.
- Schema references agree with `.ssot/registry.json` and package READMEs.
- Every command example is either verified against the current CLI README/source or marked illustrative.
- Every product page has "best for" and "not for" guidance.
- Generated content does not make claims stronger than package READMEs.

## Developer Relations Brief

### Demo Narrative

Use a demo that starts with a repo that has scattered release facts, then turns it into a registry-backed workflow.

Suggested demo sequence:

1. Install.

```bash
python -m pip install ssot-registry
```

2. Initialize or inspect.

```bash
ssot init .
ssot validate .
```

3. Show entities.

```bash
ssot feature list .
ssot claim list .
ssot test list .
ssot evidence list .
```

4. Show proof checks.

```bash
ssot test run . --id <test-id>
ssot claim evaluate . --claim-id <claim-id>
ssot evidence verify . --evidence-id <evidence-id>
```

5. Show scope and release.

```bash
ssot boundary freeze . --boundary-id <boundary-id>
ssot release certify . --release-id <release-id> --write-report
ssot release promote . --release-id <release-id>
ssot release publish . --release-id <release-id>
```

6. Show exports.

```bash
ssot registry export . --format json
ssot graph export . --format dot
ssot graph lineage .
```

### Tutorial Ideas

- "Why boundaries are not releases."
- "How claims, tests, and evidence work together."
- "Build a release-readiness registry in 15 minutes."
- "Export a lineage graph from a governed registry."
- "Use SSOT Registry in CI without hand-editing JSON."
- "When to install `ssot-registry` vs `ssot-cli` vs `ssot-core`."
- "Use `ssot-mcp` with Codex for registry-safe worker campaigns."
- "Author a governance pack with `ssot-pack-contracts`."

### DevRel Assets

Use current repo assets:

- Technical marketing graphic: `assets/ssot-registry-technical-marketing.png`
- CLI help screenshot: `pkgs/ssot-cli/assets/ssot-cli-help.png`
- Boundary help screenshot: `pkgs/ssot-cli/assets/ssot-cli-boundary-help.png`
- TUI browser screenshot: `pkgs/ssot-tui/assets/ssot-tui-browser.png`
- TUI ADR screenshot: `pkgs/ssot-tui/assets/ssot-tui-adrs.png`
- TUI spec screenshot: `pkgs/ssot-tui/assets/ssot-tui-specs.png`
- TUI validation screenshot: `pkgs/ssot-tui/assets/ssot-tui-validated.png`
- Existing website social card: `public/ssot-registry-social-card.png` in `ssot-registry-com`

Asset production gap:

- `packages/site-content-pack/src/content/editorial-guidance.ts` references planned content image paths such as `/content/images/ssot-registry-hero-canonical-flow.webp`, but the inspected `public/` folder does not contain a `content/images` tree.
- Either produce those assets or revise the asset plan to use existing screenshots and marketing graphics.

### DevRel Acceptance Criteria

- Demos show a real command path, not only conceptual screenshots.
- Tutorials use `ssot` as the primary command.
- Every release-readiness claim maps to a registry entity or command.
- The MCP story is framed as optional coordination for MCP-capable clients.
- The TUI story is framed as read-first inspection.
- Lineage graph content shows both React usage and offline HTML artifact use.

## Website Implementation Work Plan

### Phase 1: Correctness

Priority: highest.

Tasks:

- Update root product README schema references from `0.7.0` to `0.8.0` before reusing README content publicly.
- Add missing portfolio surfaces in website content: `ssot-mcp` and `@ssot-registry/lineage-graph`.
- Update package chooser copy to include all product surfaces.
- Update install examples to show `uv` and `python -m pip` paths where appropriate.
- Add ADR/SPEC origin distinctions to concept, pack, and quickstart pages.
- Add graph lineage and status sync commands where relevant.
- Fix generated grammar issues.
- Regenerate content artifacts.

### Phase 2: Portfolio Pages

Priority: high.

Tasks:

- Build a package portfolio hub.
- Build focused package detail pages.
- Split Python package surfaces from npm lineage-graph surface visually.
- Add "best for" and "not for" guidance.
- Add install commands and first useful commands.

### Phase 3: Workflow Pages

Priority: high.

Tasks:

- Add React Router route registration from the content pack route manifest.
- Add canonical slugs, canonical URLs, route-level metadata, layout slots, and 404 handling.
- Add route-level JSON-LD emission for generated and hand-curated pages.
- Add nested sitemap generation and `robots.txt` sitemap references.
- Create or strengthen workflow pages for:
  - Decision to scope.
  - Scope to freeze.
  - Proof to certify.
  - Promote to publish.
  - Governance pack preflight and sync.
  - MCP worker campaign.
  - TUI review.
  - Lineage graph export.

### Phase 4: Editorial Polish

Priority: medium.

Tasks:

- Manually polish the homepage, content hub, and section index pages.
- Reduce generated repetition.
- Replace or define "Vibe coder."
- Make release certification language precise.
- Ensure every public claim has command, file, package, or artifact support.

### Phase 5: Visual And Discovery

Priority: medium.

Tasks:

- Decide whether to use generated hero imagery, existing screenshots, or both.
- Add actual content images if the asset plan stays.
- Regenerate `sitemap.xml`, `llms.txt`, content index, semantic index, and structured-data graph.
- Run content pack test/build/check scripts.

## Safe Public Claims

These claims are supported by the repo.

- SSOT Registry provides a canonical registry for ADRs, SPECs, features, profiles, tests, claims, evidence, issues, risks, boundaries, and releases.
- `.ssot/registry.json` is the canonical machine-readable registry.
- Generated views, reports, graphs, snapshots, Markdown, CSV, DOT, SQLite, and site pages are derived projections.
- Boundaries freeze feature/profile scope.
- Releases reference frozen boundaries and carry claim/evidence membership for certification, promotion, publication, or revocation workflows.
- `ssot-cli` installs `ssot`, `ssot-cli`, and `ssot-registry` as equivalent executables.
- `ssot-core` owns the canonical Python import package `ssot_registry`.
- `ssot-mcp` is optional and for MCP-capable clients and pull-worker coordination.
- `ssot-tui` is a read-oriented Textual terminal browser for registry inspection.
- `@ssot-registry/lineage-graph` is a portable React viewer for lineage graph payloads and standalone HTML artifacts.
- The website repo is a standalone MdWrk lander with generated content, structured data, sitemap, LLM files, and discovery artifacts.

## Claims To Avoid Or Qualify

Avoid:

- "SSOT Registry guarantees compliance."
- "SSOT Registry certifies your software for external auditors."
- "SSOT Registry replaces CI."
- "SSOT Registry replaces all docs."
- "MCP is required for registry workflows."
- "The TUI can perform every CLI mutation."
- "Governance packs are trusted automatically."
- "All generated website pages are hand-authored."
- "Release certification means public release quality is guaranteed."

Qualify:

- "Certification" as "SSOT release certification workflow" or "registry certification gate."
- "Authority" as repo-local canonical authority, not organizational omniscience.
- "Evidence" as linked artifacts/rows, not independent proof of legal compliance.
- "AI" as optional MCP-capable coordination, not autonomous governance.

## Suggested Website Copy Blocks

### Package Chooser

```text
Choose the smallest surface that matches the job. Install `ssot-registry` for the full local operator bundle. Install `ssot-cli` for command-line automation, `ssot-core` for Python APIs, `ssot-conformance` for reusable proof checks, `ssot-contracts` for schemas and templates, `ssot-pack-contracts` for governance-pack authoring, `ssot-views` for reports and graph projections, `ssot-codegen` for derived metadata regeneration, `ssot-mcp` for MCP-capable coordination, `ssot-tui` for terminal review, and `@ssot-registry/lineage-graph` for embeddable graph visualization.
```

### Boundary vs Release

```text
A boundary freezes the scope a delivery unit will be judged against. A release references that frozen boundary and carries the claims, evidence, certification, promotion, publication, or revocation state. This split keeps scope changes from silently rewriting what was certified.
```

### Proof Chain

```text
Claims state what must be true. Tests verify behavior. Evidence records the artifact that supports the claim. SSOT Registry keeps those links inspectable so release review can fail closed when proof is missing or stale.
```

### MCP

```text
`ssot-mcp` lets Codex and other MCP-capable clients coordinate registry-safe work through validated tools, mirrored CLI command paths, pull-worker leases, worker events, and campaign status. Ordinary CLI and Python workflows do not require MCP.
```

### TUI

```text
`ssot-tui` gives reviewers a keyboard-first terminal browser for registry sections, linked entity details, validation state, and safe read previews. It is designed for inspection first, with the CLI remaining the complete workflow surface.
```

### Lineage Graph

```text
`@ssot-registry/lineage-graph` renders SSOT lineage payloads in React and powers standalone HTML graph artifacts from the Python graph lineage workflow.
```

## Open Questions For The Website Team

- Should the site keep "Vibe coder" as a public audience label, or replace it with "AI-assisted developer"?
- Should exact live registry counts appear on the website, or should they stay internal to docs and audits because they drift?
- Should package detail pages live under `/packages/<package>/` or remain generated under the current section matrix?
- Should `@ssot-registry/lineage-graph` be placed in the same package grid as Python packages, or in a separate "visualization" product band?
- Should "Certifications" pages remain if users may confuse them with professional credentials?
- Should the website produce the planned `/content/images/*.webp` assets or reuse current CLI/TUI screenshots and marketing graphic?

## Verification Checklist Before Publishing

Run from `ssot-registry-com` after content edits:

```bash
npm --prefix packages/site-content-pack run test
npm run build
npm run check
```

Confirm:

- Homepage renders with updated package portfolio.
- Package grid includes `ssot-mcp`.
- Package grid or visualization section includes `@ssot-registry/lineage-graph`.
- React Router routes resolve canonical slugs and canonical URLs.
- Route-level JSON-LD is emitted for homepage, package, workflow, FAQ, glossary, and proof pages.
- Root `sitemap.xml`, nested sitemaps, `robots.txt`, `llms.txt`, `llms-full.txt`, `semantic-index.json`, and `structured-data-graph.json` are regenerated.
- SEO, AEO, and AiEO scorecards each meet 10/10 before publication.
- Public pages use the corpus matrix for coverage without advertising the raw 3,840-page count as the value proposition.
- ADR/SPEC pages distinguish `ssot-core`, `ssot-origin`, `repo-local`, and `extension-pack` origins.
- Governance-pack pages explain `ssot-pack-contracts`, trust, manifests, reservations, and extension-pack source metadata.
- Generated content count changes are intentional.
- No generated direct-answer copy has obvious grammar errors.
- Package versions and schema references match current repo state.
- Public claims do not overstate compliance, certification, AI, or TUI mutation scope.

Run from `ssot-registry` before reusing repo README copy:

```bash
ssot validate .
```

Confirm:

- README schema references match `.ssot/registry.json`.
- Package README package lists match current pyproject/package.json inventory.
- Existing screenshots and marketing graphics still exist at the referenced paths.
