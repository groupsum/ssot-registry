# Repository policy

## Status
Draft

This file is seeded into your repository by `ssot-registry init` / `sync`.

## Scope

This is part of your operator contract in `.ssot/specs`.

## Origin model

- `ssot-origin`: packaged contract docs synced from `ssot-registry` and immutable in operator repos.
- `repo-local`: docs authored by your repository and editable locally.
- `ssot-core`: upstream-only governance and not permitted in operator repositories.

## Numbering and reservations

- `1..499` is reserved for `ssot-origin` docs.
- `500..999` is reserved for upstream `ssot-core` governance.
- `1000..4999` is assignable to `repo-local` docs.

## Required locations

- ADR files SHALL live under `.ssot/adr`.
- SPEC files SHALL live under `.ssot/specs`.
- Registry metadata SHALL keep ADR/SPEC records under top-level `adrs` and `specs` in `.ssot/registry.json`.
