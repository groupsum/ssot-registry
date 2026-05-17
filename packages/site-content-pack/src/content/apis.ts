export const relatedApis = [
  "ssot init",
  "ssot validate",
  "ssot upgrade --sync-docs --write-report",
  "ssot adr sync",
  "ssot spec sync",
  "ssot feature list",
  "ssot feature plan",
  "ssot test run",
  "ssot claim evaluate",
  "ssot evidence verify",
  "ssot boundary freeze",
  "ssot boundary run-tests",
  "ssot release certify",
  "ssot release promote",
  "ssot release publish",
  "ssot registry export",
  "ssot graph export",
  "ssot conformance run",
] as const;

export type RelatedApi = (typeof relatedApis)[number];
