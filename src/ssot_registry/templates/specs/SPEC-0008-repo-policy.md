# Repository policy

This file is seeded into your repository by `ssot-registry init` / `sync`.

## Scope

This spec is part of your operator contract in `.ssot/specs`.
Use it for repository-local policy that applies to your repo.

## SSOT core vs repo-local documents

- Seeded core ADRs/SPECs are `origin: ssot-core` and immutable unless replaced by newer packaged content.
- Repository-specific ADRs/SPECs are `origin: repo-local` and are mutable by your repository.
- Core ADR/SPEC ranges `1..999` are reserved for `origin: ssot-core` and are not repo-assignable.
- Repo-local ADR/SPEC ranges `1000..4999` are assignable for `origin: repo-local` by your repository.

## Required locations

- ADR files SHALL live under `.ssot/adr`.
- SPEC files SHALL live under `.ssot/specs`.
- Registry metadata SHALL keep ADR/SPEC records under top-level `adrs` and `specs` in `.ssot/registry.json`.

Repository-local policy belongs in `.ssot/specs/SPEC-0008-repo-policy.md`.
Portable defaults are strict and fail closed.
