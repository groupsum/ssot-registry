# ADR-0013: Enforce max path and filename lengths under `.ssot`

- Status: accepted
- Date: 2026-04-15

## Context

The `.ssot` directory is intended to be portable across developer environments and CI systems. In practice, very long paths and filenames create brittle behavior across filesystems, archive tools, and downstream integrations.

## Decision

We enforce hard limits for any file path that lives under `.ssot`:

- Maximum relative path length: **240** characters.
- Maximum filename length: **120** characters.

Validation fails when either limit is exceeded.

## Consequences

- Repositories get deterministic, cross-platform-safe path constraints.
- Oversized paths fail early during validation instead of surfacing later in tooling or packaging workflows.
- Existing registries do not require schema migration; this is a validator policy change.
