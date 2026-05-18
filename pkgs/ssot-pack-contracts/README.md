<div align="center">
  <h1>🔷 ssot-pack-contracts</h1>
  <p><strong>Shared metadata, manifest, and packaged-document contracts for installable SSOT governance packs.</strong></p>
</div>

<div align="center">
  <a href="https://pypi.org/project/ssot-pack-contracts/"><img src="https://img.shields.io/pypi/v/ssot-pack-contracts?label=PyPI%20version" alt="PyPI version" /></a>
  <a href="https://pypi.org/project/ssot-pack-contracts/"><img src="https://img.shields.io/pypi/pyversions/ssot-pack-contracts?label=Python" alt="Supported Python versions" /></a>
  <a href="https://pepy.tech/project/ssot-pack-contracts"><img src="https://static.pepy.tech/badge/ssot-pack-contracts" alt="Downloads" /></a>
  <a href="https://hits.sh/github.com/groupsum/ssot-registry/"><img src="https://hits.sh/github.com/groupsum/ssot-registry.svg?style=flat-square" alt="Repository hits" /></a>
<!-- ssot-schema-badges:start -->
  <img src="https://img.shields.io/badge/schema_version-0.5.0-blue" alt="schema_version 0.5.0" />
  <img src="https://img.shields.io/badge/migration%20coverage-12%2F12-brightgreen" alt="Migration coverage 12/12" />
<!-- ssot-schema-badges:end -->
</div>

`ssot-pack-contracts` is the shared Python contract package for installable SSOT governance packs.

