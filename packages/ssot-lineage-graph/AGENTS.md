# SSOT Lineage Graph Agent Context

This file adds package-local context for Codex work in `packages/ssot-lineage-graph`.
It is additive guidance for the reusable React lineage viewer and should not replace
repo-wide instructions, SSOT registry rules, or explicit user requests.

## Package Boundary

- Keep the public API stable unless the user explicitly asks for a breaking change:
  `LineageGraph`, `LineageGraphApp`, `createStandaloneHtml`, and exported types.
- Treat `_lineage_payload()` in `ssot-core` as the canonical payload source. This
  package owns rendering, interaction, layout controls, and standalone app behavior.
- Preserve offline portability. Built standalone assets must be vendored into
  `pkgs/ssot-core/src/ssot_registry/assets/lineage_graph` so PyPI users do not need
  Node, npm, CDNs, or network access at runtime.

## UIX Principles

- Build the actual graph workspace first: controls, canvas, selection details,
  connected edges, legend, and export actions are core UI, not decorative content.
- Prefer dense operational UI over marketing layout. Keep sidebars scan-friendly,
  scrollable where needed, and avoid card-in-card composition.
- Components should expose stable `className` hooks and keep visual styling in CSS
  files. Avoid inline style except where runtime canvas drawing or export generation
  requires computed values.
- Right-side diagnostic sections may use collapsible accordion panels when content
  can become long. Preserve keyboard/native semantics where possible.
- Do not show raw JSON payloads in user-facing panels. Render key/value data,
  navigable connected edges, and concise summaries.

## Graph Behavior

- Network mode should apply force layout to every currently visible family up to the
  configured force cutoff. Do not special-case ADRs, specs, features, claims, tests,
  evidence, boundaries, profiles, releases, issues, or risks out of force behavior.
- Top-down lineage mode is deterministic and stratified. It should honor x/y scale
  controls, left-align nodes within each layer, and render edges through the same
  visible edge/ribbon layer as network mode.
- Node selection and focus are separate:
  clicking selects, `Deselect` clears selection, and `Focus` changes the lineage ego.
- Canvas interaction must support node dragging, empty-space panning, wheel zoom,
  finite fit behavior, and PNG/SVG exports.
- Edges/ribbons must remain visible at default settings. If changing edge colors,
  widths, opacity, or culling, update tests that assert the visibility contract.

## Test Expectations

- Run `npm run build:lineage-graph` after runtime or style changes; this rebuilds and
  vendors the standalone app.
- Run `npm run test:lineage-graph` for package-level contracts.
- For CLI/Python integration changes, run the targeted graph export/parity tests:
  `uv run pytest tests\unit\test_graph_export.py tests\integration\test_cli_graph.py tests\ssot_scaffold\test_graph_lineage_viewer_parity.py`.
- When changing high-volume behavior, also run the T0/T1/T2 high-volume renderer
  proof graph tests under `tests\ssot_scaffold`.
- After rebuilding vendored assets, regenerate a real repo artifact when the user is
  reviewing one, for example:
  `uv run ssot graph lineage E:\swarmauri_github\tigrcorn --output E:\swarmauri_github\tigrcorn\tmp\ssot-lineage-graph.html`.

## Release And Packaging

- Keep package metadata aligned with the Python release train when release scripts
  expect shared versioning.
- Do not add runtime dependencies casually. The standalone artifact must remain
  compact, portable, and deterministic.
- If package source changes but vendored assets are stale, treat that as a release
  blocker and rebuild before final verification.
