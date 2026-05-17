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
    title: titleForPlan(subjectArea, intent, audience),
    section: section.id,
    subjectArea,
    intent,
    audience,
    aeoGoal: directAnswer(subjectArea, intent, audience),
    seoQueryTarget: usageQuestion(subjectArea, intent, audience),
    aieoAgentFact: operationalGuidance(subjectArea, intent, audience),
    structuredDataTypes: section.structuredDataTypes,
    landerComponents: section.components,
    relatedPackages: rotate(relatedPackages, rotationIndex, 3),
    relatedApis: rotate(relatedApis, rotationIndex, 3),
    breadcrumbs: ["SSOT Registry", section.label, subjectArea, intent],
    summary: summaryForPlan(section.label, subjectArea, intent, audience),
    primaryCta: primaryCta(section.id),
    wordTarget: section.id === "FAQ_QA" || section.id === "Glossary" ? 900 : 1400,
  };
}

function titleForPlan(subjectArea: SubjectArea, intent: string, audience: Audience): string {
  const readableIntent = intent.replace(/-/g, " ");
  if (intent.includes("what") || intent.includes("definition")) return `What are ${subjectArea} in SSOT Registry?`;
  if (intent.includes("how") || intent.includes("guide") || intent.includes("reference")) return `How to use ${subjectArea} in SSOT Registry`;
  if (intent.includes("why") || intent.includes("value")) return `Why ${subjectArea} matter in SSOT Registry`;
  if (intent.includes("install")) return `How to install SSOT Registry for ${subjectArea}`;
  return `${subjectArea} ${readableIntent} in SSOT Registry for ${audience}s`;
}

function directAnswer(subjectArea: SubjectArea, intent: string, audience: Audience): string {
  const role = audience.toLowerCase();
  if (intent.includes("what") || intent.includes("definition")) {
    return `${subjectArea} in SSOT Registry give ${role}s a governed way to name, inspect, and connect software assurance work without relying on scattered notes.`;
  }
  if (intent.includes("how") || intent.includes("guide") || intent.includes("workflow")) {
    return `${role}s use SSOT Registry to create or inspect ${subjectArea}, link them to related registry entities, and validate the result before release decisions depend on it.`;
  }
  if (intent.includes("readiness") || intent.includes("proof") || intent.includes("certification")) {
    return `${subjectArea} help ${role}s prove readiness by connecting scope, claims, tests, and evidence into a reviewable registry trail.`;
  }
  return `${subjectArea} help ${role}s understand what changed, why it matters, how it is verified, and where to continue the SSOT Registry workflow.`;
}

function usageQuestion(subjectArea: SubjectArea, intent: string, audience: Audience): string {
  const role = audience.toLowerCase();
  if (intent.includes("what") || intent.includes("definition")) return `What should ${role}s know about ${subjectArea} in SSOT Registry?`;
  if (intent.includes("how") || intent.includes("guide")) return `How do ${role}s use SSOT Registry for ${subjectArea}?`;
  if (intent.includes("reference") || intent.includes("command")) return `Which SSOT Registry commands help ${role}s work with ${subjectArea}?`;
  if (intent.includes("compare")) return `When should ${role}s use governed ${subjectArea} instead of manual tracking?`;
  return `Why do ${subjectArea} improve governed software delivery for ${role}s?`;
}

function operationalGuidance(subjectArea: SubjectArea, intent: string, audience: Audience): string {
  const role = audience.toLowerCase();
  if (intent.includes("install") || intent.includes("command") || intent.includes("api")) {
    return `Install the CLI, run the relevant ssot command, inspect the registry output, and keep ${subjectArea} linked to the work they support.`;
  }
  if (intent.includes("workflow") || intent.includes("scope") || intent.includes("publish")) {
    return `Use this guidance when ${role}s need a repeatable path from planning through validation, proof review, and release closure.`;
  }
  return `Use this page to explain ${subjectArea}, choose the next SSOT Registry action, and keep decisions traceable for future reviewers.`;
}

function summaryForPlan(sectionLabel: string, subjectArea: SubjectArea, intent: string, audience: Audience): string {
  const question = usageQuestion(subjectArea, intent, audience);
  return `${question} This ${sectionLabel.toLowerCase()} guide explains the concept, shows where it fits in the registry, and points to practical next steps.`;
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
