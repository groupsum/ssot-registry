<div align="center">
  <h1>🔷 ssot-conformance</h1>
  <p><strong>Reusable SSOT conformance harness for downstream repositories.</strong></p>
</div>

<div align="center">
  <a href="https://pypi.org/project/ssot-conformance/"><img src="https://img.shields.io/pypi/v/ssot-conformance?label=PyPI%20version" alt="PyPI version" /></a>
  <a href="https://pypi.org/project/ssot-conformance/"><img src="https://img.shields.io/pypi/pyversions/ssot-conformance?label=Python" alt="Supported Python versions" /></a>
  <a href="https://pepy.tech/project/ssot-conformance"><img src="https://static.pepy.tech/badge/ssot-conformance" alt="Downloads" /></a>
  <a href="https://hits.sh/github.com/groupsum/ssot-registry/"><img src="https://hits.sh/github.com/groupsum/ssot-registry.svg?style=flat-square" alt="Repository hits" /></a>
</div>

Reusable SSOT conformance harness for downstream repositories.

This package provides:

- portable conformance case families grouped by registry, document, id, SPEC-to-ADR, feature-to-SPEC, proof-chain, and boundary/release concerns
- a `pytest` plugin entry point for repo-root selection, case-family filtering, and evidence-output emission
- scaffold helpers that can compute and optionally create missing conformance SSOT rows
- machine-readable evidence output suitable for later SSOT evidence ingestion and status synchronization

The package is intentionally repo-agnostic. It evaluates a target repository through `.ssot` artifacts and registry semantics rather than assuming a specific implementation language for the target system.

## Install

```bash
python -m pip install ssot-conformance
```

For local development from this repository:

```bash
python -m pip install -e pkgs/ssot-conformance
```

## Execution model

Packaged `ssot-core` conformance remains pytest-based, but the operator-facing execution model is registry-driven:

- packaged conformance rows store executable `tests[].execution` metadata
- `ssot conformance run` resolves governed conformance tests and runs those stored commands
- downstream repos can use the same `tests[].execution` contract for arbitrary command-backed suites

For direct SSOT entity execution, prefer:

```text
ssot test run . --id tst:pytest.conformance.registry-contract
ssot spec run-tests . --id spc:0525
ssot boundary run-tests . --id bnd:full-cert
```

## Package relationships

- Package type: reusable conformance and pytest plugin package
- Depends on: [ssot-core](https://pypi.org/project/ssot-core/), [ssot-contracts](https://pypi.org/project/ssot-contracts/)
- Consumed by: [ssot-cli](https://pypi.org/project/ssot-cli/) and downstream repositories that run packaged SSOT conformance checks

If you need the CLI wrapper for these checks, install [ssot-cli](https://pypi.org/project/ssot-cli/). If you need to embed or run the reusable conformance cases directly, this is the package to install.
