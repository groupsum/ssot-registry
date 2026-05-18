import type { LanderSite } from "@mdwrk/lander-content-contract";
import {
  boundaryVsReleaseCopy,
  canonicalVsDerivedCopy,
  packageChooserCopy,
} from "./content/editorial-guidance.js";
import { generatedContentIndexPage, generatedCorpusPages, generatedSectionIndexPages } from "./content/page-corpus.js";
import { relatedPackageDetails } from "./content/packages.js";

export * from "./content/apis.js";
export * from "./content/audiences.js";
export * from "./content/component-traceability.js";
export * from "./content/components.js";
export * from "./content/editorial-guidance.js";
export * from "./content/packages.js";
export * from "./content/page-corpus.js";
export * from "./content/page-plan.js";
export * from "./content/sections.js";
export * from "./content/site-content-audit.js";
export * from "./content/sitemap-tree.js";
export * from "./content/structured-data.js";
export * from "./content/subjects.js";

export const ssotRegistryHomePage = {
  kind: "home",
  slug: "/",
  title: "SSOT Registry",
  description:
    "A governed release-readiness registry for teams that need decisions, scope, proof, and publication state in one canonical record.",
  h1: "Ship from a registry that proves the release.",
  intro:
    "SSOT Registry turns ADRs, SPECs, features, tests, claims, evidence, frozen boundaries, and releases into one inspectable `.ssot/registry.json` authority file.",
  seo: {
    keywords: ["ssot", "single source of truth", "canonical registry", "canon", "software authority", "software assurance", "adr", "release certification", "evidence registry"],
  },
  schema: [
    { kind: "WebPage" },
    { kind: "WebSite" },
    { kind: "Organization" },
    {
      kind: "SoftwareApplication",
      data: {
        applicationCategory: "DeveloperApplication",
        operatingSystem: "Cross-platform",
      },
    },
    {
      kind: "SoftwareSourceCode",
      data: {
        codeRepository: "https://github.com/groupsum/ssot-registry",
        programmingLanguage: "Python",
      },
    },
    { kind: "FAQPage" },
  ],
  sections: [
    {
      id: "hero",
      kind: "hero",
      eyebrow: "SSOT Registry",
      title: "Ship from a registry that proves the release.",
      subtitle:
        "Freeze the intended scope, run the required proof, certify the release, and publish the authority trail without reconstructing truth from tickets, docs, and CI logs.",
      primaryCta: {
        label: "Follow the release workflow",
        href: "/content/workflows/",
      },
      secondaryCta: {
        label: "Install SSOT Registry",
        href: "/content/packages/",
      },
    },
    {
      id: "first-five-minutes",
      kind: "feature_grid",
      title: "A concrete first run",
      items: [
        {
          title: "1. Install",
          description: "`uv add ssot-registry` gives operators the full CLI for registry initialization, validation, proof review, and release closure.",
          href: "/content/packages/",
        },
        {
          title: "2. Validate the registry",
          description: "`ssot validate` checks schema, links, status, and readiness before automation or reviewers trust `.ssot/registry.json`.",
          href: "/content/api-reference/",
        },
        {
          title: "3. Certify a release",
          description: "`ssot boundary freeze`, `ssot claim evaluate`, `ssot evidence verify`, and `ssot release certify` turn scope and proof into a reviewable release decision.",
          href: "/content/workflows/",
        },
      ],
    },
    {
      id: "features",
      kind: "feature_grid",
      title: "What the registry replaces",
      items: [
        {
          title: "Spreadsheets of release scope",
          description:
            "Feature and profile rows are selected into frozen boundaries, so the target set for certification is explicit and cannot drift during review.",
          href: "/content/features/",
        },
        {
          title: "Unreviewable proof claims",
          description:
            "Claims stay linked to required features, test rows, evidence artifacts, and claim tiers, so certification can fail closed instead of trusting prose.",
          href: "/content/proofs/",
        },
        {
          title: "Release notes as authority",
          description:
            "Release rows reference a frozen boundary, carry certification state, and publish closure snapshots as derived outputs from registry truth.",
          href: "/content/workflows/",
        },
      ],
    },
    {
      id: "canonical-authority",
      kind: "comparison",
      title: "Canonical records and derived projections stay separate",
      columns: [
        { id: "concern", label: "Concern" },
        { id: "authority", label: "Authority rule" },
        { id: "operator", label: "Operator takeaway" },
      ],
      rows: [
        {
          id: "registry",
          label: "Registry",
          cells: {
            concern: ".ssot/registry.json",
            authority: "Canonical machine-readable source for governed software assurance entities.",
            operator: "Change registry state through SSOT workflows, then validate before review.",
          },
        },
        {
          id: "documents",
          label: "ADRs and SPECs",
          cells: {
            concern: "Canonical companion documents",
            authority: "ADR and SPEC JSON documents carry governed decision and requirement detail.",
            operator: "Sync companion documents so document metadata and registry links agree.",
          },
        },
        {
          id: "projections",
          label: "Reports and site pages",
          cells: {
            concern: "Derived projections",
            authority: canonicalVsDerivedCopy,
            operator: "Regenerate projections from registry truth instead of editing them as competing authority.",
          },
        },
      ],
    },
    {
      id: "boundary-release",
      kind: "markdown",
      title: "Frozen scope is not the same thing as shipment",
      body: boundaryVsReleaseCopy,
    },
    {
      id: "operator-journeys",
      kind: "feature_grid",
      title: "Choose the work you are doing",
      items: [
        {
          title: "Planning a change",
          description:
            "Start with ADRs and SPECs, create targetable feature rows, and keep the decision-to-scope trail inspectable before implementation starts.",
          href: "/content/features/",
        },
        {
          title: "Preparing release proof",
          description:
            "Link claims to tests and evidence, verify the artifacts, and certify only against the scope frozen into the boundary.",
          href: "/content/proofs/",
        },
        {
          title: "Installing or automating",
          description:
            "Pick the package surface for the job: full operator bundle, CLI-only automation, core APIs, conformance checks, views, codegen, or TUI review.",
          href: "/content/api-reference/",
        },
        {
          title: "Importing governed content",
          description:
            "Use governance packs when external ADR and SPEC material must sync into reserved ranges instead of being copied as loose documentation.",
          href: "/content/packs/",
        },
      ],
    },
    {
      id: "proof",
      kind: "proof_matrix",
      title: "Proof surfaces stay visible",
      items: [
        {
          claim: "Registry validation",
          status: "verified",
          evidence: "The CLI validates registry structure, links, status, and release readiness.",
          href: "/content/proofs/",
        },
        {
          claim: "Release boundaries",
          status: "supported",
          evidence: "Frozen boundary snapshots preserve feature and profile scope as canonical authority for release review.",
          href: "/content/workflows/",
        },
        {
          claim: "Evidence traceability",
          status: "supported",
          evidence: "Evidence rows point at concrete artifacts and link back to claims and tests in the SSOT canon.",
          href: "/content/proofs/",
        },
      ],
    },
    {
      id: "packages",
      kind: "package_grid",
      title: "Choose the package for the job",
      packages: relatedPackageDetails.map((detail) => ({
        name: detail.name,
        description: `${detail.role} Best for: ${detail.bestFor} Proof point: ${detail.proofPoint}`,
        install: detail.install,
        href: detail.name === "ssot-registry" ? "https://pypi.org/project/ssot-registry/" : "/content/packages/",
        api: detail.primaryCommands,
      })),
    },
    {
      id: "package-chooser",
      kind: "markdown",
      title: "Package chooser",
      body: packageChooserCopy,
    },
    {
      id: "workflow",
      kind: "markdown",
      title: "The release workflow in one line",
      body:
        "`ssot adr sync` and `ssot spec sync` establish decision authority; feature rows define targetable work; tests and evidence prove claims; `ssot boundary freeze` locks scope; `ssot release certify`, `ssot release promote`, and `ssot release publish` close the release.",
    },
    {
      id: "faq",
      kind: "faq",
      title: "SSOT Registry FAQ",
      items: [
        {
          question: "What is the source of truth?",
          answer:
            "The registry JSON and its linked ADR, SPEC, feature, claim, test, evidence, boundary, and release entities are the SSOT, canonical source of truth, and authority record.",
        },
        {
          question: "Why use release boundaries?",
          answer:
            "Boundaries freeze the target set so certification evaluates the intended scope instead of whatever changed later.",
        },
        {
          question: "How do I start using SSOT Registry in a repo?",
          answer:
            "Install the package, run `ssot init .`, add or sync ADRs and specs, create feature rows for targetable work, link tests and evidence, then run `ssot validate .` before relying on the registry.",
        },
      ],
    },
  ],
  faq: [
    {
      question: "Can SSOT Registry publish release evidence?",
      answer:
        "Yes. Release rows can include claim and evidence membership, certification reports, promotion snapshots, publication snapshots, and the final canonical authority state.",
    },
    {
      question: "What can a release reviewer inspect?",
      answer:
        "A release reviewer can inspect the frozen boundary, feature targets, claim tiers, linked tests, evidence rows, certification report, promotion state, publication state, canon, and any blocking issues or risks.",
    },
  ],
} satisfies LanderSite["pages"][number];

