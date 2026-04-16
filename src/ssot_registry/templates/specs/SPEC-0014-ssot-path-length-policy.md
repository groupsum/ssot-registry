# SSOT path-length policy

## Scope

This specification defines path and filename limits for artifacts stored under `.ssot/`.

## Rules

For any file path that is under `.ssot`:

1. The full repository-relative path MUST be at most **240** characters.
2. The filename component MUST be at most **120** characters.

These limits apply to:

- Declared `.ssot` paths in registry entities (for example evidence/documents).
- Materialized files physically present under `.ssot`.

## Enforcement

Validation MUST fail when either rule is violated.
