<div align="center">
  <h1>🔷 ssot-tui</h1>
  <p><strong>Textual terminal UI for browsing SSOT registries.</strong></p>
</div>

<div align="center">
  <a href="https://pypi.org/project/ssot-tui/"><img src="https://img.shields.io/pypi/v/ssot-tui?label=PyPI%20version" alt="PyPI version" /></a>
  <a href="https://pypi.org/project/ssot-tui/"><img src="https://img.shields.io/pypi/pyversions/ssot-tui?label=Python" alt="Supported Python versions" /></a>
  <a href="https://pepy.tech/project/ssot-tui"><img src="https://static.pepy.tech/badge/ssot-tui" alt="Downloads" /></a>
  <a href="https://hits.sh/github.com/groupsum/ssot-registry/"><img src="https://hits.sh/github.com/groupsum/ssot-registry.svg?style=flat-square" alt="Repository hits" /></a>
</div>

`ssot-tui` is a Textual-based terminal UI for browsing SSOT registries.

It is focused on read-oriented exploration and safe workflow bridges rather than full CRUD parity with the CLI.

## What this package owns

- The `ssot-tui` console entry point
- The Textual app shell and browser screen
- TUI widgets for section navigation, entity tables, and detail panes

## When to use this package

Use `ssot-tui` when you want:

- an interactive terminal browser for SSOT registry content
- a navigable view across entity sections with filters, recent repos, and keyboard-first navigation
- structured entity detail views with a raw JSON fallback
- safe workflow bridges such as validation, CLI read previews, and opening repo resources
- a Textual UI on top of the `ssot-registry` runtime

Use another package when you want:

- `ssot-cli` for full command-line workflow coverage
- `ssot-registry` for direct Python API access
- `ssot-contracts` for packaged schemas and templates
- `ssot-views` for report and graph builders
- `ssot-codegen` for regeneration of metadata artifacts

## Install

```bash
python -m pip install ssot-tui
```

For local development from this repository:

```bash
python -m pip install -e pkgs/ssot-tui
```

This package depends on `ssot-registry`, `ssot-contracts`, and `textual`.

## Start the TUI

```bash
ssot-tui
```

The current entry point launches `SsotTuiApp`, which mounts a browser-oriented screen when the application starts.

## Interaction model

The browser now supports:

- repo auto-discovery from the current working directory
- persisted recent repos and last-viewed session state
- inline filtering with `/`
- a command palette with `Ctrl+P`
- a help overlay with `?`
- pane navigation with `Tab`, `Shift+Tab`, `h`, `j`, `k`, and `l`
- reload and validation via `r` and `v`
- structured detail rendering with `t` to toggle raw JSON
- table view cycling with `m`

The detail pane can traverse linked entity ids, preview file-backed resources, and render safe CLI read previews for the current section or entity.

## Screenshots

Regenerate these assets with `python scripts/generate_tui_screenshots.py`.

Captured against [`examples/minimal-repo`](../../examples/minimal-repo/README.md) in this workspace:

![SSOT TUI browser](assets/ssot-tui-browser.png)

![SSOT TUI ADR browser](assets/ssot-tui-adrs.png)

![SSOT TUI spec browser](assets/ssot-tui-specs.png)

![SSOT TUI validation status](assets/ssot-tui-validated.png)

## Current scope

The current implementation is browser-first and read-first:

- workspace loading, recent repo switching, and validation summaries
- section-based navigation with per-section counts and failure rollups
- tabular browsing with filter and mode switching
- structured and raw detail inspection for the selected item
- safe bridge actions for opening files, revealing paths, and previewing read-only CLI output

The package still does not implement full CRUD or guided operational workflows with CLI-level parity.

## Main UI concepts

The current source tree exposes these UI building blocks:

- `BrowserScreen`: the primary browser screen
- `SectionNavigation`: a section chooser with counts and validation indicators
- `EntityTable`: a table view for entities in the active section
- `EntityDetailPane`: a structured detail view with related-resource traversal
- `CommandPaletteScreen`: an action launcher backed by the shared action registry
- `HelpScreen`: a keyboard and action reference overlay
- `StatusCenter`: a persistent status and toast history panel

At the application level, `SsotTuiApp` provides a header, footer, and browser screen composition.

## Package relationships

- Package type: terminal UI package
- Depends on: `ssot-registry`, `ssot-contracts`, `textual`
- Consumed by: users who want interactive browsing on top of the core SSOT runtime

If you need complete operational coverage today, use `ssot-cli`. If you want an interactive terminal browser for current registry content, this package is the right entry point.
