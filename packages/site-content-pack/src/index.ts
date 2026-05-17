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
export * from "./content/components.js";
export * from "./content/editorial-guidance.js";
export * from "./content/packages.js";
export * from "./content/page-corpus.js";
export * from "./content/page-plan.js";
export * from "./content/sections.js";
export * from "./content/sitemap-tree.js";
export * from "./content/structured-data.js";
export * from "./content/subjects.js";

export const ssotRegistryHomePage = {
  kind: "home",
  slug: "/",
  title: "SSOT Registry",
  description:
    "A governed SSOT and single source of truth for ADRs, specs, features, claims, tests, evidence, boundaries, authority, and releases.",
  h1: "Govern software truth from decision to release.",
  intro:
    "SSOT Registry makes .ssot/registry.json the governed authority for delivery work: decisions, specifications, targetable features, tests, claims, evidence, risks, frozen boundaries, and releases.",
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
      title: "Govern software truth from decision to release.",
      subtitle:
        "Answer one release-review question clearly: what was intended, what changed, what proves it, and which canonical record says so.",
      primaryCta: {
        label: "Browse Content",
        href: "/content/",
      },
      secondaryCta: {
        label: "View GitHub",
        href: "https://github.com/groupsum/ssot-registry",
      },
    },
    {
      id: "features",
      kind: "feature_grid",
      title: "A registry for the full assurance chain",
      items: [
        {
          title: "Governed entity model",
          description:
            "Track ADRs, specs, features, issues, risks, profiles, tests, claims, evidence, boundaries, and releases with stable IDs in one canonical SSOT.",
          href: "/content/features/",
        },
        {
          title: "Proof-linked claims",
          description:
            "Connect claims to required features, test rows, and evidence artifacts so certification can fail closed against the authority record.",
          href: "/content/proofs/",
        },
        {
          title: "Boundary-driven release closure",
          description:
            "Freeze release scope, execute verification, certify claims, promote releases, and publish closure snapshots.",
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
      id: "content-corpus",
      kind: "feature_grid",
      title: "Learn SSOT Registry by the work you need to do",
      items: [
        {
          title: "Start from the content hub",
          description:
            "Browse SSOT Registry by features, proof, packages, and direct answers, then drill into the guide that matches your next operation.",
          href: "/content/",
        },
        {
          title: "Answer real implementation questions",
          description:
            "Every guide answers what, why, how, and when questions about the registry model, then points to practical CLI-backed next steps for the single source of truth.",
          href: "/content/",
        },
        {
          title: "Queryable registry exports",
          description:
            "Use registry export, graph export, validation reports, and conformance output when a reviewer needs machine-readable proof.",
          href: "/content/api-reference/",
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
        description: detail.role,
        install: detail.install,
        href: detail.name === "ssot-registry" ? "https://pypi.org/project/ssot-registry/" : "/content/packages/",
        api: detail.name === "ssot-cli" ? ["ssot validate", "ssot boundary freeze", "ssot release certify"] : undefined,
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
      title: "How SSOT Registry work moves",
      body:
        "A typical SSOT Registry workflow starts with ADRs and specs, targets features, links claims to tests and evidence, freezes a boundary, runs verification, certifies the release, promotes it, and publishes the final canonical state.",
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
