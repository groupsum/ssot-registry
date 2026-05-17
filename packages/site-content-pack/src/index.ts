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
        label: "Read the Docs",
        href: "/docs/",
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
        },
        {
          title: "Proof-linked claims",
          description:
            "Connect claims to required features, test rows, and evidence artifacts so certification can fail closed.",
        },
        {
          title: "Boundary-driven release closure",
          description:
            "Freeze release scope, execute verification, certify claims, promote releases, and publish closure snapshots.",
        },
      ],
    },
    {
      id: "content-corpus",
      kind: "feature_grid",
      title: "3,840 generated content pages",
      items: [
        {
          title: "Visible corpus index",
          description:
            "Browse the generated SSOT Registry content plan from the content index and section indexes.",
          href: "/content/",
        },
        {
          title: "AEO, SEO, and AiEO coverage",
          description:
            "Every generated page carries answer goals, search targets, agent facts, breadcrumbs, schema intents, and component intents.",
          href: "/content/",
        },
        {
          title: "Discovery artifacts",
          description:
            "The corpus publishes sitemap, robots, llms, full llms, content index, semantic index, and structured-data graph artifacts.",
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
          href: "/docs/",
        },
        {
          claim: "Release boundaries",
          status: "supported",
          evidence: "Frozen boundary snapshots preserve feature and profile scope for release review.",
          href: "/docs/",
        },
        {
          claim: "Evidence traceability",
          status: "supported",
          evidence: "Evidence rows point at concrete artifacts and link back to claims and tests.",
          href: "/docs/",
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
          href: "/docs/",
        },
      ],
    },
    {
      id: "workflow",
      kind: "markdown",
      title: "How the website is assembled",
      body:
        "The SSOT Registry website host imports this content pack and renders it through reusable lander packages. Product copy, page structure, FAQ, proof claims, and structured-data intents live in the content pack rather than in the React host.",
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
        "It provides product pages, generated corpus pages, structured-data intents, proof surfaces, related package and API metadata, and discovery artifacts.",
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
      { label: "Features", href: "#features" },
      { label: "Proof", href: "#proof" },
      { label: "Packages", href: "#packages" },
      { label: "FAQ", href: "#faq" },
    ],
    cta: {
      label: "View GitHub",
      href: "https://github.com/groupsum/ssot-registry",
      variant: "primary",
    },
  },
  footer: {
    links: [
      { label: "Documentation", href: "/docs/" },
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
