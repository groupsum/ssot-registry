# ADR-0501: Contracts, views, and codegen split

## Status
Draft

## Decision

- `ssot-contracts` owns canonical schemas, manifests, packaged templates, and generated contract metadata.
- `ssot-views` owns derived projections and report / graph builders.
- `ssot-codegen` generates derived Python artifacts from contracts and views.
- `ssot-registry` remains the runtime behavior engine.

## Consequences

- Static definitions move out of the runtime package.
- UI and future npm consumers can share generated metadata.
