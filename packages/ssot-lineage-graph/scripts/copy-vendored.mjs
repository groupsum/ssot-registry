import { copyFileSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { build } from "vite";

const here = dirname(fileURLToPath(import.meta.url));
const root = resolve(here, "..");
const repo = resolve(root, "..", "..");
const vendorDir = resolve(repo, "pkgs", "ssot-core", "src", "ssot_registry", "assets", "lineage_graph");

await build({ mode: "standalone", configFile: resolve(root, "vite.config.ts") });

mkdirSync(vendorDir, { recursive: true });
copyFileSync(resolve(root, "dist", "standalone", "ssot-lineage-graph.js"), resolve(vendorDir, "ssot-lineage-graph.js"));
copyFileSync(resolve(root, "dist", "standalone", "ssot-lineage-graph.css"), resolve(vendorDir, "ssot-lineage-graph.css"));

const pkg = JSON.parse(readFileSync(resolve(root, "package.json"), "utf8"));
writeFileSync(
  resolve(vendorDir, "manifest.json"),
  JSON.stringify(
    {
      package: pkg.name,
      version: pkg.version,
      js: "ssot-lineage-graph.js",
      css: "ssot-lineage-graph.css",
    },
    null,
    2,
  ) + "\n",
);
