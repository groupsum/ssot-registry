import assert from "node:assert/strict";
import { existsSync, readFileSync, statSync } from "node:fs";
import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { generatedCorpusPages, ssotRegistrySite } from "@ssot-registry/site-content-pack";
import { App } from "../src/App";

const markup = renderToStaticMarkup(<App />);
const styles = [
  "packages/site-content-pack/styles/base.css",
  "packages/site-content-pack/styles/shell.css",
  "packages/site-content-pack/styles/content.css",
  "packages/site-content-pack/styles/breadcrumbs.css",
  "packages/site-content-pack/styles/index.css",
].map((path) => readFileSync(path, "utf8")).join("\n");
const htmlShell = readFileSync("index.html", "utf8");
const nginxConfig = readFileSync("nginx/default.conf", "utf8");

assert.ok(markup.includes("SSOT Registry"));
assert.ok(!markup.includes("Hello, world."));
assert.ok(markup.includes('class="site-header"'));
assert.ok(markup.includes('<main id="main-content" class="site-main">'));
assert.ok(markup.includes('class="site-brand-tagline"'));
assert.ok(markup.includes('class="site-brand-mark"'));
assert.ok(markup.includes(">SR</span>"));
assert.ok(markup.includes('data-page-path="/"'));
assert.ok(markup.includes("Govern software truth from decision to release."));
assert.ok(markup.includes("what was intended, what changed, what proves it"));
assert.ok(markup.includes("Canonical records and derived projections stay separate"));
assert.ok(markup.includes("Frozen scope is not the same thing as shipment"));
assert.ok(markup.includes("Learn SSOT Registry by the work you need to do"));
assert.ok(markup.includes("Answer real implementation questions"));
assert.ok(markup.includes("Proof surfaces stay visible"));
assert.ok(markup.includes("Choose the package for the job"));
assert.ok(markup.includes("A typical SSOT Registry workflow starts with ADRs and specs"));
assert.ok(markup.includes("Copyright 2026 Groupsum"));
assert.ok(!markup.includes("AEO"));
assert.ok(!markup.includes("AiEO"));
assert.ok(!markup.includes("agent fact"));
assert.ok(!markup.includes("page has"));
assert.ok(!markup.includes("generated corpus proof"));
assert.ok(!markup.includes("Related SSOT Registry package surface"));
assert.ok(!markup.includes("content pack"));
assert.ok(!markup.includes("site pack"));
assert.ok(markup.includes("application/ld+json"));
assert.ok(markup.includes('"SoftwareApplication"'));
assert.ok(markup.includes('href="/content/features/"'));
assert.ok(markup.includes('href="/content/proofs/"'));
assert.ok(markup.includes('href="/content/packages/"'));
assert.ok(markup.includes('href="/content/faq-qa/"'));
assert.ok(!markup.includes('href="#features"'));
assert.ok(!markup.includes('href="#proof"'));
assert.ok(styles.includes('.lander-page__inner > nav[aria-label="Breadcrumb"]'));
assert.ok(styles.includes(".lander-breadcrumbs"));
assert.ok(styles.includes('[data-lander-theme="lander-dark"] .lander-breadcrumbs'));
assert.ok(styles.includes(".site-header"));
assert.ok(styles.includes("backdrop-filter: blur(18px)"));
assert.ok(styles.includes(".site-brand-tagline"));
assert.ok(!styles.includes(".site-nav-links {\n  display: none;\n  align-items: center;\n  gap: 0.2rem;\n  border: 1px"));
assert.ok(styles.includes(".site-shell .lander-page"));
assert.ok(styles.includes("display: flow-root"));
assert.ok(styles.includes("content-visibility: auto"));
assert.ok(styles.includes("contain-intrinsic-size: 1px 520px"));
assert.ok(styles.includes('.site-shell:not([data-page-path="/"]) .lander-page__hero'));
assert.ok(styles.includes(".lander-page__hero .lander-page__eyebrow"));
assert.ok(styles.includes('.site-shell[data-page-path="/"] .lander-page__inner > nav[aria-label="Breadcrumb"]'));
assert.ok(htmlShell.includes("@ssot-registry/site-content-pack/styles") === false);
assert.ok(!htmlShell.includes("<h1>SSOT Registry</h1>"));
assert.ok(htmlShell.includes("app-boot-shell"));
assert.ok(htmlShell.includes("app-boot-sr"));
assert.ok(htmlShell.includes('<div class="app-boot-mark">SR</div>'));
assert.ok(htmlShell.includes('rel="icon" href="/favicon.ico"'));
assert.ok(htmlShell.includes('href="/favicon-32.png"'));
assert.ok(htmlShell.includes('href="/favicon-16.png"'));
assert.ok(htmlShell.includes('rel="apple-touch-icon"'));
assert.ok(htmlShell.includes('property="og:image" content="https://ssot-registry.com/ssot-registry-social-card.png"'));
assert.ok(htmlShell.includes('property="og:image:width" content="1200"'));
assert.ok(htmlShell.includes('property="og:image:height" content="630"'));
assert.ok(htmlShell.includes('name="twitter:card" content="summary_large_image"'));
assert.ok(htmlShell.includes('name="twitter:image" content="https://ssot-registry.com/ssot-registry-social-card.png"'));
for (const faviconPath of [
  "public/favicon.ico",
  "public/favicon-32.png",
  "public/favicon-16.png",
  "public/favicon-192.png",
  "public/apple-touch-icon.png",
  "public/ssot-registry-favicon-512.png",
  "public/ssot-registry-social-card.png",
]) {
  assert.ok(existsSync(faviconPath), `${faviconPath} must exist`);
  assert.ok(statSync(faviconPath).size > 0, `${faviconPath} must be non-empty`);
}
assert.deepEqual(pngSize("public/favicon-32.png"), [32, 32]);
assert.deepEqual(pngSize("public/favicon-16.png"), [16, 16]);
assert.deepEqual(pngSize("public/favicon-192.png"), [192, 192]);
assert.deepEqual(pngSize("public/apple-touch-icon.png"), [192, 192]);
assert.deepEqual(pngSize("public/ssot-registry-favicon-512.png"), [512, 512]);
assert.deepEqual(pngSize("public/ssot-registry-social-card.png"), [1200, 630]);
assert.equal(readFileSync("public/favicon.ico").readUInt16LE(2), 1);
assert.equal(readFileSync("public/favicon.ico").readUInt16LE(4), 2);
assert.ok(nginxConfig.includes('Cache-Control "public, max-age=31536000, immutable"'));
assert.ok(nginxConfig.includes('Cache-Control "no-cache, must-revalidate"'));
assert.ok(ssotRegistrySite.pages.length >= 2500);
assert.equal(generatedCorpusPages.length, 3840);
assert.equal(ssotRegistrySite.pages[0]?.slug, "/");
assert.ok(ssotRegistrySite.pages.some((page) => page.slug === "/content/"));
assert.ok(ssotRegistrySite.pages.some((page) => page.slug === "/content/features/"));
assert.ok(ssotRegistrySite.pages.some((page) => page.slug === "/features/developer/adrs/what-is/"));
assert.ok(!readFileSync("src/App.tsx", "utf8").includes("ssotRegistrySite.pages.map((page)"));

