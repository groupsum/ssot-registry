import assert from "node:assert/strict";
import { readFileSync } from "node:fs";

const plan = JSON.parse(readFileSync(new URL("../artifacts/content-plan.json", import.meta.url), "utf8"));
const pages = plan.pages;
const slugs = new Set(pages.map((page) => page.slug));
const pageIds = new Set(pages.map((page) => page.pageId));

assert.equal(plan.totalPlannedPages, 3840);
assert.ok(plan.totalPlannedPages >= plan.minimumRequiredPages);
assert.equal(pages.length, plan.totalPlannedPages);
assert.equal(slugs.size, pages.length);
assert.equal(pageIds.size, pages.length);
assert.ok(plan.audiences.includes("Vibe coder"));
assert.equal(JSON.stringify(plan.relatedPackages).toLowerCase().includes("mdwrk"), false);

for (const page of pages) {
  assert.ok(page.seoQueryTarget, `${page.pageId} must define SEO content`);
  assert.ok(page.aeoGoal, `${page.pageId} must define AEO content`);
  assert.ok(page.aieoAgentFact, `${page.pageId} must define AiEO content`);
  assert.ok(page.structuredDataTypes.length > 0, `${page.pageId} must define structured data types`);
  assert.ok(page.landerComponents.length > 0, `${page.pageId} must define structured-data-backed components`);
  assert.ok(page.breadcrumbs.length >= 4, `${page.pageId} must define breadcrumbs`);
  assert.ok(page.relatedPackages.length > 0, `${page.pageId} must define related packages`);
  assert.ok(page.relatedApis.length > 0, `${page.pageId} must define related APIs`);
  assert.ok(page.learnerLevel, `${page.pageId} must define learner level`);
  assert.ok(page.prerequisites.length >= 2, `${page.pageId} must define prerequisites`);
  assert.match(page.learningOutcome, /explain|practice|choose|run|move|judge|identify/i, `${page.pageId} must define a measurable learning outcome`);
  assert.ok(page.exercise.includes(page.relatedApis[0]) || page.exercise.includes("registry"), `${page.pageId} must define a concrete exercise`);
  assert.ok(page.checkpoint.length > 60, `${page.pageId} must define a checkpoint`);
  assert.ok(page.nextStep.length > 30, `${page.pageId} must define a next step`);

  const segments = page.slug.split("/").filter(Boolean);
  assert.notEqual(segments.at(-1), page.audience.toLowerCase().replace(/[^a-z0-9]+/g, "-"));
}
