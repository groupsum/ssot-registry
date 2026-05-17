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
}

export const relatedPackageDetails = [
  {
    name: "ssot-registry",
    role: "Umbrella package for operators who want the full SSOT Registry CLI and registry workflow bundle.",
    install: "uv add ssot-registry",
  },
  {
    name: "ssot-core",
    role: "Runtime APIs, registry models, validation helpers, and canonical data operations for embedding SSOT behavior.",
    install: "uv add ssot-core",
  },
  {
    name: "ssot-cli",
    role: "Command surface for repo operators, CI jobs, and release workflows that mutate or inspect governed registry state.",
    install: "uv add ssot-cli",
  },
  {
    name: "ssot-conformance",
    role: "Reusable conformance checks that turn expected registry behavior into repeatable proof and evidence inputs.",
    install: "uv add ssot-conformance",
  },
  {
    name: "ssot-pack-contracts",
    role: "Governance pack interoperability contracts for external ADR and SPEC content with manifests and reserved ranges.",
    install: "uv add ssot-pack-contracts",
  },
  {
    name: "ssot-contracts",
    role: "Shared schemas, templates, and package metadata contracts used by registry tooling and generated surfaces.",
    install: "uv add ssot-contracts",
  },
  {
    name: "ssot-views",
    role: "Derived reports, graph exports, Markdown, CSV, SQLite, and reviewer-facing projections generated from registry truth.",
    install: "uv add ssot-views",
  },
  {
    name: "ssot-codegen",
    role: "Regeneration utilities for metadata and typed artifacts that should stay derived from canonical registry state.",
    install: "uv add ssot-codegen",
  },
  {
    name: "ssot-tui",
    role: "Read-oriented terminal browser for reviewers who need to inspect registry relationships without editing the source.",
    install: "uv add ssot-tui",
  },
] as const satisfies readonly RelatedPackageDetail[];
