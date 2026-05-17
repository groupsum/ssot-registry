import type { PageSpec, SchemaSpec, SectionSpec } from "@mdwrk/lander-content-contract";
import { generatePagePlans, slugify, type PlannedPage } from "./page-plan.js";
import { sectionBlueprints } from "./sections.js";

export interface GeneratedCorpusPage extends PageSpec {
  planId: string;
}

const primaryContentSections = [
  {
    id: "features",
    label: "Features",
    href: "/content/features/",
    description: "Learn what SSOT Registry tracks, why each entity matters, and how governed records support delivery work.",
    subsections: ["Features", "Workflows", "Comparisons"],
  },
  {
    id: "proof",
    label: "Proof",
    href: "/content/proofs/",
    description: "Understand claims, evidence, certification, release boundaries, and the review trail that supports release decisions.",
    subsections: ["Proofs", "Certifications", "Courses", "Lessons"],
  },
  {
    id: "packages",
    label: "Packages",
    href: "/content/packages/",
    description: "Install SSOT Registry, find package and API entry points, and connect content packs to the site experience.",
    subsections: ["Packages", "Packs", "API_Reference"],
  },
  {
    id: "faq",
    label: "FAQ",
    href: "/content/faq-qa/",
    description: "Get direct answers, definitions, and operational explanations for common SSOT Registry questions.",
    subsections: ["FAQ_QA", "Glossary"],
  },
] as const;

export const generatedPagePlans = generatePagePlans();
export const generatedCorpusPages = generatedPagePlans.map(pageSpecFromPlan);
export const generatedSectionIndexPages = sectionBlueprints.map((section) =>
  sectionIndexPage(
    section.id,
    section.label,
    generatedCorpusPages.filter((page) => page.slug.startsWith(`/${slugify(section.id)}/`)),
  ),
);
export const generatedContentIndexPage = contentIndexPage(generatedSectionIndexPages);

export function pageSpecFromPlan(plan: PlannedPage): GeneratedCorpusPage {
  return {
    planId: plan.pageId,
    kind: pageKindForSection(plan.section),
    slug: plan.slug,
    title: plan.title,
    description: plan.summary,
    h1: plan.title,
    intro: plan.summary,
    seo: {
      title: plan.title,
      description: plan.summary,
      keywords: [
        "ssot registry",
        slugify(plan.subjectArea),
        plan.intent,
        slugify(plan.audience),
      ],
    },
    schema: schemaForPlan(plan),
    componentIntents: plan.landerComponents.map((component, index) => ({
      id: `${plan.pageId}.component.${index + 1}`,
      kind: componentIntentKind(component),
      data: {
        component,
        structuredDataTypes: plan.structuredDataTypes,
      },
    })),
    sections: sectionsForPlan(plan),
    faq: [
      {
        question: `What should ${plan.audience.toLowerCase()}s know about ${plan.subjectArea} ${plan.intent.replace(/-/g, " ")}?`,
        answer: plan.aeoGoal,
      },
      {
        question: `How does this page help agent discovery?`,
        answer: plan.aieoAgentFact,
      },
    ],
  };
}

function sectionsForPlan(plan: PlannedPage): SectionSpec[] {
  return [
    {
      id: "overview",
      kind: "hero",
      eyebrow: `${plan.section} / ${plan.audience}`,
      title: plan.title,
      subtitle: plan.summary,
      primaryCta: {
        label: plan.primaryCta,
        href: `/content/${slugify(plan.section)}/`,
      },
    },
    {
      id: "answer",
      kind: "feature_grid",
      title: "What this explains",
      items: [
        {
          title: "What it means",
          description: plan.aeoGoal,
        },
        {
          title: "Question this answers",
          description: plan.seoQueryTarget,
        },
        {
          title: "How to apply it",
          description: plan.aieoAgentFact,
        },
      ],
    },
    {
      id: "structured-data",
      kind: "comparison",
      title: "How SSOT Registry keeps this governed",
      columns: [
        { id: "schema", label: "Registry concern" },
        { id: "component", label: "How it is used" },
        { id: "purpose", label: "Why it helps" },
      ],
      rows: plan.structuredDataTypes.map((schemaType, index) => ({
        id: slugify(`${schemaType}-${index}`),
        label: registryConcern(schemaType),
        cells: {
          schema: registryConcern(schemaType),
          component: registryUsage(plan, index),
          purpose: registryBenefit(plan),
        },
      })),
    },
    {
      id: "related-surfaces",
      kind: "package_grid",
      title: "Commands and next steps",
      packages: plan.relatedPackages.map((name, index) => ({
        name,
        description: nextStepDescription(plan, index),
        href: `/content/${slugify(plan.section)}/`,
        api: [plan.relatedApis[index % plan.relatedApis.length] ?? plan.relatedApis[0] ?? "ssot validate"],
      })),
    },
    {
      id: "proof",
      kind: "proof_matrix",
      title: "How teams use this in practice",
      items: [
        {
          claim: `${plan.subjectArea} stay connected to decisions and delivery scope`,
          status: "useful",
          evidence: `${plan.audience}s can inspect the registry trail before relying on ${plan.subjectArea.toLowerCase()} during planning or review.`,
        },
        {
          claim: `${plan.subjectArea} can be explained without losing traceability`,
          status: "practical",
          evidence: plan.aeoGoal,
        },
        {
          claim: `${plan.subjectArea} guide the next SSOT Registry action`,
          status: "actionable",
          evidence: plan.aieoAgentFact,
        },
      ],
    },
  ];
}

