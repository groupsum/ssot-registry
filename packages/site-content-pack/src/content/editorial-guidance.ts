export interface EditorialPrinciple {
  id: string;
  title: string;
  guidance: string;
}

export interface ContentAssetPlan {
  id: string;
  filename: string;
  path: string;
  ratio: string;
  placement: readonly string[];
  alt: string;
  prompt: string;
}

export const ssotRegistryAuthorityPrinciples = [
  {
    id: "registry-authority",
    title: "Treat .ssot/registry.json as the authority record",
    guidance:
      "Explain that .ssot/registry.json is the canonical machine-readable authority for governed software assurance work: ADRs, SPECs, features, profiles, tests, claims, evidence, issues, risks, boundaries, and releases.",
  },
  {
    id: "canonical-companions",
    title: "Separate canonical companions from derived projections",
    guidance:
      "Describe ADR and SPEC JSON documents as canonical companion records, then describe Markdown, CSV, DOT graphs, SQLite exports, validation reports, discovery files, and site pages as derived projections that should be regenerated from the registry.",
  },
  {
    id: "boundary-release-split",
    title: "Keep boundaries and releases distinct",
    guidance:
      "A boundary freezes feature and profile scope. A release references that frozen boundary, then carries the claims, evidence, certification, promotion, publication, or revocation state used for review.",
  },
  {
    id: "proof-chain-language",
    title: "Name the proof chain explicitly",
    guidance:
      "Proof copy should distinguish claims, tests, and evidence. Claims state what is true, tests verify behavior, and evidence points to concrete artifacts that support certification.",
  },
  {
    id: "operator-workflow",
    title: "Teach the operating workflow",
    guidance:
      "Prefer concrete workflow language: initialize the repo, sync ADRs and SPECs, create targetable features, link tests, claims, and evidence, freeze a boundary, validate the registry, certify the release, then promote and publish the result.",
  },
] as const satisfies readonly EditorialPrinciple[];

export const canonicalVsDerivedCopy =
  "The registry is the source of truth. ADR and SPEC JSON files are canonical companion documents. Reports, Markdown, CSV, DOT graphs, SQLite exports, validation output, discovery artifacts, and site pages are projections. They should be regenerated from the registry, not edited as competing authority.";

export const boundaryVsReleaseCopy =
  "A boundary freezes scope: the feature and profile set that a delivery unit will be judged against. A release references that frozen boundary, then carries the claims and evidence used for certification, promotion, publication, or revocation. Scope and shipment stay separate so late changes cannot silently rewrite what was certified.";

export const packageChooserCopy =
  "Install ssot-registry when you want the full operator bundle. Install ssot-core when you are embedding registry APIs. Install ssot-cli when automation needs commands such as ssot validate, ssot boundary freeze, and ssot release certify. Use ssot-contracts for schemas and templates, ssot-conformance for reusable checks, ssot-pack-contracts for governance pack interoperability, ssot-views for derived reports and graphs, ssot-codegen for regenerated metadata, and ssot-tui when reviewers need a read-oriented terminal browser.";

export const governancePackCopy =
  "Governance packs let external packages ship trusted ADR and SPEC content without copying SSOT internals. ssot pack inspect reads pack metadata and manifests, ssot pack preflight checks compatibility before mutation, and ssot pack sync imports declared documents into reserved registry ranges. Pack documents remain governed inputs, not loose documentation.";

