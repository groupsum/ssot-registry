# SPEC-0512: Document origin boundaries and ID ranges

## Status
Draft

## Scope

This is an `ssot-core` maintainer specification for the upstream `ssot-registry` repository.

## Rules

- Upstream `ssot-core` ADRs and specs SHALL be authored canonically under `.ssot/adr/` and `.ssot/specs/` in `ssot-registry`.
- `docs/adr/` and `docs/specs/` are maintainer-facing mirrors of the upstream `ssot-core` inventory.
- Packaged downstream templates SHALL live under `pkgs/ssot-contracts/src/ssot_contracts/templates/`.
- Packaged template ADRs/specs are `ssot-origin` content intended to be copied into operator repositories.
- Repo-local ADRs/specs are authored inside downstream repositories under `.ssot/adr/` and `.ssot/specs/`.

## Number ranges

- `ADR-0001..ADR-0599` and `SPEC-0001..SPEC-0599` are reserved for `ssot-core`.
- `ADR-0600..ADR-0999` and `SPEC-0600..SPEC-0999` are reserved for `ssot-origin`.
- `ADR-1000..ADR-4999` and `SPEC-1000..SPEC-4999` are reserved for repo-local downstream use.

## Uniqueness

- ADR numbers SHALL be unique across `ssot-origin`, `ssot-core`, and repo-local scopes.
- SPEC numbers SHALL be unique across `ssot-origin`, `ssot-core`, and repo-local scopes.
- Upstream maintainers SHALL NOT publish core ADRs or specs that reuse an `ssot-origin` number.
- Packaged `ssot-origin` templates SHALL NOT consume `ssot-core` or repo-local ranges.

## Consequences

- `docs/` is not a mirror of downstream templates.
- `.ssot/` in `ssot-registry` is the canonical `ssot-core` source for upstream governance docs.
- Public operator docs stay downstream-facing and MUST avoid upstream repository layout assumptions.
- Range and collision checks MUST fail CI when the inventories drift.
