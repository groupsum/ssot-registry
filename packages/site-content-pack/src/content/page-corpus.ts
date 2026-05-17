import type { PageSpec, SchemaSpec, SectionSpec } from "@mdwrk/lander-content-contract";
import { generatePagePlans, slugify, type PlannedPage } from "./page-plan.js";
import { sectionBlueprints } from "./sections.js";

export interface GeneratedCorpusPage extends PageSpec {
  planId: string;
}

export const generatedPagePlans = generatePagePlans();
export const generatedCorpusPages = generatedPagePlans.map(pageSpecFromPlan);
export const generatedSectionIndexPages = sectionBlueprints.map((section) =>
  sectionIndexPage(section.id, section.label, generatedCorpusPages.filter((page) => page.slug.startsWith(`/${slugify(section.id)}/`))),
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
        href: "/docs/",
      },
    },
    {
      id: "answer",
      kind: "feature_grid",
      title: "Answer and discovery targets",
      items: [
        {
          title: "AEO direct answer",
          description: plan.aeoGoal,
        },
        {
          title: "SEO query target",
          description: plan.seoQueryTarget,
        },
        {
          title: "AiEO agent fact",
          description: plan.aieoAgentFact,
        },
      ],
    },
    {
      id: "structured-data",
      kind: "comparison",
      title: "Structured-data component plan",
      columns: [
        { id: "schema", label: "Structured data" },
        { id: "component", label: "Lander component" },
        { id: "purpose", label: "Purpose" },
      ],
      rows: plan.structuredDataTypes.map((schemaType, index) => ({
        id: slugify(`${schemaType}-${index}`),
        label: schemaType,
        cells: {
          schema: schemaType,
          component: plan.landerComponents[index % plan.landerComponents.length] ?? "Breadcrumbs",
          purpose: `Support ${plan.section} ${plan.intent} discovery for ${plan.audience}s.`,
        },
      })),
    },
    {
      id: "related-surfaces",
      kind: "package_grid",
      title: "Related SSOT surfaces",
      packages: plan.relatedPackages.map((name, index) => ({
        name,
        description: `Related SSOT Registry package surface for ${plan.subjectArea}.`,
        href: "/docs/",
        api: [plan.relatedApis[index % plan.relatedApis.length] ?? plan.relatedApis[0] ?? "ssot validate"],
      })),
    },
    {
      id: "proof",
      kind: "proof_matrix",
      title: "Proof and traceability cues",
      items: [
        {
          claim: `${plan.subjectArea} page has SEO intent`,
          status: "supported",
          evidence: plan.seoQueryTarget,
        },
        {
          claim: `${plan.subjectArea} page has AEO answer`,
          status: "supported",
          evidence: plan.aeoGoal,
        },
        {
          claim: `${plan.subjectArea} page has AiEO fact`,
          status: "supported",
          evidence: plan.aieoAgentFact,
        },
      ],
    },
  ];
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
    title: "SSOT Registry Content Corpus",
    description: "Index of the generated SSOT Registry content corpus across all section families.",
    h1: "SSOT Registry content corpus",
    intro: "The content pack generates 3,840 AEO, SEO, and AiEO-oriented pages from governed SSOT Registry subject, audience, intent, structured-data, and component sets.",
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
        title: "Generated corpus proof",
        items: [
          {
            title: "3,840 generated pages",
            description: "Twelve section families, twenty subject areas, four intents, and four audiences produce the visible page corpus.",
          },
          {
            title: "Structured-data backed",
            description: "Every page declares schema intents and structured-data-backed component families for retrieval and rendering.",
          },
          {
            title: "Discovery artifacts",
            description: "The same corpus emits sitemap.xml, robots.txt, llms.txt, llms-full.txt, semantic index, content index, and structured-data graph artifacts.",
          },
        ],
      },
      {
        id: "section-indexes",
        kind: "package_grid",
        title: "Section indexes",
        packages: sectionPages.map((page) => ({
          name: page.title,
          description: page.description,
          href: page.slug,
          api: ["section corpus index"],
        })),
      },
    ],
    faq: [
      {
        question: "How many generated pages does the content pack expose?",
        answer: "The content pack exposes 3,840 generated corpus pages, plus index pages and the home page.",
      },
    ],
  };
}

function sectionIndexPage(sectionId: string, sectionLabel: string, pages: GeneratedCorpusPage[]): GeneratedCorpusPage {
  const slug = `/content/${slugify(sectionId)}/`;
  return {
    planId: `page:ssot.content.${slugify(sectionId)}.index`,
    kind: sectionId === "Packages" ? "package" : "docs_bridge",
    slug,
    title: `${sectionLabel} Content Index`,
    description: `Index of ${pages.length} generated SSOT Registry ${sectionLabel} pages.`,
    h1: `${sectionLabel} content index`,
    intro: `This section exposes ${pages.length} generated pages for the ${sectionLabel} corpus family.`,
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
      {
        id: "page-links",
        kind: "package_grid",
        title: `${sectionLabel} pages`,
        packages: pages.map((page) => ({
          name: page.title,
          description: page.description,
          href: page.slug,
          api: [page.planId],
        })),
      },
    ],
  };
}
