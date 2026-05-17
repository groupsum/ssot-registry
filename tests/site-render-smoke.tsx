import assert from "node:assert/strict";
import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { generatedCorpusPages, ssotRegistrySite } from "@ssot-registry/site-content-pack";
import { App } from "../src/App";

const markup = renderToStaticMarkup(<App />);

assert.ok(markup.includes("SSOT Registry"));
assert.ok(markup.includes("Govern software truth from decision to release."));
assert.ok(markup.includes("A registry for the full assurance chain"));
assert.ok(markup.includes("Proof surfaces stay visible"));
assert.ok(markup.includes("Product copy, page structure, FAQ, proof claims, and structured-data intents live in the content pack"));
assert.ok(markup.includes("application/ld+json"));
assert.ok(markup.includes('"SoftwareApplication"'));
assert.ok(ssotRegistrySite.pages.length >= 2500);
assert.equal(generatedCorpusPages.length, 3840);
assert.equal(ssotRegistrySite.pages[0]?.slug, "/");
assert.ok(ssotRegistrySite.pages.some((page) => page.slug === "/features/developer/adrs/what-is/"));