It gives external governance packs one common API for declaring pack identity, schema compatibility, trust metadata, document manifests, and packaged ADR/SPEC resources. It is the contract layer between pack authors and the SSOT runtime: governance packs use it to expose stable package metadata, while [ssot-core](https://pypi.org/project/ssot-core/) and [ssot-cli](https://pypi.org/project/ssot-cli/) use those contracts to inspect, preflight, and synchronize pack content.

- GitHub: https://github.com/groupsum/ssot-registry/tree/main/pkgs/ssot-pack-contracts
- PyPI: https://pypi.org/project/ssot-pack-contracts/

## What this package owns

- Governance-pack metadata loading and validation
- Governance-pack schema version access
- PyPI distribution name and version discovery through installed package metadata
- Pack document manifest loading for ADR and SPEC payloads
- Packaged document text and byte readers
- Document ID listing and manifest-entry lookup helpers
- Fail-closed validation errors for invalid pack metadata or manifest entries
- A reusable binder that exposes the same root API from every compatible governance pack

## When to use this package

Use `ssot-pack-contracts` when you want:

- to publish an installable governance pack that ships governed ADR, SPEC, or packaged policy documents
- a stable root API for pack metadata, document manifests, and packaged document resources
- fail-closed validation around pack identity, compatibility, trust metadata, and manifest shape
- the package contract consumed by SSOT pack inspection, preflight, and synchronization workflows

Use another package when you want:

- [ssot-contracts](https://pypi.org/project/ssot-contracts/) for canonical SSOT schemas, registry templates, and generated contract metadata
- [ssot-core](https://pypi.org/project/ssot-core/) for registry loading, validation, synchronization, pack ingestion, and mutation APIs
- [ssot-cli](https://pypi.org/project/ssot-cli/) for command-line pack inspection, preflight checks, and sync workflows
- [ssot-registry](https://pypi.org/project/ssot-registry/) for the umbrella runtime bundle

## Governance packs using this contract

These governance packs are expected to expose the `ssot-pack-contracts` API surface from their package root:

- [seo-aeo-aieo-governance-pack](https://pypi.org/project/seo-aeo-aieo-governance-pack/) packages SEO, AEO, and AiEO governance ADR/SPEC content.
- [digital-signature-governance-pack](https://pypi.org/project/digital-signature-governance-pack/) packages digital-signature governance ADR/SPEC content.
- [cache-freshness-governance-pack](https://pypi.org/project/cache-freshness-governance-pack/) packages cache freshness and cache governance ADR/SPEC content.

Each pack should depend on `ssot-pack-contracts`, include a packaged `metadata.json`, include declared document manifests, and bind the shared API at the package root.

## Install

```bash
python -m pip install ssot-pack-contracts
```

For local development from this repository:

```bash
python -m pip install -e pkgs/ssot-pack-contracts
```

## Pack authoring pattern

Governance packs should not reimplement the contract API. Their package root should bind and export the shared contract functions:

```python
from ssot_pack_contracts import bind_pack_contract

globals().update(bind_pack_contract(__name__))
```

The binder resolves:

- `__pypi_package_name__` from installed distribution metadata
- `__version__` from `importlib.metadata.version(...)`
- `__ssot_package_name__` from packaged governance metadata
- `load_pack_metadata`
- `load_pack_schema_version`
- `load_pack_manifest`
- `load_document_manifest`
- `read_packaged_document_bytes`
- `read_packaged_document_text`
- `list_packaged_document_ids`
- `get_packaged_document_entry`

## Required metadata

Every governance pack must package a `metadata.json` resource at the import-package root. The metadata file is the source of truth for SSOT pack identity.

Required top-level fields:

```json
{
  "schema_version": "1.0.0",
  "ssot_package_name": "example-governance-pack",
  "origin": {
    "id": "pack:example-governance-pack",
    "package_name": "example-governance-pack",
    "import_name": "example_governance_pack",
    "kind": "governance-pack"
  },
  "compatibility": {
    "python": ">=3.10,<3.15",
    "ssot_registry_schema": ">=0.5.0,<0.6.0",
    "ssot_pack_contract": ">=0.2.19,<0.3.0"
  },
  "trust": {
    "origin": "extension-pack",
    "trusted_by_default": false,
    "reservation_owner": "extension-pack:example-governance-pack"
  },
  "documents": {
    "adr": {
      "manifest_path": "adr/manifest.json"
    },
    "spec": {
      "manifest_path": "specs/manifest.json"
    }
  }
}
```

The package version is not authored in `metadata.json`. It is loaded from the installed PyPI distribution metadata, which is generated from the pack's `pyproject.toml`.

## Public API

```python
from ssot_pack_contracts import (
    bind_pack_contract,
    get_packaged_document_entry,
    list_packaged_document_ids,
    load_document_manifest,
    load_pack_manifest,
    load_pack_metadata,
    load_pack_schema_version,
    read_packaged_document_bytes,
    read_packaged_document_text,
)
```

## Programmatic usage

Load pack identity and schema version:

```python
from ssot_pack_contracts import load_pack_metadata, load_pack_schema_version

metadata = load_pack_metadata("seo_aeo_aieo_governance_pack")
schema_version = load_pack_schema_version("seo_aeo_aieo_governance_pack")

print(metadata["ssot_package_name"])
print(metadata["pypi_package_name"])
print(metadata["version"])
print(schema_version)
```

List and read packaged documents:

```python
from ssot_pack_contracts import (
    get_packaged_document_entry,
    list_packaged_document_ids,
    read_packaged_document_text,
)

document_ids = list_packaged_document_ids("seo_aeo_aieo_governance_pack", "spec")
entry = get_packaged_document_entry("seo_aeo_aieo_governance_pack", document_ids[0])
body = read_packaged_document_text("seo_aeo_aieo_governance_pack", "spec", entry["filename"])
```

Bind the contract into a pack root:

```python
from ssot_pack_contracts import bind_pack_contract

pack_api = bind_pack_contract("seo_aeo_aieo_governance_pack")
print(pack_api["__ssot_package_name__"])
print(pack_api["list_packaged_document_ids"]("spec"))
```

## Contract rules

- Pack root APIs must be loaded from `ssot-pack-contracts`, not copied by hand.
- `metadata.schema_version` is required and must be available through `load_pack_schema_version`.
- `metadata.ssot_package_name` is required and must match `metadata.origin.package_name`.
- `metadata.origin.id` must use the `pack:*` identity model.
- `metadata.origin.import_name` must match the installed import package.
- `metadata.origin.kind` must be `governance-pack`.
- `metadata.trust.origin` must be `extension-pack`.
- `metadata.trust.reservation_owner` must start with `extension-pack:`.
- `metadata.compatibility.python`, `metadata.compatibility.ssot_registry_schema`, and `metadata.compatibility.ssot_pack_contract` are required.
- Document manifest kinds must use normalized keys: `adr` and `spec`.
- Packaged document entries must include stable IDs, filenames, target paths, SHA-256 hashes, origin, reservation owner, compatibility metadata, status, and supersession fields.

## Package relationships

- Package type: governance-pack contract package
- Depends on: standard library only, plus `tomli` on Python earlier than 3.11
- Used by: governance packs such as [seo-aeo-aieo-governance-pack](https://pypi.org/project/seo-aeo-aieo-governance-pack/), [digital-signature-governance-pack](https://pypi.org/project/digital-signature-governance-pack/), and [cache-freshness-governance-pack](https://pypi.org/project/cache-freshness-governance-pack/)
- Consumed by: [ssot-core](https://pypi.org/project/ssot-core/) pack ingestion and [ssot-cli](https://pypi.org/project/ssot-cli/) pack inspection, preflight, and sync workflows

If you are publishing an SSOT governance pack, use `ssot-pack-contracts` as the root API contract. If you are consuming packs, use [ssot-cli](https://pypi.org/project/ssot-cli/) or [ssot-core](https://pypi.org/project/ssot-core/) to inspect, preflight, and synchronize pack content into a governed registry.
