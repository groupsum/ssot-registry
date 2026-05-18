import { mkdirSync, writeFileSync } from "node:fs";
import { resolve } from "node:path";
import { siteContentPackCurrentStateAudit } from "../src/content/site-content-audit.js";

const artifactsDir = resolve("artifacts");
mkdirSync(artifactsDir, { recursive: true });

const jsonPath = resolve(artifactsDir, "site-content-pack-audit.json");
const markdownPath = resolve(artifactsDir, "site-content-pack-audit.md");

writeFileSync(jsonPath, `${JSON.stringify(siteContentPackCurrentStateAudit, null, 2)}\n`);

writeFileSync(
  markdownPath,
  [
    "# SSOT Registry site content pack audit",
    "",
    siteContentPackCurrentStateAudit.summary,
    "",
    "## Corpus contract",
    "",
    `- Formula: ${siteContentPackCurrentStateAudit.corpusContract.formula}`,
    `- Generated detail pages: ${siteContentPackCurrentStateAudit.corpusContract.generatedDetailPages}`,
    `- Section index pages: ${siteContentPackCurrentStateAudit.corpusContract.sectionIndexPages}`,
    `- Primary groups: ${siteContentPackCurrentStateAudit.corpusContract.primaryGroups.join(", ")}`,
    "",
    "## Review lanes",
    "",
    ...siteContentPackCurrentStateAudit.lanes.flatMap((lane) => [
      `### ${lane.role}`,
      "",
      `Checked surfaces: ${lane.checkedSurfaces.join(", ")}.`,
      "",
      "Findings:",
      ...lane.findings.map((finding) => `- ${finding}`),
      "",
      "Upgrade actions:",
      ...lane.upgradeActions.map((action) => `- ${action}`),
      "",
      "Acceptance criteria:",
      ...lane.acceptanceCriteria.map((criterion) => `- ${criterion}`),
      "",
    ]),
  ].join("\n"),
);

console.log(`wrote ${jsonPath}`);
console.log(`wrote ${markdownPath}`);
