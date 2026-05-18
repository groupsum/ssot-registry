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
  output: string;
  workflowStage: string;
}

export const relatedApiDetails = [
  {
    command: "ssot config init",
    description: "Creates or normalizes local SSOT CLI configuration before repo-level governance work begins.",
    output: "Repo-local SSOT CLI configuration ready for repeatable commands.",
    workflowStage: "setup",
  },
  {
    command: "ssot init",
    description: "Bootstraps the .ssot registry scaffold so the repo has a canonical authority location.",
    output: "A normalized .ssot directory with the registry scaffold in place.",
    workflowStage: "setup",
  },
  {
    command: "ssot validate",
    description: "Checks schema, links, status, and release-readiness rules before automation trusts the registry.",
    output: "Validation diagnostics that identify registry errors before review or automation.",
    workflowStage: "validation",
  },
  {
    command: "ssot upgrade --sync-docs --write-report",
    description: "Migrates an older registry to the current schema, synchronizes document metadata, and writes an upgrade report.",
    output: "Updated registry metadata and an upgrade report that explains changed compatibility state.",
    workflowStage: "migration",
  },
  {
    command: "ssot adr sync",
    description: "Synchronizes canonical ADR companion documents with registry metadata.",
    output: "ADR document metadata aligned with the canonical registry records.",
    workflowStage: "decision",
  },
  {
    command: "ssot spec sync",
    description: "Synchronizes canonical SPEC companion documents with registry metadata.",
    output: "SPEC document metadata aligned with the canonical registry records.",
    workflowStage: "decision",
  },
  {
    command: "ssot feature list",
    description: "Lists targetable feature records used for planning, boundaries, claims, and proof review.",
    output: "A feature inventory for planning, scope selection, and release review.",
    workflowStage: "scope",
  },
  {
    command: "ssot feature plan",
    description: "Moves features into a planned delivery horizon so later boundaries can freeze explicit target scope.",
    output: "Feature planning state that can feed boundary membership decisions.",
    workflowStage: "scope",
  },
  {
    command: "ssot profile list",
    description: "Lists profile compositions that can be included in frozen delivery boundaries.",
    output: "Profile composition records available for frozen boundary scope.",
    workflowStage: "scope",
  },
  {
    command: "ssot test run",
    description: "Executes registered test rows or boundary test bundles and records pass/fail evidence candidates.",
    output: "Test execution results that can support claims and release certification.",
    workflowStage: "proof",
  },
  {
    command: "ssot claim evaluate",
    description: "Evaluates claims against linked features, tests, evidence, tiers, and readiness policy.",
    output: "Claim evaluation state suitable for certification review.",
    workflowStage: "proof",
  },
  {
    command: "ssot evidence verify",
    description: "Verifies linked evidence artifacts before claims or releases rely on them.",
    output: "Evidence verification status for proof-chain review.",
    workflowStage: "proof",
  },
  {
    command: "ssot boundary freeze",
    description: "Freezes scoped features and profiles so release review has an immutable target set.",
    output: "A frozen boundary that fixes the feature and profile target set.",
    workflowStage: "freeze",
  },
  {
    command: "ssot boundary run-tests",
    description: "Runs the tests required by a frozen boundary and produces boundary-scoped proof results.",
    output: "Boundary test results that can be linked into release certification evidence.",
    workflowStage: "proof",
  },
  {
    command: "ssot release certify",
    description: "Evaluates claims, tests, evidence, and frozen scope before a release can be promoted.",
    output: "Certification state showing whether the release satisfies its frozen boundary.",
    workflowStage: "release",
  },
  {
    command: "ssot release promote",
    description: "Promotes a certified release after proof gates and release policy have passed.",
    output: "Promoted release state ready for publication or downstream handoff.",
    workflowStage: "release",
  },
  {
    command: "ssot release publish",
    description: "Publishes a promoted release closure snapshot and final authority state.",
    output: "Publication metadata and a final release authority snapshot.",
    workflowStage: "release",
  },
  {
    command: "ssot pack inspect",
    description: "Reads governance pack metadata and manifests before imported ADR or SPEC material is trusted.",
    output: "Pack manifest detail for compatibility and governance review.",
    workflowStage: "pack",
  },
  {
    command: "ssot pack preflight",
    description: "Checks compatibility, ranges, and mutations before syncing pack-owned governed documents.",
    output: "Preflight diagnostics that show whether pack sync can proceed.",
    workflowStage: "pack",
  },
  {
    command: "ssot pack sync",
    description: "Imports declared pack documents into reserved registry ranges without treating them as loose docs.",
    output: "Imported pack documents and registry links in reserved governed ranges.",
    workflowStage: "pack",
  },
  {
    command: "ssot registry export",
    description: "Exports registry state into derived machine-readable views for review, automation, or reporting.",
    output: "JSON, CSV, YAML, graph, or related derived views generated from registry truth.",
    workflowStage: "projection",
  },
  {
    command: "ssot graph export",
    description: "Exports registry relationships as graph data so reviewers can inspect entity links.",
    output: "Graph projection of registry entities, links, proof chains, and release relationships.",
    workflowStage: "projection",
  },
  {
    command: "ssot conformance run",
    description: "Runs reusable conformance checks that can become evidence for registry claims.",
    output: "Conformance results suitable for evidence and certification workflows.",
    workflowStage: "proof",
  },
] as const satisfies readonly RelatedApiDetail[];
