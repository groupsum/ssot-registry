# ADR-0010: Generated projections are non-canonical

## Status
Draft

## Decision
Only upstream authored sources are canonical.

Generated projections include:

- graph/report artifacts,
- `docs/**` mirrors,
- packaged template docs and manifests under `pkgs/ssot-registry/src/ssot_registry/templates/**`.

## Consequences
- Canonical authorship remains singular.
- Projection generation MUST be deterministic.
- Manual edits to generated projections are treated as drift.
