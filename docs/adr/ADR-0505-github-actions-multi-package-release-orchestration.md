# ADR-0505: GitHub Actions multi-package release orchestration

## Status
Draft

## Decision

GitHub Actions SHALL use one central release orchestrator workflow plus normalized package publish workflows.

- `release.yml` validates release policy and drives package publication in canonical order.
- `publish-ssot-*.yml` workflows own package-local tag, build, release, and PyPI publish behavior.
- Reusable workflows SHALL hold the shared package CI and publish logic.

## Consequences

- Release logic is package-aware rather than root-package-aware.
- Per-package workflows remain manually callable without diverging from the orchestrated path.
