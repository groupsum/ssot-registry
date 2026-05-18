export const relatedPackages = [
  "ssot-registry",
  "ssot-core",
  "ssot-cli",
  "ssot-conformance",
  "ssot-pack-contracts",
  "ssot-contracts",
  "ssot-views",
  "ssot-codegen",
  "ssot-tui",
] as const;

export type RelatedPackage = (typeof relatedPackages)[number];

export interface RelatedPackageDetail {
  name: RelatedPackage;
  role: string;
  install: string;
  bestFor: string;
  proofPoint: string;
  primaryCommands: readonly string[];
}

export const relatedPackageDetails = [
  {
    name: "ssot-registry",
    role: "Umbrella package for operators who want the full SSOT Registry CLI and registry workflow bundle.",
    install: "uv add ssot-registry",
    bestFor: "Teams that want one install target for daily registry operation.",
    proofPoint: "Carries the full path from registry initialization through validation, proof review, and release closure.",
    primaryCommands: ["ssot init", "ssot validate", "ssot release certify"],
  },
  {
    name: "ssot-core",
    role: "Runtime APIs, registry models, validation helpers, and canonical data operations for embedding SSOT behavior.",
    install: "uv add ssot-core",
    bestFor: "Applications embedding registry reads, writes, validation, or canonical entity operations.",
    proofPoint: "Keeps embedded integrations aligned with the same canonical entity model used by the CLI.",
    primaryCommands: ["ssot validate", "ssot registry export"],
  },
  {
    name: "ssot-cli",
    role: "Command surface for repo operators, CI jobs, and release workflows that mutate or inspect governed registry state.",
    install: "uv add ssot-cli",
    bestFor: "CI lanes and operators that need explicit commands for governed registry workflows.",
    proofPoint: "Exposes the command path for validation, boundary freeze, claim evaluation, and release certification.",
    primaryCommands: ["ssot validate", "ssot boundary freeze", "ssot release certify"],
  },
  {
    name: "ssot-conformance",
    role: "Reusable conformance checks that turn expected registry behavior into repeatable proof and evidence inputs.",
    install: "uv add ssot-conformance",
    bestFor: "Projects that need portable checks before evidence is trusted.",
    proofPoint: "Produces reusable conformance results that can support claims and release certification.",
    primaryCommands: ["ssot conformance run", "ssot test run"],
  },
  {
    name: "ssot-pack-contracts",
    role: "Governance pack interoperability contracts for external ADR and SPEC content with manifests and reserved ranges.",
    install: "uv add ssot-pack-contracts",
    bestFor: "Pack authors and downstream repos importing governed ADR or SPEC content.",
    proofPoint: "Defines the manifest and reserved-range contract used before pack sync mutates a registry.",
    primaryCommands: ["ssot pack inspect", "ssot pack preflight", "ssot pack sync"],
  },
  {
    name: "ssot-contracts",
    role: "Shared schemas, templates, and package metadata contracts used by registry tooling and generated surfaces.",
    install: "uv add ssot-contracts",
    bestFor: "Tooling that needs stable registry schemas and shared document contracts.",
    proofPoint: "Keeps schema and template consumers aligned with canonical registry wire shapes.",
    primaryCommands: ["ssot validate", "ssot upgrade --sync-docs --write-report"],
  },
  {
    name: "ssot-views",
    role: "Derived reports, graph exports, Markdown, CSV, SQLite, and reviewer-facing projections generated from registry truth.",
    install: "uv add ssot-views",
    bestFor: "Reviewers and automation that need projections without editing source records.",
    proofPoint: "Produces derived views while keeping .ssot/registry.json as the authority record.",
    primaryCommands: ["ssot registry export", "ssot graph export"],
  },
  {
    name: "ssot-codegen",
    role: "Regeneration utilities for metadata and typed artifacts that should stay derived from canonical registry state.",
    install: "uv add ssot-codegen",
    bestFor: "Repos that regenerate typed metadata instead of hand-maintaining derived files.",
    proofPoint: "Reduces drift by regenerating artifacts from canonical registry state.",
    primaryCommands: ["ssot registry export", "ssot validate"],
  },
  {
    name: "ssot-tui",
    role: "Read-oriented terminal browser for reviewers who need to inspect registry relationships without editing the source.",
    install: "uv add ssot-tui",
    bestFor: "Reviewers who need a navigable terminal view of registry relationships.",
    proofPoint: "Makes proof chains, boundaries, releases, and linked entities inspectable without mutating the registry.",
    primaryCommands: ["ssot validate", "ssot graph export"],
  },
] as const satisfies readonly RelatedPackageDetail[];
