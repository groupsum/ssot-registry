import assert from "node:assert/strict";
import { compileLanderSite } from "@mdwrk/lander-core";
import { generatedPagePlans, ssotRegistrySite } from "../dist/index.js";

const compiled = compileLanderSite(ssotRegistrySite);
const generatedPages = ssotRegistrySite.pages.filter((page) => page.slug !== "/");
const slugs = new Set(ssotRegistrySite.pages.map((page) => page.slug));
const planIds = new Set(generatedPagePlans.map((plan) => plan.pageId));

assert.ok(ssotRegistrySite.pages.length >= 2500);
assert.equal(generatedPages.length, 3840);
assert.equal(slugs.size, ssotRegistrySite.pages.length);
assert.equal(compiled.pages.length, ssotRegistrySite.pages.length);

for (const page of generatedPages) {
  assert.ok(page.planId, `${page.slug} must map back to a plan`);
  assert.ok(planIds.has(page.planId), `${page.slug} must map to a known plan`);
  assert.ok(page.schema?.length > 0, `${page.slug} must declare schema intents`);
  assert.ok(page.componentIntents?.length > 0, `${page.slug} must declare component intents`);
  assert.ok(page.sections.length >= 4, `${page.slug} must use at least four section types`);
  assert.notDeepEqual([...new Set(page.sections.map((section) => section.kind))], ["markdown"]);
  assert.ok(compiled.pageByPath.has(page.slug), `${page.slug} must be routable after compile`);
}
