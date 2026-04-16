# ADR-0503: Python runtime remains the canonical behavior engine

## Status
Draft

## Decision

`ssot-registry` SHALL remain the canonical implementation of:

- validation semantics
- guards
- migrations
- mutations
- lifecycle and release behavior

Generated code and views SHALL not replace those semantics.
