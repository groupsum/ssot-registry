# ssot-conformance

Reusable SSOT conformance harness for downstream repositories.

This package provides:

- portable conformance case families grouped by registry, document, id, SPEC-to-ADR, feature-to-SPEC, proof-chain, and boundary/release concerns
- a `pytest` plugin entry point for repo-root selection, case-family filtering, and evidence-output emission
- scaffold helpers that can compute and optionally create missing conformance SSOT rows
- machine-readable evidence output suitable for later SSOT evidence ingestion and status synchronization

The package is intentionally repo-agnostic. It evaluates a target repository through `.ssot` artifacts and registry semantics rather than assuming a specific implementation language for the target system.
