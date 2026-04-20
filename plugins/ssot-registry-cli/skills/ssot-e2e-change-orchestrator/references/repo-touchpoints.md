# Repo Touchpoints

For this repository, end-to-end changes often touch:

- `.ssot/adr/` and `.ssot/specs/` for governed docs
- `.ssot/registry.json` through SSOT CLI sync or entity commands
- `pkgs/ssot-contracts/src/ssot_contracts/schema/` for packaged schemas
- `pkgs/ssot-core/src/ssot_registry/model/` for canonical model changes
- `pkgs/ssot-core/src/ssot_registry/api/` for runtime APIs and upgrade paths
- `pkgs/ssot-cli/src/ssot_cli/` for command-surface changes
- `tests/` and checked-in report or schema fixtures when behavior or migrations change

Read the relevant phase skill before giving concrete instructions.
