---
name: ssot-decision-to-scope
description: Drive the early SSOT workflow from decision through governed scope definition by creating or updating ADRs, SPECs, and target features with explicit document-to-feature mapping. Use when Codex needs to turn a proposed change into repo-local ADRs, specs, feature rows, and planning metadata before boundary freeze.
---

# SSOT Decision To Scope

Use this skill for the pre-freeze planning phase. The output is a governed scope definition, not implementation.

## Goals

- Create or update ADRs and SPECs that define the change.
- Create the target features and set their planning fields.
- Make the mapping from each ADR or SPEC to governed feature IDs explicit.

## Workflow

1. Inspect ADR, SPEC, and feature state if numbering or IDs are unclear.
2. Reserve document numbers when deterministic numbering matters.
3. Create or update repo-local ADRs and SPECs.
4. Create the governed feature rows.
5. Set planning fields with `feature plan`.
6. Link documents and features so the scope definition is inspectable.
7. If the request also includes test creation for the same scoped change, hand off to `$ssot-feature-test-linking` after the feature rows and planning metadata exist.

## Operating rules

- Do not freeze a boundary from this skill; hand off to `$ssot-scope-to-frozen-boundary`.
- Treat this skill as the first half of a pre-freeze scoped flow when the user asks for ADR + SPEC + feature + test setup.
- Require an explicit document-to-feature mapping in the response or links.
- Prefer `ssot adr|spec create|update|sync` over editing files by hand.
- If the request already includes freeze, implementation, migration, or release work, escalate to `$ssot-e2e-change-orchestrator`.

## Common commands

```powershell
ssot adr list .
ssot spec list .
ssot feature list .
ssot adr reserve create . --kind adr
ssot spec reserve create . --kind spec
ssot adr create . --title "..." --slug "..." --body-file adr-body.yaml
ssot spec create . --title "..." --slug "..." --body-file spec-body.yaml
ssot feature create . --id feat:demo.change --title "Demo change"
ssot feature plan . --ids feat:demo.change --horizon current --claim-tier T1 --target-lifecycle-stage active
ssot adr sync .
ssot spec sync .
```

## References

- `references/doc-to-feature-mapping.md`
- `references/decision-checklist.md`
