# ADR-0506: Hybrid package versioning policy

## Status
Draft

## Decision

Python package versioning SHALL follow a hybrid model.

- `ssot-contracts`, `ssot-views`, `ssot-codegen`, and `ssot-registry` SHALL remain in lockstep.
- `ssot-cli` and `ssot-tui` SHALL version independently.
- Surface packages SHALL depend on compatible released `ssot-registry` ranges rather than exact lockstep versions.

## Consequences

- Core compatibility stays explicit and easy to validate.
- UI surfaces can ship independently without forcing a full core release train.
