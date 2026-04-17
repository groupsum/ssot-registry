# Agent Instructions

## SSOT Operating Rule

- Treat `ssot-registry` as the authoritative SSOT runtime.
- Treat `ssot-cli` as the primary CLI distribution for that runtime.
- Treat `ssot`, `ssot-cli`, and `ssot-registry` as equivalent executables over the same parser and runtime.
- In this repository, use the `ssot-registry` CLI surface for SSOT operations unless the task is explicitly about implementing the runtime/CLI itself.

## Strict CLI Requirement

- Do not manually mutate SSOT state in `.ssot/registry.json`.
- Do not hand-edit `.ssot/adr/*` or `.ssot/specs/*` in order to create, delete, renumber, reserve, sync, supersede, or lifecycle-manage documents.
- Do not hand-edit downstream/operator SSOT fixtures to enact registry changes when the CLI can perform the operation.
- Use the CLI to inspect state as well when practical: `list`, `get`, `validate`, `registry export`, `graph export`.

## Preferred Workflows

- Initialize repos with `ssot-registry init`.
- Validate after SSOT changes with `ssot-registry validate`.
- Upgrade older repos with `ssot-registry upgrade --sync-docs --write-report`.
- Manage ADRs with `ssot-registry adr ...`.
- Manage specs with `ssot-registry spec ...`.
- Manage features, profiles, tests, issues, claims, evidence, risks, boundaries, and releases with the corresponding `ssot-registry` noun command.
- Sync managed ADR/spec content with `ssot-registry adr sync` and `ssot-registry spec sync`.
- Export machine-readable views with `ssot-registry registry export` and `ssot-registry graph export`.

## Document-Origin Model

- `ssot-core` is upstream-maintainer-facing content for `ssot-registry`.
- Canonical `ssot-core` ADRs/specs live in `.ssot/adr/` and `.ssot/specs/`.
- `docs/adr/` and `docs/specs/` are maintainer-facing mirrors of `.ssot/`.
- In the upstream `ssot-registry` repository, root `.ssot/` is `ssot-core` only.

- `ssot-origin` is packaged downstream/public-operator content.
- Canonical `ssot-origin` templates live in `pkgs/ssot-contracts/src/ssot_contracts/templates/`.
- `pkgs/ssot-registry/src/ssot_registry/templates/` mirrors those packaged templates.
- Template manifest `target_path` values intentionally point at downstream `.ssot/...` locations because operator repositories materialize synced `ssot-origin` docs under their own `.ssot/`.
- Those downstream target paths do not mean the upstream repo's root `.ssot/` should contain `ssot-origin` docs.

- `repo-local` is authored by a downstream repository for its own local decisions and policies.

## Reserved Ranges

- `ssot-core`: `ADR-0001..0599`, `SPEC-0001..0599`
- `ssot-origin`: `ADR-0600..0999`, `SPEC-0600..0999`
- `repo-local`: `ADR-1000..4999`, `SPEC-1000..4999`

## Allowed Exceptions

- Editing `pkgs/ssot-registry`, `pkgs/ssot-cli`, tests, schemas, docs, or templates as source code is normal when the task is to implement or repair the packages themselves.
- For upstream repository maintenance, do not hand-edit mirrors or packaged manifests; run `python scripts/sync_packaged_docs.py` after changing canonical `.ssot/` docs or packaged template sources.
- If a task explicitly requires changing runtime behavior or fixing CLI implementation, edit the code directly and then use the CLI to validate the behavior.
