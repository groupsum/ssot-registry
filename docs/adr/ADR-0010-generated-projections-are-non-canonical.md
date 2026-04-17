# ADR-0010: Generated projections are non-canonical

## Status
Draft

## Decision
In the `ssot-registry` upstream repository, canonical authored sources are the package-owned contract and runtime artifacts that maintainers edit directly.

Generated projections include:

- mirrored maintainer docs under `docs/**`,
- packaged operator-facing document copies emitted from upstream contract sources,
- generated metadata, reports, snapshots, and graph exports,
- rendered assets such as CLI/TUI screenshots and exported SVG/PNG/DOT artifacts.

## Consequences
- Maintainers SHALL edit upstream canonical sources rather than mirrored or generated projections.
- Projection generation MUST be deterministic.
- Manual edits to generated projections are treated as drift and MAY be overwritten by regeneration.
