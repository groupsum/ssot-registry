import assert from "node:assert/strict";
import { existsSync, readFileSync } from "node:fs";
import { compileLanderSite, buildLlmsTxt, buildRobotsTxt, buildSitemap } from "@mdwrk/lander-core";
import {
  canonicalVsDerivedCopy,
  relatedApiDetails,
  relatedPackageDetails,
  ssotRegistryAuthorityPrinciples,
  ssotRegistryHomePage,
  ssotRegistryImageAssetPlan,
  ssotRegistrySite,
} from "../dist/index.js";

const compiled = compileLanderSite(ssotRegistrySite);
const errors = compiled.diagnostics.filter((item) => item.level === "error");
const home = compiled.pageByPath.get("/");

assert.deepEqual(errors, []);
assert.equal(ssotRegistrySite.product.name, "SSOT Registry");
assert.equal(ssotRegistryHomePage.slug, "/");
assert.ok(home, "home page must compile");
assert.equal(home?.canonicalUrl, "https://ssot-registry.com/");
assert.ok(home?.componentIntents.some((intent) => intent.kind === "page_shell"));
assert.ok(home?.componentIntents.some((intent) => intent.kind === "hero"));
assert.ok(home?.schemaIntents.some((intent) => intent.kind === "WebPage"));
assert.ok(home?.schemaIntents.some((intent) => intent.kind === "SoftwareApplication"));
assert.ok(home?.schemaIntents.some((intent) => intent.kind === "SoftwareSourceCode"));
assert.ok(ssotRegistryHomePage.intro.includes(".ssot/registry.json"));
assert.ok(JSON.stringify(ssotRegistryHomePage.sections).includes(canonicalVsDerivedCopy));
assert.ok(JSON.stringify(ssotRegistryHomePage.sections).includes("Frozen scope is not the same thing as shipment"));
assert.ok(ssotRegistryAuthorityPrinciples.some((principle) => principle.id === "boundary-release-split"));
assert.ok(ssotRegistryAuthorityPrinciples.some((principle) => principle.guidance.includes("claims, tests, and evidence")));
assert.equal(ssotRegistryImageAssetPlan.length, 8);
assert.ok(ssotRegistryImageAssetPlan.every((asset) => asset.path.startsWith("/content/images/")));
assert.ok(ssotRegistryImageAssetPlan.every((asset) => asset.alt.includes("SSOT Registry")));
assert.ok(ssotRegistryImageAssetPlan.some((asset) => asset.id === "hero-canonical-flow" && asset.ratio === "16:9"));
assert.ok(relatedApiDetails.some((detail) => detail.command === "ssot pack preflight"));
assert.ok(relatedApiDetails.some((detail) => detail.command === "ssot profile list"));
assert.ok(relatedApiDetails.every((detail) => detail.output && detail.workflowStage));
assert.ok(relatedPackageDetails.some((detail) => detail.name === "ssot-tui" && detail.role.includes("terminal browser")));
assert.ok(relatedPackageDetails.every((detail) => detail.bestFor && detail.proofPoint && detail.primaryCommands.length > 0));
assert.ok(JSON.stringify(ssotRegistryHomePage.sections).includes("First five minutes"));
assert.ok(JSON.stringify(ssotRegistryHomePage.sections).includes("Best for:"));
for (const stylePath of [
  "styles/base.css",
  "styles/shell.css",
  "styles/content.css",
  "styles/breadcrumbs.css",
  "styles/index.css",
]) {
  assert.ok(existsSync(stylePath), `${stylePath} must exist`);
}
assert.match(readFileSync("styles/index.css", "utf8"), /@import "\.\/shell\.css"/);

assert.match(buildLlmsTxt(compiled), /# SSOT Registry/);
assert.match(buildRobotsTxt(compiled), /OAI-SearchBot/);
assert.equal(buildSitemap(compiled)[0]?.loc, "https://ssot-registry.com/");
