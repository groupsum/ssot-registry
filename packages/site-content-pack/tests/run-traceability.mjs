import assert from "node:assert/strict";
import { existsSync, readFileSync } from "node:fs";
import {
  landerReactStructuredDataTraceabilityMatrix,
  sectionBlueprints,
  ssotComponentTraceabilityMatrix,
  structuredDataBackedComponents,
} from "../dist/index.js";

const jsonPath = "artifacts/component-traceability-matrix.json";
const markdownPath = "artifacts/component-traceability-matrix.md";

assert.ok(existsSync(jsonPath), "component traceability JSON artifact must exist");
assert.ok(existsSync(markdownPath), "component traceability Markdown artifact must exist");

const artifact = JSON.parse(readFileSync(jsonPath, "utf8"));
const markdown = readFileSync(markdownPath, "utf8");

assert.equal(artifact.product, "SSOT Registry");
assert.deepEqual(artifact.matrices.ssotComponentToLanderReact, ssotComponentTraceabilityMatrix);
assert.deepEqual(artifact.matrices.landerReactToStructuredData, landerReactStructuredDataTraceabilityMatrix);
assert.match(markdown, /SSOT Registry component traceability matrix/);
assert.match(markdown, /SSOT Registry components to lander-react renderers/);
assert.match(markdown, /lander-react structured data components to shared structured-data types/);

const tracedSsotComponents = new Set(ssotComponentTraceabilityMatrix.map((row) => row.ssotComponent));
for (const component of structuredDataBackedComponents) {
  assert.ok(tracedSsotComponents.has(component), `${component} must have SSOT component traceability`);
}

for (const row of ssotComponentTraceabilityMatrix) {
  assert.ok(row.sections.length > 0, `${row.ssotComponent} must be owned by at least one section`);
  assert.ok(row.structuredDataTypes.length > 0, `${row.ssotComponent} must link to at least one structured data type`);
  assert.ok(row.landerReactRenderers.length > 0, `${row.ssotComponent} must map to at least one lander-react renderer`);
}

const landerStructuredTypes = new Set(landerReactStructuredDataTraceabilityMatrix.map((row) => row.structuredDataType));
for (const section of sectionBlueprints) {
  for (const structuredDataType of section.structuredDataTypes) {
    if (structuredDataType === "DefinedTerm" || structuredDataType === "DefinedTermSet" || structuredDataType === "LearningResource" || structuredDataType === "EducationalOccupationalCredential" || structuredDataType === "Code") {
      continue;
    }
    assert.ok(landerStructuredTypes.has(structuredDataType), `${structuredDataType} must map to a lander-react structured data renderer`);
  }
}

assert.ok(
  landerReactStructuredDataTraceabilityMatrix.some((row) => row.structuredDataType === "Course" && row.usedBySsotRegistry),
  "Course structured data must be traceable",
);
assert.ok(
  landerReactStructuredDataTraceabilityMatrix.some((row) => row.structuredDataType === "ClaimReview" && row.usedBySsotRegistry),
  "ClaimReview structured data must be traceable",
);

