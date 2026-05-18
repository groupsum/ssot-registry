import assert from "node:assert/strict";
import { existsSync, readFileSync } from "node:fs";
import {
  relatedApiDetails,
  relatedApis,
  relatedPackageDetails,
  relatedPackages,
  siteContentPackCurrentStateAudit,
} from "../dist/index.js";

assert.equal(siteContentPackCurrentStateAudit.product, "SSOT Registry");
assert.equal(siteContentPackCurrentStateAudit.corpusContract.generatedDetailPages, 3840);
assert.equal(siteContentPackCurrentStateAudit.corpusContract.sectionIndexPages, 12);
assert.deepEqual(siteContentPackCurrentStateAudit.corpusContract.primaryGroups, ["Features", "Proof", "Packages", "FAQ"]);
assert.deepEqual(
  siteContentPackCurrentStateAudit.lanes.map((lane) => lane.role),
  ["Technical Writer", "Curriculum Planner", "SEO, AEO, and AiEO Specialist", "Technical Marketing Engineer"],
);
for (const lane of siteContentPackCurrentStateAudit.lanes) {
  assert.ok(lane.checkedSurfaces.length >= 4, `${lane.role} must name checked surfaces`);
  assert.ok(lane.findings.length >= 2, `${lane.role} must include findings`);
  assert.ok(lane.upgradeActions.length >= 2, `${lane.role} must include upgrade actions`);
  assert.ok(lane.acceptanceCriteria.length >= 2, `${lane.role} must include acceptance criteria`);
}

const apiDetailByCommand = new Map(relatedApiDetails.map((detail) => [detail.command, detail]));
for (const command of relatedApis) {
  const detail = apiDetailByCommand.get(command);
  assert.ok(detail, `${command} must have detail copy`);
  assert.ok(detail.description.length > 40, `${command} must have a useful description`);
  assert.ok(detail.output.length > 30, `${command} must name expected output`);
  assert.ok(detail.workflowStage.length > 0, `${command} must name a workflow stage`);
}

const packageDetailByName = new Map(relatedPackageDetails.map((detail) => [detail.name, detail]));
for (const packageName of relatedPackages) {
  const detail = packageDetailByName.get(packageName);
  assert.ok(detail, `${packageName} must have detail copy`);
  assert.ok(detail.install.startsWith("uv add "), `${packageName} must include uv install guidance`);
  assert.ok(detail.bestFor.length > 30, `${packageName} must define who it is best for`);
  assert.ok(detail.proofPoint.length > 30, `${packageName} must define a proof point`);
  assert.ok(detail.primaryCommands.length > 0, `${packageName} must define primary commands`);
}

for (const file of ["artifacts/site-content-pack-audit.json", "artifacts/site-content-pack-audit.md"]) {
  assert.ok(existsSync(file), `${file} must exist`);
  assert.match(readFileSync(file, "utf8"), /Technical Writer/);
  assert.match(readFileSync(file, "utf8"), /Curriculum Planner/);
}