function registryConcern(schemaType: string): string {
  const labels: Record<string, string> = {
    WebPage: "Readable guidance",
    TechArticle: "Technical explanation",
    DefinedTerm: "Shared vocabulary",
    BreadcrumbList: "Navigation context",
    ClaimReview: "Claim review",
    Dataset: "Evidence set",
    SoftwareApplication: "Installable application",
    SoftwareSourceCode: "Source repository",
    Product: "Package entry point",
    ItemList: "Indexed resources",
    FAQPage: "Direct answer",
    QAPage: "Question and answer",
    Course: "Learning path",
    CourseInstance: "Course delivery",
    LearningResource: "Lesson material",
    HowTo: "Step-by-step workflow",
    Code: "Command or code example",
    Article: "Explanatory article",
    DefinedTermSet: "Glossary group",
  };
  return labels[schemaType] ?? schemaType.replace(/([a-z])([A-Z])/g, "$1 $2");
}

function registryUsage(plan: PlannedPage, index: number): string {
  const api = plan.relatedApis[index % plan.relatedApis.length] ?? "ssot validate";
  if (plan.section === "Packages" || plan.section === "API_Reference") return `Use ${api} while installing, validating, or inspecting SSOT Registry.`;
  if (plan.section === "Proofs" || plan.section === "Certifications") return `Use ${api} to connect ${plan.subjectArea.toLowerCase()} to claims, tests, evidence, or release review.`;
  if (plan.section === "FAQ_QA" || plan.section === "Glossary") return `Use ${api} when a direct answer needs to point back to registry truth.`;
  return `Use ${api} to inspect or update governed ${plan.subjectArea.toLowerCase()} records.`;
}

function registryBenefit(plan: PlannedPage): string {
  return `This keeps ${plan.subjectArea.toLowerCase()} understandable for ${plan.audience.toLowerCase()}s while preserving the registry links needed for review.`;
}

function nextStepDescription(plan: PlannedPage, index: number): string {
  const api = plan.relatedApis[index % plan.relatedApis.length] ?? "ssot validate";
  if (index === 0) return `Start by running ${api} and reading the registry output for the relevant ${plan.subjectArea.toLowerCase()} records.`;
  if (index === 1) return `Use ${api} to connect this guidance to adjacent SSOT Registry entities instead of tracking it in prose alone.`;
  return `Finish by validating the registry so ${plan.subjectArea.toLowerCase()} remain ready for review, automation, and release work.`;
}

function schemaForPlan(plan: PlannedPage): SchemaSpec[] {
  const normalized = new Set(["WebPage", "BreadcrumbList", ...plan.structuredDataTypes.map(normalizeSchemaKind)]);
  return Array.from(normalized).map((kind) => ({
    kind: kind as SchemaSpec["kind"],
    data: {
      name: plan.title,
      description: plan.summary,
    },
  }));
}

function normalizeSchemaKind(kind: string): string {
  if (kind === "LearningResource") return "Course";
  if (kind === "EducationalOccupationalCredential") return "Course";
  if (kind === "Code") return "SoftwareSourceCode";
  if (kind === "DefinedTerm" || kind === "DefinedTermSet") return "TechArticle";
  return kind;
}

function pageKindForSection(section: string): PageSpec["kind"] {
  if (section === "Packages") return "package";
  if (section === "Proofs") return "proof";
  if (section === "FAQ_QA") return "answer";
  if (section === "Comparisons") return "compare";
  if (section === "Courses" || section === "Lessons" || section === "Certifications") return "docs_bridge";
  return "feature";
}

function componentIntentKind(component: string): string {
  const normalized = component.toLowerCase();
  if (normalized.includes("breadcrumb")) return "breadcrumbs";
  if (normalized.includes("faq") || normalized.includes("qa")) return "faq";
  if (normalized.includes("package")) return "package_grid";
  if (normalized.includes("proof") || normalized.includes("claim")) return "proof_matrix";
  if (normalized.includes("comparison")) return "comparison";
  if (normalized.includes("course") || normalized.includes("lesson") || normalized.includes("article")) return "markdown";
  if (normalized.includes("api") || normalized.includes("code") || normalized.includes("source")) return "markdown";
  return "structured_data_node";
}

