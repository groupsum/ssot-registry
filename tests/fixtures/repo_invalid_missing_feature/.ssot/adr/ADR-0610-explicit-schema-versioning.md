# ADR-0610: Explicit schema versioning

## Status
Draft

## Decision
Breaking schema changes increment `schema_version` and require migration.

## Consequences
- No compatibility shims.
- No ambiguous reader behavior.

