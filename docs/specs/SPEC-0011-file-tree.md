# File tree

## Status
Draft

Your repository MUST maintain the following `.ssot` tree:

```text
.ssot/
  registry.json
  schemas/
  adr/
  specs/
  evidence/
  graphs/
  reports/
  releases/
  cache/
```

## ADR/SPEC contract

- ADR files SHALL be stored under `.ssot/adr`.
- SPEC files SHALL be stored under `.ssot/specs`.
- `.ssot/registry.json` SHALL track ADR/SPEC metadata in top-level `adrs` and `specs` sections.
- Synced packaged documents use `origin: ssot-origin` and are immutable.
- Repository-authored documents use `origin: repo-local` and are mutable.
- `origin: ssot-core` is upstream-only and is not valid in operator repositories.
