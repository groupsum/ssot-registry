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
  const readableIntent = formatCopyAcronyms(intent.replace(/-/g, " "));
  if (intent.includes("what") || intent.includes("definition")) return `What are ${subjectArea} in SSOT Registry?`;
  if (intent.includes("how") || intent.includes("guide") || intent.includes("reference")) return `How to use ${subjectArea} in SSOT Registry`;
  if (intent.includes("why") || intent.includes("value")) return `Why ${subjectArea} matter in SSOT Registry`;
  if (intent.includes("install")) return `How to install SSOT Registry for ${subjectArea}`;
  if (intent.includes("answer")) return `${subjectArea} answers for ${audience}s using SSOT Registry`;
  if (intent.includes("vocabulary")) return `${subjectArea} vocabulary for ${audience}s using SSOT Registry`;
  if (intent.includes("pack")) return `${subjectArea} governed pack guidance in SSOT Registry`;
  return `${subjectArea} ${readableIntent} in SSOT Registry for ${audience}s`;
}

function directAnswer(subjectArea: SubjectArea, intent: string, audience: Audience): string {
  const role = audience.toLowerCase();
  if (intent.includes("what") || intent.includes("definition")) {
    return `SSOT Registry explains ${subjectArea} as governed records in .ssot/registry.json, the canonical single source of truth that gives ${role}s authority to name, inspect, and connect software assurance work without relying on scattered notes.`;
  }
  if (intent.includes("how") || intent.includes("guide") || intent.includes("workflow")) {
    return `SSOT Registry explains how ${role}s create or inspect ${subjectArea}, link them to features, claims, tests, evidence, boundaries, or releases, and validate the canonical result before release decisions depend on it.`;
  }
  if (intent.includes("readiness") || intent.includes("proof") || intent.includes("certification")) {
    return `SSOT Registry explains how ${subjectArea} help ${role}s prove readiness by connecting frozen scope, claims, tests, and evidence into a reviewable SSOT authority trail.`;
  }
  return `SSOT Registry explains how ${subjectArea} help ${role}s understand what changed, why it matters, how it is verified, and where the next CLI-backed workflow step belongs in the canonical source of truth.`;
}

function usageQuestion(subjectArea: SubjectArea, intent: string, audience: Audience): string {
  const role = audience.toLowerCase();
  if (intent.includes("what") || intent.includes("definition")) {
    return `${subjectArea} matter because SSOT Registry turns them into named, normalized, inspectable SSOT records instead of leaving ${role}s to reconstruct intent from scattered documents.`;
  }
  if (intent.includes("how") || intent.includes("guide")) {
    return `${role}s use ${subjectArea} by reading or changing the registry entity, linking it to adjacent work, and validating the canonical result before downstream automation or release review depends on it.`;
  }
  if (intent.includes("reference") || intent.includes("command")) {
    return `SSOT Registry commands help ${role}s list, create, link, execute, export, or verify ${subjectArea} while keeping the canonical registry, canon views, and derived views aligned.`;
  }
  if (intent.includes("compare")) {
    return `Governed ${subjectArea} give ${role}s a stronger alternative to manual tracking because IDs, links, status, evidence, and authority can be validated and exported.`;
  }
  if (intent.includes("proof") || intent.includes("certification") || intent.includes("readiness")) {
    return `${subjectArea} improve release readiness because claims, tests, evidence, frozen boundaries, and release status can be reviewed from the same canonical registry trail.`;
  }
  return `${subjectArea} improve governed software delivery for ${role}s by making scope, proof, decisions, and next actions visible in one registry-backed single source of truth workflow.`;
}

function operationalGuidance(subjectArea: SubjectArea, intent: string, audience: Audience): string {
  const role = audience.toLowerCase();
  if (intent.includes("install") || intent.includes("command") || intent.includes("api")) {
    return `Install SSOT Registry with pip or uv, run the relevant ssot command, inspect JSON, CSV, YAML, or graph output, and keep ${subjectArea} linked to the canonical work they support.`;
  }
  if (intent.includes("workflow") || intent.includes("scope") || intent.includes("publish")) {
    return `Use this guidance when ${role}s need a repeatable operating path from ADR and SPEC decisions through scoped features, validation, proof review, certification, promotion, publication, and authority handoff.`;
  }
  return `Use this page to explain ${subjectArea}, choose the next SSOT Registry command or workflow, and keep registry decisions traceable for future maintainers, release reviewers, and canonical authority checks.`;
}

function summaryForPlan(sectionLabel: string, subjectArea: SubjectArea, intent: string, audience: Audience): string {
  const value = usageQuestion(subjectArea, intent, audience);
  return `${value} This ${formatCopyAcronyms(sectionLabel.toLowerCase())} guide explains the concept, shows where it fits in the SSOT canon, and points to practical next steps for a governed single source of truth.`;
}

function rotate(values: readonly string[], index: number, count: number): string[] {
  return Array.from({ length: count }, (_, offset) => values[(index + offset) % values.length] ?? values[0]);
}

function primaryCta(section: string): string {
  const ctas: Record<string, string> = {
    Features: "Inspect feature registry",
    Proofs: "Review proof chain",
    Packages: "Install package",
    Packs: "Review governed pack",
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

function formatCopyAcronyms(value: string): string {
  return value
    .replace(/\bfaq\b/gi, "FAQ")
    .replace(/\bqa\b/gi, "QA");
}
