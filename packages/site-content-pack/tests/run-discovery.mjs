import assert from "node:assert/strict";
import { existsSync, readFileSync, statSync } from "node:fs";
import { resolve } from "node:path";
import { ssotRegistrySite } from "../dist/index.js";

const discoveryDir = resolve("artifacts/discovery");
const required = [
  "sitemap.xml",
  "robots.txt",
  "llms.txt",
  "llms-full.txt",
  "content-index.json",
  "semantic-index.json",
  "structured-data-graph.json",
];

for (const file of required) {
  const path = resolve(discoveryDir, file);
  assert.ok(existsSync(path), `${file} must exist`);
  assert.ok(statSync(path).size > 0, `${file} must be non-empty`);
}

const sitemap = readFileSync(resolve(discoveryDir, "sitemap.xml"), "utf8");
const robots = readFileSync(resolve(discoveryDir, "robots.txt"), "utf8");
const llms = readFileSync(resolve(discoveryDir, "llms.txt"), "utf8");
const llmsFull = readFileSync(resolve(discoveryDir, "llms-full.txt"), "utf8");
const contentIndex = JSON.parse(readFileSync(resolve(discoveryDir, "content-index.json"), "utf8"));
const semanticIndex = JSON.parse(readFileSync(resolve(discoveryDir, "semantic-index.json"), "utf8"));
const graph = JSON.parse(readFileSync(resolve(discoveryDir, "structured-data-graph.json"), "utf8"));
const expectedPageCount = ssotRegistrySite.pages.length;
const sitemapUrls = sitemap.match(/<url>/g) ?? [];

assert.equal(sitemapUrls.length, expectedPageCount);
assert.ok(sitemapUrls.length >= 2500);
assert.match(sitemap, /https:\/\/ssot-registry\.com\/content\//);
assert.match(sitemap, /https:\/\/ssot-registry\.com\/content\/features\//);
assert.match(sitemap, /https:\/\/ssot-registry\.com\/features\/developer\/adrs\/what-is\//);
assert.equal(sitemap.includes("swarmauri"), false);
assert.equal(sitemap.includes("agent-answer"), false);
assert.equal(sitemap.includes("agent-vocabulary"), false);
assert.equal(sitemap.includes("content-packs"), false);
assert.equal(sitemap.includes("site-packages"), false);
assert.match(robots, /Sitemap: https:\/\/ssot-registry\.com\/sitemap\.xml/);
assert.match(robots, /User-agent: \*/);
assert.match(llms, /SSOT Registry/);
assert.match(llmsFull, /SSOT Registry Full Content Index/);
assert.equal(contentIndex.product, "SSOT Registry");
assert.equal(contentIndex.pageCount, expectedPageCount);
assert.equal(contentIndex.pages.length, expectedPageCount);
assert.ok(contentIndex.pageCount >= 2500);
assert.equal(contentIndex.pageCount, semanticIndex.pageCount);
assert.equal(semanticIndex.product, "SSOT Registry");
assert.equal(semanticIndex.terms.length, expectedPageCount);
assert.equal(graph.product, "SSOT Registry");
assert.ok(graph.nodes.length > contentIndex.pageCount);
assert.ok(graph.nodes.every((node) => node.canonicalUrl.startsWith("https://ssot-registry.com/")));
