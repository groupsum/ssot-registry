# ADR-0013: Enforce max path and filename lengths under `.ssot`

## Status
Accepted

## Decision
Files under `.ssot` MUST respect these limits:

- Maximum relative path length: **240** characters.
- Maximum filename length: **120** characters.

Validation fails when either limit is exceeded.

## Consequences
- Repositories get deterministic, cross-platform-safe path constraints.
- Oversized paths fail early during validation instead of surfacing later in tooling workflows.
- Existing registries do not require schema migration because this is a validation policy change.
