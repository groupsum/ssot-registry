import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import { existsSync, readFileSync, statSync } from "node:fs";
import { resolve } from "node:path";
import { ssotRegistrySite } from "@ssot-registry/site-content-pack";

const artifactsDir = resolve("packages/site-content-pack/artifacts/discovery");
const publicDir = resolve("public");
const requiredArtifacts = [
  "sitemap.xml",
  "robots.txt",
  "llms.txt",
  "llms-full.txt",
  "content-index.json",
  "semantic-index.json",
  "structured-data-graph.json",
];
const expectedPageCount = ssotRegistrySite.pages.length;

for (const artifact of requiredArtifacts) {
  const packagePath = resolve(artifactsDir, artifact);
  const publicPath = resolve(publicDir, artifact);
  assert.ok(existsSync(packagePath), `${artifact} must exist in the site content pack artifacts`);
  assert.ok(existsSync(publicPath), `${artifact} must exist in public/`);
  assert.ok(statSync(packagePath).size > 0, `${artifact} package artifact must be non-empty`);
  assert.ok(statSync(publicPath).size > 0, `${artifact} public artifact must be non-empty`);
  assert.equal(sha256(packagePath), sha256(publicPath), `${artifact} in public/ must match the generated package artifact`);
}

const sitemap = readFileSync(resolve(publicDir, "sitemap.xml"), "utf8");
const robots = readFileSync(resolve(publicDir, "robots.txt"), "utf8");
const llms = readFileSync(resolve(publicDir, "llms.txt"), "utf8");
const llmsFull = readFileSync(resolve(publicDir, "llms-full.txt"), "utf8");
const contentIndex = JSON.parse(readFileSync(resolve(publicDir, "content-index.json"), "utf8"));
const semanticIndex = JSON.parse(readFileSync(resolve(publicDir, "semantic-index.json"), "utf8"));
const structuredDataGraph = JSON.parse(readFileSync(resolve(publicDir, "structured-data-graph.json"), "utf8"));
const sitemapUrls = sitemap.match(/<url>/g) ?? [];

assert.equal(sitemapUrls.length, expectedPageCount);
assert.ok(expectedPageCount >= 2500);
assert.match(sitemap, /https:\/\/ssot-registry\.com\//);
assert.match(sitemap, /https:\/\/ssot-registry\.com\/content\/features\//);
assert.match(sitemap, /https:\/\/ssot-registry\.com\/features\/developer\/adrs\/what-is\//);
assert.equal(sitemap.includes("swarmauri"), false);
assert.equal(sitemap.includes("agent-answer"), false);
assert.equal(sitemap.includes("agent-vocabulary"), false);
assert.equal(sitemap.includes("content-packs"), false);
assert.equal(sitemap.includes("site-packages"), false);

assert.match(robots, /User-agent: \*/);
assert.match(robots, /Sitemap: https:\/\/ssot-registry\.com\/sitemap\.xml/);
assert.match(llms, /SSOT Registry/);
assert.match(llmsFull, /SSOT Registry Full Content Index/);

assert.equal(contentIndex.product, "SSOT Registry");
assert.equal(contentIndex.pageCount, expectedPageCount);
assert.equal(contentIndex.pages.length, expectedPageCount);
assert.equal(semanticIndex.product, "SSOT Registry");
assert.equal(semanticIndex.pageCount, expectedPageCount);
assert.equal(semanticIndex.terms.length, expectedPageCount);
assert.equal(structuredDataGraph.product, "SSOT Registry");
assert.ok(structuredDataGraph.nodes.length > expectedPageCount);
assert.ok(structuredDataGraph.nodes.every((node) => node.canonicalUrl.startsWith("https://ssot-registry.com/")));

function sha256(path) {
  return createHash("sha256").update(readFileSync(path)).digest("hex");
}
