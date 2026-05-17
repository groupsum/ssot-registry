export const subjectAreas = [
  "ADRs",
  "Specifications",
  "Features",
  "Claims",
  "Tests",
  "Evidence",
  "Boundaries",
  "Profiles",
  "Risks",
  "Issues",
  "Releases",
  "Certification",
  "Promotion",
  "Publication",
  "CLI workflows",
  "Registry schemas",
  "Conformance",
  "Content packs",
  "Site packages",
  "Operator guides",
] as const;

export type SubjectArea = (typeof subjectAreas)[number];
