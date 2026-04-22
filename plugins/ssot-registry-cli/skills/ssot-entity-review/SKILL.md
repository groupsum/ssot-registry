---
name: ssot-entity-review
description: Review SSOT entities for correctness, completeness, and readiness by combining get/list inspection with evaluation and verification commands where supported. Use when Codex should judge whether entities are healthy or ready, not just display them.
---

# SSOT Entity Review

Use this skill for quality and readiness checks across entity types.

## Command surface

- Core inspection: `<entity> get`, `<entity> list`
- Review-focused verbs: `profile evaluate`, `profile verify`, `claim evaluate`, `claim set-status`, `claim set-tier`, `evidence verify`, `risk mitigate|accept|retire`
- Repo-level guard: `validate`

## Workflow

1. Start with `get`/`list` on in-scope entities.
2. Run review verbs for the entity families that support them.
3. Check linked proof-chain context (feature, claim, test, evidence) where release-readiness is implied.
4. Run `ssot-registry validate .` before finalizing findings.

## Operating rules

- Separate factual inspection from judgment: list/get first, evaluate/verify second.
- If the user asks for broad lifecycle execution from decision to release, escalate to `$ssot-e2e-change-orchestrator`.
- Keep review outputs actionable: state what fails, why, and what command can fix it.

## Examples

```powershell
ssot-registry profile evaluate . --id prof:security.default
ssot-registry claim evaluate . --id clm:demo.login.t1
ssot-registry evidence verify . --id evd:demo.login.pytest
ssot-registry validate . --write-report
```

