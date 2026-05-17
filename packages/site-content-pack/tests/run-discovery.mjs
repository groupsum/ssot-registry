import assert from "node:assert/strict";
import { existsSync, readFileSync } from "node:fs";
import { resolve } from "node:path";

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
  assert.ok(existsSync(resolve(discoveryDir, file)), `${file} must exist`);
}

const sitemap = readFileSync(resolve(discoveryDir, "sitemap.xml"), "utf8");
const llmsFull = readFileSync(resolve(discoveryDir, "llms-full.txt"), "utf8");
const contentIndex = JSON.parse(readFileSync(resolve(discoveryDir, "content-index.json"), "utf8"));
const semanticIndex = JSON.parse(readFileSync(resolve(discoveryDir, "semantic-index.json"), "utf8"));
const graph = JSON.parse(readFileSync(resolve(discoveryDir, "structured-data-graph.json"), "utf8"));

assert.ok((sitemap.match(/<url>/g) ?? []).length >= 2500);
assert.match(sitemap, /https:\/\/ssot-registry\.swarmauri\.com\/content\//);
assert.match(sitemap, /https:\/\/ssot-registry\.swarmauri\.com\/content\/features\//);
assert.match(sitemap, /https:\/\/ssot-registry\.swarmauri\.com\/features\/developer\/adrs\/what-is\//);
assert.match(llmsFull, /SSOT Registry Full Content Index/);
assert.ok(contentIndex.pageCount >= 2500);
assert.equal(contentIndex.pageCount, semanticIndex.pageCount);
assert.ok(graph.nodes.length > contentIndex.pageCount);
