import { cpSync, mkdirSync } from "node:fs";
import { resolve } from "node:path";

const source = resolve("packages/site-content-pack/artifacts/discovery");
const publicDir = resolve("public");

mkdirSync(publicDir, { recursive: true });
cpSync(resolve(source, "sitemap.xml"), resolve(publicDir, "sitemap.xml"));
cpSync(resolve(source, "robots.txt"), resolve(publicDir, "robots.txt"));
cpSync(resolve(source, "llms.txt"), resolve(publicDir, "llms.txt"));
cpSync(resolve(source, "llms-full.txt"), resolve(publicDir, "llms-full.txt"));
cpSync(resolve(source, "content-index.json"), resolve(publicDir, "content-index.json"));
cpSync(resolve(source, "semantic-index.json"), resolve(publicDir, "semantic-index.json"));
cpSync(resolve(source, "structured-data-graph.json"), resolve(publicDir, "structured-data-graph.json"));

console.log(`synced discovery artifacts to ${publicDir}`);
