# ADR-0502: Generated artifacts are derived and non-canonical

## Status
Draft

## Decision

Generated outputs from `ssot-codegen` are derived artifacts.

- Contracts and governance remain canonical.
- Generated Python metadata MAY be committed for stability and parity testing.
- Generated outputs SHALL not become the source of truth.
