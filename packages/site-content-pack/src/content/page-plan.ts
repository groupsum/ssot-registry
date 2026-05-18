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
  learnerLevel: "foundation" | "operator" | "reviewer" | "advanced";
  prerequisites: readonly string[];
  learningOutcome: string;
  exercise: string;
  checkpoint: string;
  nextStep: string;
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
  const relatedApiSlice = rotate(relatedApis, rotationIndex, 3);
  const primaryCommand = relatedApiSlice[0] ?? "ssot validate";
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
    relatedApis: relatedApiSlice,
    breadcrumbs: ["SSOT Registry", section.label, subjectArea, intent],
    summary: summaryForPlan(section.label, subjectArea, intent, audience),
    primaryCta: primaryCta(section.id),
    wordTarget: section.id === "FAQ_QA" || section.id === "Glossary" ? 900 : 1400,
    learnerLevel: learnerLevel(section.id, intent),
    prerequisites: prerequisitesFor(section.id, subjectArea),
    learningOutcome: learningOutcomeFor(section.id, subjectArea, intent, audience, primaryCommand),
    exercise: exerciseFor(section.id, subjectArea, audience, primaryCommand),
    checkpoint: checkpointFor(section.id, subjectArea, audience),
    nextStep: nextStepFor(section.id, subjectArea),
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

function learnerLevel(section: string, intent: string): PlannedPage["learnerLevel"] {
  if (section === "FAQ_QA" || section === "Glossary" || intent.includes("what") || intent.includes("definition")) {
    return "foundation";
  }
  if (section === "Proofs" || section === "Certifications" || intent.includes("proof") || intent.includes("readiness")) {
    return "reviewer";
  }
  if (section === "API_Reference" || section === "Workflows" || section === "Packs" || intent.includes("reference")) {
    return "advanced";
  }
  return "operator";
}

function prerequisitesFor(section: string, subjectArea: SubjectArea): string[] {
  const basics = [
    "Know that .ssot/registry.json is the canonical registry authority.",
    `Recognize ${subjectArea} as governed SSOT Registry entities or relationships.`,
  ];
  const additions: Record<string, string> = {
    Proofs: "Understand that claims, tests, and evidence are separate proof-chain records.",
    Certifications: "Understand frozen boundaries before judging release certification.",
    Courses: "Be ready to inspect registry records and follow command output.",
    Lessons: "Complete the matching course overview or understand the entity vocabulary first.",
    API_Reference: "Have a repo with an initialized .ssot registry or a sample registry to inspect.",
    Workflows: "Understand ADR, SPEC, feature, claim, test, evidence, boundary, and release relationships.",
    Packs: "Understand that governed packs import declared ADR and SPEC material into reserved ranges.",
  };
  return additions[section] ? [...basics, additions[section]] : basics;
}

function learningOutcomeFor(
  section: string,
  subjectArea: SubjectArea,
  intent: string,
  audience: Audience,
  command: string,
): string {
  const role = audience.toLowerCase();
  const subject = formatCopyAcronyms(subjectArea.toLowerCase());
  if (section === "Courses") {
    return `By the end, ${role}s can explain ${subject}, run ${command}, and decide the next registry action.`;
  }
  if (section === "Lessons") {
    return `Practice one concrete ${subject} task and verify the result with ${command}.`;
  }
  if (section === "API_Reference") {
    return `Choose and run ${command} for ${subject} without breaking canonical registry authority.`;
  }
  if (section === "Workflows") {
    return `Move ${subject} through the ${intent.replace(/-/g, " ")} workflow with a visible validation checkpoint.`;
  }
  if (section === "Proofs" || section === "Certifications") {
    return `Judge whether ${subject} are backed by linked claims, tests, evidence, and frozen release scope.`;
  }
  return `Explain ${subject} and identify the next command-backed SSOT Registry step.`;
}

function exerciseFor(section: string, subjectArea: SubjectArea, audience: Audience, command: string): string {
  const role = audience.toLowerCase();
  const subject = formatCopyAcronyms(subjectArea.toLowerCase());
  if (section === "Glossary" || section === "FAQ_QA") {
    return `Write a one-paragraph answer for another ${role}, then point it back to ${command} or a registry record.`;
  }
  return `In a sample repo, run ${command}, find the relevant ${subject} records, and note the canonical link or status that should change next.`;
}

function checkpointFor(section: string, subjectArea: SubjectArea, audience: Audience): string {
  const role = audience.toLowerCase();
  const subject = formatCopyAcronyms(subjectArea.toLowerCase());
  if (section === "Certifications" || section === "Proofs") {
    return `A ${role} can identify which claim, test, evidence, boundary, or release row proves the ${subject} state.`;
  }
  return `A ${role} can describe what ${subject} mean, where they live in the registry, and which command validates them.`;
}

function nextStepFor(section: string, subjectArea: SubjectArea): string {
  const subject = formatCopyAcronyms(subjectArea.toLowerCase());
  const next: Record<string, string> = {
    Features: `Link ${subject} to claims, tests, evidence, and a target boundary.`,
    Proofs: `Run claim, test, or evidence verification before release certification.`,
    Packages: `Install the package surface that owns the next ${subject} operation.`,
    Packs: `Run pack preflight before syncing governed ${subject} material.`,
    FAQ_QA: `Open the related workflow or glossary entry for ${subject}.`,
    Courses: `Continue to the linked lessons and complete the quiz checkpoint.`,
    Lessons: `Apply the lesson in a sample registry and validate the result.`,
    Certifications: `Compare the proof chain with the frozen boundary before promotion.`,
    API_Reference: `Run the referenced command and inspect the output artifact.`,
    Workflows: `Validate the registry before moving to the next lifecycle stage.`,
    Comparisons: `Choose the governed registry path when ${subject} need auditability.`,
    Glossary: `Use the term consistently in feature, claim, evidence, boundary, and release copy.`,
  };
  return next[section] ?? `Validate ${subject} before relying on the registry state.`;
}

function formatCopyAcronyms(value: string): string {
  return value
    .replace(/\badr\b/gi, "ADR")
    .replace(/\badrs\b/gi, "ADRs")
    .replace(/\bspec\b/gi, "SPEC")
    .replace(/\bspecs\b/gi, "SPECs")
    .replace(/\bapi\b/gi, "API")
    .replace(/\bfaq\b/gi, "FAQ")
    .replace(/\bqa\b/gi, "QA");
}
