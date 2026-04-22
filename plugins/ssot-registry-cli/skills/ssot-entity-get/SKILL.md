---
name: ssot-entity-get
description: Get a single SSOT entity by ID across ADR, SPEC, feature, profile, test, issue, claim, evidence, risk, boundary, and release surfaces. Use when Codex should inspect one entity deeply before mutation, linking, review, or lifecycle decisions.
---

# SSOT Entity Get

Use this skill when the user asks to fetch or inspect one specific entity. Prefer direct `get` calls before proposing edits.

## Command surface

- `adr get`, `spec get`, `feature get`, `profile get`, `test get`, `issue get`, `claim get`, `evidence get`, `risk get`, `boundary get`, `release get`

## Workflow

1. Identify the entity family from the ID prefix (`adr:`, `spec:`, `feat:`, `prof:`, `tst:`, `iss:`, `clm:`, `evd:`, `rsk:`, `bnd:`, `rel:`).
2. Run the matching `<entity> get` command.
3. Return the important fields first: ID, title/summary, lifecycle or status, and linked IDs.
4. If the entity is missing, confirm with `<entity> list` filters before creating anything new.

## Operating rules

- Use CLI output as source of truth; do not infer entity details from stale docs.
- Prefer `get` over broad `list` when the user already provided an ID.
- If the user requests edits after inspection, hand off to the specific CRUD/linking skill for that surface.

## Examples

```powershell
ssot-registry feature get . --id feat:demo.login
ssot-registry claim get . --id clm:demo.login.t1
ssot-registry release get . --id rel:demo.2026q2
```

