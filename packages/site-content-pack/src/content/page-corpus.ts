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
    description: "Install SSOT Registry, find the package split, and use CLI, runtime, conformance, contract, view, codegen, and TUI entry points.",
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
    componentIntents: componentIntentsForPlan(plan),
    sections: sectionsForPlan(plan),
    faq: [
      {
        question: `What should ${plan.audience.toLowerCase()}s know about ${plan.subjectArea} in SSOT Registry?`,
        answer: plan.aeoGoal,
      },
      {
        question: `How should ${plan.audience.toLowerCase()}s use this guidance?`,
        answer: plan.aieoAgentFact,
      },
    ],
  };
}

function sectionsForPlan(plan: PlannedPage): SectionSpec[] {
  if (plan.section === "Courses") return courseSectionsForPlan(plan);
  return [
    {
      id: "overview",
      kind: "hero",
      eyebrow: `${formatSectionLabel(plan.section)} / ${plan.audience}`,
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
      title: "What, why, how, and when",
      items: [
        {
          title: `What are ${plan.subjectArea}?`,
          description: plan.aeoGoal,
        },
        {
          title: "Why it matters",
          description: plan.seoQueryTarget,
        },
        {
          title: "How to use it",
          description: plan.aieoAgentFact,
        },
        {
          title: "When to use it",
          description: whenToUse(plan),
        },
      ],
    },
    {
      id: "usage",
      kind: "feature_grid",
      title: "Install, use, and operate SSOT Registry",
      items: usageSteps(plan),
    },
    {
      id: "structured-data",
      kind: "comparison",
      title: "How SSOT Registry explains the governed record",
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

function courseSectionsForPlan(plan: PlannedPage): SectionSpec[] {
  return [
    {
      id: "overview",
      kind: "hero",
      eyebrow: `Course / ${plan.audience}`,
      title: plan.title,
      subtitle: `${plan.summary} Start with the course overview, then work through lessons and the follow-up quiz.`,
      primaryCta: {
        label: "Start course",
        href: "#course-overview",
      },
      secondaryCta: {
        label: "View course index",
        href: "/content/courses/",
      },
    },
    {
      id: "course-metadata",
      kind: "comparison",
      title: "Course metadata",
      columns: [
        { id: "field", label: "Field" },
        { id: "value", label: "Value" },
        { id: "registry-use", label: "How SSOT Registry uses it" },
      ],
      rows: [
        {
          id: "course-audience",
          label: "Audience",
          cells: {
            field: "Audience",
            value: plan.audience,
            "registry-use": `Keeps the course focused on how ${plan.audience.toLowerCase()}s use ${plan.subjectArea.toLowerCase()} in governed delivery work.`,
          },
        },
        {
          id: "course-subject",
          label: "Subject",
          cells: {
            field: "Subject",
            value: plan.subjectArea,
            "registry-use": `Connects course work to the ${plan.subjectArea.toLowerCase()} records that appear in .ssot/registry.json.`,
          },
        },
        {
          id: "course-outcome",
          label: "Outcome",
          cells: {
            field: "Outcome",
            value: "Operational registry confidence",
            "registry-use": "The learner should know which registry entity to inspect, which command to run, and which proof link matters next.",
          },
        },
        {
          id: "course-structured-data",
          label: "Structured data",
          cells: {
            field: "Structured data",
            value: "Course, CourseInstance, ItemList, QAPage",
            "registry-use": "Search and assistant surfaces can identify the page as a course, its delivery instance, its lesson list, and its quiz questions.",
          },
        },
      ],
    },
    {
      id: "course-overview",
      kind: "feature_grid",
      title: "What, why, how, and when",
      items: [
        {
          title: "What you will learn",
          description: plan.aeoGoal,
        },
        {
          title: "Why the course matters",
          description: plan.seoQueryTarget,
        },
        {
          title: "How to operate it",
          description: plan.aieoAgentFact,
        },
        {
          title: "When to use this course",
          description: `Use this course when ${plan.audience.toLowerCase()}s need to turn ${plan.subjectArea.toLowerCase()} from a concept into a registry action they can validate.`,
        },
      ],
    },
    {
      id: "course-operation",
      kind: "feature_grid",
      title: "Install, use, and operate SSOT Registry",
      items: usageSteps(plan),
    },
    {
      id: "course-lessons",
      kind: "package_grid",
      title: "Course lessons",
      packages: courseLessons(plan).map((lesson, index) => ({
        name: lesson.title,
        description: lesson.description,
        href: lesson.href,
        api: [plan.relatedApis[index % plan.relatedApis.length] ?? "ssot validate"],
      })),
    },
    {
      id: "course-quiz",
      kind: "faq",
      title: "Follow-up course quiz",
      items: courseQuiz(plan),
    },
    {
      id: "course-proof",
      kind: "proof_matrix",
      title: "Completion checks",
      items: [
        {
          claim: `${plan.subjectArea} course explains the governed entity`,
          status: "course objective",
          evidence: "The learner can describe the entity, its registry links, and the command used to inspect or update it.",
        },
        {
          claim: `${plan.subjectArea} course prepares a practical next step`,
          status: "course objective",
          evidence: `The learner can choose ${plan.relatedApis[0] ?? "ssot validate"} or another relevant command before making release decisions.`,
        },
        {
          claim: `${plan.subjectArea} course includes a quiz`,
          status: "course objective",
          evidence: "The follow-up quiz checks concept, operation, and release-readiness understanding.",
        },
      ],
    },
  ];
}

function courseLessons(plan: PlannedPage) {
  const subjectSlug = slugify(plan.subjectArea);
  const audienceSlug = slugify(plan.audience);
  return [
    {
      title: `Lesson 1: Locate ${plan.subjectArea} in the registry`,
      description: `Inspect how ${plan.subjectArea.toLowerCase()} are represented, named, and linked inside .ssot/registry.json before changing them.`,
      href: `/lessons/${audienceSlug}/${subjectSlug}/lesson/`,
    },
    {
      title: `Lesson 2: Connect ${plan.subjectArea} to proof`,
      description: `Trace the path from ${plan.subjectArea.toLowerCase()} to features, claims, tests, evidence, and reviewable release state.`,
      href: `/lessons/${audienceSlug}/${subjectSlug}/worked-example/`,
    },
    {
      title: `Lesson 3: Operate the workflow`,
      description: `Run the relevant SSOT Registry command, inspect output, and decide whether the registry is ready for validation or release review.`,
      href: `/workflows/${audienceSlug}/${subjectSlug}/proof-to-certify/`,
    },
  ];
}

function courseQuiz(plan: PlannedPage) {
  const command = plan.relatedApis[0] ?? "ssot validate";
  return [
    {
      question: `What makes ${plan.subjectArea} trustworthy in SSOT Registry?`,
      answer: `${plan.subjectArea} become trustworthy when they are named with stable IDs, linked to adjacent registry entities, and validated instead of being tracked only in prose.`,
    },
    {
      question: `Which command should a ${plan.audience.toLowerCase()} try first after this course?`,
      answer: `Start with ${command}, then inspect whether the output confirms the relevant ${plan.subjectArea.toLowerCase()} links and statuses.`,
    },
    {
      question: `How does this course support release review?`,
      answer: `It teaches how ${plan.subjectArea.toLowerCase()} connect to proof, boundaries, certification, promotion, publication, or the next reviewable registry action.`,
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

function whenToUse(plan: PlannedPage): string {
  if (plan.section === "Packages" || plan.section === "API_Reference") {
    return `Use this when you need to install SSOT Registry, find the right command, or understand how ${plan.subjectArea.toLowerCase()} fit into daily operation.`;
  }
  if (plan.section === "Proofs" || plan.section === "Certifications") {
    return `Use this before certification, release review, or any decision that depends on traceable ${plan.subjectArea.toLowerCase()}.`;
  }
  if (plan.section === "FAQ_QA" || plan.section === "Glossary") {
    return `Use this when a teammate, reviewer, or automation needs a clear explanation of ${plan.subjectArea.toLowerCase()} without losing registry context.`;
  }
  return `Use this when ${plan.audience.toLowerCase()}s need to understand, update, validate, or explain ${plan.subjectArea.toLowerCase()} in SSOT Registry.`;
}

function usageSteps(plan: PlannedPage): Array<Record<string, unknown>> {
  const firstApi = plan.relatedApis[0] ?? "ssot validate";
  const secondApi = plan.relatedApis[1] ?? "ssot feature list";
  const thirdApi = plan.relatedApis[2] ?? "ssot release certify";
  return [
    {
      title: "Install",
      description: "Install SSOT Registry with `python -m pip install ssot-registry`, `uv add ssot-registry`, or a project-local uv environment before changing registry state.",
      href: "/content/packages/",
    },
    {
      title: "Inspect",
      description: `Run ${firstApi} to inspect .ssot/registry.json and its derived views before changing ${plan.subjectArea.toLowerCase()}.`,
      href: `/content/${slugify(plan.section)}/`,
    },
    {
      title: "Use",
      description: `Run ${secondApi} when you need to create, list, link, execute, export, or explain ${plan.subjectArea.toLowerCase()} as part of an SSOT Registry workflow.`,
      href: `/content/${slugify(plan.section)}/`,
    },
    {
      title: "Operate",
      description: `Run ${thirdApi} or validate the registry before certification, promotion, publication, or release closure depends on this work.`,
      href: "/content/workflows/",
    },
  ];
}

function registryUsage(plan: PlannedPage, index: number): string {
  const api = plan.relatedApis[index % plan.relatedApis.length] ?? "ssot validate";
  if (plan.section === "Packages" || plan.section === "API_Reference") return `Use ${api} while installing, validating, exporting, or inspecting SSOT Registry.`;
  if (plan.section === "Proofs" || plan.section === "Certifications") return `Use ${api} to connect ${plan.subjectArea.toLowerCase()} to claims, tests, evidence, or release review.`;
  if (plan.section === "FAQ_QA" || plan.section === "Glossary") return `Use ${api} when a direct answer needs to point back to registry truth.`;
  return `Use ${api} to inspect or update governed ${plan.subjectArea.toLowerCase()} records.`;
}

function registryBenefit(plan: PlannedPage): string {
  return `This keeps ${plan.subjectArea.toLowerCase()} understandable for ${plan.audience.toLowerCase()}s while preserving the registry links needed for validation, automation, and release review.`;
}

function nextStepDescription(plan: PlannedPage, index: number): string {
  const api = plan.relatedApis[index % plan.relatedApis.length] ?? "ssot validate";
  if (index === 0) return `Start by running ${api} and reading the registry output for the relevant ${plan.subjectArea.toLowerCase()} records.`;
  if (index === 1) return `Use ${api} to connect this guidance to adjacent SSOT Registry entities instead of tracking it in prose alone.`;
  return `Finish by validating the registry so ${plan.subjectArea.toLowerCase()} remain ready for review, automation, and release work.`;
}

function schemaForPlan(plan: PlannedPage): SchemaSpec[] {
  const normalized = new Set(["WebPage", "BreadcrumbList", ...plan.structuredDataTypes.map(normalizeSchemaKind)]);
  if (plan.section === "Courses") {
    normalized.add("Course");
    normalized.add("CourseInstance");
    normalized.add("ItemList");
    normalized.add("FAQPage");
    normalized.add("QAPage");
  }
  return Array.from(normalized).map((kind) => ({
    kind: kind as SchemaSpec["kind"],
    data: {
      name: plan.title,
      description: plan.summary,
    },
  }));
}

function componentIntentsForPlan(plan: PlannedPage) {
  const componentNames = [...plan.landerComponents];
  if (plan.section === "Courses") {
    componentNames.push("CourseBlock", "LessonListBlock", "FAQPageBlock", "QAPageBlock");
  }
  return componentNames.map((component, index) => ({
    id: `${plan.pageId}.component.${index + 1}`,
    kind: componentIntentKind(component),
    data: {
      component,
      structuredDataTypes: plan.section === "Courses"
        ? [...new Set([...plan.structuredDataTypes, "Course", "CourseInstance", "ItemList", "FAQPage", "QAPage"])]
        : plan.structuredDataTypes,
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
    description: "Start with the main SSOT Registry sections, then drill into focused guides for governed entities, proof chains, packages, commands, and direct operating answers.",
    h1: "Learn SSOT Registry by outcome",
    intro: "Choose the area that matches your question: what SSOT Registry tracks, how proof works, how to install and operate the CLI, or how to answer a release-review question from registry truth.",
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
        question: "How much SSOT Registry guidance is available?",
        answer: "The SSOT Registry site organizes 3,840 focused guides, answers, references, and workflow pages around registry entities, proof chains, package surfaces, and release operations.",
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
    description: `Find SSOT Registry ${formatCopyAcronyms(sectionLabel.toLowerCase())} guides, explanations, workflows, and next steps.`,
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
          name: indexCardTitle(page),
          description: indexCardDescription(page),
          href: page.slug,
          api: indexCardActions(page),
        })),
      },
    ],
  };
}

function planForPage(page: GeneratedCorpusPage) {
  return generatedPagePlans.find((plan) => plan.pageId === page.planId);
}

function indexCardTitle(page: GeneratedCorpusPage): string {
  const plan = planForPage(page);
  if (!plan) return page.title;
  const audience = plan.audience === "Vibe coder" ? "Vibe coder" : `${plan.audience} guide`;
  if (plan.section === "API_Reference") return `${audience}: ${plan.subjectArea} ${intentLabel(plan.intent)}`;
  if (plan.section === "FAQ_QA") return `${audience}: ${plan.subjectArea} answer`;
  if (plan.section === "Glossary") return `${audience}: ${plan.subjectArea} vocabulary`;
  if (plan.section === "Workflows") return `${audience}: ${intentLabel(plan.intent)} for ${plan.subjectArea}`;
  if (plan.section === "Certifications") return `${audience}: ${plan.subjectArea} readiness`;
  return `${audience}: ${page.title}`;
}

function indexCardDescription(page: GeneratedCorpusPage): string {
  const plan = planForPage(page);
  if (!plan) return page.description;
  const role = plan.audience.toLowerCase();
  const subject = plan.subjectArea.toLowerCase();
  const command = plan.relatedApis[0] ?? "ssot validate";
  const variants: Record<string, string> = {
    Features: `Shows ${role}s how ${subject} become targetable registry records, where they link to specs, claims, tests, and evidence, and what to validate next.`,
    Proofs: `Connects ${subject} to claim review, evidence status, and release confidence so ${role}s can see what is proved and what still needs work.`,
    Packages: `Helps ${role}s choose the package surface for ${subject}, install the right tool, and move from package discovery into a working SSOT command.`,
    Packs: `Explains how governed packs keep ${subject} reusable, reserved, and reviewable without mixing package-owned material into repo-local scope.`,
    FAQ_QA: `Answers the practical ${subject} question in a direct form, then points ${role}s back to the registry relationship that makes the answer trustworthy.`,
    Courses: `Frames ${subject} as a learning path for ${role}s, including the prerequisite concepts and the registry outcome the lesson should produce.`,
    Lessons: `Gives ${role}s a focused exercise for ${subject}, with enough operating context to practice the command path instead of only reading definitions.`,
    Certifications: `Prepares ${role}s to review ${subject} against claim tiers, passing tests, evidence rows, frozen boundaries, and release status.`,
    API_Reference: `Maps ${subject} to ${command}, explains when ${role}s should run it, and shows how command output supports validation, export, or review.`,
    Workflows: `Places ${subject} inside the ${intentLabel(plan.intent)} workflow so ${role}s can move from decision state to the next governed action.`,
    Comparisons: `Compares manual ${subject} tracking with SSOT Registry records, emphasizing stable IDs, links, evidence, and exportable review trails.`,
    Glossary: `Defines ${subject} in operational language for ${role}s and connects the term to commands, proof links, and release-review vocabulary.`,
  };
  return variants[plan.section] ?? page.description;
}

function indexCardActions(page: GeneratedCorpusPage): string[] {
  const plan = planForPage(page);
  if (!plan) return ["open guide"];
  return [plan.relatedApis[0] ?? "ssot validate"];
}

function intentLabel(intent: string): string {
  return formatCopyAcronyms(intent.replace(/-/g, " "));
}

function formatSectionLabel(sectionId: string): string {
  const section = sectionBlueprints.find((blueprint) => blueprint.id === sectionId);
  return section?.label ?? formatCopyAcronyms(sectionId.replace(/_/g, " "));
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
    Packs: "Understand packaged contracts, immutable document ranges, and reusable governed registry material.",
    API_Reference: "Find command and API references for practical SSOT Registry operation.",
    FAQ_QA: "Get direct answers to common SSOT Registry questions.",
    Glossary: "Learn shared vocabulary for registry entities, proof chains, and release workflows.",
  };
  return descriptions[sectionId] ?? `Open ${formatCopyAcronyms(sectionLabel.toLowerCase())} guidance for SSOT Registry.`;
}

function formatCopyAcronyms(value: string): string {
  return value
    .replace(/\bfaq\b/gi, "FAQ")
    .replace(/\bqa\b/gi, "QA");
}