function contentIndexPage(sectionPages: GeneratedCorpusPage[]): GeneratedCorpusPage {
  return {
    planId: "page:ssot.content.index",
    kind: "docs_bridge",
    slug: "/content/",
    title: "SSOT Registry Learning and Reference Hub",
    description: "Start with the main SSOT Registry sections, then drill into focused guides, answers, package references, and proof workflows.",
    h1: "Learn SSOT Registry by outcome",
    intro: "Choose the area that matches your question: what SSOT Registry tracks, how proof works, how to install and use the packages, or where to find direct answers.",
    schema: [
      { kind: "WebPage" },
      { kind: "ItemList" },
      { kind: "BreadcrumbList" },
    ],
    componentIntents: [
      { id: "page:ssot.content.index.component.1", kind: "page_shell" },
      { id: "page:ssot.content.index.component.2", kind: "package_grid" },
      { id: "page:ssot.content.index.component.3", kind: "structured_data_graph" },
    ],
    sections: [
      {
        id: "corpus-summary",
        kind: "feature_grid",
        title: "Start with a primary section",
        items: primaryContentSections.map((section) => ({
          title: section.label,
          description: section.description,
          href: section.href,
        })),
      },
      {
        id: "section-indexes",
        kind: "package_grid",
        title: "Browse all focused subsections",
        packages: sectionPages.map((page) => ({
          name: page.title,
          description: page.description,
          href: page.slug,
          api: ["guided index"],
        })),
      },
    ],
    faq: [
      {
        question: "How many generated pages does the content pack expose?",
        answer: "The SSOT Registry site exposes 3,840 focused guides, answers, references, and workflow pages, plus the main indexes that organize them.",
      },
    ],
  };
}

function sectionIndexPage(sectionId: string, sectionLabel: string, pages: GeneratedCorpusPage[]): GeneratedCorpusPage {
  const slug = `/content/${slugify(sectionId)}/`;
  const primarySection = primaryContentSections.find((section) => (section.subsections as readonly string[]).includes(sectionId));
  const subsectionPages = primarySection?.subsections
    .map((subsectionId) => sectionBlueprints.find((section) => section.id === subsectionId))
    .filter((section): section is NonNullable<typeof section> => Boolean(section))
    .map((section) => ({
      name: section.label,
      description: subsectionDescription(section.id, section.label),
      href: `/content/${slugify(section.id)}/`,
      api: ["subsection index"],
    })) ?? [];
  return {
    planId: `page:ssot.content.${slugify(sectionId)}.index`,
    kind: sectionId === "Packages" ? "package" : "docs_bridge",
    slug,
    title: `${sectionLabel} Guide Index`,
    description: `Find SSOT Registry ${sectionLabel.toLowerCase()} guides, explanations, workflows, and next steps.`,
    h1: `${sectionLabel} guides for SSOT Registry`,
    intro: `${sectionLabel} pages explain what to do, why it matters, and how to keep SSOT Registry work inspectable, validated, and ready for review.`,
    schema: [
      { kind: "WebPage" },
      { kind: "ItemList" },
      { kind: "BreadcrumbList" },
    ],
    componentIntents: [
      { id: `page:ssot.content.${slugify(sectionId)}.component.1`, kind: "page_shell" },
      { id: `page:ssot.content.${slugify(sectionId)}.component.2`, kind: "package_grid" },
      { id: `page:ssot.content.${slugify(sectionId)}.component.3`, kind: "structured_data_node" },
    ],
    sections: [
      ...(subsectionPages.length > 1 ? [{
        id: "subsections",
        kind: "package_grid" as const,
        title: `${primarySection?.label ?? sectionLabel} subsections`,
        packages: subsectionPages,
      }] : []),
      {
        id: "page-links",
        kind: "package_grid",
        title: `${sectionLabel} questions and guides`,
        packages: pages.map((page) => ({
          name: page.title,
          description: page.description,
          href: page.slug,
          api: ["open guide"],
        })),
      },
    ],
  };
}

function subsectionDescription(sectionId: string, sectionLabel: string): string {
  const descriptions: Record<string, string> = {
    Features: "Understand the registry entities that SSOT Registry tracks and how they work together.",
    Workflows: "Follow operational paths from decision, scope, proof, certification, promotion, and publication.",
    Comparisons: "Compare governed registry workflows with manual tracking and document-only approaches.",
    Proofs: "Learn how claims, tests, evidence, and boundaries create a reviewable proof chain.",
    Certifications: "Prepare releases for certification using traceable claims and evidence.",
    Courses: "Follow learning paths that teach SSOT Registry concepts in order.",
    Lessons: "Use focused lessons and examples to learn specific SSOT Registry tasks.",
    Packages: "Install and use SSOT Registry package entry points.",
    Packs: "Understand content packs and site packs used to publish registry-backed websites.",
    API_Reference: "Find command and API references for practical SSOT Registry operation.",
    FAQ_QA: "Get direct answers to common SSOT Registry questions.",
    Glossary: "Learn shared vocabulary for registry entities, proof chains, and release workflows.",
  };
  return descriptions[sectionId] ?? `Open ${sectionLabel.toLowerCase()} guidance for SSOT Registry.`;
}
