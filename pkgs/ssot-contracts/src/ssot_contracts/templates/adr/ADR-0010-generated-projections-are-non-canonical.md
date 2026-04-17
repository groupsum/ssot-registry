# ADR-0010: Generated projections are non-canonical

## Status
Draft

## Decision
The canonical authored sources in an SSOT repository are the registry and the ADR/spec documents that live under `.ssot/`.

Generated projections include:

- graph exports,
- reports and snapshots,
- rendered or exported representations such as CSV, YAML, TOML, DOT, PNG, and SVG,
- mirrored or regenerated documentation derived from the canonical SSOT content.

## Consequences
- Operators SHALL edit canonical SSOT content, not derived projections.
- Projection generation MUST be deterministic.
- Manual edits to generated projections are treated as drift and MAY be overwritten by regeneration.
