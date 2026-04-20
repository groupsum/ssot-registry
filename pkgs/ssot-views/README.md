<div align="center">
  <h1>🔷 ssot-views</h1>
  <p><strong>Derived reports and graph projections for SSOT registries.</strong></p>
</div>

<div align="center">
  <a href="https://pypi.org/project/ssot-views/"><img src="https://img.shields.io/pypi/v/ssot-views?label=PyPI%20version" alt="PyPI version" /></a>
  <a href="https://pypi.org/project/ssot-views/"><img src="https://img.shields.io/pypi/pyversions/ssot-views?label=Python" alt="Supported Python versions" /></a>
  <a href="https://pepy.tech/project/ssot-views"><img src="https://static.pepy.tech/badge/ssot-views" alt="Downloads" /></a>
  <a href="https://hits.sh/github.com/groupsum/ssot-registry/"><img src="https://hits.sh/github.com/groupsum/ssot-registry.svg?style=flat-square" alt="Repository hits" /></a>
</div>

`ssot-views` provides reusable derived projections for SSOT registries.

These outputs are non-canonical views built from registry data. The registry JSON remains the source of truth; this package focuses on reports and graph exports derived from that source.

## What this package owns

- validation and certification report builders
- summary projections
- graph export builders for JSON and DOT output

## When to use this package

Use `ssot-views` when you want:

- reusable Python functions for building SSOT reports
- graph export payloads or DOT output outside the CLI
- a small library dedicated to derived, read-oriented views

Use another package when you want:

- [ssot-registry](https://pypi.org/project/ssot-registry/) for core runtime APIs and mutation/validation workflows
- [ssot-cli](https://pypi.org/project/ssot-cli/) for command-line rendering and file output
- [ssot-contracts](https://pypi.org/project/ssot-contracts/) for packaged schemas and templates
- [ssot-tui](https://pypi.org/project/ssot-tui/) for interactive terminal browsing
- [ssot-codegen](https://pypi.org/project/ssot-codegen/) for contract metadata regeneration

## Install

```bash
python -m pip install ssot-views
```

For local development from this repository:

```bash
python -m pip install -e pkgs/ssot-views
```

## Public API

The top-level package currently exports:

- `build_validation_report`
- `build_certification_report`
- `build_summary`
- `build_graph_json`
- `build_graph_dot`

## Programmatic usage

Build a summary projection:

```python
from ssot_views import build_summary

summary = build_summary(registry)
print(summary)
```

Build validation and certification reports:

```python
from ssot_views import build_certification_report, build_validation_report

validation = build_validation_report(
    registry,
    ".ssot/registry.json",
    failures=[],
    warnings=[],
)

certification = build_certification_report(
    registry,
    ".ssot/registry.json",
    release_report={"passed": True, "boundary": {"id": "bnd:demo", "profile_ids": [], "feature_ids": []}},
)
```

Build graph exports:

```python
from ssot_views import build_graph_dot, build_graph_json

graph_payload = build_graph_json(registry)
dot_text = build_graph_dot(registry)
```

## Canonical vs derived outputs

- Canonical: `.ssot/registry.json`
- Derived: reports, summaries, graph exports, and similar projections

This distinction matters for workflow design: views are meant to be regenerated from canonical data, not edited as the source of truth.

## Package relationships

- Package type: derived-view library
- Depends on: [ssot-contracts](https://pypi.org/project/ssot-contracts/)
- Consumed by: [ssot-codegen](https://pypi.org/project/ssot-codegen/), library users, and any tooling that needs reusable reports or graph exports

If you are building reporting, analysis, or export tooling around SSOT registries, this package is the appropriate reusable layer.
