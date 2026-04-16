# ADR-0500: Monorepo package topology under `pkgs/`

## Status
Draft

## Decision

All publishable packages SHALL live under `pkgs/`.

Initial package set:

- `ssot-registry`
- `ssot-contracts`
- `ssot-views`
- `ssot-codegen`
- `ssot-cli`
- `ssot-tui`

Deferred package:

- `ssot-registry-npm`

## Consequences

- Root-level tooling becomes workspace-oriented.
- Package boundaries are explicit and versionable.
