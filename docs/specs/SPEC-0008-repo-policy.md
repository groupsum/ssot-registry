# Repository policy

## Status
Draft

## Purpose and scope (maintainer-only)

This spec is maintainer-facing guidance for the `ssot-registry` repository itself.
It governs how maintainers publish operator-facing ADR/SPEC contracts and how repo-local operator policy is supported.

Stability: accepted.
Operational impact: affects packaged templates and validator behavior.
Promotion criterion: maintainer-only guidance is promoted into templates only when it becomes an operator requirement.

## Documentation layers

`ssot-registry` has two documentation layers:

1. Maintainer governance docs in this repository:
   - `docs/adr/**`
   - `docs/specs/**`
2. Packaged operator-facing core docs distributed into user repos:
   - `src/ssot_registry/templates/adr/**`
   - `src/ssot_registry/templates/specs/**`

Maintainer-only rules SHALL stay in `docs/**`.
Operator-required rules SHALL be published in `src/ssot_registry/templates/**` (and MAY be mirrored in `docs/**` for readability).

## Origin and mutability policy

- Packaged template ADRs/SPECs are `origin: ssot-core`, managed, and immutable in operator repos.
- Repo-local ADRs/SPECs are `origin: repo-local`, mutable, and owned by the operator repository.
- Maintainers SHALL keep this distinction explicit in specs and templates.

## Numbering and reservation policy

- Core reserved ranges are non-assignable by repos: `1..999` for ADR and SPEC.
- Repo-local default ranges are assignable by repos: `1000..4999` for ADR and SPEC.
- Maintainers SHALL ship defaults and validation behavior consistent with these ranges.

## File-tree conformance policy

Maintainers SHALL deliver `ssot-registry` so initialized repositories conform to:

- `.ssot/adr` for ADR files,
- `.ssot/specs` for SPEC files,
- top-level `adrs` and `specs` sections in `.ssot/registry.json`.

Repository-local policy belongs in `.ssot/specs/SPEC-0008-repo-policy.md`.
Portable defaults are strict and fail closed.
