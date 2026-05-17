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
  "ADR and SPEC sync",
  "Graph exports",
  "Operator guides",
] as const;

export type SubjectArea = (typeof subjectAreas)[number];
