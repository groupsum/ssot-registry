# File tree

## Purpose and scope (maintainer-only)

This spec defines the required `.ssot` filesystem layout that `ssot-registry` MUST initialize, sync, and validate.
It also defines the source locations maintainers MUST keep aligned when publishing ADR/SPEC contracts.

## Maintainer source and packaged output

Maintainer governance sources:

- `docs/adr/**`
- `docs/specs/**`

Packaged operator contract sources:

- `src/ssot_registry/templates/adr/**`
- `src/ssot_registry/templates/specs/**`

Maintainers SHALL ensure packaged templates produce a conformant `.ssot` tree in operator repositories.

## Required `.ssot` tree in operator repositories

```text
.ssot/
  registry.json
  schemas/
  adr/
    ADR-0001-canonical-json-registry.md
  specs/
    SPEC-0001-registry-core.md
  evidence/
  graphs/
  reports/
  releases/
  cache/
```

## ADR/SPEC placement and metadata rules

- ADR markdown files SHALL resolve under `.ssot/adr`.
- SPEC markdown files SHALL resolve under `.ssot/specs`.
- `.ssot/registry.json` SHALL expose top-level `adrs` and `specs` arrays.
- Core seeded documents SHALL be represented as `origin: ssot-core` and immutable.
- Repo-local documents SHALL be represented as `origin: repo-local`.
