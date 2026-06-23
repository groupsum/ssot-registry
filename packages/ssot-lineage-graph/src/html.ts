import type { LineagePayload, StandaloneHtmlOptions } from "./types";

function escapeJsonForHtml(value: unknown): string {
  return JSON.stringify(value).replace(/</g, "\\u003c").replace(/>/g, "\\u003e").replace(/&/g, "\\u0026");
}

export function createStandaloneHtml(payload: LineagePayload, options: StandaloneHtmlOptions = {}): string {
  const title = options.title || "SSOT Lineage Graph";
  const rootId = options.rootId || "ssot-lineage-root";
  return `<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>${title}</title>
  <style>html,body,#${rootId}{width:100%;height:100%;margin:0}body{overflow:hidden}#${rootId}{min-height:100vh}${options.style || ""}</style>
</head>
<body>
  <div id="${rootId}"></div>
  <script>window.__SSOT_LINEAGE_PAYLOAD__=${escapeJsonForHtml(payload)};</script>
  <script>${options.script || ""}</script>
</body>
</html>
`;
}
