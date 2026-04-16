# File tree

Your repository MUST maintain the following `.ssot` tree:

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

## ADR/SPEC contract

- ADR files SHALL be stored under `.ssot/adr`.
- SPEC files SHALL be stored under `.ssot/specs`.
- `.ssot/registry.json` SHALL track ADR/SPEC metadata in top-level `adrs` and `specs` sections.
- Seeded core documents are `origin: ssot-core` and immutable.
- Repository-authored documents are `origin: repo-local` and mutable according to your repo policy.
- Core reserved ranges are `1..999`; repo-local default assignable ranges are `1000..4999`.
