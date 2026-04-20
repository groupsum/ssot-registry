# Repo Touchpoints

Use this checklist when the request involves actual repository delivery work:

- `pkgs/ssot-contracts/src/ssot_contracts/schema/` for packaged schemas
- `pkgs/ssot-contracts/src/ssot_contracts/templates/` when generated or checked-in templates must stay aligned
- `pkgs/ssot-core/src/ssot_registry/model/` for schema-facing types
- `pkgs/ssot-core/src/ssot_registry/api/` for load, validate, mutate, freeze, release, or upgrade behavior
- `pkgs/ssot-core/src/ssot_registry/guards/` when gates change
- `pkgs/ssot-cli/src/ssot_cli/` when CLI surface or flags change
- `tests/` for unit, integration, contract, and migration coverage

Use only the touched surfaces required by the frozen scope.
