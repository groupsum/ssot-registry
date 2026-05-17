import assert from "node:assert/strict";
import { existsSync, readFileSync } from "node:fs";
import { compileLanderSite, buildLlmsTxt, buildRobotsTxt, buildSitemap } from "@mdwrk/lander-core";
import { ssotRegistryHomePage, ssotRegistrySite } from "../dist/index.js";

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
