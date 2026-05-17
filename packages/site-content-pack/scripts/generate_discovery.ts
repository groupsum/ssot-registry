import { mkdirSync, writeFileSync } from "node:fs";
import { resolve } from "node:path";
import { buildLlmsTxt, buildRobotsTxt, compileLanderSite } from "@mdwrk/lander-core";
import { ssotRegistrySite } from "../src/index.ts";

const outputDir = resolve("artifacts/discovery");
const compiled = compileLanderSite(ssotRegistrySite);
const pages = compiled.pages;

mkdirSync(outputDir, { recursive: true });

writeFileSync(resolve(outputDir, "sitemap.xml"), sitemapXml(pages), "utf8");
writeFileSync(resolve(outputDir, "robots.txt"), buildRobotsTxt(compiled), "utf8");
writeFileSync(resolve(outputDir, "llms.txt"), buildLlmsTxt(compiled), "utf8");
writeFileSync(resolve(outputDir, "llms-full.txt"), llmsFullTxt(pages), "utf8");
writeFileSync(resolve(outputDir, "content-index.json"), `${JSON.stringify(contentIndex(pages), null, 2)}\n`, "utf8");
writeFileSync(resolve(outputDir, "semantic-index.json"), `${JSON.stringify(semanticIndex(pages), null, 2)}\n`, "utf8");
writeFileSync(resolve(outputDir, "structured-data-graph.json"), `${JSON.stringify(structuredDataGraph(pages), null, 2)}\n`, "utf8");

console.log(`wrote ${outputDir}`);
console.log(`discovery_pages=${pages.length}`);

function sitemapXml(items: typeof pages) {
  const urls = items
    .map((page) => `  <url><loc>${escapeXml(page.canonicalUrl)}</loc></url>`)
    .join("\n");
  return `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n${urls}\n</urlset>\n`;
}

function llmsFullTxt(items: typeof pages) {
  return [
    "# SSOT Registry Full Content Index",
    "",
    ...items.map((page) => [
      `## ${page.title}`,
      `URL: ${page.canonicalUrl}`,
      `Description: ${page.description}`,
      `Schema: ${page.schemaIntents.map((intent) => intent.kind).join(", ")}`,
      `Components: ${page.componentIntents.map((intent) => intent.kind).join(", ")}`,
      "",
    ].join("\n")),
  ].join("\n");
}

function contentIndex(items: typeof pages) {
  return {
    product: ssotRegistrySite.product.name,
    pageCount: items.length,
    pages: items.map((page) => ({
      path: page.path,
      canonicalUrl: page.canonicalUrl,
      title: page.title,
      description: page.description,
      sectionIds: page.sections.map((section) => section.id),
    })),
  };
}

function semanticIndex(items: typeof pages) {
  return {
    product: ssotRegistrySite.product.name,
    pageCount: items.length,
    terms: items.map((page) => ({
      path: page.path,
      title: page.title,
      breadcrumbs: page.breadcrumbs.map((item) => item.label),
      schemaTypes: page.schemaIntents.map((intent) => intent.kind),
      componentKinds: page.componentIntents.map((intent) => intent.kind),
      wordCount: page.wordCount,
    })),
  };
}

function structuredDataGraph(items: typeof pages) {
  return {
    product: ssotRegistrySite.product.name,
    nodes: items.flatMap((page) =>
      page.schemaIntents.map((intent) => ({
        id: intent.id,
        kind: intent.kind,
        pagePath: page.path,
        canonicalUrl: page.canonicalUrl,
        source: intent.source,
      })),
    ),
  };
}

function escapeXml(value: string) {
  return value
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&apos;");
}
