# Registry core

## Status
Draft

The canonical registry is `.ssot/registry.json`.

## Repository discriminator

`repo.kind` is required and MUST be one of:

- `ssot-upstream`
- `operator-repo`

## Top-level sections

- `schema_version`
- `repo`
- `tooling`
- `paths`
- `program`
- `guard_policies`
- `document_id_reservations`
- `features`
- `profiles`
- `tests`
- `claims`
- `evidence`
- `issues`
- `risks`
- `boundaries`
- `releases`
- `adrs`
- `specs`

## ADR/SPEC row contract

ADR and SPEC rows MUST include:

- identity/location: `id`, `number`, `slug`, `title`, `path`
- provenance/materialization: `origin`, `managed`, `immutable`, `package_version`, `content_sha256`
- lifecycle/supersession: `status`, `supersedes`, `superseded_by`, `status_notes`

Allowed `origin` values:

- `ssot-core`
- `ssot-origin`
- `repo-local`

SPEC `kind` is a non-provenance label and MUST be one of:

- `normative`
- `operational`
- `governance`
- `local-policy`
