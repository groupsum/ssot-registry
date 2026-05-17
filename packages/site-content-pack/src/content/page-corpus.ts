import type { PageSpec, SchemaSpec, SectionSpec } from "@mdwrk/lander-content-contract";
import { generatePagePlans, slugify, type PlannedPage } from "./page-plan.js";

export interface GeneratedCorpusPage extends PageSpec {
  planId: string;
}

export const generatedPagePlans = generatePagePlans();
export const generatedCorpusPages = generatedPagePlans.map(pageSpecFromPlan);

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