export const ssotRegistrySite = {
  product: {
    name: "SSOT Registry",
    slug: "ssot-registry",
    tagline: "Governed single source of truth for software assurance.",
    description:
      "SSOT Registry keeps architectural decisions, specifications, features, claims, tests, evidence, boundaries, and releases in one inspectable canonical single source of truth.",
    category: "DeveloperApplication",
    canonicalUrl: "https://ssot-registry.com",
    sameAs: [
      "https://github.com/groupsum/ssot-registry",
    ],
  },
  nav: {
    primary: [
      { label: "Features", href: "/content/features/" },
      { label: "Proof", href: "/content/proofs/" },
      { label: "Packages", href: "/content/packages/" },
      { label: "FAQ", href: "/content/faq-qa/" },
    ],
    cta: {
      label: "View GitHub",
      href: "https://github.com/groupsum/ssot-registry",
      variant: "primary",
    },
  },
  footer: {
    links: [
      { label: "Documentation", href: "/content/" },
      { label: "GitHub", href: "https://github.com/groupsum/ssot-registry" },
      { label: "PyPI", href: "https://pypi.org/project/ssot-registry/" },
    ],
    note: "Copyright 2026 Groupsum. SSOT Registry keeps software decisions, scope, proof, and release state inspectable.",
  },
  seo: {
    defaultTitle: "SSOT Registry",
    defaultDescription:
      "A governed SSOT and canonical registry for ADRs, specs, features, claims, tests, evidence, release boundaries, authority, and certification workflows.",
    titleTemplate: "%s | SSOT Registry",
  },
  ai: {
    llmsTxtTitle: "SSOT Registry",
    summary:
      "SSOT Registry is a governed software assurance registry and CLI for managing architecture, scope, claims, tests, evidence, boundaries, canon, authority, and releases as a single source of truth.",
    coreFacts: [
      "The registry is the canonical source, canon, and authority record for governed software assurance entities.",
      "Boundaries freeze scoped delivery targets before certification and release.",
      "Claims link behavior to tests and evidence instead of relying on prose assertions.",
    ],
  },
  theme: {
    id: "ssot-registry-light",
    label: "SSOT Registry Light",
    mode: "light",
    tokens: {
      "--lander-accent": "#2563eb",
      "--lander-accent-alt": "#0f766e",
      "--lander-app-bg": "#f8fafc",
      "--lander-panel-muted": "#eef6ff",
    },
  },
  pages: [ssotRegistryHomePage, generatedContentIndexPage, ...generatedSectionIndexPages, ...generatedCorpusPages],
} satisfies LanderSite;
