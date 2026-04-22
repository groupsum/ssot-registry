---
name: ssot-entity-list
description: List SSOT entities by family and filter criteria across ADR, SPEC, feature, profile, test, issue, claim, evidence, risk, boundary, and release. Use when Codex needs inventories, gap scans, or quick state overviews from CLI truth.
---

# SSOT Entity List

Use this skill when the request is inventory-shaped: "list all", "show current", "what exists", or "what is missing".

## Command surface

- `adr list`, `spec list`, `feature list`, `profile list`, `test list`, `issue list`, `claim list`, `evidence list`, `risk list`, `boundary list`, `release list`

## Workflow

1. Determine which entity families are in scope.
2. Run one `list` command per requested family instead of mixing manual file scans.
3. Apply filters/format options when available to keep output focused.
4. Summarize totals and key slices (for example current vs explicit horizons for features).

## Operating rules

- Prefer multiple narrow list commands over one broad dump.
- Keep output tied to user intent: IDs and titles for inventories, status/lifecycle for health views.
- If the user asks for relationships across families, escalate to `$ssot-entity-analyze`.
- If a list request becomes a mutation request for one entity family, route to that per-entity skill (`$ssot-adr`, `$ssot-spec`, `$ssot-feature`, `$ssot-profile`, `$ssot-test`, `$ssot-issue`, `$ssot-claim`, `$ssot-evidence`, `$ssot-risk`, `$ssot-boundary`, `$ssot-release`).

## Examples

```powershell
ssot-registry feature list .
ssot-registry test list .
ssot-registry --output-format csv claim list .
```
