import assert from "node:assert/strict";
import { compileLanderSite } from "@mdwrk/lander-core";
import {
  flattenSitemapTree,
  generatedContentIndexPage,
  generatedCorpusPages,
  generatedPagePlans,
  generatedSectionIndexPages,
  primarySitemapSections,
  ssotRegistrySite,
  ssotRegistrySitemapTree,
} from "../dist/index.js";

const compiled = compileLanderSite(ssotRegistrySite);
const generatedPages = generatedCorpusPages;
const slugs = new Set(ssotRegistrySite.pages.map((page) => page.slug));
const planIds = new Set(generatedPagePlans.map((plan) => plan.pageId));
const nonCopyKeys = new Set([
  "api",
  "componentIntents",
  "href",
  "id",
  "kind",
  "keywords",
  "pageId",
  "planId",
  "schema",
  "slug",
]);

assert.ok(ssotRegistrySite.pages.length >= 2500);
assert.equal(generatedPages.length, 3840);
assert.equal(generatedSectionIndexPages.length, 12);
assert.equal(generatedContentIndexPage.slug, "/content/");
assert.ok(ssotRegistrySite.pages.some((page) => page.slug === "/content/features/"));
assert.equal(slugs.size, ssotRegistrySite.pages.length);
assert.equal(compiled.pages.length, ssotRegistrySite.pages.length);

const sitemapNodes = flattenSitemapTree(ssotRegistrySitemapTree);
const sitemapPaths = new Set(sitemapNodes.map((node) => node.path));
assert.equal(ssotRegistrySitemapTree.pageCount, ssotRegistrySite.pages.length);
assert.equal(sitemapNodes.length, ssotRegistrySite.pages.length);
assert.equal(sitemapPaths.size, ssotRegistrySite.pages.length);
for (const page of ssotRegistrySite.pages) {
  assert.ok(sitemapPaths.has(page.slug), `${page.slug} must be represented in the formal sitemap tree`);
}
assert.deepEqual(
  ssotRegistrySitemapTree.children[0]?.children.map((node) => node.path),
  primarySitemapSections.map((section) => section.path),
  "formal sitemap tree must start from the four primary header sections",
);
for (const primary of ssotRegistrySitemapTree.children[0]?.children ?? []) {
  assert.equal(primary.kind, "primary-section");
  assert.ok(primary.pageCount > 1, `${primary.path} must own subsection or detail descendants`);
}

for (const page of generatedPages) {
  assert.ok(page.planId, `${page.slug} must map back to a plan`);
  assert.ok(planIds.has(page.planId), `${page.slug} must map to a known plan`);
  assert.ok(page.schema?.length > 0, `${page.slug} must declare schema intents`);
  assert.ok(page.componentIntents?.length > 0, `${page.slug} must declare component intents`);
  assert.ok(page.sections.length >= 4, `${page.slug} must use at least four section types`);
  assert.notDeepEqual([...new Set(page.sections.map((section) => section.kind))], ["markdown"]);
  assert.equal(page.sections[0]?.eyebrow, undefined, `${page.slug} must not render generated intro badge copy`);
  assert.ok(compiled.pageByPath.has(page.slug), `${page.slug} must be routable after compile`);
  const renderedText = JSON.stringify(page);
  assert.ok(renderedText.includes("What, why, how, and when"), `${page.slug} must answer reader question types`);
  assert.ok(renderedText.includes("Install, use, and operate SSOT Registry"), `${page.slug} must teach install/use/operation`);
  assert.ok(
    renderedText.includes("Learning outcome and checkpoint") || renderedText.includes("Course metadata"),
    `${page.slug} must expose curriculum checkpoint content`,
  );
  assert.ok(renderedText.includes("Prerequisites"), `${page.slug} must expose prerequisites`);
  assert.ok(renderedText.includes("Exercise"), `${page.slug} must expose exercises`);
  assert.ok(renderedText.includes("SSOT Registry explains"), `${page.slug} must use reader-facing explanatory language`);
  const copy = visibleCopy(page);
  assert.match(copy, /\bSSOT\b/, `${page.slug} visible copy must strengthen SSOT presence`);
  assert.match(copy, /single source of truth/i, `${page.slug} visible copy must mention single source of truth`);
  assert.match(copy, /canonical/i, `${page.slug} visible copy must mention canonical positioning`);
  assert.match(copy, /\bcanon\b/i, `${page.slug} visible copy must mention canon positioning`);
  assert.match(copy, /authority/i, `${page.slug} visible copy must mention authority positioning`);
  assert.equal(renderedText.includes("agent discovery"), false, `${page.slug} must not expose discovery mechanics`);
  assert.equal(renderedText.includes("page has"), false, `${page.slug} must not expose generation mechanics`);
}

const apiReferenceIndex = generatedSectionIndexPages.find((page) => page.slug === "/content/api-reference/");
assert.ok(apiReferenceIndex, "API Reference index must exist");
const apiCards = apiReferenceIndex.sections
  .find((section) => section.id === "page-links")
  ?.packages ?? [];
