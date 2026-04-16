# SPEC-0511: Release train order and compatibility gates

## Status
Draft

## Release order

1. `ssot-contracts`
2. `ssot-views`
3. `ssot-codegen`
4. `ssot-registry`
5. `ssot-cli`
6. `ssot-tui`

## Compatibility gates

- Core packages SHALL share one version.
- Core package dependencies SHALL pin the shared core version exactly.
- `ssot-cli` and `ssot-tui` SHALL depend on a compatible `ssot-registry` range.
- Release automation SHALL validate train order and dependency constraints before tags are created.