const packagesIndex = ssotRegistrySite.pages.find((page) => page.slug === "/content/packages/");
const packagesPageLinks = packagesIndex?.sections.find((section) => section.id === "page-links");
assert.ok(packagesPageLinks, "packages index must include representative page links");
assert.ok((packagesPageLinks?.packages?.length ?? 0) <= 48, "section indexes must avoid rendering hundreds of cards on initial load");

const featuresIndex = ssotRegistrySite.pages.find((page) => page.slug === "/content/features/");
const featuresSubsections = featuresIndex?.sections.find((section) => section.id === "subsections");
assert.ok(featuresSubsections, "primary section index must include child subsection navigation");
assert.deepEqual(
  featuresSubsections?.packages?.map((entry) => entry.href),
  ["/content/features/", "/content/workflows/", "/content/comparisons/"],
);

const workflowsIndex = ssotRegistrySite.pages.find((page) => page.slug === "/content/workflows/");
assert.ok(workflowsIndex, "workflows index must exist");
assert.equal(
  workflowsIndex?.sections.some((section) => section.id === "subsections"),
  false,
  "subsection pages must not render sibling areas as child subsections",
);
assert.deepEqual(
  workflowsIndex?.sections.map((section) => section.id),
  ["page-links", "related-areas"],
  "subsection pages should list own pages first and related areas last",
);
const workflowsRelatedAreas = workflowsIndex?.sections.find((section) => section.id === "related-areas");
assert.ok(workflowsRelatedAreas, "subsection pages should expose adjacent areas as related links");
assert.deepEqual(
  workflowsRelatedAreas?.packages?.map((entry) => entry.href),
  ["/content/features/", "/content/comparisons/"],
);

function pngSize(path: string) {
  const bytes = readFileSync(path);
  assert.equal(bytes.toString("ascii", 1, 4), "PNG", `${path} must be a PNG`);
  return [bytes.readUInt32BE(16), bytes.readUInt32BE(20)];
}
