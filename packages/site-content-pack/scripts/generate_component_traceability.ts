import { mkdirSync, writeFileSync } from "node:fs";
import { resolve } from "node:path";
import {
  landerReactStructuredDataTraceabilityMatrix,
  ssotComponentTraceabilityMatrix,
} from "../src/content/component-traceability.js";

const artifactsDir = resolve("artifacts");
mkdirSync(artifactsDir, { recursive: true });

const payload = {
  product: "SSOT Registry",
  generatedFrom: "packages/site-content-pack/src/content/component-traceability.ts",
  matrices: {
    ssotComponentToLanderReact: ssotComponentTraceabilityMatrix,
    landerReactToStructuredData: landerReactStructuredDataTraceabilityMatrix,
  },
};

writeFileSync(
  resolve(artifactsDir, "component-traceability-matrix.json"),
  `${JSON.stringify(payload, null, 2)}\n`,
);

writeFileSync(
  resolve(artifactsDir, "component-traceability-matrix.md"),
  [
    "# SSOT Registry component traceability matrix",
    "",
    "Generated from `packages/site-content-pack/src/content/component-traceability.ts`.",
    "",
    "## SSOT Registry components to lander-react renderers",
    "",
    markdownTable(
      ["SSOT component", "Sections", "Structured data types", "Lander React renderers", "Status", "Notes"],
      ssotComponentTraceabilityMatrix.map((row) => [
        row.ssotComponent,
        row.sections.join(", "),
        row.structuredDataTypes.join(", "),
        row.landerReactRenderers.join(", "),
        row.rendererStatus,
        row.notes,
      ]),
    ),
    "",
    "## lander-react structured data components to shared structured-data types",
    "",
    markdownTable(
      ["Structured data type", "lander-react component", "Shared builder", "Used by SSOT Registry", "SSOT sections", "Notes"],
      landerReactStructuredDataTraceabilityMatrix.map((row) => [
        row.structuredDataType,
        row.landerReactComponent,
        row.sharedStructuredDataBuilder,
        row.usedBySsotRegistry ? "yes" : "no",
        row.ssotSections.join(", "),
        row.notes,
      ]),
    ),
    "",
  ].join("\n"),
);

console.log(`wrote ${resolve(artifactsDir, "component-traceability-matrix.json")}`);
console.log(`wrote ${resolve(artifactsDir, "component-traceability-matrix.md")}`);

function markdownTable(headers: string[], rows: string[][]): string {
  const escapeCell = (value: string) => value.replace(/\|/g, "\\|").replace(/\n/g, " ");
  return [
    `| ${headers.map(escapeCell).join(" | ")} |`,
    `| ${headers.map(() => "---").join(" | ")} |`,
    ...rows.map((row) => `| ${row.map(escapeCell).join(" | ")} |`),
  ].join("\n");
}

