<div align="center">
  <h1>ðŸ”· ssot-contracts</h1>
  <p><strong>Canonical schemas, templates, manifests, and generated contract metadata for SSOT.</strong></p>
</div>

<div align="center">
  <a href="https://pypi.org/project/ssot-contracts/"><img src="https://img.shields.io/pypi/v/ssot-contracts?label=PyPI%20version" alt="PyPI version" /></a>
  <a href="https://pypi.org/project/ssot-contracts/"><img src="https://img.shields.io/pypi/pyversions/ssot-contracts?label=Python" alt="Supported Python versions" /></a>
  <a href="https://pepy.tech/project/ssot-contracts"><img src="https://static.pepy.tech/badge/ssot-contracts" alt="Downloads" /></a>
  <a href="https://hits.sh/github.com/groupsum/ssot-registry/"><img src="https://hits.sh/github.com/groupsum/ssot-registry.svg?style=flat-square" alt="Repository hits" /></a>
</div>

`ssot-contracts` is the canonical artifact package for SSOT.

It ships machine-readable schemas, registry templates, upstream-derived packaged ADR/spec manifests, and generated Python metadata that other SSOT packages consume at runtime.

## What this package owns

- JSON Schemas for registries, reports, graph exports, and snapshots
- Packaged registry templates such as `registry.minimal.json` and `registry.full.json`
- Immutable packaged ADR and spec document manifests derived from the upstream `.ssot/registry.json` `ssot-origin` inventory
- Generated Python contract metadata used by CLI and TUI packages

## When to use this package

Use `ssot-contracts` when you want:

- packaged schemas and templates without the full CLI
- a stable place to load SSOT manifests and contract metadata from Python
- the artifact layer consumed by [ssot-registry](https://pypi.org/project/ssot-registry/), [ssot-cli](https://pypi.org/project/ssot-cli/), [ssot-conformance](https://pypi.org/project/ssot-conformance/), [ssot-tui](https://pypi.org/project/ssot-tui/), [ssot-views](https://pypi.org/project/ssot-views/), and [ssot-codegen](https://pypi.org/project/ssot-codegen/)

Use another package when you want:

- [ssot-registry](https://pypi.org/project/ssot-registry/) for core runtime APIs and registry mutation/validation flows
- [ssot-cli](https://pypi.org/project/ssot-cli/) for command-line workflows
- [ssot-tui](https://pypi.org/project/ssot-tui/) for terminal UI browsing
- [ssot-views](https://pypi.org/project/ssot-views/) for reusable derived report and graph builders
- [ssot-codegen](https://pypi.org/project/ssot-codegen/) to regenerate contract-side metadata outputs

## Install

```bash
python -m pip install ssot-contracts
```

For local development from this repository:

```bash
python -m pip install -e pkgs/ssot-contracts
```

## Shipped artifacts

This package currently includes:

- schemas under `ssot_contracts.schema`
- registry templates under `ssot_contracts.templates`
- packaged ADR manifests and JSON files under `ssot_contracts.templates.adr`
- packaged spec manifests and JSON files under `ssot_contracts.templates.specs`
- generated Python metadata under `ssot_contracts.generated.python`

Representative schemas include:

- `registry.schema.json`
- `validation.report.schema.json`
- `certification.report.schema.json`
- `graph.export.schema.json`
- `boundary.snapshot.schema.json`
- `release.snapshot.schema.json`
- `published.snapshot.schema.json`

## Programmatic usage

Load contract metadata:

```python
from ssot_contracts import CONTRACT_DATA

print(CONTRACT_DATA["schema_version"])
print(CONTRACT_DATA["output_formats"])
```

Load a packaged document manifest:

```python
from ssot_contracts import load_document_manifest

adr_manifest = load_document_manifest("adr")
spec_manifest = load_document_manifest("spec")
print(adr_manifest[0]["id"])
print(spec_manifest[0]["id"])
```

List available schema files or load one as text:

```python
from ssot_contracts import list_schema_names, load_schema_text

print(list_schema_names())
schema_text = load_schema_text("registry.schema.json")
```

Read packaged document bodies:

```python
from ssot_contracts import read_packaged_document_text

text = read_packaged_document_text("adr", "ADR-0600-canonical-json-registry.yaml")
print(text.splitlines()[0])
```

## Generated metadata

Generated Python modules currently include:

- `generated.python.cli_metadata`
- `generated.python.tui_metadata`
- `generated.python.ids`
- `generated.python.enums`

These modules provide shared constants such as output formats, entity section labels, and identifier prefixes. They are intended to be imported by other SSOT packages rather than edited by hand.

## Package relationships

- Package type: artifact and contract package
- Depends on: standard library only, plus `tomli` on Python earlier than 3.11
- Consumed by: [ssot-registry](https://pypi.org/project/ssot-registry/), [ssot-cli](https://pypi.org/project/ssot-cli/), [ssot-conformance](https://pypi.org/project/ssot-conformance/), [ssot-tui](https://pypi.org/project/ssot-tui/), [ssot-views](https://pypi.org/project/ssot-views/), [ssot-codegen](https://pypi.org/project/ssot-codegen/)

If you need the canonical packaged schemas and manifests, install this package. It is the lowest-level reusable contract layer in the workspace.
