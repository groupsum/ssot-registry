export const relatedApis = [
  "ssot config init",
  "ssot init",
  "ssot validate",
  "ssot upgrade --sync-docs --write-report",
  "ssot adr sync",
  "ssot spec sync",
  "ssot feature list",
  "ssot feature plan",
  "ssot profile list",
  "ssot test run",
  "ssot claim evaluate",
  "ssot evidence verify",
  "ssot boundary freeze",
  "ssot boundary run-tests",
  "ssot release certify",
  "ssot release promote",
  "ssot release publish",
  "ssot pack inspect",
  "ssot pack preflight",
  "ssot pack sync",
  "ssot registry export",
  "ssot graph export",
  "ssot conformance run",
] as const;

export type RelatedApi = (typeof relatedApis)[number];

export interface RelatedApiDetail {
  command: RelatedApi;
  description: string;
}

export const relatedApiDetails = [
  {
    command: "ssot config init",
    description: "Creates or normalizes local SSOT CLI configuration before repo-level governance work begins.",
  },
  {
    command: "ssot init",
    description: "Bootstraps the .ssot registry scaffold so the repo has a canonical authority location.",
  },
  {
    command: "ssot validate",
    description: "Checks schema, links, status, and release-readiness rules before automation trusts the registry.",
  },
  {
    command: "ssot adr sync",
    description: "Synchronizes canonical ADR companion documents with registry metadata.",
  },
  {
    command: "ssot spec sync",
    description: "Synchronizes canonical SPEC companion documents with registry metadata.",
  },
  {
    command: "ssot feature list",
    description: "Lists targetable feature records used for planning, boundaries, claims, and proof review.",
  },
  {
    command: "ssot profile list",
    description: "Lists profile compositions that can be included in frozen delivery boundaries.",
  },
  {
    command: "ssot boundary freeze",
    description: "Freezes scoped features and profiles so release review has an immutable target set.",
  },
  {
    command: "ssot release certify",
    description: "Evaluates claims, tests, evidence, and frozen scope before a release can be promoted.",
  },
  {
    command: "ssot pack inspect",
    description: "Reads governance pack metadata and manifests before imported ADR or SPEC material is trusted.",
  },
  {
    command: "ssot pack preflight",
    description: "Checks compatibility, ranges, and mutations before syncing pack-owned governed documents.",
  },
  {
    command: "ssot pack sync",
    description: "Imports declared pack documents into reserved registry ranges without treating them as loose docs.",
  },
  {
    command: "ssot conformance run",
    description: "Runs reusable conformance checks that can become evidence for registry claims.",
  },
] as const satisfies readonly RelatedApiDetail[];
