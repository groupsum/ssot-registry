import { mkdirSync, writeFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import {
  audiences,
  contentPlanFormula,
  generatePagePlans,
  relatedApis,
  relatedPackages,
  sectionBlueprints,
  structuredDataBackedComponents,
  structuredDataTypes,
  subjectAreas,
} from "../src/index.ts";

const outputPath = resolve("artifacts/content-plan.json");
const pages = generatePagePlans();

const payload = {
  generatedAt: new Date(0).toISOString(),
  formula: contentPlanFormula,
  minimumRequiredPages: 2500,
  totalPlannedPages: pages.length,
  subjectAreas,
  audiences,
  relatedPackages,
  relatedApis,
  structuredDataTypes,
  structuredDataBackedComponents,
  sections: sectionBlueprints,
  pages,
};

mkdirSync(dirname(outputPath), { recursive: true });
writeFileSync(outputPath, `${JSON.stringify(payload, null, 2)}\n`, "utf8");
console.log(`wrote ${outputPath}`);
console.log(`planned_pages=${pages.length}`);
