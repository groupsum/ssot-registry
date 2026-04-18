---
name: ssot-adr-spec-crud
description: Create, update, delete, reserve, sync, and inspect SSOT ADR and SPEC documents in repository-local `.ssot/adr` and `.ssot/specs` trees. Use when Codex needs to CRUD ADRs or SPECs, reserve numbers, sync document metadata into `.ssot/registry.json`, or connect architectural/spec changes to feature and release work.
---

# SSOT ADR/SPEC CRUD

Use this skill for document-level SSOT work around ADRs and SPECs. Prefer the CLI over editing `.ssot/registry.json` directly so filenames, numbering, slugs, and registry metadata stay aligned.

## Command surface

- ADRs: `adr create|get|list|update|delete|sync|reserve create|reserve list`
- SPECs: `spec create|get|list|update|delete|sync|reserve create|reserve list`
- Prefer `ssot ...` in new commands; accept `ssot-registry ...` when the user names it.

## Workflow

1. Inspect current state first with `adr list` or `spec list` when numbering or collisions are unclear.
2. Reserve numbers before creating repo-local documents when the user cares about deterministic numbering.
3. Create or update the document with a body file and explicit `--slug`; use YAML bodies when the repo is treating ADR/SPEC files as canonical SSOT documents.
4. Run `adr sync` or `spec sync` after document changes so `.ssot/registry.json` reflects file contents.
5. If the document affects implementation planning, follow by linking the impacted features, claims, tests, boundaries, or releases with the other SSOT skills.

## Operating rules

- Repository-local ADRs live under `.ssot/adr`; SPECs live under `.ssot/specs`.
- Treat packaged `ssot-origin` ADRs and specs as upstream inputs; do not rewrite synced template copies unless the user explicitly asks.
- Prefer `create` and `update` over hand-authoring filenames; the CLI enforces `ADR-NNNN-slug.yaml` and `SPEC-NNNN-slug.yaml`.
- Use `sync` after file edits done outside the CLI.
- Delete only when the user explicitly wants removal; otherwise prefer updating status/body to preserve history.

## Examples

```powershell
ssot adr create . --title "Use repo-local ADR numbering" --slug use-repo-local-adr-numbering --body-file adr-body.yaml
ssot spec create . --title "Maintainer operating conventions" --slug maintainer-operating-conventions --body-file spec-body.md --kind operational
ssot adr sync .
ssot spec sync .
```

## Source of truth

- `README.md` ADR/SPEC command sections
- `README.md` "E2E example 1b: create repo-local ADRs and specs"
- `pkgs/ssot-core/src/ssot_registry/api/documents.py`
