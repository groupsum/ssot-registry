# ADR-0609: Generated projections are non-canonical

## Status
Draft

## Decision
This is an `ssot-origin` ADR copied into downstream SSOT repositories.

In an operator repository, canonical authored SSOT content lives under `.ssot/`:

- `.ssot/registry.json`,
- repo-local ADRs under `.ssot/adr/`,
- repo-local specs under `.ssot/specs/`.

Packaged `ssot-origin` ADRs/specs provide baseline policy, but operators do not edit those synced copies directly.

Generated projections include:

- graph exports,
- reports and snapshots,
- rendered or exported representations such as CSV, YAML, TOML, DOT, PNG, and SVG,
- mirrored or regenerated documentation derived from the canonical SSOT content.

## Consequences
- Operators SHALL edit repo-local canonical SSOT content, not derived projections.
- Operators SHALL treat synced `ssot-origin` docs as immutable baseline content.
- Projection generation MUST be deterministic.
- Manual edits to generated projections are treated as drift and MAY be overwritten by regeneration.

