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