assert.ok(apiCards.length > 0, "API Reference index must include guide cards");
const firstNineCards = apiCards.slice(0, 9);
assert.ok(
  new Set(firstNineCards.map((card) => card.name)).size > 3,
  "API Reference index card titles must vary beyond repeated page titles",
);
assert.ok(
  new Set(firstNineCards.map((card) => card.description)).size > 3,
  "API Reference index card descriptions must vary beyond repeated page summaries",
);
assert.ok(
  firstNineCards.some((card) => card.description.includes("command output supports validation")),
  "API Reference cards must describe practical command usage",
);

const faqIndex = generatedSectionIndexPages.find((page) => page.slug === "/content/faq-qa/");
assert.ok(faqIndex, "FAQ / QA index must exist");
const faqIndexCopy = [
  faqIndex.title,
  faqIndex.description,
  faqIndex.h1,
  faqIndex.intro,
  JSON.stringify(faqIndex.sections),
].join("\n");
assert.equal(faqIndexCopy.includes("faq / qa"), false, "FAQ / QA copy must not use lowercase faq / qa");
assert.match(faqIndexCopy, /FAQ \/ QA/, "FAQ / QA copy must preserve uppercase acronyms");

const qaAnswerPage = generatedPages.find((page) => page.slug === "/faq-qa/developer/adrs/qa-answer/");
assert.ok(qaAnswerPage, "sample QA answer page must exist");
const qaAnswerCopy = visibleCopy(qaAnswerPage);
assert.equal(qaAnswerCopy.includes("qa answer"), false, "QA answer copy must not use lowercase qa");

const faqAnswerPage = generatedPages.find((page) => page.slug === "/faq-qa/developer/adrs/faq-answer/");
assert.ok(faqAnswerPage, "sample FAQ answer page must exist");
const faqAnswerCopy = visibleCopy(faqAnswerPage);
assert.equal(faqAnswerCopy.includes("faq answer"), false, "FAQ answer copy must not use lowercase faq");

for (const page of ssotRegistrySite.pages) {
  const copy = visibleCopy(page);
  assert.equal(/\bfaq\b/.test(copy), false, `${page.slug} visible copy must uppercase FAQ`);
  assert.equal(/\bqa\b/.test(copy), false, `${page.slug} visible copy must uppercase QA`);
  assert.equal(copy.includes("FAQ_QA"), false, `${page.slug} visible copy must not expose FAQ_QA internals`);
}

const coursePage = generatedPages.find((page) => page.slug === "/courses/developer/adrs/course-overview/");
assert.ok(coursePage, "sample course page must exist");
assert.ok(
  coursePage.schema.some((schema) => schema.kind === "Course"),
  "course pages must declare Course structured data",
);
assert.ok(
  coursePage.schema.some((schema) => schema.kind === "CourseInstance"),
  "course pages must declare CourseInstance structured data",
);
assert.ok(
  coursePage.schema.some((schema) => schema.kind === "QAPage") || coursePage.schema.some((schema) => schema.kind === "FAQPage"),
  "course pages must declare quiz-oriented structured data",
);
assert.ok(
  coursePage.componentIntents.some((intent) => JSON.stringify(intent).includes("CourseBlock")),
  "course pages must include a CourseBlock component intent",
);
assert.ok(
  coursePage.componentIntents.some((intent) => JSON.stringify(intent).includes("LessonListBlock")),
  "course pages must include a LessonListBlock component intent",
);
assert.ok(
  coursePage.sections.some((section) => section.id === "course-metadata"),
  "course pages must render course metadata",
);
assert.ok(
  JSON.stringify(coursePage.sections).includes("Learner level") &&
  JSON.stringify(coursePage.sections).includes("Prerequisites") &&
  JSON.stringify(coursePage.sections).includes("Exercise") &&
  JSON.stringify(coursePage.sections).includes("Checkpoint"),
  "course pages must render explicit curriculum metadata",
);
assert.ok(
  coursePage.sections.some((section) => section.id === "course-overview"),
  "course pages must render course content",
);
assert.ok(
  coursePage.sections.some((section) => section.id === "course-lessons"),
  "course pages must render lesson follow-up links",
);
assert.ok(
  coursePage.sections.some((section) => section.id === "course-quiz" && section.kind === "faq" && section.items.length >= 3),
  "course pages must render follow-up course quizzes",
);
assert.equal(
  coursePage.sections[0].primaryCta.href,
  "#course-overview",
  "Start course CTA must jump to the course content on the course page",
);

const lessonPage = generatedPages.find((page) => page.slug === "/lessons/developer/adrs/lesson/");
assert.ok(lessonPage, "sample lesson page must exist");
assert.ok(
  lessonPage.sections.some((section) => section.id === "learning-checkpoint"),
  "lesson pages must render a learning checkpoint section",
);
assert.ok(
  JSON.stringify(lessonPage.sections).includes("Exercise") &&
  JSON.stringify(lessonPage.sections).includes("Next step:"),
  "lesson pages must include exercise and next-step copy",
);

function visibleCopy(value, key = "") {
  if (typeof value === "string") return nonCopyKeys.has(key) ? "" : value;
  if (Array.isArray(value)) return value.map((item) => visibleCopy(item, key)).filter(Boolean).join("\n");
  if (!value || typeof value !== "object") return "";
  return Object.entries(value)
    .filter(([entryKey]) => !nonCopyKeys.has(entryKey))
    .map(([entryKey, entryValue]) => visibleCopy(entryValue, entryKey))
    .filter(Boolean)
    .join("\n");
}
