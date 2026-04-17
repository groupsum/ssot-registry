# SPEC-0509: Workflow contract for package CI/build/publish

## Status
Draft

## Requirements

- CI SHALL build packages from `pkgs/<name>`.
- CI SHALL fail if release workflows rely on root `uv build` or root package version metadata.
- Package publish workflows SHALL validate package-local tags and versions before publishing.
- Reusable workflows SHALL define the shared package CI and package publish contract.
