---
name: ssot-implementation-and-migration-delivery
description: Guide SSOT implementation work after scope freeze, including schema changes, code changes, schema version advancement, migration updates, and test coverage aligned with the frozen boundary. Use when Codex needs repo-specific delivery guidance for implementing governed changes in this ssot-registry repository.
---

# SSOT Implementation And Migration Delivery

Use this skill after the boundary is frozen and the task is to deliver the governed change in code, schemas, migrations, and tests. In many real workflows this is the largest phase between freeze and any later proof/certification work.

## Repo checklist

- update packaged schemas in `pkgs/ssot-contracts/src/ssot_contracts/schema/`
- update canonical runtime models and APIs in `pkgs/ssot-core/src/ssot_registry/model/` and `pkgs/ssot-core/src/ssot_registry/api/`
- update CLI surface in `pkgs/ssot-cli/src/ssot_cli/` when command behavior or flags change
- update upgrade-path logic in `pkgs/ssot-core/src/ssot_registry/api/upgrade.py`
- update tests and checked-in schema or report fixtures when behavior changes

## Workflow

1. Confirm the frozen boundary and the target features being delivered.
2. Map each required code or schema change back to the governed feature set.
3. Implement schema and runtime changes.
4. If the schema is broken compatibly or incompatibly, advance the schema version and add migration coverage.
5. Add or update tests for behavior, CLI, and migrations.
6. Keep feature implementation state aligned with code reality.
7. Hand off to proof/certification only after the frozen implementation is real and verifiable.

## Operating rules

- Breaking schema changes require schema-version advancement and migration logic.
- Do not treat implementation as complete until tests and migration coverage exist.
- Freeze locks scope. It does not eliminate the need for post-freeze implementation, migration, and verification work.
- If the request also needs claims, evidence, or release work, escalate to `$ssot-e2e-change-orchestrator` or hand off to `$ssot-proof-chain-and-certification`.
- Read `references/repo-touchpoints.md` before giving concrete edit guidance.

## References

- `references/repo-touchpoints.md`
- `references/migration-rules.md`
- `references/test-coverage-notes.md`
