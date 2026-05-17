export const relatedApis = [
  "ssot validate",
  "ssot feature list",
  "ssot claim evaluate",
  "ssot evidence verify",
  "ssot boundary freeze",
  "ssot release certify",
  "ssot release promote",
  "registry entity get",
  "registry content export",
  "registry conformance generate",
] as const;

export type RelatedApi = (typeof relatedApis)[number];
