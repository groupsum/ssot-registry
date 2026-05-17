export const relatedPackages = [
  "ssot-registry",
  "ssot-core",
  "ssot-cli",
  "ssot-conformance",
  "@ssot-registry/site-content-pack",
  "ssot-contracts",
  "ssot-views",
  "ssot-codegen",
  "ssot-tui",
  "ssot-registry-docs",
] as const;

export type RelatedPackage = (typeof relatedPackages)[number];
