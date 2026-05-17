import type { LanderSite } from "@mdwrk/lander-content-contract";
import { generatedContentIndexPage, generatedCorpusPages, generatedSectionIndexPages } from "./content/page-corpus.js";

export * from "./content/apis.js";
export * from "./content/audiences.js";
export * from "./content/components.js";
export * from "./content/packages.js";
export * from "./content/page-corpus.js";
export * from "./content/page-plan.js";
export * from "./content/sections.js";
export * from "./content/structured-data.js";
export * from "./content/subjects.js";

export const ssotRegistryHomePage = {
  kind: "home",
  slug: "/",
  title: "SSOT Registry",
  description:
    "A governed single source of truth for ADRs, specs, features, claims, tests, evidence, boundaries, and releases.",
  h1: "Govern software truth from decision to release.",
  intro:
    "SSOT Registry turns architecture, scope, proof, and release state into durable registry entities that can be validated, queried, and certified.",
  seo: {
    keywords: ["ssot", "software assurance", "adr", "release certification", "evidence registry"],
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
        "Model ADRs, specs, features, claims, tests, evidence, boundaries, and releases as one validated source of truth.",
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
            "Track ADRs, specs, features, issues, risks, profiles, tests, claims, evidence, boundaries, and releases with stable IDs.",
          href: "/content/features/",
        },
        {
          title: "Proof-linked claims",
          description:
            "Connect claims to required features, test rows, and evidence artifacts so certification can fail closed.",
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
      id: "content-corpus",
      kind: "feature_grid",
      title: "SSOT Registry learning paths",
      items: [
        {
          title: "Start from the content hub",
          description:
            "Browse SSOT Registry by features, proof, packages, and direct answers, then drill into focused guides.",
          href: "/content/",
        },
        {
          title: "Answer real implementation questions",
          description:
            "Every guide answers a real reader question, explains the SSOT Registry concept, and points to practical next steps.",
          href: "/content/",
        },
        {
          title: "Discovery artifacts",
          description:
            "The site publishes sitemap, robots, llms, full llms, content index, semantic index, and structured-data graph artifacts.",
          href: "/sitemap.xml",
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
          evidence: "Frozen boundary snapshots preserve feature and profile scope for release review.",
          href: "/content/workflows/",
        },
        {
          claim: "Evidence traceability",
          status: "supported",
          evidence: "Evidence rows point at concrete artifacts and link back to claims and tests.",
          href: "/content/proofs/",
        },
      ],
    },
    {
      id: "packages",
      kind: "package_grid",
      title: "Primary package surfaces",
      packages: [
        {
          name: "ssot-registry",
          description: "CLI and registry APIs for governed SSOT workflows.",
          install: "uv add ssot-registry",
          href: "https://pypi.org/project/ssot-registry/",
          api: ["ssot validate", "ssot feature list", "ssot release certify"],
        },
        {
          name: "ssot-cli skills",
          description: "Operator workflows for ADRs, specs, features, tests, evidence, and releases.",
          href: "/content/workflows/",
        },
      ],
    },
    {
      id: "workflow",
      kind: "markdown",
      title: "How the website is assembled",
      body:
        "The SSOT Registry website teaches the registry from the reader's point of view: what each governed entity does, why it matters, how to use the CLI, and how proof carries through release work.",
    },
    {
      id: "faq",
      kind: "faq",
      title: "SSOT Registry FAQ",
      items: [
        {
          question: "What is the source of truth?",
          answer:
            "The registry JSON and its linked ADR, SPEC, feature, claim, test, evidence, boundary, and release entities are the source of truth.",
        },
        {
          question: "Why use release boundaries?",
          answer:
            "Boundaries freeze the target set so certification evaluates the intended scope instead of whatever changed later.",
        },
        {
          question: "Why a content pack?",
          answer:
            "The content pack makes the product site portable while keeping the website host thin and reusable.",
        },
      ],
    },
  ],
  faq: [
    {
      question: "Can SSOT Registry publish release evidence?",
      answer:
        "Yes. Release rows can include claim and evidence membership, certification reports, promotion snapshots, and publication snapshots.",
    },
    {
      question: "What does the SSOT Registry content pack provide?",
      answer:
        "It provides product pages, learning guides, proof workflow pages, package references, direct answers, and discovery artifacts for the SSOT Registry website.",
    },
  ],
} satisfies LanderSite["pages"][number];

export const ssotRegistrySite = {
  product: {
    name: "SSOT Registry",
    slug: "ssot-registry",
    tagline: "Governed single source of truth for software assurance.",
    description:
      "SSOT Registry keeps architectural decisions, specifications, features, claims, tests, evidence, boundaries, and releases in one inspectable registry.",
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
    note: "SSOT Registry content is packaged separately from the website host.",
  },
  seo: {
    defaultTitle: "SSOT Registry",
    defaultDescription:
      "A governed registry for ADRs, specs, features, claims, tests, evidence, release boundaries, and certification workflows.",
    titleTemplate: "%s | SSOT Registry",
  },
  ai: {
    llmsTxtTitle: "SSOT Registry",
    summary:
      "SSOT Registry is a governed software assurance registry and CLI for managing architecture, scope, claims, tests, evidence, boundaries, and releases.",
    coreFacts: [
      "The registry is the canonical source for governed software assurance entities.",
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
