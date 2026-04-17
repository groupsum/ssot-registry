# ADR-0010: Generated projections are non-canonical

## Status
Draft

## Decision
In the upstream `ssot-registry` repository, canonical governance documents are the `ssot-core` ADRs and specs authored under `.ssot/`.

Generated projections include:

- graph/report artifacts,
- maintainer-facing `docs/**` mirrors,
- packaged `ssot-origin` template docs and manifests under `pkgs/ssot-contracts/src/ssot_contracts/templates/**`,
- mirrored package copies under `pkgs/ssot-registry/src/ssot_registry/templates/**`.

## Consequences
- Maintainers SHALL edit upstream `.ssot/**` sources, not their mirrors or packaged copies.
- Projection generation MUST be deterministic.
- Manual edits to generated projections are treated as drift.
