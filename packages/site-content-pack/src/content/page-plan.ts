import { audiences, type Audience } from "./audiences.js";
import { relatedApis } from "./apis.js";
import { relatedPackages } from "./packages.js";
import { sectionBlueprints, type SectionBlueprint } from "./sections.js";
import { subjectAreas, type SubjectArea } from "./subjects.js";

export interface PlannedPage {
  pageId: string;
  slug: string;
  title: string;
  section: string;
  subjectArea: SubjectArea;
  intent: string;
  audience: Audience;
  aeoGoal: string;
  seoQueryTarget: string;
  aieoAgentFact: string;
  structuredDataTypes: readonly string[];
  landerComponents: readonly string[];
  relatedPackages: readonly string[];
  relatedApis: readonly string[];
  breadcrumbs: readonly string[];
  summary: string;
  primaryCta: string;
  wordTarget: number;
}

export const contentPlanFormula = "12 sections * 20 subject areas * 4 intents * 4 audiences = 3840 pages";

export function slugify(value: string): string {
  return value
    .toLowerCase()
    .replace(/_/g, "-")
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");
}

export function generatePagePlans(): PlannedPage[] {
  return sectionBlueprints.flatMap((section) =>
    subjectAreas.flatMap((subjectArea, subjectIndex) =>
      section.intents.flatMap((intent, intentIndex) =>
        audiences.map((audience, audienceIndex) =>
          buildPagePlan(section, subjectArea, intent, audience, subjectIndex + intentIndex + audienceIndex),
        ),
      ),
    ),
  );
}

function buildPagePlan(
  section: SectionBlueprint,
  subjectArea: SubjectArea,
  intent: string,
  audience: Audience,
  rotationIndex: number,
): PlannedPage {
  const sectionSlug = slugify(section.id);
  const subjectSlug = slugify(subjectArea);
  const intentSlug = slugify(intent);
  const audienceSlug = slugify(audience);
  return {
    pageId: `page:ssot.${sectionSlug}.${audienceSlug}.${subjectSlug}.${intentSlug}`,
    slug: `/${sectionSlug}/${audienceSlug}/${subjectSlug}/${intentSlug}/`,
    title: `${subjectArea} ${intent.replace(/-/g, " ")} for ${audience}s`,
    section: section.id,
    subjectArea,
    intent,
    audience,
    aeoGoal: `Answer the ${audience.toLowerCase()} question for ${subjectArea} with a direct, snippet-ready explanation.`,
    seoQueryTarget: `ssot registry ${slugify(subjectArea)} ${intent.replace(/-/g, " ")}`,
    aieoAgentFact: `Agent fact: ${subjectArea} uses ${intent} content in the ${section.id} section with governed relationships.`,
    structuredDataTypes: section.structuredDataTypes,
    landerComponents: section.components,
    relatedPackages: rotate(relatedPackages, rotationIndex, 3),
    relatedApis: rotate(relatedApis, rotationIndex, 3),
    breadcrumbs: ["SSOT Registry", section.label, subjectArea, intent],
    summary: `Planned ${section.label} page combining ${subjectArea}, ${intent}, and ${audience} content for SEO, AEO, and AiEO discovery.`,
    primaryCta: primaryCta(section.id),
    wordTarget: section.id === "FAQ_QA" || section.id === "Glossary" ? 900 : 1400,
  };
}

function rotate(values: readonly string[], index: number, count: number): string[] {
  return Array.from({ length: count }, (_, offset) => values[(index + offset) % values.length] ?? values[0]);
}

function primaryCta(section: string): string {
  const ctas: Record<string, string> = {
    Features: "Inspect feature registry",
    Proofs: "Review proof chain",
    Packages: "Install package",
    Packs: "Open content pack",
    FAQ_QA: "Read related answer",
    Courses: "Start course",
    Lessons: "Open lesson",
    Certifications: "Check readiness",
    API_Reference: "Run command",
    Workflows: "Execute workflow",
    Comparisons: "Compare paths",
    Glossary: "Explore related terms",
  };
  return ctas[section] ?? "Read page";
}