export const ssotRegistryImageAssetPlan = [
  {
    id: "hero-canonical-flow",
    filename: "ssot-registry-hero-canonical-flow.webp",
    path: "/content/images/ssot-registry-hero-canonical-flow.webp",
    ratio: "16:9",
    placement: ["home hero", "content hub hero"],
    alt: "Abstract canonical flow from SSOT Registry decisions through features, claims, tests, evidence, frozen boundaries, and releases.",
    prompt:
      "A restrained technical hero image for SSOT Registry: a clean canonical software assurance flow from decision documents to features, claims, tests, evidence, frozen boundaries, and releases. Light slate background, dark navy registry core, blue and teal connection lines, small square SR-style mark motif, crisp product UI diagram aesthetic, no people, no mascots, no decorative blobs, no readable body text, leave open negative space on the left for headline overlay.",
  },
  {
    id: "entity-model-banner",
    filename: "ssot-registry-entity-model-banner.webp",
    path: "/content/images/ssot-registry-entity-model-banner.webp",
    ratio: "3:1",
    placement: ["features index", "entity model articles"],
    alt: "Connected SSOT Registry entity cards around one central canonical registry file.",
    prompt:
      "Wide technical section banner showing a canonical registry entity model: ADR, SPEC, feature, issue, risk, profile, test, claim, evidence, boundary, and release represented as compact connected cards around a central registry file. Minimal light UI, blue and teal highlights, dark navy outlines, precise grid, no fake paragraphs, no people, no 3D, no heavy gradients.",
  },
  {
    id: "proof-chain-banner",
    filename: "ssot-registry-proof-chain-banner.webp",
    path: "/content/images/ssot-registry-proof-chain-banner.webp",
    ratio: "3:1",
    placement: ["proofs index", "release certification guides"],
    alt: "SSOT Registry claims connected to tests, evidence artifacts, validation states, and a release certification gate.",
    prompt:
      "Wide proof-chain banner for a software assurance site: claims connected to tests and evidence artifacts, with validation check states and a release certification gate. Restrained enterprise developer aesthetic, light background, blue primary path, teal verified states, dark navy labels as abstract blocks, no human figures, no unreadable text blocks, sharp vector-like composition.",
  },
  {
    id: "release-boundary-workflow",
    filename: "ssot-registry-release-boundary-workflow.webp",
    path: "/content/images/ssot-registry-release-boundary-workflow.webp",
    ratio: "16:9",
    placement: ["workflows index", "boundary and release articles"],
    alt: "SSOT Registry decision-to-scope, scope-to-freeze, proof-to-certify, and promote-to-publish workflow stages.",
    prompt:
      "Technical workflow illustration of a release boundary lifecycle: decision to scope, scope to freeze, proof to certify, promote to publish. Show four horizontal stages with a frozen boundary snapshot in the center and release artifacts at the end. Minimal UI panels, light slate surface, blue and teal accents, dark navy checkpoint markers, no people, no marketing illustration style, no readable small text.",
  },
  {
    id: "package-surfaces",
    filename: "ssot-registry-package-surfaces.webp",
    path: "/content/images/ssot-registry-package-surfaces.webp",
    ratio: "16:9",
    placement: ["packages index", "API reference index", "packs index"],
    alt: "SSOT Registry package surfaces feeding one canonical registry.",
    prompt:
      "Clean package-surface diagram for a Python developer toolchain: ssot-core, ssot-cli, ssot-conformance, ssot-contracts, ssot-views, ssot-codegen, ssot-tui arranged as modular package tiles feeding one canonical registry. Light technical site style, blue and teal accents, dark navy package outlines, subtle terminal and schema motifs, no fake code text, no people.",
  },
  {
    id: "course-learning-path",
    filename: "ssot-registry-course-learning-path.webp",
    path: "/content/images/ssot-registry-course-learning-path.webp",
    ratio: "4:3",
    placement: ["courses index", "lesson cards"],
    alt: "Stepped learning path through SSOT Registry concepts, CLI exercises, proof review, and readiness checks.",
    prompt:
      "Course and lesson image for a technical learning path: a clean stepped path through concepts, CLI exercises, proof review, and readiness checks, represented as compact cards and check markers. Light background, restrained blue and teal, small SR-style square motif, no people, no classroom scene, no cartoon style, no readable text.",
  },
  {
    id: "cli-reference-terminal",
    filename: "ssot-registry-cli-reference-terminal.webp",
    path: "/content/images/ssot-registry-cli-reference-terminal.webp",
    ratio: "16:10",
    placement: ["API command pages", "operator workflow articles"],
    alt: "Abstract terminal, JSON registry outline, and graph export nodes for SSOT Registry command reference content.",
    prompt:
      "Technical API reference image with a realistic but abstract terminal panel beside a JSON registry outline and graph export nodes. Use dark navy terminal surface, light slate surrounding UI, blue command accents, teal validation status indicators, no exact readable commands, no tiny fake text, no people, crisp developer documentation aesthetic.",
  },
  {
    id: "faq-glossary-map",
    filename: "ssot-registry-faq-glossary-map.webp",
    path: "/content/images/ssot-registry-faq-glossary-map.webp",
    ratio: "4:3",
    placement: ["FAQ index", "glossary index"],
    alt: "Semantic map connecting SSOT Registry direct answers, defined terms, related APIs, and authority nodes.",
    prompt:
      "Minimal knowledge-map image for FAQ and glossary pages: defined terms, direct answers, related APIs, and registry authority nodes arranged as a clean semantic map. Light slate background, dark navy node cards, blue and teal connector lines, understated documentation style, no people, no speech bubbles, no decorative blobs, no readable body text.",
  },
] as const satisfies readonly ContentAssetPlan[];
